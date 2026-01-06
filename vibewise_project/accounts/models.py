from django.contrib.auth.models import AbstractUser
from django.db import models
from django.core.validators import URLValidator

class User(AbstractUser):
    email = models.EmailField(unique=True)
    name = models.CharField(max_length=100, default='User') 
    spotify_id = models.CharField(max_length=100, blank=True, null=True)
    spotify_access_token = models.TextField(blank=True, null=True)
    spotify_refresh_token = models.TextField(blank=True, null=True)
    profile_picture = models.ImageField(upload_to='profile_pics/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']
    
    def __str__(self):
        return self.email

class UserPreferences(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='preferences')
    preferred_genres = models.JSONField(default=list, blank=True)
    mood_detection_enabled = models.BooleanField(default=True)
    auto_create_playlists = models.BooleanField(default=True)
    notification_preferences = models.JSONField(default=dict, blank=True)
    
    def __str__(self):
        return f"{self.user.email} Preferences"