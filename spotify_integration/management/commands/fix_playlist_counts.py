from django.core.management.base import BaseCommand
from spotify_integration.models import SpotifyPlaylist, SpotifyUser
import spotipy

class Command(BaseCommand):
    help = 'Fix track counts for existing playlists'

    def handle(self, *args, **options):
        playlists = SpotifyPlaylist.objects.all()
        self.stdout.write(f"Checking {playlists.count()} playlists...")
        
        for playlist in playlists:
            try:
                spotify_user = SpotifyUser.objects.get(user=playlist.user)
                
                if spotify_user.is_token_expired():
                    continue
                
                sp = spotipy.Spotify(auth=spotify_user.access_token)
                playlist_info = sp.playlist(playlist.spotify_id)
                actual_count = playlist_info['tracks']['total']
                
                playlist.total_tracks = actual_count
                playlist.save()
                
                self.stdout.write(self.style.SUCCESS(
                    f"✅ {playlist.name}: {actual_count} tracks"
                ))
                    
            except Exception as e:
                self.stdout.write(self.style.ERROR(f"❌ {playlist.name}: {str(e)}"))