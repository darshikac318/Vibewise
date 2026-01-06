"""
Spotify Integration Models
"""
from django.db import models
from accounts.models import User
from django.utils import timezone


class SpotifyUser(models.Model):
    """Store Spotify user information and tokens"""
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='spotify_profile')
    spotify_id = models.CharField(max_length=100, unique=True)
    display_name = models.CharField(max_length=200, blank=True)
    email = models.EmailField(blank=True)
    country = models.CharField(max_length=10, blank=True)
    profile_image = models.URLField(blank=True, null=True)
    
    # Spotify OAuth tokens
    access_token = models.TextField()
    refresh_token = models.TextField()
    token_expires_at = models.DateTimeField()
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    last_login = models.DateTimeField(default=timezone.now)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Spotify User'
        verbose_name_plural = 'Spotify Users'
    
    def __str__(self):
        return f"{self.display_name or self.spotify_id} ({self.email})"
    
    def is_token_expired(self):
        """Check if access token is expired"""
        return timezone.now() >= self.token_expires_at


class MoodDetectionResult(models.Model):
    """Store mood detection results"""
    
    MOOD_CHOICES = [
        ('happy', 'Happy'),
        ('sad', 'Sad'),
        ('angry', 'Angry'),
        ('neutral', 'Neutral'),
        ('surprised', 'Surprised'),
        ('fear', 'Fear'),
        ('disgust', 'Disgust'),
        ('excited', 'Excited'),
        ('confident', 'Confident'),
        ('motivated', 'Motivated'),
        ('dancing', 'Dancing'),
        ('romantic', 'Romantic'),
        ('peaceful', 'Peaceful'),
        ('energetic', 'Energetic'),
        ('melancholic', 'Melancholic'),
        ('playful', 'Playful'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='mood_detections')
    mood = models.CharField(max_length=50, choices=MOOD_CHOICES)
    confidence = models.FloatField(default=0.0)
    detected_at = models.DateTimeField(auto_now_add=True)
    
    # Optional: Store additional data
    raw_data = models.JSONField(blank=True, null=True)
    
    class Meta:
        ordering = ['-detected_at']
        verbose_name = 'Mood Detection Result'
        verbose_name_plural = 'Mood Detection Results'
        indexes = [
            models.Index(fields=['-detected_at']),
            models.Index(fields=['user', '-detected_at']),
        ]
    
    def __str__(self):
        return f"{self.user.email} - {self.mood} ({self.confidence:.2%})"


class SpotifyPlaylist(models.Model):
    """Store Spotify playlist information"""
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='spotify_playlists')
    spotify_id = models.CharField(max_length=100, unique=True)
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    image_url = models.URLField(blank=True, null=True)
    spotify_url = models.URLField(blank=True)
    total_tracks = models.IntegerField(default=0)
    is_public = models.BooleanField(default=True)
    
    # Link to mood
    mood = models.CharField(max_length=50, blank=True)
    genres_used = models.JSONField(blank=True, null=True)
    
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