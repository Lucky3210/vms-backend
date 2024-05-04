from rest_framework.views import APIView
from django.contrib.auth import login, logout, authenticate
from django.utils import timezone
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from rest_framework import status
from .models import GenericUser, Visitor, VisitorLog
from .serializers import VisitorSerializer



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


class RegisterVisitorView(generics.CreateAPIView):
    serializer_class = VisitorSerializer
    permission_classes = [IsAuthenticated] # only authenticated user(attendant/staff) can register a visitor

    def perform_create(self, serializer):
        # create new visitor instance
        
        visitor = serializer.save()

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


class ListVisitorView(generics.ListAPIView):
    serializer_class = VisitorSerializer

    # queryset to return all the visitors
    queryset = Visitor.objects.all()
    permission_classes = [IsAuthenticated]
    


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
