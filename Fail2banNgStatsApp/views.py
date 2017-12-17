import json
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
from django.contrib.auth.models import User

import arrow


class ChartsJSONView(BaseLineChartView):
    def get_labels(self):
        return ["Niedziela", "Poniedziałek", "Wtorek", "Środa"]

    def get_providers(self):
        return ["Chiny", "Korea Południowa", "Ukraina"]

    def get_data(self):
        return [[30, 12, 5, 20],
                [9, 17, 12, 6],
                [1, 2, 4, 3]]


charts = TemplateView.as_view(template_name='charts.html')
charts_json = ChartsJSONView.as_view()


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
        labels = ["Korea Południowa", "Chiny", "Ukraina"]
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
