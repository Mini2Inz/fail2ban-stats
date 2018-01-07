import json
import socket
import csv
from django.shortcuts import render
from django.http import JsonResponse
from flask import Flask
from flask import Markup
from flask import Flask
from flask import render_template
from random import randint
from django.views.generic import TemplateView
from django import http
from chartjs.views.lines import BaseLineChartView
from django.views.generic import TemplateView
from rest_framework.views import APIView
from rest_framework.response import Response
from .models import BansTableData, LocationTableData
from django.contrib.auth.models import User
from datetime import datetime

class ChartsJSONView(BaseLineChartView):
    def get_labels(self):
        return ["Poniedziałek", "Wtorek", "Środa", "Czwartek", "Piątek"]

    def get_providers(self):
        return ["Chiny", "Korea Południowa", "Ukraina"]

    def get_data(self):
        return [[30, 12, 5, 20, 22, 28],
                [9, 17, 12, 6, 15],
                [1, 2, 4, 3, 2]]


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


class PieChartData(APIView):
    authentication_classes = []
    permission_classes = []

    def get(self, request, format=None):
        labels = ["Chiny", "Korea Południowa", "Ukraina"]
        default_items = [23, 3, 12]
        background_colors = ["#2ecc71",
                             "#3498db",
                             "#95a5a6"]
        data = {
            "labels": labels,
            "default": default_items,
            "colors": background_colors,
        }
        return Response(data)

class PolarChartData(APIView):
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
                    data = s.recv(1024)
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

                    try:
                        int(locationData)
                        locationData.banscount = int(banscount)
                    except ValueError:
                        locationData.banscount = -1

                    locationData.save()
    return JsonResponse({"ok": True})


def refresh(request):
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



