"""
API URL Configuration - COMPLETE VERSION
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

# Create a router for ViewSets
router = DefaultRouter()
router.register(r'auth', views.AuthViewSet, basename='auth')
router.register(r'mood', views.MoodDetectionViewSet, basename='mood')
router.register(r'spotify', views.SpotifyViewSet, basename='spotify')

urlpatterns = [
    # Router URLs (includes all ViewSet actions)
    path('', include(router.urls)),
    
    # Additional views
    path('profile/', views.UserProfileView.as_view(), name='user-profile'),
    path('dashboard/stats/', views.DashboardStatsView.as_view(), name='dashboard-stats'),
]