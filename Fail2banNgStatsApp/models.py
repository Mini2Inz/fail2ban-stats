from django.db import models
from django.utils import timezone


class LineChartData(models.Model):
    country = models.CharField(max_length=50)
    dayOfWeek = models.CharField(max_length=50)
    count = models.IntegerField()

    class Meta:
        db_table = "linechartdata"
