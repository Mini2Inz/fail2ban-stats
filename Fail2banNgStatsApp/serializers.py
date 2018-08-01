from datetime import datetime
from rest_framework import serializers
from django.utils import timezone

class LocationTableDataSerializer(serializers.Serializer):
    code = serializers.CharField(max_length=50)
    name = serializers.CharField(max_length=50)
    dateTime = serializers.DateTimeField()
    dayOfTheWeek = serializers.CharField(max_length=20, default='UNKNOWN')
    banscount = serializers.IntegerField()


class BansTableDataSerializer(serializers.Serializer):
    jail = serializers.CharField(max_length=50)
    ip = serializers.CharField(max_length=50)
    timeofban = serializers.IntegerField()
    bantime = serializers.IntegerField()
    recived_from_address = serializers.CharField(max_length=50, default='UNKNOWN')
    recived_from_port = serializers.CharField(max_length=50, default='UNKNOWN')