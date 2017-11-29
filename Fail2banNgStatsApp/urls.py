from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^line_chart/json/$', views.line_chart_json,
        name='line_chart_json'),
    url(r'^$', views.line_chart,name='line_chart'),
]