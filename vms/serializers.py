from rest_framework import serializers
from vms.models import Visitor, VisitorLog, VisitRequest, Staff

class StaffSerializer(serializers.ModelSerializer):
    class Meta:
        model = Staff
        fields = ['staffId', 'firstName', 'lastName', 'email', 'department', 'phoneNumber'] 

class VisitorSerializer(serializers.ModelSerializer):
    whomToSee = StaffSerializer(read_only=True)
    class Meta:
        model = Visitor
        fields = ['id', 'firstName', 'lastName', 'email', 'phoneNumber', 'organization', 'department', 'isApproved', 'whomToSee']


class VisitorLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = VisitorLog
        fields = '__all__'

class VisitRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = VisitRequest
        fields = '__all__'


