from django.shortcuts import render
from django.contrib.admin.views.decorators import staff_member_required
from .models import SpotifyUser, SpotifyPlaylist, SpotifyTrack
from django.db.models import Count
from django.utils import timezone
from datetime import timedelta

@staff_member_required
def admin_dashboard(request):
    total_users = SpotifyUser.objects.count()
    total_playlists = SpotifyPlaylist.objects.count()
    total_tracks=SpotifyTrack.objects.count()
    
    week_ago = timezone.now() - timedelta(days=7)
    new_users_week = SpotifyUser.objects.filter(created_at__gte=week_ago).count()
    
    popular_moods = MoodDetectionResult.objects.values('mood').annotate(
        count=Count('mood')
    ).order_by('-count')[:5]
    
    recent_users = SpotifyUser.objects.order_by('-created_at')[:10]
    
    context = {
        'total_users': total_users,
        'total_detections': total_detections,
        'total_playlists': total_playlists,
        'total_tracks':total_tracks,
        'new_users_week': new_users_week,
        'popular_moods': popular_moods,
        'recent_users': recent_users,
    }
    
    return render(request, 'admin/dashboard.html', context)