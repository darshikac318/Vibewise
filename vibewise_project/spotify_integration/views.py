# Add to api/views.py or spotify_integration/views.py

from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.contrib.auth.decorators import login_required
from spotify_integration.models import SpotifyPlaylist, SpotifyUser, MoodDetectionResult
import spotipy
from spotipy.oauth2 import SpotifyOAuth

@api_view(['GET'])
def get_user_playlists(request):
    """Get user's VibeWise playlists with correct track counts from Spotify"""
    try:
        # Get SpotifyUser
        spotify_user = SpotifyUser.objects.filter(user=request.user).first()
        
        if not spotify_user:
            return Response({'playlists': []})
        
        # Initialize Spotify client
        sp = spotipy.Spotify(auth=spotify_user.access_token)
        
        # Get user's VibeWise playlists from database
        db_playlists = SpotifyPlaylist.objects.filter(user=request.user).order_by('-created_at')
        
        playlists_data = []
        
        for playlist in db_playlists:
            try:
                # Fetch real-time data from Spotify API
                spotify_data = sp.playlist(playlist.spotify_id)
                
                # Update track count in database
                actual_track_count = spotify_data['tracks']['total']
                playlist.total_tracks = actual_track_count
                playlist.save(update_fields=['total_tracks'])
                
                playlists_data.append({
                    'id': playlist.id,
                    'spotify_id': playlist.spotify_id,
                    'name': playlist.name,
                    'description': playlist.description,
                    'total_tracks': actual_track_count,  # Real count from Spotify
                    'mood': playlist.mood,
                    'spotify_url': f"https://open.spotify.com/playlist/{playlist.spotify_id}",
                    'created_at': playlist.created_at.isoformat(),
                })
            except Exception as e:
                print(f"Error fetching playlist {playlist.spotify_id}: {e}")
                # Use database value as fallback
                playlists_data.append({
                    'id': playlist.id,
                    'spotify_id': playlist.spotify_id,
                    'name': playlist.name,
                    'description': playlist.description,
                    'total_tracks': playlist.total_tracks,
                    'mood': playlist.mood,
                    'spotify_url': f"https://open.spotify.com/playlist/{playlist.spotify_id}",
                    'created_at': playlist.created_at.isoformat(),
                })
        
        return Response({
            'playlists': playlists_data,
            'total': len(playlists_data)
        })
        
    except Exception as e:
        print(f"Error in get_user_playlists: {e}")
        return Response({'error': str(e)}, status=500)


@api_view(['POST'])
def create_mood_playlist(request):
    """Create playlist and save mood detection result"""
    from datetime import datetime, timedelta
    import requests
    from django.conf import settings
    
    try:
        mood = request.data.get('mood')
        
        if not mood:
            return Response({'error': 'Mood is required'}, status=400)
        
        # Get or create SpotifyUser
        spotify_user, created = SpotifyUser.objects.get_or_create(
            user=request.user,
            defaults={
                'spotify_id': 'temp_id',
                'access_token': 'temp_token',
                'refresh_token': 'temp_refresh',
                'token_expires_at': datetime.now() + timedelta(hours=1)
            }
        )
        
        # Save mood detection result
        MoodDetectionResult.objects.create(
            user=request.user,
            mood=mood,
            confidence=0.85  # Default confidence
        )
        
        # Get Spotify session data
        spotify_data = request.session.get('spotify_auth', {})
        access_token = spotify_data.get('access_token')
        
        if not access_token:
            return Response({'error': 'Not authenticated with Spotify'}, status=401)
        
        # Update SpotifyUser tokens
        spotify_user.access_token = access_token
        spotify_user.refresh_token = spotify_data.get('refresh_token', '')
        spotify_user.token_expires_at = datetime.fromtimestamp(
            spotify_data.get('expires_at', datetime.now().timestamp())
        )
        spotify_user.save()
        
        # Initialize Spotify client
        sp = spotipy.Spotify(auth=access_token)
        
        # Get user's Spotify profile
        user_profile = sp.current_user()
        
        # Update SpotifyUser profile
        spotify_user.spotify_id = user_profile['id']
        spotify_user.display_name = user_profile.get('display_name', '')
        spotify_user.email = user_profile.get('email', '')
        spotify_user.save()
        
        # Mood to genre mapping
        mood_genres = {
            'happy': ['pop', 'dance', 'happy'],
            'sad': ['sad', 'acoustic', 'indie'],
            'angry': ['metal', 'rock', 'hard-rock'],
            'neutral': ['pop', 'indie', 'alternative'],
            'surprised': ['electronic', 'edm', 'dance'],
            'playful': ['pop', 'k-pop', 'dance'],
            'romantic': ['r-n-b', 'soul', 'romantic'],
            'energetic': ['workout', 'power', 'energy'],
        }
        
        # Get user's top tracks
        top_tracks = sp.current_user_top_tracks(limit=50, time_range='medium_term')
        
        # Create playlist
        playlist_name = f"VibeWise - {mood.title()} Vibes"
        new_playlist = sp.user_playlist_create(
            user_profile['id'],
            playlist_name,
            public=True,
            description=f"Your {mood} mood playlist curated by VibeWise"
        )
        
        # Add tracks to playlist
        track_uris = [track['uri'] for track in top_tracks['items'][:30]]
        
        if track_uris:
            sp.playlist_add_items(new_playlist['id'], track_uris)
        
        # Get actual track count from Spotify
        playlist_data = sp.playlist(new_playlist['id'])
        actual_track_count = playlist_data['tracks']['total']
        
        # Save to database with correct track count
        db_playlist = SpotifyPlaylist.objects.create(
            user=request.user,
            spotify_id=new_playlist['id'],
            name=playlist_name,
            description=new_playlist['description'],
            spotify_url=new_playlist['external_urls']['spotify'],
            total_tracks=actual_track_count,  # Correct count from Spotify
            mood=mood,
            genres_used=mood_genres.get(mood, ['pop']),
            is_public=True
        )
        
        return Response({
            'success': True,
            'playlist': {
                'id': db_playlist.id,
                'name': db_playlist.name,
                'spotify_id': db_playlist.spotify_id,
                'spotify_url': db_playlist.spotify_url,
                'total_tracks': actual_track_count,
                'mood': mood
            },
            'spotify_url': new_playlist['external_urls']['spotify'],
            'message': f'Created playlist with {actual_track_count} tracks!'
        })
        
    except Exception as e:
        print(f"Error creating playlist: {e}")
        import traceback
        traceback.print_exc()
        return Response({'error': str(e)}, status=500)