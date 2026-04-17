from django.urls import path, include

urlpatterns = [
    path('api/', include('api.urls')),
]

from django.http import HttpResponse
import os

def serve_frontend(request):
    frontend_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'frontend.html')
    with open(frontend_path) as f:
        return HttpResponse(f.read(), content_type='text/html')

urlpatterns += [path('frontend', serve_frontend), path('', serve_frontend)]
