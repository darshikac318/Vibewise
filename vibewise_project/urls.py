from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import TemplateView
from spotify_integration.admin_views import admin_dashboard

urlpatterns = [
    path('admin/', admin.site.urls),
    path('admin/dashboard/', admin_dashboard, name='admin_dashboard'),
    
    # API endpoints
    path('api/', include('api.urls')),
    
    # Frontend pages
    path('', TemplateView.as_view(template_name='index.html'), name='index'),
    path('login/', TemplateView.as_view(template_name='login.html'), name='login'),
    path('about/', TemplateView.as_view(template_name='about.html'), name='about'),
    path('profile/', TemplateView.as_view(template_name='profile.html'), name='profile'),
    path('callback/', TemplateView.as_view(template_name='callback.html'), name='callback'),  # ADD THIS
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)