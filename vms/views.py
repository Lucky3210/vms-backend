# from django.contrib.auth import authenticate
from django.contrib.auth import logout
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from .models import GenericUser
from rest_framework.response import Response
from rest_framework import status
from .serializers import UserSerializer


class LoginView(APIView):
    def post(self, request):
        serializer = UserSerializer(data=request.data)

        if serializer.is_valid():
            # Authentication successful
            return Response({'status': 'success', 'message': 'Login Successful'}, status=status.HTTP_200_OK)
        else:
            # Return validation errors
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


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
