from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'auth', views.AuthViewSet, basename='auth')
router.register(r'mood', views.MoodDetectionViewSet, basename='mood')
router.register(r'spotify', views.SpotifyViewSet, basename='spotify')

urlpatterns = [
    path('', include(router.urls)),
    
    path('profile/', views.UserProfileView.as_view(), name='user-profile'),
    path('dashboard/stats/', views.DashboardStatsView.as_view(), name='dashboard-stats'),
    
    path('spotify/connect/', views.connect, name='spotify_connect'),
    path('spotify/create_playlist/', views.create_playlist, name='create_playlist'),
    path('spotify/playlists/', views.get_playlists, name='get_playlists'),
    path('spotify/delete-playlist/', views.delete_playlist, name='delete_playlist'),
]