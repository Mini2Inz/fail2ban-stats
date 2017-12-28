from django.conf.urls import url
from . import views
from django.conf.urls.static import static
from django.conf import settings
from .views import PieChartData, PolarChartData
from .readservers import ServerListReader
from .bansfromdb import BansListReader

urlpatterns = [
                  url(r'^charts/json/$', views.charts_json, name='charts_json'),
                  url(r'^$', views.charts, name='charts'),
                  url(r'^control$', views.control, name='index'),
                  url(r'^api/chart/data/pie$', PieChartData.as_view()),
                  url(r'^api/chart/data/polar$', PolarChartData.as_view()),
                  url(r'^api/chart/data/serverList$', ServerListReader.as_view()),
                  url(r'^refresh$', views.refresh, name='refresh'),
                  url(r'^api/chart/data/serverList$', ServerListReader.as_view()),
                  url(r'^api/chart/data/bans$', BansListReader.as_view()),
                  url(r'^refresh_location$', views.refresh_location, name='refresh_location'),

              ] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
