"""
API Serializers for VibeWise
"""
from rest_framework import serializers
from accounts.models import User, UserPreferences
from mood_detection.models import MoodDetectionResult
from spotify_integration.models import SpotifyPlaylist

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'email', 'name', 'username', 'profile_picture', 'created_at')
        read_only_fields = ('id', 'created_at')

class UserPreferencesSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserPreferences
        fields = '__all__'

class MoodDetectionSerializer(serializers.ModelSerializer):
    class Meta:
        model = MoodDetectionResult
        fields = ('id', 'mood', 'confidence', 'image', 'detected_at')
        read_only_fields = ('id', 'detected_at')

class SpotifyPlaylistSerializer(serializers.ModelSerializer):
    class Meta:
        model = SpotifyPlaylist
        fields = ('id', 'spotify_id', 'name', 'description', 'image_url', 
                 'total_tracks', 'is_public', 'created_at', 'updated_at')
        read_only_fields = ('id', 'created_at', 'updated_at')