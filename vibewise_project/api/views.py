import json
import base64
from datetime import datetime, timedelta
from django.contrib.auth import authenticate, login, logout
from django.core.files.base import ContentFile
from django.db import models
from django.conf import settings
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.views import APIView
from accounts.models import User, UserPreferences
from mood_detection.models import MoodDetectionResult
from spotify_integration.models import SpotifyPlaylist
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
        """Fixed logout - clears session and tokens"""
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
        """Check if user is authenticated"""
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
    """⚠️ PRIVACY-FOCUSED: Requires authentication, DOES NOT SAVE IMAGES"""
    permission_classes = [IsAuthenticated]
    
    @action(detail=False, methods=['post'])
    def detect(self, request):
        """Detect mood from image - PRIVACY PROTECTED (NO IMAGE STORAGE)"""
        try:
            # Double-check authentication
            if not request.user.is_authenticated:
                return Response({
                    'error': 'Authentication required. Please login to use mood detection.',
                    'authenticated': False
                }, status=status.HTTP_401_UNAUTHORIZED)
            
            image_data = request.data.get('image')
            save_image = request.data.get('save_image', False)  # Default: DON'T save
            
            if not image_data:
                return Response({
                    'error': 'No image provided'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Process base64 image
            if 'base64,' in image_data:
                format, imgstr = image_data.split(';base64,')
                ext = format.split('/')[-1]
            else:
                imgstr = image_data
                ext = 'jpg'
            
            # Use mood detection service
            mood_service = MoodDetectionService()
            mood_result = mood_service.detect_mood_from_base64(imgstr)
            
            if mood_result:
                # ⚠️ PRIVACY: Save ONLY mood result, NOT the image
                mood_detection = MoodDetectionResult.objects.create(
                    user=request.user,
                    mood=mood_result['mood'],
                    confidence=mood_result['confidence']
                    # image field is LEFT EMPTY for privacy
                )
                
                print(f"✅ Mood detected for {request.user.email}: {mood_result['mood']} "
                      f"(image NOT saved for privacy)")
                
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
        """Get mood detection history (without images for privacy)"""
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
        """Connect Spotify account"""
        code = request.data.get('code')
        redirect_uri = request.data.get('redirect_uri', settings.SPOTIFY_REDIRECT_URI)
        
        print(f"Spotify connect - Code: {code[:20] if code else 'None'}...")
        print(f"Redirect URI: {redirect_uri}")
        
        if not code:
            return Response({
                'error': 'Authorization code required'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            spotify_service = SpotifyService()
            tokens = spotify_service.exchange_code_for_tokens(code, redirect_uri)
            
            spotify_user = spotify_service.get_user_profile(tokens['access_token'])
            print(f"Spotify user: {spotify_user.get('id')}, {spotify_user.get('display_name')}")
            
            email = spotify_user.get('email')
            spotify_id = spotify_user.get('id')
            display_name = spotify_user.get('display_name', 'Spotify User')
            
            if not email:
                email = f"{spotify_id}@spotify.user"
            
            user, created = User.objects.get_or_create(
                email=email,
                defaults={
                    'username': email,
                    'name': display_name,
                    'spotify_id': spotify_id,
                    'spotify_access_token': tokens['access_token'],
                    'spotify_refresh_token': tokens.get('refresh_token', '')
                }
            )
            
            if not created:
                user.name = display_name
                user.spotify_id = spotify_id
                user.spotify_access_token = tokens['access_token']
                user.spotify_refresh_token = tokens.get('refresh_token', '')
                user.save()
            else:
                user.set_password(User.objects.make_random_password())
                user.save()
                UserPreferences.objects.get_or_create(user=user)
            
            login(request, user, backend='django.contrib.auth.backends.ModelBackend')
            
            return Response({
                'message': 'Spotify connected successfully',
                'spotify_user': spotify_user,
                'user': {
                    'id': user.id,
                    'name': user.name,
                    'email': user.email,
                    'spotify_id': user.spotify_id
                }
            })
            
        except Exception as e:
            import traceback
            print(f"Spotify connection error: {e}")
            traceback.print_exc()
            return Response({
                'error': f'Failed to connect Spotify: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @action(detail=False, methods=['post'])
    def create_playlist(self, request):
        """Create personalized Spotify playlist based on mood AND user's listening habits"""
        mood = request.data.get('mood')
        if not mood:
            return Response({
                'error': 'Mood is required'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        if not request.user.is_authenticated:
            return Response({
                'error': 'Please login with Spotify to create playlists'
            }, status=status.HTTP_401_UNAUTHORIZED)
        
        if not request.user.spotify_access_token:
            return Response({
                'error': 'Spotify not connected. Please connect your Spotify account.'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        access_token = request.user.spotify_access_token
        spotify_id = request.user.spotify_id
        
        try:
            spotify_service = SpotifyService()
            
            # ✅ GET USER'S ACTUAL LISTENING HABITS
            print(f"🎵 Fetching listening habits for {request.user.email}...")
            user_genres = spotify_service.get_user_top_genres(access_token)
            print(f"User's top genres: {user_genres}")
            
            # Create personalized playlist based on BOTH mood and user preferences
            playlist = spotify_service.create_personalized_mood_playlist(
                access_token,
                spotify_id,
                mood,
                user_genres  # ✅ Uses actual user listening history
            )
            
            # Save to database
            db_playlist = SpotifyPlaylist.objects.create(
                user=request.user,
                spotify_id=playlist['id'],
                name=playlist['name'],
                description=playlist.get('description', ''),
                image_url=playlist.get('images', [{}])[0].get('url') if playlist.get('images') else None,
                total_tracks=playlist.get('tracks', {}).get('total', 0),
                is_public=playlist.get('public', True)
            )
            
            return Response({
                'playlist': SpotifyPlaylistSerializer(db_playlist).data,
                'spotify_url': playlist['external_urls']['spotify'],
                'genres_used': user_genres[:3],
                'message': f'Created personalized {mood} playlist with your favorite genres: {", ".join(user_genres[:3])}!'
            })
            
        except Exception as e:
            print(f"Playlist creation error: {e}")
            import traceback
            traceback.print_exc()
            return Response({
                'error': f'Failed to create playlist: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @action(detail=False, methods=['get'])
    def playlists(self, request):
        """Get user's playlists"""
        if not request.user.is_authenticated:
            return Response({
                'error': 'Authentication required'
            }, status=status.HTTP_401_UNAUTHORIZED)
        
        playlists = SpotifyPlaylist.objects.filter(user=request.user).order_by('-created_at')
        return Response({
            'playlists': SpotifyPlaylistSerializer(playlists, many=True).data
        })

    @action(detail=False, methods=['get'])
    def status(self, request):
        """Check Spotify connection status"""
        if request.user.is_authenticated and request.user.spotify_access_token:
            return Response({
                'connected': True,
                'user': {
                    'name': request.user.name or request.user.username,
                    'email': request.user.email,
                    'spotify_id': request.user.spotify_id
                }
            })
        else:
            return Response({'connected': False})
    
    @action(detail=False, methods=['post', 'get'])
    def logout(self, request):
        """Logout and clear Spotify tokens"""
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
                'message': 'Logged out successfully'
            })
            
        except Exception as e:
            import traceback
            print(f"Logout error: {e}")
            traceback.print_exc()
            return Response({
                'success': False,
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


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
        now = datetime.now()
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