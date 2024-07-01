from .serializers import *
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User
from django.shortcuts import render, get_object_or_404
from rest_framework.views import APIView
from rest_framework.authtoken.models import Token
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import generics, status
from .models import *
from django.views.generic import View
from django.core.mail import send_mail
from django.conf import settings
from django.utils import timezone
from django.contrib.auth import login, logout, authenticate


def register_user(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        email = request.POST['email']
        is_staff = request.POST.get('is_staff', 'off') == 'on'

        user = User.objects.create_user(
            username=username, password=password, email=email)
        user.is_staff = is_staff
        user.save()

        return HttpResponse(f'User {username} registered successfully')

    return render(request, 'register.html')


class LoginView(APIView):

    def post(self, request):
        user_id = request.data.get('user_id')
        password = request.data.get('password')
        # print(user_id,password)
        user = authenticate(request, username=user_id, password=password)

        if user is not None:
            token, created = Token.objects.get_or_create(user=user)

            login(request, user)

            return Response({
                'status': 'success',
                'message': 'Login Successful',
                'token': token.key,
                'is_staff': user.is_staff
            }, status=status.HTTP_200_OK)

        else:
            return Response({"error": "Invalid User ID or Password"}, status=status.HTTP_400_BAD_REQUEST)


# Register/Schedule Visitor
class RegisterVisitorView(generics.CreateAPIView):
    serializer_class = VisitorSerializer
    # only authenticated user(attendant/staff) can register a visitor
    # permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        # create new visitor instance
        visitor = serializer.save()
        
        # save visitor instance in the VLog db
        # attendant = get_object_or_404(Attendant, user=self.request.user)
        attendant = self.request.user

        # create a new instance of the newly registered visitor and store in the visitorlog db
        VisitorLog.objects.create(
                visitor=visitor,
                staff=visitor.whomToSee,
                attendant=attendant,
                checkInTime=timezone.now(),
            )

        # send visitor's details to the expected staff
        
        firstName, lastName = self.request.data.get('whomToSeeInput').split(maxsplit=1)
        # print(firstName, lastName) 
        # print(visitor.whomToSee)
        try:
            staffMember = Staff.objects.get(firstName=firstName.lower(), lastName=lastName.lower())
            print(staffMember)
        except Staff.DoesNotExist:
            return Response({'error': f'Staff with name "{firstName}, {lastName}" does not exist'}, status=status.HTTP_400_BAD_REQUEST)
        
        VisitRequest.objects.create(
            visitor=visitor,
            staff=staffMember,
            # attendant=attendant,
            status=VisitRequest.PENDING,
        )

        return Response(serializer.data, status=status.HTTP_201_CREATED)
                # Send email notification to the staff member
                # subject = 'New Visitor Request'
                # message = f'Hello {staff.name},\n\nYou have a new visitor request.\nVisitor Details:\nName: {visitor.firstName} {visitor.lastName}\nEmail: {visitor.email}\nPhone: {visitor.phoneNumber}\n\nPlease login to your account to approve or decline the request.\n\nBest regards,\nIGCOMSAT'

                # send_mail(subject, message, settings.EMAIL_HOST_USER, [staff.email])


# Render all visitors
class ListVisitorView(generics.ListAPIView):
    serializer_class = VisitorSerializer
    # permission_classes = [IsAuthenticated]

    # queryset to return all the visitors
    queryset = Visitor.objects.all()
    def get_queryset(self):
        return Visitor.objects.all().select_related('whomToSee', 'department')


# Render all staff
class ListStaffView(generics.ListAPIView):
    serializer_class = StaffSerializer
    queryset = Staff.objects.all()
    def get_queryset(self):
        return Staff.objects.all().select_related('department')

# Render all visitors that have been approved and checkout
class ListVisitorLogView(generics.ListAPIView):
    serializer_class = VisitorLogSerializer
    # permission_classes = [IsAuthenticated]

    # queryset to return all the visitors
    queryset = VisitorLog.objects.all().select_related('visitor', 'staff')  # visitorlog instead of visitor


# Accept Visitors Request
class AcceptVisitRequest(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, pk):
        visitRequest = VisitRequest.objects.get(id=pk)

        # if visitRequest.staff != request.user:
        #     return Response({'error': 'You do not have permission to make this decision.'}, status=status.HTTP_403_FORBIDDEN)

        try:
            visitRequest.status = VisitRequest.APPROVED
            visitRequest.save()

            # feedback = request.data.get('feedback')
            # if feedback:
            #     visitRequest.feedback = feedback
            #     visitRequest.save()

            # update Approval field for visitor
            visitor = visitRequest.visitor
            visitor.isApproved = True
            visitor.save()

            return Response({"message": "Request Approved"}, status=status.HTTP_200_OK)

        except VisitRequest.DoesNotExist:
            return Response({"error": "Request Not found"}, status=status.HTTP_404_NOT_FOUND)


# Decline Visitors Request
class DeclineVisitRequest(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, pk):
        visitRequest = VisitRequest.objects.get(id=pk)

        # if visitRequest.staff != request.user:
        #     return Response({'error': 'You do not have permission to make this decision.'}, status=status.HTTP_403_FORBIDDEN)
        try:
            visitRequest.status = VisitRequest.DECLINED
            visitRequest.save()

            # Update Approval field for visitor
            visitor = visitRequest.visitor
            visitor.isApproved = False
            visitor.save()

            return Response({"message": "Request Approved"}, status=status.HTTP_200_OK)

        except VisitRequest.DoesNotExist:
            return Response({"error": "Request Not found"}, status=status.HTTP_404_NOT_FOUND)


# Check out visitor view from the approval list
class CheckoutVisitorView(View):
    def post(self, request, pk):
        try:
            visitorLog = VisitorLog.objects.get(id=pk)
            visitorLog.checkOutTime = timezone.now()
            visitorLog.save()

            # update the approved list
            visitor = VisitorLog.visitor
            visitor.isApproved = False
            visitor.checkOut = True
            visitor.save()

            return Response({'message': 'Checkout successful'}, status=status.HTTP_200_OK)
        except VisitorLog.DoesNotExist:
            return Response({'message': 'Visitor not found'}, status=status.HTTP_400_BAD_REQUEST)


# Check in a vistor from the waiting list
class CheckInVisitorView(View):
    def post(self, request, pk):
        try:
            visitorLog = VisitorLog.objects.get(id=pk)
            visitorLog.checkInTime = timezone.now()
            visitorLog.save()

            # update the approved list
            visitor = VisitorLog.visitor
            visitor.isApproved = True
            visitor.checkOut = False
            visitor.save()

            return Response({'message': 'CheckIn successful'}, status=status.HTTP_200_OK)
        except VisitorLog.DoesNotExist:
            return Response({'message': 'Visitor not found'}, status=status.HTTP_400_BAD_REQUEST)


# View for Staff Scheduling a Visit
class StaffVisitRegisterView(generics.CreateAPIView):
    serializer_class = VisitorSerializer
    # only authenticated user(attendant/staff) can register a visitor
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        # create new visitor instance
        visitor = serializer.save()

        # set isApproved to true
        visitor.isApproved = True
        visitor.save()

        # save visitor instance in the VLog db
        staff = self.request.user

        # create a new instance of the newly registered visitor and store in the visitorlog db
        VisitorLog.objects.create(
            visitor=visitor,
            staff=staff,
            checkInTime=timezone.now(),
        )


# List all Staff Schedules
class StaffScheduleListView(generics.ListAPIView):
    queryset = VisitorLog.objects.all()
    serializer_class = VisitorLogSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        # Filter visitor logs by staff member
        return self.queryset.filter(staff=self.request.user)


# render visit request of a particular staff
class ListVisitRequestView(generics.ListAPIView):
    # permission_classes = [IsAuthenticated]
    serializer_class = VisitRequestSerializer

    def get_queryset(self):
        # Retrieve the staff ID from the URL query parameters or request data
        staff_id = self.request.query_params.get('staff_id')
        # print(staff_id)
        
        # Filter VisitRequest objects based on the staff ID
        queryset = VisitRequest.objects.filter(staff__staffId=staff_id).select_related('visitor', 'staff')
        return queryset

# render staff-scheduled visit/appointment
class ListStaffScheduleListView(generics.ListAPIView):
    serializer_class = VisitRequestSerializer

    def get_queryset(self):
        staffId = self.kwargs['staffId']
        return VisitRequest.objects.filter(staff__staffId=staffId, status="Approved")

# Staff Reschedule Visit


class StaffRescheduleVisit(generics.UpdateAPIView):
    pass


class LogoutView(APIView):
    # Ensure only authenticated users can access this view
    permission_classes = [IsAuthenticated]

    def post(self, request):
        # Logout the user
        logout(request)

        # Return a successful response
        return Response({'success': True, 'message': 'Logged out successfully'}, status=200)

# class LoginView(APIView):
#     def post(self, request):
#         serializer = UserSerializer(data=request.data)

#         if serializer.is_valid():
#             # Authenticate the user
#             user_id = serializer.validated_data.get('user_id')
#             password = serializer.validated_data.get('password')

#             user = authenticate(request, user_id=user_id, password=password)

#             if user:
#                 # Handle successful authentication (e.g., return a success response)
#                 return Response({'status': 'success', 'message': 'Login successful'}, status=status.HTTP_200_OK)
#             else:
#                 # Handle invalid credentials
#                 return Response({'status': 'error', 'message': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)

#         # Handle invalid request data
#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
