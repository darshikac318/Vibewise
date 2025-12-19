"""
Spotify Integration Admin Configuration
"""
from django.contrib import admin
from django.conf import settings
from django.http import HttpResponse
import csv
from .models import SpotifyUser, MoodDetectionResult, SpotifyPlaylist, SpotifyTrack

# Customize admin site
admin.site.site_header = getattr(settings, 'ADMIN_SITE_HEADER', 'VibeWise Admin')
admin.site.site_title = getattr(settings, 'ADMIN_SITE_TITLE', 'VibeWise Admin')
admin.site.index_title = getattr(settings, 'ADMIN_INDEX_TITLE', 'Welcome to VibeWise Administration')


# CSV Export Action
def export_to_csv(modeladmin, request, queryset):
    """Export selected items to CSV"""
    meta = modeladmin.model._meta
    field_names = [field.name for field in meta.fields]
    
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename={meta}.csv'
    
    writer = csv.writer(response)
    writer.writerow(field_names)
    
    for obj in queryset:
        writer.writerow([getattr(obj, field) for field in field_names])
    
    return response

export_to_csv.short_description = "Export to CSV"


@admin.register(SpotifyUser)
class SpotifyUserAdmin(admin.ModelAdmin):
    list_display = ['spotify_id', 'display_name', 'email', 'country', 'created_at', 'last_login']
    search_fields = ['spotify_id', 'display_name', 'email']
    list_filter = ['country', 'created_at', 'last_login']
    readonly_fields = ['spotify_id', 'created_at', 'updated_at', 'last_login']
    actions = [export_to_csv]
    
    fieldsets = (
        ('User Information', {
            'fields': ('user', 'spotify_id', 'display_name', 'email', 'country', 'profile_image')
        }),
        ('OAuth Tokens', {
            'fields': ('access_token', 'refresh_token', 'token_expires_at'),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at', 'last_login')
        }),
    )
    
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.select_related('user')


@admin.register(MoodDetectionResult)
class MoodDetectionResultAdmin(admin.ModelAdmin):
    list_display = ['user', 'mood', 'confidence_percentage', 'detected_at']
    search_fields = ['user__email', 'mood']
    list_filter = ['mood', 'detected_at']
    readonly_fields = ['detected_at']
    date_hierarchy = 'detected_at'
    actions = [export_to_csv]
    
    def confidence_percentage(self, obj):
        return f"{obj.confidence * 100:.1f}%"
    confidence_percentage.short_description = 'Confidence'
    
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.select_related('user')


@admin.register(SpotifyPlaylist)
class SpotifyPlaylistAdmin(admin.ModelAdmin):
    list_display = ['name', 'user', 'mood', 'total_tracks', 'is_public', 'created_at']
    search_fields = ['name', 'user__email', 'mood']
    list_filter = ['mood', 'is_public', 'created_at']
    readonly_fields = ['spotify_id', 'spotify_url', 'created_at', 'updated_at']
    date_hierarchy = 'created_at'
    actions = [export_to_csv]
    
    fieldsets = (
        ('Playlist Information', {
            'fields': ('name', 'description', 'mood', 'user')
        }),
        ('Spotify Details', {
            'fields': ('spotify_id', 'spotify_url', 'image_url', 'total_tracks', 'genres_used', 'is_public')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at')
        }),
    )
    
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.select_related('user')


@admin.register(SpotifyTrack)
class SpotifyTrackAdmin(admin.ModelAdmin):
    list_display = ['name', 'artist', 'album', 'popularity', 'energy', 'valence']
    search_fields = ['name', 'artist', 'album']
    list_filter = ['popularity']
    readonly_fields = ['spotify_id']
    actions = [export_to_csv]
    
    fieldsets = (
        ('Track Information', {
            'fields': ('spotify_id', 'name', 'artist', 'album', 'duration_ms', 'preview_url')
        }),
        ('Audio Features', {
            'fields': ('popularity', 'energy', 'valence')
        }),
    )