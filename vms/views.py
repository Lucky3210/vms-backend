from django.contrib.auth import login, logout, authenticate
from django.utils import timezone
from django.conf import settings
from django.core.mail import send_mail
from django.views.generic import View
from .models import GenericUser, Visitor, VisitorLog, Staff, VisitRequest
from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from rest_framework.views import APIView
from .serializers import VisitorSerializer, VisitorLogSerializer



class LoginView(APIView):

    def post(self, request):
        user_id = request.data.get('user_id')
        password = request.data.get('password')

        user = authenticate(request, username=user_id, password=password)

        if user is not None:
            token, created = Token.objects.get_or_create(user=user)

            login(request, user)

            return Response({
                'status': 'success', 
                'message': 'Login Successful',
                'token' : token.key, 
                'is_staff': user.is_staff
            }, status=status.HTTP_200_OK)
        
        else:
            return Response({"error": "Invalid User ID or Password"}, status=status.HTTP_400_BAD_REQUEST)


# Register/Schedule Visitor
class RegisterVisitorView(generics.CreateAPIView):
    serializer_class = VisitorSerializer
    permission_classes = [IsAuthenticated] # only authenticated user(attendant/staff) can register a visitor

    def perform_create(self, serializer):
        # create new visitor instance
        
        visitor = serializer.save()

        # save visitor instance in the VLog db
        whom_to_see = visitor.whomToSee.all()
        attendant = self.request.user

        for staff in whom_to_see:
            # create a new instance of the newly registered visitor and store in the visitorlog db
            VisitorLog.objects.create(
                visitor = visitor,
                staff = staff,
                attendant = attendant,
                checkInTime = timezone.now(),
                )
            
        # send visitor's details to the expected staff
        staffId = self.request.data.get('staffId')
        if staffId:
            try:
                staff = Staff.objects.get(id=staffId)
                attendant = self.request.user
                VisitRequest.objects.create(
                    visitor = visitor,
                    staff = staff,
                    attendant = attendant,
                    status = VisitRequest.status
                )
                # Send email notification to the staff member
                # subject = 'New Visitor Request'
                # message = f'Hello {staff.name},\n\nYou have a new visitor request.\nVisitor Details:\nName: {visitor.firstName} {visitor.lastName}\nEmail: {visitor.email}\nPhone: {visitor.phoneNumber}\n\nPlease login to your account to approve or decline the request.\n\nBest regards,\nIGCOMSAT'

                # send_mail(subject, message, settings.EMAIL_HOST_USER, [staff.email])

            except Staff.DoesNotExist:
                return Response({"error": "Invalid Staff ID"}, status=status.HTTP_400_BAD_REQUEST)


# Render all visitors
class ListVisitorView(generics.ListAPIView):
    serializer_class = VisitorSerializer
    permission_classes = [IsAuthenticated]

    # queryset to return all the visitors
    queryset = VisitorLog.objects.all() # visitorlog instead of visitor
    
    

# Accept Visitors Request
class AcceptVisitRequest(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, visitRequestId):
        visitRequest = VisitRequest.objects.get(id=visitRequestId)

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

            return Response({"message" : "Request Approved"}, status=status.HTTP_200_OK)
        
        except VisitRequest.DoesNotExist:
            return Response({"error" : "Request Not found"}, status=status.HTTP_404_NOT_FOUND)


# Decline Visitors Request
class DeclineVisitRequest(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, visitRequestId):
        visitRequest = VisitRequest.objects.get(id=visitRequestId)

        # if visitRequest.staff != request.user:
        #     return Response({'error': 'You do not have permission to make this decision.'}, status=status.HTTP_403_FORBIDDEN)
        try:
            visitRequest.status = VisitRequest.DECLINED
            visitRequest.save()

            # Update Approval field for visitor
            visitor = visitRequest.visitor
            visitor.isApproved = False
            visitor.save()

            return Response({"message" : "Request Approved"}, status=status.HTTP_200_OK)
        
        except VisitRequest.DoesNotExist:
            return Response({"error" : "Request Not found"}, status=status.HTTP_404_NOT_FOUND)


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
            visitorLog.checkOutTime = timezone.now()
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
    permission_classes = [IsAuthenticated] # only authenticated user(attendant/staff) can register a visitor

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
            visitor = visitor,
            staff = staff,
            checkInTime = timezone.now(),
            )


# List all Staff Schedules
class StaffScheduleListView(generics.ListAPIView):
    queryset = VisitorLog.objects.all()
    serializer_class = VisitorLogSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        # Filter visitor logs by staff member
        return self.queryset.filter(staff=self.request.user)

        
class LogoutView(APIView):
    permission_classes = [IsAuthenticated]  # Ensure only authenticated users can access this view

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
