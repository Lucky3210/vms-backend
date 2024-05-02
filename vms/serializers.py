from rest_framework import serializers
from django.contrib.auth import authenticate


class UserSerializer(serializers.Serializer):
    user_id = serializers.CharField(max_length=4, required=True)
    password = serializers.CharField(max_length=8, required=True, write_only=True)

    def validate_user_id(self, value):
        # Custom validation for user_id if needed
        if len(value) != 4:
            raise serializers.ValidationError("User ID must be exactly 4 characters long.")
        if not value.isdigit():
            raise serializers.ValidationError("User ID must consist only of digits.")
        return value

    def validate(self, data):
        # Additional validation logic for the serializer
        # For example, you can verify the user's credentials here
        user_id = data.get('user_id')
        password = data.get('password')

        # Check user credentials
        user = authenticate(username=user_id, password=password)
        if user is None:
            raise serializers.ValidationError("Invalid credentials.")

        # Return the data if validation is successful
        return data



# from rest_framework import serializers
# from .models import GenericUser
# from django.core.exceptions import PermissionDenied

# class UserSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = GenericUser
#         fields = ['user_id', 'password']

        
