from django.conf.urls import url
from . import views
from django.conf.urls.static import static
from django.conf import settings

urlpatterns = [
                  url(r'^charts/json/$', views.charts_json, name='charts_json'),
                  url(r'^$', views.charts, name='charts'),


              ] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
