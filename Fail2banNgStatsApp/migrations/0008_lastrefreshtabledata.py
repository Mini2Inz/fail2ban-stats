# Generated by Django 2.0 on 2018-01-15 00:10

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Fail2banNgStatsApp', '0007_auto_20180109_2126'),
    ]

    operations = [
        migrations.CreateModel(
            name='LastRefreshTableData',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('time', models.IntegerField()),
            ],
            options={
                'db_table': 'lastrefreshtabledata',
            },
        ),
    ]
