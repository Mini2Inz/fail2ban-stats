# Generated by Django 2.0 on 2018-01-09 21:26

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('Fail2banNgStatsApp', '0006_locationtabledata_dayoftheweek'),
    ]

    operations = [
        migrations.AlterField(
            model_name='locationtabledata',
            name='dateTime',
            field=models.DateTimeField(blank=True, default=django.utils.timezone.now),
        ),
    ]