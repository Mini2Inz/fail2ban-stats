from django.conf.urls import url
from . import views
from django.conf.urls.static import static
from django.conf import settings
from .views import PieChartData, PolarChartData

urlpatterns = [
                  url(r'^charts/json/$', views.charts_json, name='charts_json'),
                  url(r'^$', views.charts, name='charts'),
                  url(r'^api/chart/data/pie$', PieChartData.as_view()),
                  url(r'^api/chart/data/polar$', PolarChartData.as_view())

              ] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
