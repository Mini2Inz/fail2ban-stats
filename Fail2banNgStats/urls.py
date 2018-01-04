"""Fail2banNgStats URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/dev/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.conf.urls import url, include
from django.contrib import admin
from Fail2banNgStatsApp.views import PieChartData, PolarChartData, refresh, control
from Fail2banNgStatsApp.readservers import ServerListReader
from Fail2banNgStatsApp.bansfromdb import BansListReader
from Fail2banNgStatsApp.locationsfromdb import LocationListReader

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^', include('Fail2banNgStatsApp.urls')),
    url(r'^api/chart/data/pie$', PieChartData.as_view()),
    url(r'^api/chart/data/polar$', PolarChartData.as_view()),
    url(r'^api/chart/data/serverList$', ServerListReader.as_view()),
    url(r'^control$', control, name='index'),
    url(r'^api/chart/data/bans$', BansListReader.as_view()),
    url(r'^api/chart/data/locations$', LocationListReader.as_view()),

]
