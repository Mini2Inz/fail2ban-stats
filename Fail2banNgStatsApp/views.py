import json
import socket
import csv
from random import randint
import calendar
import locale
import datetime
from django.shortcuts import render
from django.http import JsonResponse
from flask import Flask
from flask import Markup
from flask import render_template
from django import http
from django.http import JsonResponse
from django.shortcuts import render
from django.views.generic import TemplateView
from django.contrib.auth.models import User
from rest_framework.views import APIView
from django.db.models import Sum, Min
from rest_framework.response import Response
from django.utils import timezone
from chartjs.views.lines import BaseLineChartView
from .models import BansTableData, LocationTableData
from .statsreader import read_config
from .statsutils import StatsReader, RefreshContext
from rest_framework import generics

locale.setlocale(locale.LC_ALL, 'pl_PL.utf8')


def on_startup():
    # too_old = datetime.datetime.today() - datetime.timedelta(days=7)
    # LocationTableData.objects.filter(dateTime__gte=too_old).delete()
    return None


class ChartsJSONView(BaseLineChartView):
    def get_labels(self):
        weekDaysDict = [list(calendar.day_name)[int(e[0])] for e in
                        LocationTableData.objects.order_by().values('dayOfTheWeek').distinct().values_list(
                            'dayOfTheWeek')]
        return weekDaysDict

    def get_providers(self):
        countries = [e for e in LocationTableData.objects.order_by().values('name').distinct().values_list('name')]
        return countries

    def get_data(self):
        countries = [e for e in LocationTableData.objects.order_by().values('name').distinct().values_list('name')]
        output_list = []

        for c in countries:
            bans_by_country = [int(e[0]) for e in
                               LocationTableData.objects.filter(name=c[0]).values_list('banscount').order_by(
                                   'dateTime')]
            output_list.append(bans_by_country)
        return output_list


charts = TemplateView.as_view(template_name='charts.html')
charts_json = ChartsJSONView.as_view()

control = TemplateView.as_view(template_name='index.html')


class ComplexEncoder(json.JSONEncoder):
    def default(self, obj):
        try:
            return super(ComplexEncoder, obj).default(obj)
        except TypeError:
            if hasattr(obj, 'pk'):
                return obj.pk
            return str(obj)


class JSONResponseMixin(object):
    def render_to_response(self, context):
        return self.get_json_response(self.convert_context_to_json(context))

    def get_json_response(self, content, **httpresponse_kwargs):
        return http.HttpResponse(content,
                                 content_type='application/json',
                                 **httpresponse_kwargs)

    def convert_context_to_json(self, context):
        return json.dumps(context, cls=ComplexEncoder)


class JSONView(JSONResponseMixin, TemplateView):
    pass


# API/COUNTRY

class PieChartData(generics.ListAPIView):
    authentication_classes = []
    permission_classes = []

    # locationTableData = LocationTableData()
    # locationTableData.code = "POL"
    # locationTableData.dateTime = "2018-08-01T20:00+00:00"
    # locationTableData.banscount = 5
    # locationTableData.dayOfTheWeek = 2
    # locationTableData.save()

    def get(self, request, format=None):
        timespan = self.kwargs['timespan']
        labels = [e for e in LocationTableData.objects.order_by().values('name').distinct().values_list('name')]
        countries = [e for e in LocationTableData.objects.order_by().values('name').distinct().values_list('name')]
        default_items = []
        for c in countries:
            bans_by_country_sum = LocationTableData.objects.filter(name=c[0]).aggregate(Sum('banscount'))[
                'banscount__sum']
            default_items.extend([bans_by_country_sum])
        background_colors = ["#3e95cd", "#8e5ea2", "#3cba9f", "#e8c3b9", "#c45850", "#2a5a63", "#e00813"]
        # for c in countries:
        #     r = lambda: randint(0, 255)
        #     background_colors.extend(['#%02X%02X%02X' % (r(), r(), r())])
        data = {
            "labels": labels,
            "default": default_items,
            "colors": background_colors,
        }
        return Response(data)

# API/JAILBANS

class PieChartBans(generics.ListAPIView):
    authentication_classes = []
    permission_classes = []

    def get(self, request, format=None):
        # labels = [e for e in LocationTableData.objects.order_by().values('name').distinct().values_list('name')]
        labels = [e['jail'] for e in BansTableData.objects.order_by().values('jail').distinct()]
        print(labels)
        default_items = []
        for l in labels:
            jails_count = [BansTableData.objects.filter(jail=l).count()]
            default_items.extend([jails_count])
        background_colors = ["#2a5a63", "#e00813", "#c45850", "#3e95cd", "#8e5ea2", "#3cba9f", "#e8c3b9"]
        # for c in countries:
        #     r = lambda: randint(0, 255)
        #     background_colors.extend(['#%02X%02X%02X' % (r(), r(), r())])
        data = {
            "labels": labels,
            "default": default_items,
            "colors": background_colors,
        }
        return Response(data)


class BarChartData(generics.ListAPIView):
    authentication_classes = []
    permission_classes = []

    def get(self, request, format=None):
        labels = [list(calendar.day_name)[int(e[0])] for e in
                  LocationTableData.objects.order_by().values('dayOfTheWeek').distinct().values_list(
                      'dayOfTheWeek')]
        data = []
        i = datetime.datetime.weekday(
            LocationTableData.objects.order_by('dateTime').aggregate(Min('dateTime'))['dateTime__min'])
        print(i)
        for wd in labels:
            print(i)
            perday = [
                LocationTableData.objects.order_by('dayOfTheWeek').filter(dayOfTheWeek=i).aggregate(Sum('banscount'))[
                    'banscount__sum']]
            data.extend(perday)
            i += 1
            i %= 7
            print(perday)
        datasets = [{
            "label": "Number of bans per week day",
            "backgroundColor": ["#3e95cd", "#8e5ea2", "#3cba9f", "#e8c3b9", "#c45850", "#2a5a63", "#e00813"],
            "data": data
        }]
        data = {
            "labels": labels,
            "datasets": datasets,
        }
        return Response(data)


class PolarChartData(generics.ListAPIView):
    authentication_classes = []
    permission_classes = []

    def get(self, request, format=None):
        labels = ["Poniedziałek", "Wtorek", "Środa", "Czwartek", "Piątek"]
        datasets = [{
            "label": 'Ukraina',
            "backgroundColor": "rgba(153,255,51,0.4)",
            "borderColor": "rgba(153,255,51,1)",
            "data": [3, 7, 8, 9, 4],
        }, {
            "label": 'Chiny',
            "backgroundColor": "rgba(255,47,30,0.4)",
            "borderColor": "rgba(255,153,0,1)",
            "data": [12, 14, 11, 11, 10]
        }, {
            "label": 'Korea Południowa',
            "backgroundColor": "rgba(100,30,250,0.4)",
            "borderColor": "rgba(50,30,250,1)",
            "data": [9, 11, 7, 8, 6]
        }]

        data = {
            "labels": labels,
            "datasets": datasets
        }

        return Response(data)


def refresh_location(request):
    config = read_config('stats.config')
    reader = StatsReader(config)
    ctx = RefreshContext(reader, True)
    ctx.refreshLocations()
    return JsonResponse({'ok': True})


def old_refresh_location(request):
    HOST = '127.0.0.1'
    PORT = 7500
    csv.register_dialect("Dial", delimiter='/')
    csvfile = open('ServerList.csv', 'r')
    fieldnames = ("Number", "Address", "Port")
    reader = csv.DictReader(csvfile, fieldnames, dialect="Dial")
    for row in reader:
        for key, value in row.items():
            if key == 'Port':
                PORT = int(value)
            if key == 'Address':
                HOST = value
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            try:
                s.connect((HOST, PORT))
            except ConnectionRefusedError:
                print("Connection refused:")
                print(PORT, HOST)
                continue
            s.sendall(('LOCATIONS').encode())
            with s:
                print('Connected by', HOST)
                while True:
                    data = s.recv(5024)
                    if data.decode() == '\n': break
                    # s.sendall(data)
                    print(data.decode())
                    dataDec = data.decode()
                    divided = dataDec.split(',')

                    code = divided[0]
                    name = divided[1]
                    banscount = divided[2]

                    print(code)
                    print(name)
                    print(banscount)

                    locationData = LocationTableData()
                    locationData.code = code
                    locationData.name = name
                    locationData.dateTime = datetime.datetime.now()
                    locationData.dayOfTheWeek = datetime.datetime.now().weekday()
                    print(datetime.datetime.now())

                    try:
                        int(banscount)
                        locationData.banscount = int(banscount)
                    except ValueError:
                        locationData.banscount = -1

                    locationData.save()
    return JsonResponse({"ok": True})


def refresh(request):
    config = read_config('stats.config')
    reader = StatsReader(config)
    ctx = RefreshContext(reader, True)
    ctx.refreshBans()
    return JsonResponse({'ok': True})


def old_refresh(request):
    HOST = '127.0.0.1'
    PORT = 7500
    csv.register_dialect("Dial", delimiter='/')
    csvfile = open('ServerList.csv', 'r')
    fieldnames = ("Number", "Address", "Port")
    reader = csv.DictReader(csvfile, fieldnames, dialect="Dial")
    for row in reader:
        for key, value in row.items():
            if key == 'Port':
                PORT = int(value)
            if key == 'Address':
                HOST = value
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            try:
                s.connect((HOST, PORT))
            except ConnectionRefusedError:
                print("Connection refused:")
                print(PORT, HOST)
                continue
            s.sendall(('BANS').encode())
            # conn, addr = s.accept()
            with s:
                print('Connected by', HOST)
                while True:
                    data = s.recv(1024)
                    if data.decode() == '\n': break
                    # s.sendall(data)
                    print(data.decode())
                    dataDec = data.decode()
                    divided = dataDec.split(',')

                    jail = divided[0]
                    ip = divided[1]
                    timeofban = divided[2]
                    bantime = divided[3]

                    print(jail)
                    print(ip)
                    print(timeofban)
                    print(bantime)

                    banData = BansTableData()
                    banData.jail = jail
                    banData.ip = ip
                    banData.recived_from_address = HOST
                    banData.recived_from_port = PORT

                    try:
                        int(timeofban)
                        banData.timeofban = int(timeofban)
                    except ValueError:
                        banData.timeofban = -1

                    try:
                        int(bantime)
                        banData.bantime = int(bantime)
                    except ValueError:
                        banData.bantime = -1

                    banData.save()
    return JsonResponse({"ok": True})
