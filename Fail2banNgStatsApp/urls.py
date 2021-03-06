from django.conf.urls import url
from . import views
from django.conf.urls.static import static
from django.conf import settings
from .views import PieChartData, PolarChartData, on_startup, PieChartBans, WeeklyPrisonData
from .readservers import ServerListReader
from .bansfromdb import BansListReader
from .locationsfromdb import LocationListReader

on_startup()

urlpatterns = urlpatterns = [
                  url(r'^charts/json/$', views.charts_json, name='charts_json'),
                  url(r'^$', views.charts, name='charts'),
                  url(r'^control$', views.control, name='index'),
                  url(r'^api/country/(?P<timespan>.+)/$', PieChartData.as_view()),
                  url(r'^api/chart/data/polar$', PolarChartData.as_view()),
                  # url(r'^api/chart/data/bar$', BarChartData.as_view()),
                  url(r'^api/servers/(?P<timespan>.+)/$', ServerListReader.as_view()),
                  url(r'^api/jailsbans/(?P<timespan>.+)/$', PieChartBans.as_view()),
                  url(r'^api/weeklybans/$', WeeklyPrisonData.as_view()),
                  url(r'^refresh$', views.refresh, name='refresh'),
                  url(r'^api/chart/data/serverList$', ServerListReader.as_view()),
                  url(r'^api/chart/data/bans$', BansListReader.as_view()),
                  url(r'^api/chart/data/locations$', LocationListReader.as_view()),
                  url(r'^refresh_location$', views.refresh_location, name='refresh_location'),

] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
