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
    def __init__(self):
        self.mood_labels = [
            'happy', 'sad', 'angry', 'neutral', 'surprised', 'fear', 'disgust',
            'excited', 'confident', 'motivated', 'dancing', 'romantic', 'peaceful',
            'energetic', 'melancholic', 'playful'
        ]
        
        self.face_cascade = cv2.CascadeClassifier(
            cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
        )
        
        self.mood_categories = {
            'positive_high': ['excited', 'dancing', 'energetic', 'playful', 'happy'],
            'positive_calm': ['confident', 'motivated', 'peaceful', 'romantic'],
            'neutral': ['neutral'],
            'negative': ['sad', 'melancholic', 'fear', 'angry', 'disgust', 'surprised']
        }
    
    def detect_mood_from_base64(self, image_data):
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
            
            largest_face = max(faces, key=lambda f: f[2] * f[3])
            (x, y, w, h) = largest_face
            
            face = gray[y:y+h, x:x+w]
            
            mood, confidence = self._analyze_facial_features(face)
            
            return {
                'mood': mood,
                'confidence': round(confidence, 2)
            }
            
        except Exception as e:
            print(f"Error in mood detection: {e}")
            return None
    
    def _analyze_facial_features(self, face_image):
        brightness = np.mean(face_image)
        variance = np.var(face_image)
        
        if brightness > 130:
            category = random.choice(['positive_high', 'positive_calm', 'positive_calm'])
        elif brightness < 80:
            category = random.choice(['negative', 'neutral'])
        else:
            category = random.choice(['positive_calm', 'neutral', 'positive_high'])
        
        possible_moods = self.mood_categories.get(category, self.mood_labels)
        mood = random.choice(possible_moods)
        
        base_confidence = 0.65 + (variance / 10000)
        confidence = min(max(base_confidence, 0.6), 0.95)
        
        return mood, confidence

class SpotifyService:
    def __init__(self):
        self.client_id = settings.SPOTIFY_CLIENT_ID
        self.client_secret = settings.SPOTIFY_CLIENT_SECRET
        self.redirect_uri = settings.SPOTIFY_REDIRECT_URI
    
    def exchange_code_for_tokens(self, code, redirect_uri=None):
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
        headers = {'Authorization': f'Bearer {access_token}'}
        response = requests.get('https://api.spotify.com/v1/me', headers=headers)
        
        if response.status_code == 200:
            return response.json()
        else:
            raise Exception(f"Failed to get profile: {response.text}")
    
    def get_user_top_genres(self, access_token, limit=10):
        try:
            sp = spotipy.Spotify(auth=access_token)
            
            top_artists = sp.current_user_top_artists(limit=50, time_range='medium_term')
            
            genres = []
            for artist in top_artists['items']:
                genres.extend(artist.get('genres', []))
            
            if genres:
                genre_counts = Counter(genres)
                top_genres = [genre for genre, count in genre_counts.most_common(limit)]
                print(f"✅ User's top genres: {top_genres}")
                return top_genres
            
            return ['pop', 'rock']
            
        except Exception as e:
            print(f"Error getting top genres: {e}")
            return ['pop', 'rock']
    
    def get_user_top_tracks(self, access_token, limit=50):
        try:
            sp = spotipy.Spotify(auth=access_token)
            tracks = []
            recent = sp.current_user_top_tracks(limit=20, time_range='short_term')
            tracks.extend(recent['items'])
            
            medium = sp.current_user_top_tracks(limit=20, time_range='medium_term')
            tracks.extend(medium['items'])
            
            long_term = sp.current_user_top_tracks(limit=10, time_range='long_term')
            tracks.extend(long_term['items'])
            
            print(f"✅ Got {len(tracks)} user top tracks")
            return tracks
            
        except Exception as e:
            print(f"Error getting top tracks: {e}")
            return []
    
    def get_audio_features_for_mood(self, mood):
        mood_features = {
            'happy': {'valence': (0.7, 1.0), 'energy': (0.6, 1.0), 'danceability': (0.5, 1.0)},
            'excited': {'valence': (0.8, 1.0), 'energy': (0.8, 1.0), 'danceability': (0.7, 1.0)},
            'playful': {'valence': (0.7, 1.0), 'energy': (0.6, 0.9), 'danceability': (0.6, 1.0)},
            'dancing': {'valence': (0.6, 1.0), 'energy': (0.7, 1.0), 'danceability': (0.8, 1.0)},
            'energetic': {'valence': (0.6, 1.0), 'energy': (0.8, 1.0), 'danceability': (0.7, 1.0)},
            'confident': {'valence': (0.5, 0.8), 'energy': (0.5, 0.8), 'danceability': (0.4, 0.8)},
            'motivated': {'valence': (0.6, 0.9), 'energy': (0.6, 0.9), 'danceability': (0.5, 0.9)},
            'peaceful': {'valence': (0.4, 0.7), 'energy': (0.2, 0.5), 'danceability': (0.2, 0.5)},
            'romantic': {'valence': (0.5, 0.8), 'energy': (0.3, 0.6), 'danceability': (0.3, 0.7)},
            'sad': {'valence': (0.0, 0.4), 'energy': (0.2, 0.5), 'danceability': (0.2, 0.5)},
            'melancholic': {'valence': (0.1, 0.4), 'energy': (0.2, 0.5), 'danceability': (0.2, 0.5)},
            'angry': {'valence': (0.2, 0.5), 'energy': (0.7, 1.0), 'danceability': (0.4, 0.8)},
            'neutral': {'valence': (0.4, 0.6), 'energy': (0.4, 0.6), 'danceability': (0.4, 0.6)},
            'surprised': {'valence': (0.5, 0.8), 'energy': (0.6, 0.9), 'danceability': (0.5, 0.8)},
        }
        
        return mood_features.get(mood.lower(), mood_features['neutral'])

    def create_personalized_mood_playlist(self, access_token, user_id, mood, user_genres=None):
        sp = spotipy.Spotify(auth=access_token)
        print(f"\n🎵 Creating PERFECT playlist for mood: {mood}")
        
        if user_genres is None or len(user_genres) == 0:
            user_genres = self.get_user_top_genres(access_token)
        
        print(f"📊 User's top genres: {user_genres[:5]}")

        all_user_tracks = []
        
        try:
            recent = sp.current_user_top_tracks(limit=20, time_range='short_term')
            all_user_tracks.extend(recent['items'])
            print(f"✅ Got {len(recent['items'])} recent tracks")
        except:
            print("⚠️ Could not get recent tracks")
        
        try:
            medium = sp.current_user_top_tracks(limit=30, time_range='medium_term')
            all_user_tracks.extend(medium['items'])
            print(f"✅ Got {len(medium['items'])} medium-term tracks")
        except:
            print("⚠️ Could not get medium-term tracks")
        
        try:
            long_term = sp.current_user_top_tracks(limit=50, time_range='long_term')
            all_user_tracks.extend(long_term['items'])
            print(f"✅ Got {len(long_term['items'])} all-time favorites")
        except:
            print("⚠️ Could not get long-term tracks")
        
        unique_tracks = {}
        for track in all_user_tracks:
            if track['id'] not in unique_tracks:
                unique_tracks[track['id']] = track
        
        all_user_tracks = list(unique_tracks.values())
        print(f"✅ Total unique tracks from your history: {len(all_user_tracks)}")
        
        primary_genre = user_genres[0] if user_genres else 'music'
        playlist_name = f"VibeWise - {mood.title()} {primary_genre.title()} 🎵"
        
        playlist = sp.user_playlist_create(
            user_id,
            playlist_name,
            public=True,
            description=f"Your {mood} vibes playlist based on 1 year of listening! Featuring {', '.join(user_genres[:2])}"
        )
        
        print(f"✅ Created playlist: {playlist_name}")
        
        mood_selection = {
            'sad': {'energy_range': (0.0, 0.5), 'track_indices': list(range(20, 70))},
            'emotional': {'energy_range': (0.2, 0.6), 'track_indices': list(range(15, 65))},
            'melancholic': {'energy_range': (0.1, 0.5), 'track_indices': list(range(25, 75))},
            'romantic': {'energy_range': (0.3, 0.7), 'track_indices': list(range(10, 60))},
            'happy': {'energy_range': (0.6, 1.0), 'track_indices': list(range(0, 50))},
            'dancing': {'energy_range': (0.7, 1.0), 'track_indices': list(range(0, 40))},
            'excited': {'energy_range': (0.7, 1.0), 'track_indices': list(range(0, 45))},
            'energetic': {'energy_range': (0.7, 1.0), 'track_indices': list(range(0, 50))},
            'playful': {'energy_range': (0.6, 0.9), 'track_indices': list(range(5, 55))},
            'peaceful': {'energy_range': (0.2, 0.5), 'track_indices': list(range(30, 80))},
            'confident': {'energy_range': (0.5, 0.8), 'track_indices': list(range(10, 60))},
            'motivated': {'energy_range': (0.6, 0.9), 'track_indices': list(range(0, 50))},
            'neutral': {'energy_range': (0.4, 0.7), 'track_indices': list(range(15, 65))},
        }
        
        selection = mood_selection.get(mood.lower(), mood_selection['neutral'])
        print(f"🎯 Strategy for {mood}: Using tracks from indices {selection['track_indices'][:5]}...")
        selected_tracks = []
        for idx in selection['track_indices']:
            if idx < len(all_user_tracks):
                selected_tracks.append(all_user_tracks[idx])
                if len(selected_tracks) >= 30:
                    break
        
        print(f"✅ Selected {len(selected_tracks)} tracks from your listening history")

        track_uris = [track['uri'] for track in selected_tracks]
        
        if track_uris:
            try:
                for i in range(0, len(track_uris), 100):
                    chunk = track_uris[i:i+100]
                    sp.playlist_add_items(playlist['id'], chunk)
                
                print(f"✅ Successfully added {len(track_uris)} tracks to playlist")
                
                print(f"📝 Sample tracks in playlist:")
                for i, track in enumerate(selected_tracks[:5]):
                    artists = ', '.join([artist['name'] for artist in track['artists']])
                    print(f"   {i+1}. {track['name']} - {artists}")
                
            except Exception as e:
                print(f"⚠️ Error adding tracks: {e}")
        
        if len(track_uris) < 20:
            print(f"⚠️ Need more tracks, searching for {mood} + {user_genres[0]} songs...")
            
            mood_keywords = {
                'sad': ['ballad', 'emotional', 'heartbreak'],
                'emotional': ['touching', 'meaningful', 'deep'],
                'romantic': ['love', 'romance', 'crush'],
                'happy': ['upbeat', 'bright', 'sunshine'],
                'dancing': ['dance', 'party', 'groove'],
                'excited': ['hype', 'energy', 'pump'],
                'energetic': ['powerful', 'intense', 'dynamic'],
                'playful': ['fun', 'cute', 'cheerful'],
                'peaceful': ['calm', 'soothing', 'relax'],
                'motivated': ['motivational', 'inspiring', 'strong'],
            }
            
            keywords = mood_keywords.get(mood.lower(), ['music'])
            
            for genre in user_genres[:2]:
                for keyword in keywords:
                    try:
                        query = f"{keyword} genre:{genre}"
                        results = sp.search(q=query, type='track', limit=5)
                        
                        for track in results['tracks']['items']:
                            if track['uri'] not in track_uris:
                                track_uris.append(track['uri'])
                                sp.playlist_add_items(playlist['id'], [track['uri']])
                                
                                if len(track_uris) >= 30:
                                    break
                        
                        if len(track_uris) >= 30:
                            break
                            
                    except Exception as e:
                        print(f"Search error: {e}")
                
                if len(track_uris) >= 30:
                    break
            
            print(f"✅ Added {len(track_uris) - len(selected_tracks)} more tracks from search")
        
        print(f"🎉 Final playlist has {len(track_uris)} tracks")
        
        return playlist
    
    def get_playlist_tracks(self, access_token, playlist_id):
        try:
            sp = spotipy.Spotify(auth=access_token)
            results = sp.playlist_tracks(playlist_id)
            return results['items']
        except Exception as e:
            print(f"Error getting playlist tracks: {e}")
            return []