# Generated by Django 2.0 on 2018-01-05 14:16

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Fail2banNgStatsApp', '0003_locationtabledata'),
    ]

    operations = [
        migrations.AddField(
            model_name='banstabledata',
            name='recived_from_address',
            field=models.CharField(default='UNKNOWN', max_length=50),
        ),
        migrations.AddField(
            model_name='banstabledata',
            name='recived_from_port',
            field=models.CharField(default='UNKNOWN', max_length=50),
        ),
    ]
