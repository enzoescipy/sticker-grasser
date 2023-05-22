from django.contrib import admin
from django.urls import path, include
from django.views.generic import TemplateView

urlpatterns = [
    path('',TemplateView.as_view(template_name='index.html')),
    path('admin/', admin.site.urls),
    path('api/', include('restAPI.urls')),
    path('api_auth/', include('rest_framework.urls', namespace='rest_framework'))
]