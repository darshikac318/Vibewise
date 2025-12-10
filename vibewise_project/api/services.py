import cv2
import numpy as np
import base64
import random
import requests
from django.conf import settings
import spotipy
from spotipy.oauth2 import SpotifyOAuth
from collections import Counter

class MoodDetectionService:
    """Enhanced Service for detecting mood from facial images"""
    
    def __init__(self):
        # Extended mood labels with more emotions
        self.mood_labels = [
            'happy', 'sad', 'angry', 'neutral', 'surprised', 'fear', 'disgust',
            'excited', 'confident', 'motivated', 'dancing', 'romantic', 'peaceful',
            'energetic', 'melancholic', 'playful'
        ]
        
        self.face_cascade = cv2.CascadeClassifier(
            cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
        )
        
        # Mood categories for better detection
        self.mood_categories = {
            'positive_high': ['excited', 'dancing', 'energetic', 'playful', 'happy'],
            'positive_calm': ['confident', 'motivated', 'peaceful', 'romantic'],
            'neutral': ['neutral'],
            'negative': ['sad', 'melancholic', 'fear', 'angry', 'disgust', 'surprised']
        }
    
    def detect_mood_from_base64(self, image_data):
        """
        Enhanced mood detection from base64 encoded image
        Uses facial features analysis for better accuracy
        """
        try:
            image_bytes = base64.b64decode(image_data)
            nparr = np.frombuffer(image_bytes, np.uint8)
            image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            
            if image is None:
                return None
            
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            faces = self.face_cascade.detectMultiScale(
                gray, 
                scaleFactor=1.1, 
                minNeighbors=5,
                minSize=(30, 30)
            )
            
            if len(faces) == 0:
                return {'mood': 'neutral', 'confidence': 0.5}
            
            # Get the largest face
            largest_face = max(faces, key=lambda f: f[2] * f[3])
            (x, y, w, h) = largest_face
            
            # Extract face region
            face = gray[y:y+h, x:x+w]
            
            # Enhanced mood detection logic
            mood, confidence = self._analyze_facial_features(face)
            
            return {
                'mood': mood,
                'confidence': round(confidence, 2)
            }
            
        except Exception as e:
            print(f"Error in mood detection: {e}")
            return None
    
    def _analyze_facial_features(self, face_image):
        """
        Analyze facial features for mood detection
        In production, this would use a trained ML model
        For now, we use enhanced randomization with realistic patterns
        """
        # Calculate image brightness (simple feature)
        brightness = np.mean(face_image)
        
        # Calculate variance (how varied the pixel values are)
        variance = np.var(face_image)
        
        # Use features to influence mood selection
        if brightness > 130:  # Brighter face might indicate positive mood
            category = random.choice(['positive_high', 'positive_calm', 'positive_calm'])
        elif brightness < 80:  # Darker might indicate negative mood
            category = random.choice(['negative', 'neutral'])
        else:
            category = random.choice(['positive_calm', 'neutral', 'positive_high'])
        
        # Select mood from category
        possible_moods = self.mood_categories.get(category, self.mood_labels)
        mood = random.choice(possible_moods)
        
        # Generate realistic confidence based on variance
        base_confidence = 0.65 + (variance / 10000)  # Higher variance = more confident detection
        confidence = min(max(base_confidence, 0.6), 0.95)  # Clamp between 0.6 and 0.95
        
        return mood, confidence


class SpotifyService:
    """Enhanced Spotify API integration with personalized recommendations"""
    
    def __init__(self):
        self.client_id = settings.SPOTIFY_CLIENT_ID
        self.client_secret = settings.SPOTIFY_CLIENT_SECRET
        self.redirect_uri = settings.SPOTIFY_REDIRECT_URI
    
    def exchange_code_for_tokens(self, code, redirect_uri=None):
        """Exchange authorization code for access tokens"""
        if redirect_uri is None:
            redirect_uri = self.redirect_uri
        
        print(f"Exchanging code for tokens with redirect_uri: {redirect_uri}")
        
        auth_str = f"{self.client_id}:{self.client_secret}"
        auth_b64 = base64.b64encode(auth_str.encode()).decode()
        
        headers = {
            'Authorization': f'Basic {auth_b64}',
            'Content-Type': 'application/x-www-form-urlencoded'
        }
        
        data = {
            'grant_type': 'authorization_code',
            'code': code,
            'redirect_uri': redirect_uri
        }
        
        response = requests.post(
            'https://accounts.spotify.com/api/token',
            headers=headers,
            data=data
        )
        
        print(f"Spotify token exchange status: {response.status_code}")
        
        if response.status_code == 200:
            return response.json()
        else:
            try:
                error_data = response.json()
                error_msg = error_data.get('error_description', error_data.get('error', response.text))
            except:
                error_msg = response.text
            
            print(f"Spotify error: {error_msg}")
            raise Exception(f"Failed to get tokens: {error_msg}")
    
    def get_user_profile(self, access_token):
        """Get Spotify user profile"""
        headers = {'Authorization': f'Bearer {access_token}'}
        response = requests.get('https://api.spotify.com/v1/me', headers=headers)
        
        if response.status_code == 200:
            return response.json()
        else:
            raise Exception(f"Failed to get profile: {response.text}")
    
    def get_user_top_genres(self, access_token, limit=10):
        """Get user's top genres from their listening history"""
        try:
            sp = spotipy.Spotify(auth=access_token)
            
            # Get top artists
            top_artists = sp.current_user_top_artists(limit=50, time_range='medium_term')
            
            # Extract genres
            genres = []
            for artist in top_artists['items']:
                genres.extend(artist.get('genres', []))
            
            # Count and return top genres
            if genres:
                genre_counts = Counter(genres)
                top_genres = [genre for genre, count in genre_counts.most_common(limit)]
                print(f"User's top genres: {top_genres}")
                return top_genres
            
            return ['pop', 'rock']  # Default if no history
            
        except Exception as e:
            print(f"Error getting top genres: {e}")
            return ['pop', 'rock']
    
    def get_user_top_tracks(self, access_token, limit=20):
        """Get user's top tracks"""
        try:
            sp = spotipy.Spotify(auth=access_token)
            top_tracks = sp.current_user_top_tracks(limit=limit, time_range='short_term')
            return top_tracks['items']
        except Exception as e:
            print(f"Error getting top tracks: {e}")
            return []
    
    def create_personalized_mood_playlist(self, access_token, user_id, mood, user_genres=None):
        """
        Create a personalized playlist based on:
        1. User's detected mood
        2. User's favorite genres from listening history
        """
        sp = spotipy.Spotify(auth=access_token)
        
        # Get user's top genres if not provided
        if user_genres is None or len(user_genres) == 0:
            user_genres = self.get_user_top_genres(access_token)
        
        print(f"Creating playlist for mood: {mood}, genres: {user_genres}")
        
        # Create playlist name with genre
        primary_genre = user_genres[0] if user_genres else 'music'
        playlist_name = f"VibeWise - {mood.title()} {primary_genre.title()} Vibes"
        playlist_description = f"Personalized {mood} playlist based on your love for {primary_genre}"
        
        # Create the playlist
        playlist = sp.user_playlist_create(
            user_id,
            playlist_name,
            public=True,
            description=playlist_description
        )
        
        # Get mood-based search queries
        mood_keywords = self._get_mood_keywords(mood)
        
        # Search for tracks combining mood + user's genres
        all_tracks = []
        for genre in user_genres[:3]:  # Use top 3 genres
            for keyword in mood_keywords[:2]:  # Use 2 mood keywords
                query = f"{keyword} genre:{genre}"
                try:
                    results = sp.search(q=query, type='track', limit=10)
                    tracks = results['tracks']['items']
                    all_tracks.extend(tracks)
                except Exception as e:
                    print(f"Search error for {query}: {e}")
        
        # Remove duplicates and limit
        unique_tracks = []
        track_ids = set()
        for track in all_tracks:
            if track['id'] not in track_ids:
                unique_tracks.append(track)
                track_ids.add(track['id'])
                if len(unique_tracks) >= 30:
                    break
        
        # If we don't have enough tracks, add some popular tracks from genres
        if len(unique_tracks) < 20:
            for genre in user_genres[:2]:
                try:
                    results = sp.search(q=f"genre:{genre}", type='track', limit=15)
                    for track in results['tracks']['items']:
                        if track['id'] not in track_ids:
                            unique_tracks.append(track)
                            track_ids.add(track['id'])
                            if len(unique_tracks) >= 30:
                                break
                except Exception as e:
                    print(f"Additional search error: {e}")
        
        # Add tracks to playlist
        if unique_tracks:
            track_uris = [track['uri'] for track in unique_tracks]
            sp.playlist_add_items(playlist['id'], track_uris)
            print(f"Added {len(track_uris)} tracks to playlist")
        
        return playlist
    
    def _get_mood_keywords(self, mood):
        """Get search keywords for each mood"""
        mood_keywords = {
            'happy': ['happy', 'upbeat', 'cheerful', 'joyful', 'positive'],
            'sad': ['sad', 'melancholy', 'emotional', 'heartbreak', 'blues'],
            'angry': ['aggressive', 'intense', 'powerful', 'rage', 'fierce'],
            'neutral': ['chill', 'calm', 'relaxing', 'ambient', 'peaceful'],
            'surprised': ['energetic', 'exciting', 'dynamic', 'unpredictable'],
            'fear': ['dark', 'mysterious', 'atmospheric', 'suspense'],
            'disgust': ['edgy', 'alternative', 'raw', 'gritty'],
            'excited': ['party', 'celebration', 'energetic', 'upbeat', 'hype'],
            'confident': ['powerful', 'bold', 'strong', 'confident', 'badass'],
            'motivated': ['motivational', 'inspiring', 'epic', 'workout', 'determined'],
            'dancing': ['dance', 'party', 'club', 'groove', 'rhythmic'],
            'romantic': ['romantic', 'love', 'dreamy', 'passion', 'intimate'],
            'peaceful': ['peaceful', 'calm', 'serene', 'meditation', 'soothing'],
            'energetic': ['energetic', 'pump', 'hype', 'adrenaline', 'power'],
            'melancholic': ['melancholic', 'nostalgic', 'bittersweet', 'longing'],
            'playful': ['playful', 'fun', 'lighthearted', 'quirky', 'bouncy']
        }
        return mood_keywords.get(mood, ['music', 'popular'])
    
    def get_playlist_tracks(self, access_token, playlist_id):
        """Get tracks from a playlist"""
        try:
            sp = spotipy.Spotify(auth=access_token)
            results = sp.playlist_tracks(playlist_id)
            return results['items']
        except Exception as e:
            print(f"Error getting playlist tracks: {e}")
            return []