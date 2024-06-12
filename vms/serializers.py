from rest_framework import serializers
from vms.models import Visitor, VisitorLog, VisitRequest

class VisitorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Visitor
        fields = '__all__'


class VisitorLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = VisitorLog
        fields = '__all__'

class VisitRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = VisitRequest
        fields = '__all__'
