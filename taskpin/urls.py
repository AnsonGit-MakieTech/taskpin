from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
import os
from base import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/register/', views.register, name='register'),
    path('accounts/', include('django.contrib.auth.urls')),
    path('', include('base.urls')),
]

_serve_media = settings.DEBUG or os.environ.get('SERVE_MEDIA', '').lower() in ('1', 'true', 'yes')
if _serve_media:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
