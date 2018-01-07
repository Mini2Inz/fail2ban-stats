from django.db import models
from django.utils import timezone
from datetime import datetime

class LineChartData(models.Model):
    code = models.CharField(max_length=10,  default='UNKNOWN')
    country = models.CharField(max_length=50)
    dayOfWeek = models.CharField(max_length=50)
    count = models.IntegerField()

    class Meta:
        db_table = "linechartdata"


class BansTableData(models.Model):
    jail = models.CharField(max_length=50)
    ip = models.CharField(max_length=50)
    timeofban = models.IntegerField()
    bantime = models.IntegerField()
    recived_from_address = models.CharField(max_length=50, default='UNKNOWN')
    recived_from_port = models.CharField(max_length=50, default='UNKNOWN')

    class Meta:
        db_table = "banstabledata"


class LocationTableData(models.Model):
    code = models.CharField(max_length=50)
    name = models.CharField(max_length=50)
    dateTime = models.DateTimeField(default=datetime.now, blank=True)
    banscount = models.IntegerField()

    class Meta:
        db_table = "locationtabledata"

class LocationTableWeekViewData(models.Model):
    code = models.CharField(max_length=50)
    name = models.CharField(max_length=50)
    weekday = models.CharField(max_length=50)
    banscount = models.IntegerField()

    class Meta:
        db_table = "locationtabledata"

