from django.conf.urls import url
from . import views
from django.conf.urls.static import static
from django.conf import settings

urlpatterns = [
                  url(r'^line_chart/json/$', views.line_chart_json, name='line_chart_json'),
                  url(r'^$', views.line_chart, name='line_chart'),


              ] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
