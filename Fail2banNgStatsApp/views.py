import json
from django.shortcuts import render
from flask import Flask
from flask import Markup
from flask import Flask
from flask import render_template
from random import randint
from django.views.generic import TemplateView
from django import http
from chartjs.views.lines import BaseLineChartView


def index(request):
    return render(request, 'index.html')


def chart():
    labels = ["January","February","March","April","May","June","July","August"]
    values = [10,9,8,7,6,4,7,8]
    return render_template('chart.html', values=values, labels=labels)


class LineChartJSONView(BaseLineChartView):
    def get_labels(self):
        return ["Niedziela", "Poniedziałek", "Wtorek", "Środa"]

    def get_providers(self):
        return ["Chiny", "Korea Północna", "Ukraina"]

    def get_data(self):
        return [[30, 12, 5, 20],
                [9, 17, 12, 6],
                [1, 2, 4, 3]]


line_chart = TemplateView.as_view(template_name='line_chart.html')
line_chart_json = LineChartJSONView.as_view()



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

