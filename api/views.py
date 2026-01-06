import json
import base64
from datetime import datetime, timedelta
from django.contrib.auth import authenticate, login, logout
from django.core.files.base import ContentFile
from django.db import models
from django.conf import settings
from rest_framework import viewsets, status
from rest_framework.decorators import action, api_view
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.views import APIView
from accounts.models import User, UserPreferences
from mood_detection.models import MoodDetectionResult
from spotify_integration.models import SpotifyUser, SpotifyPlaylist
from django.utils import timezone
from datetime import timedelta
import spotipy
import requests
from .serializers import (
    UserSerializer, MoodDetectionSerializer, SpotifyPlaylistSerializer
)
from .services import MoodDetectionService, SpotifyService


class AuthViewSet(viewsets.ViewSet):
    permission_classes = [AllowAny]
    
    @action(detail=False, methods=['post'])
    def login(self, request):
        email = request.data.get('email')
        password = request.data.get('password')
        
        if not email or not password:
            return Response({
                'message': 'Email and password are required'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        user = authenticate(request, username=email, password=password)
        if user:
            login(request, user)
            return Response({
                'message': 'Login successful',
                'user': UserSerializer(user).data
            })
        else:
            return Response({
                'message': 'Invalid credentials'
            }, status=status.HTTP_401_UNAUTHORIZED)
    
    @action(detail=False, methods=['post'])
    def register(self, request):
        name = request.data.get('name')
        email = request.data.get('email')
        password = request.data.get('password')
        
        if not all([name, email, password]):
            return Response({
                'message': 'All fields are required'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        if User.objects.filter(email=email).exists():
            return Response({
                'errors': {'email': ['Email already exists']}
            }, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            user = User.objects.create_user(
                username=email,
                email=email,
                password=password,
                name=name
            )
            UserPreferences.objects.create(user=user)
            
            login(request, user)
            return Response({
                'message': 'Registration successful',
                'user': UserSerializer(user).data
            }, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response({
                'message': 'Registration failed'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @action(detail=False, methods=['post', 'get'])
    def logout(self, request):
        try:
            if request.user.is_authenticated:
                request.user.spotify_access_token = None
                request.user.spotify_refresh_token = None
                request.user.spotify_id = None
                request.user.save()
            
            if hasattr(request, 'session'):
                request.session.flush()
            
            logout(request)
            
            return Response({
                'success': True,
                'message': 'Logout successful'
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            print(f"Logout error: {e}")
            return Response({
                'success': False,
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @action(detail=False, methods=['get'])
    def check_auth(self, request):
        is_authenticated = request.user.is_authenticated
        
        if is_authenticated:
            return Response({
                'authenticated': True,
                'user': UserSerializer(request.user).data
            })
        else:
            return Response({
                'authenticated': False
            })
    
    @action(detail=False, methods=['post'])
    def forgot_password(self, request):
        email = request.data.get('email')
        if not email:
            return Response({
                'message': 'Email is required'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        return Response({
            'message': 'Password reset link sent to your email'
        })


class MoodDetectionViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]
    
    @action(detail=False, methods=['post'])
    def detect(self, request):
        try:
            if not request.user.is_authenticated:
                return Response({
                    'error': 'Authentication required. Please login to use mood detection.',
                    'authenticated': False
                }, status=status.HTTP_401_UNAUTHORIZED)
            
            image_data = request.data.get('image')
            
            if not image_data:
                return Response({
                    'error': 'No image provided'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            if 'base64,' in image_data:
                format, imgstr = image_data.split(';base64,')
                ext = format.split('/')[-1]
            else:
                imgstr = image_data
                ext = 'jpg'
            
            mood_service = MoodDetectionService()
            mood_result = mood_service.detect_mood_from_base64(imgstr)
            
            if mood_result:
                mood_detection = MoodDetectionResult.objects.create(
                    user=request.user,
                    mood=mood_result['mood'],
                    confidence=mood_result['confidence'],
                    detected_at=timezone.now()
                )
                
                print(f"Mood detected for {request.user.email}: {mood_result['mood']}")
                
                return Response({
                    'mood': mood_result['mood'],
                    'confidence': mood_result['confidence'],
                    'id': mood_detection.id,
                    'message': 'Mood detected successfully',
                    'privacy': 'Image processed but not saved'
                })
            else:
                return Response({
                    'error': 'Failed to detect mood from image'
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
                
        except Exception as e:
            print(f"Mood detection error: {e}")
            import traceback
            traceback.print_exc()
            return Response({
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @action(detail=False, methods=['get'])
    def history(self, request):
        moods = MoodDetectionResult.objects.filter(
            user=request.user
        ).order_by('-detected_at')[:20]
        
        return Response({
            'results': MoodDetectionSerializer(moods, many=True).data
        })


class SpotifyViewSet(viewsets.ViewSet):
    permission_classes = [AllowAny]
    
    @action(detail=False, methods=['post'])
    def connect(self, request):
        try:
            code = request.data.get('code')
            redirect_uri = request.data.get('redirect_uri', 'http://127.0.0.1:8000/callback/')
            
            if not code:
                return Response({'error': 'No authorization code provided'}, status=400)
            
            print(f"Spotify connect - Code: {code[:20]}...")
            
            token_url = 'https://accounts.spotify.com/api/token'
            
            data = {
                'grant_type': 'authorization_code',
                'code': code,
                'redirect_uri': redirect_uri,
                'client_id': settings.SPOTIFY_CLIENT_ID,
                'client_secret': settings.SPOTIFY_CLIENT_SECRET,
            }
            
            response = requests.post(token_url, data=data)
            print(f"Spotify token exchange status: {response.status_code}")
            
            if response.status_code != 200:
                error_msg = response.json().get('error_description', 'Unknown error')
                print(f"Spotify error: {error_msg}")
                return Response({'error': f'Spotify authentication failed: {error_msg}'}, status=400)
            
            tokens = response.json()
            access_token = tokens.get('access_token')
            refresh_token = tokens.get('refresh_token')
            expires_in = tokens.get('expires_in', 3600)
            
            sp = spotipy.Spotify(auth=access_token)
            user_info = sp.current_user()
            
            print(f"Spotify user: {user_info['id']}, {user_info.get('display_name', 'No name')}")
            
            expires_at = timezone.now() + timedelta(seconds=expires_in)
            
            django_user, user_created = User.objects.get_or_create(
                email=user_info.get('email', f"{user_info['id']}@spotify.user"),
                defaults={
                    'username': user_info.get('email', user_info['id']),
                    'name': user_info.get('display_name', 'Spotify User')
                }
            )
            
            if user_created:
                django_user.set_password(User.objects.make_random_password())
                django_user.save()
            
            spotify_user, created = SpotifyUser.objects.update_or_create(
                user=django_user,
                defaults={
                    'spotify_id': user_info['id'],
                    'display_name': user_info.get('display_name', ''),
                    'email': user_info.get('email', ''),
                    'country': user_info.get('country', ''),
                    'access_token': access_token,
                    'refresh_token': refresh_token,
                    'token_expires_at': expires_at,
                    'last_login': timezone.now()
                }
            )
            
            login(request, django_user)
            
            request.session['spotify_auth'] = {
                'access_token': access_token,
                'refresh_token': refresh_token,
                'expires_at': expires_at.timestamp(),
                'user_id': user_info['id']
            }
            request.session.modified = True
            
            return Response({
                'success': True,
                'message': 'Successfully connected to Spotify',
                'user': {
                    'id': user_info['id'],
                    'name': user_info.get('display_name', ''),
                    'email': user_info.get('email', '')
                }
            })
            
        except Exception as e:
            print(f"Spotify connection error: {str(e)}")
            import traceback
            traceback.print_exc()
            return Response({'error': str(e)}, status=500)
    
    @action(detail=False, methods=['post'])
    def create_playlist(self, request):
        try:
            if not request.user.is_authenticated:
                return Response({'error': 'Authentication required'}, status=401)
            
            mood = request.data.get('mood')
            
            if not mood:
                return Response({'error': 'Mood is required'}, status=400)
            
            try:
                spotify_user = SpotifyUser.objects.get(user=request.user)
            except SpotifyUser.DoesNotExist:
                return Response({'error': 'Spotify not connected'}, status=401)
            
            if spotify_user.is_token_expired():
                return Response({'error': 'Token expired, please reconnect'}, status=401)
            
            sp = spotipy.Spotify(auth=spotify_user.access_token)
            user_profile = sp.current_user()
            
            MoodDetectionResult.objects.create(
                user=request.user,
                mood=mood,
                confidence=0.85,
                detected_at=timezone.now()
            )
            
            mood_genres = {
                'happy': ['pop', 'dance', 'party'],
                'sad': ['sad', 'acoustic', 'indie'],
                'angry': ['metal', 'rock', 'punk'],
                'neutral': ['pop', 'indie', 'chill'],
                'surprised': ['electronic', 'edm', 'dance'],
                'playful': ['pop', 'funk', 'dance'],
                'romantic': ['r-n-b', 'soul'],
                'energetic': ['work-out', 'edm', 'rock'],
                'melancholic': ['indie', 'folk', 'acoustic'],
                'peaceful': ['ambient', 'chill', 'acoustic'],
                'motivated': ['work-out', 'hip-hop', 'edm'],
                'dancing': ['dance', 'edm', 'pop'],
            }
            
            print("Getting ALL listening history...")
            
            all_tracks = []
            track_ids = set()
            
            for time_range in ['short_term', 'medium_term', 'long_term']:
                try:
                    response = sp.current_user_top_tracks(limit=50, time_range=time_range)
                    for track in response['items']:
                        if track['id'] not in track_ids:
                            all_tracks.append(track)
                            track_ids.add(track['id'])
                    print(f"{time_range}: {len(response['items'])}")
                except:
                    pass
            
            print(f"Total: {len(all_tracks)} tracks")
            
            top_artists = sp.current_user_top_artists(limit=50, time_range='long_term')
            
            mood_features = {
                'happy': {'min_valence': 0.6, 'target_valence': 0.85, 'min_energy': 0.5, 'target_energy': 0.75},
                'sad': {'max_valence': 0.4, 'target_valence': 0.2, 'max_energy': 0.5, 'target_energy': 0.3},
                'angry': {'min_energy': 0.7, 'target_energy': 0.9, 'min_valence': 0.2, 'target_valence': 0.4},
                'neutral': {'target_valence': 0.5, 'target_energy': 0.5},
                'surprised': {'min_valence': 0.5, 'target_valence': 0.7, 'min_energy': 0.6, 'target_energy': 0.8},
                'playful': {'min_valence': 0.6, 'target_valence': 0.8, 'target_energy': 0.65},
                'romantic': {'min_valence': 0.5, 'target_valence': 0.7, 'max_energy': 0.6, 'target_energy': 0.45},
                'energetic': {'min_energy': 0.7, 'target_energy': 0.9, 'min_valence': 0.6, 'target_valence': 0.8},
                'melancholic': {'max_valence': 0.45, 'target_valence': 0.25, 'max_energy': 0.5, 'target_energy': 0.35},
                'peaceful': {'max_energy': 0.5, 'target_energy': 0.3, 'target_valence': 0.6},
                'motivated': {'min_energy': 0.6, 'target_energy': 0.8, 'min_valence': 0.6, 'target_valence': 0.75},
                'dancing': {'min_energy': 0.7, 'target_energy': 0.85, 'min_valence': 0.6, 'target_valence': 0.8},
            }
            
            features = mood_features.get(mood.lower(), mood_features['neutral'])
            
            final_tracks = []
            track_ids_added = set()
            
            import random
            random.shuffle(all_tracks)
            
            for track in all_tracks[:10]:
                if track['id'] not in track_ids_added:
                    final_tracks.append(track)
                    track_ids_added.add(track['id'])
            
            try:
                seed_tracks = [track['id'] for track in all_tracks[:2]]
                seed_artists = [artist['id'] for artist in top_artists['items'][:2]]
                
                mood_genre_list = mood_genres.get(mood.lower(), ['pop'])
                
                print(f"Seeds: {len(seed_tracks)} tracks, {len(seed_artists)} artists, genre={mood_genre_list[0]}")
                
                recommendations = sp.recommendations(
                    seed_tracks=seed_tracks,
                    seed_artists=seed_artists,
                    seed_genres=[mood_genre_list[0]],
                    limit=30,
                    **features
                )
                
                print(f"Got {len(recommendations['tracks'])} recommendations")
                
                for track in recommendations['tracks']:
                    if track['id'] not in track_ids_added and len(final_tracks) < 30:
                        final_tracks.append(track)
                        track_ids_added.add(track['id'])
                
            except Exception as e:
                print(f"Recommendations failed: {e}")
                pass
            
            while len(final_tracks) < 30 and len(all_tracks) > len(final_tracks):
                remaining = [t for t in all_tracks if t['id'] not in track_ids_added]
                if remaining:
                    track = random.choice(remaining)
                    final_tracks.append(track)
                    track_ids_added.add(track['id'])
                else:
                    break
            
            print(f"Final: {len(final_tracks)} tracks")
            
            playlist_name = f"VibeWise - {mood.title()} Vibes 🎵"
            description = f"Your {mood} mood playlist"
            
            new_playlist = sp.user_playlist_create(
                user_profile['id'],
                playlist_name,
                public=True,
                description=description
            )
            
            track_uris = []
            
            for track in final_tracks:
                track_uris.append(track['uri'])
                
                try:
                    from spotify_integration.models import SpotifyTrack
                    
                    SpotifyTrack.objects.get_or_create(
                        spotify_id=track['id'],
                        defaults={
                            'name': track['name'],
                            'artist': ', '.join([artist['name'] for artist in track['artists']]),
                            'album': track['album']['name'],
                            'duration_ms': track['duration_ms'],
                            'preview_url': track.get('preview_url', ''),
                            'popularity': track.get('popularity', 0),
                            'energy': 0.5,
                            'valence': 0.5,
                        }
                    )
                except:
                    pass
            
            actual_track_count = 0
            if track_uris:
                sp.playlist_add_items(new_playlist['id'], track_uris)
                actual_track_count = len(track_uris)
            
            import time
            time.sleep(1)
            
            try:
                playlist_info = sp.playlist(new_playlist['id'])
                actual_track_count = playlist_info['tracks']['total']
            except:
                pass
            
            db_playlist = SpotifyPlaylist.objects.create(
                user=request.user,
                spotify_id=new_playlist['id'],
                name=playlist_name,
                description=description,
                spotify_url=new_playlist['external_urls']['spotify'],
                total_tracks=actual_track_count,
                mood=mood,
                genres_used=mood_genres.get(mood, ['pop']),
                is_public=True
            )
            
            return Response({
                'success': True,
                'message': f'Created playlist with {actual_track_count} tracks!',
                'playlist': {
                    'id': db_playlist.id,
                    'name': db_playlist.name,
                    'spotify_id': db_playlist.spotify_id,
                    'spotify_url': db_playlist.spotify_url,
                    'total_tracks': actual_track_count,
                    'mood': mood
                },
                'spotify_url': new_playlist['external_urls']['spotify']
            })
            
        except Exception as e:
            print(f"Error: {str(e)}")
            import traceback
            traceback.print_exc()
            return Response({'error': str(e)}, status=500)
    
    @action(detail=False, methods=['get'])
    def get_playlists(self, request):
        try:
            if not request.user.is_authenticated:
                return Response({'playlists': [], 'total': 0})
            
            playlists = SpotifyPlaylist.objects.filter(user=request.user).order_by('-created_at')
            
            playlists_data = []
            for playlist in playlists:
                playlists_data.append({
                    'id': playlist.id,
                    'spotify_id': playlist.spotify_id,
                    'name': playlist.name,
                    'description': playlist.description,
                    'total_tracks': playlist.total_tracks,
                    'mood': playlist.mood,
                    'spotify_url': playlist.spotify_url,
                    'created_at': playlist.created_at.isoformat(),
                })
            
            return Response({
                'playlists': playlists_data,
                'total': len(playlists_data)
            })
            
        except Exception as e:
            print(f"Error: {str(e)}")
            return Response({'error': str(e)}, status=500)

    @action(detail=False, methods=['get'])
    def status(self, request):
        if request.user.is_authenticated:
            try:
                spotify_user = SpotifyUser.objects.get(user=request.user)
                return Response({
                    'connected': True,
                    'user': {
                        'name': spotify_user.display_name,
                        'email': spotify_user.email,
                        'spotify_id': spotify_user.spotify_id
                    }
                })
            except SpotifyUser.DoesNotExist:
                return Response({'connected': False})
        else:
            return Response({'connected': False})
    
    @action(detail=False, methods=['post'])
    def logout(self, request):
        try:
            if request.user.is_authenticated:
                try:
                    spotify_user = SpotifyUser.objects.get(user=request.user)
                    spotify_user.delete()
                except SpotifyUser.DoesNotExist:
                    pass
            
            if hasattr(request, 'session'):
                request.session.flush()
            
            logout(request)
            
            return Response({
                'success': True,
                'message': 'Logged out successfully'
            })
            
        except Exception as e:
            print(f"Logout error: {e}")
            import traceback
            traceback.print_exc()
            return Response({
                'success': False,
                'error': str(e)
            }, status=500)


class UserProfileView(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        return Response({
            'user': UserSerializer(request.user).data
        })
    
    def put(self, request):
        user = request.user
        data = request.data
        
        if 'name' in data:
            user.name = data['name']
        if 'preferences' in data:
            prefs, created = UserPreferences.objects.get_or_create(user=user)
            prefs.preferred_genres = data['preferences'].get('genres', [])
            prefs.mood_detection_enabled = data['preferences'].get('mood_detection_enabled', True)
            prefs.save()
        
        user.save()
        return Response({
            'message': 'Profile updated successfully',
            'user': UserSerializer(user).data
        })


class DashboardStatsView(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        user = request.user
        now = timezone.now()
        week_ago = now - timedelta(days=7)
        
        mood_stats = MoodDetectionResult.objects.filter(
            user=user,
            detected_at__gte=week_ago
        ).values('mood').annotate(count=models.Count('mood'))
        
        playlist_count = SpotifyPlaylist.objects.filter(user=user).count()
        
        recent_moods = MoodDetectionResult.objects.filter(
            user=user
        ).order_by('-detected_at')[:5]
        
        return Response({
            'mood_stats': list(mood_stats),
            'playlist_count': playlist_count,
            'recent_moods': MoodDetectionSerializer(recent_moods, many=True).data,
            'total_detections': MoodDetectionResult.objects.filter(user=user).count()
        })


@api_view(['POST'])
def connect(request):
    viewset = SpotifyViewSet()
    viewset.request = request
    return viewset.connect(request)


@api_view(['POST'])
def create_playlist(request):
    viewset = SpotifyViewSet()
    viewset.request = request
    return viewset.create_playlist(request)


@api_view(['GET'])
def get_playlists(request):
    viewset = SpotifyViewSet()
    viewset.request = request
    return viewset.get_playlists(request)


@api_view(['POST'])
def delete_playlist(request):
    try:
        if not request.user.is_authenticated:
            return Response({'error': 'Authentication required'}, status=401)
        
        playlist_id = request.data.get('playlist_id')
        
        if not playlist_id:
            return Response({'error': 'Playlist ID required'}, status=400)
        
        print(f"Deleting playlist: {playlist_id}")
        
        try:
            playlist = SpotifyPlaylist.objects.get(id=playlist_id, user=request.user)
        except SpotifyPlaylist.DoesNotExist:
            return Response({'error': 'Playlist not found'}, status=404)
        
        playlist_name = playlist.name
        playlist.delete()
        
        return Response({
            'success': True,
            'message': f'Deleted: {playlist_name}'
        })
        
    except Exception as e:
        print(f"Error: {str(e)}")
        import traceback
        traceback.print_exc()
        return Response({'error': str(e)}, status=500)