from django.db import models
from django.utils import timezone


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

    class Meta:
        db_table = "banstabledata"
