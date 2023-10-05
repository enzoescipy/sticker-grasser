from django.contrib import admin
from django.urls import path, include
from django.views.generic import TemplateView
from django.views.decorators.csrf import ensure_csrf_cookie
from django.utils.decorators import method_decorator

class TemplateViewWithCsrf(TemplateView):
    """
    This set the csrf which could be called by the Django template
    ref : https://gist.github.com/i5on9i/10d2b65649b2a3387c34
    """
    @method_decorator(ensure_csrf_cookie)
    def get(self, request, *args, **kwargs):
        context = self.get_context_data(**kwargs)
        return self.render_to_response(context)

urlpatterns = [
    path('',TemplateViewWithCsrf.as_view(template_name='index.html')),
    path('admin/', admin.site.urls),
    path('api/', include('restAPI.urls')),
    path('api_auth/', include('rest_framework.urls', namespace='rest_framework'))
]