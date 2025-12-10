"""
Spotify Integration Models
"""
from django.db import models
from accounts.models import User

class SpotifyPlaylist(models.Model):
    """Store Spotify playlist information"""
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='spotify_playlists')
    spotify_id = models.CharField(max_length=100, unique=True)
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    image_url = models.URLField(blank=True, null=True)
    total_tracks = models.IntegerField(default=0)
    is_public = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Spotify Playlist'
        verbose_name_plural = 'Spotify Playlists'
    
    def __str__(self):
        return f"{self.user.email} - {self.name}"


class SpotifyTrack(models.Model):
    """Store Spotify track information"""
    
    spotify_id = models.CharField(max_length=100, unique=True)
    name = models.CharField(max_length=200)
    artist = models.CharField(max_length=200)
    album = models.CharField(max_length=200)
    duration_ms = models.IntegerField()
    preview_url = models.URLField(blank=True, null=True)
    popularity = models.IntegerField(default=0)
    energy = models.FloatField(default=0.0)
    valence = models.FloatField(default=0.0)  # Musical positivity
    
    class Meta:
        verbose_name = 'Spotify Track'
        verbose_name_plural = 'Spotify Tracks'
    
    def __str__(self):
        return f"{self.name} by {self.artist}"