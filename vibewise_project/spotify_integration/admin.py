from django.contrib import admin
from django.conf import settings

# Customize admin site
admin.site.site_header = settings.ADMIN_SITE_HEADER
admin.site.site_title = settings.ADMIN_SITE_TITLE
admin.site.index_title = settings.ADMIN_INDEX_TITLE

from django.http import HttpResponse
import csv

def export_users_csv(modeladmin, request, queryset):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="vibewise_users.csv"'
    
    writer = csv.writer(response)
    writer.writerow(['Spotify ID', 'Name', 'Email', 'Country', 'Created At', 'Last Login'])
    
    for user in queryset:
        writer.writerow([
            user.spotify_id,
            user.display_name,
            user.email,
            user.country,
            user.created_at,
            user.last_login
        ])
    
    return response

export_users_csv.short_description = "Export selected users to CSV"

from django.contrib import admin
from .models import SpotifyUser, MoodDetectionResult, SpotifyPlaylist

@admin.register(SpotifyUser)
class SpotifyUserAdmin(admin.ModelAdmin):
    list_display = ['spotify_id', 'display_name', 'email', 'created_at', 'last_login']
    search_fields = ['spotify_id', 'display_name', 'email']
    list_filter = ['created_at', 'last_login']
    readonly_fields = ['spotify_id', 'created_at', 'updated_at']
    actions = [export_users_csv]
    
    fieldsets = (
        ('User Info', {
            'fields': ('spotify_id', 'display_name', 'email', 'country')
        }),
        ('Tokens', {
            'fields': ('access_token', 'refresh_token', 'token_expires_at'),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at', 'last_login')
        }),
    )

@admin.register(MoodDetectionResult)
class MoodDetectionResultAdmin(admin.ModelAdmin):
    list_display = ['user', 'mood', 'confidence', 'detected_at']
    search_fields = ['user__display_name', 'mood']
    list_filter = ['mood', 'detected_at']
    readonly_fields = ['detected_at']
    date_hierarchy = 'detected_at'
    
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.select_related('user')

@admin.register(SpotifyPlaylist)
class SpotifyPlaylistAdmin(admin.ModelAdmin):
    list_display = ['name', 'user', 'mood', 'total_tracks', 'created_at']
    search_fields = ['name', 'user__display_name', 'mood']
    list_filter = ['mood', 'created_at']
    readonly_fields = ['spotify_id', 'spotify_url', 'created_at']
    date_hierarchy = 'created_at'
    
    fieldsets = (
        ('Playlist Info', {
            'fields': ('name', 'description', 'mood', 'user')
        }),
        ('Spotify Details', {
            'fields': ('spotify_id', 'spotify_url', 'total_tracks', 'genres_used')
        }),
        ('Timestamps', {
            'fields': ('created_at',)
        }),
    )