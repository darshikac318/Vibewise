import spotipy
from spotipy.oauth2 import SpotifyOAuth
from django.shortcuts import redirect

def spotify_login(request):
    sp_oauth = SpotifyOAuth(
        client_id=settings.SPOTIFY_CLIENT_ID,
        client_secret=settings.SPOTIFY_CLIENT_SECRET,
        redirect_uri=settings.SPOTIFY_REDIRECT_URI,
        scope="playlist-modify-private user-read-private",
    )
    auth_url = sp_oauth.get_authorize_url()
    return redirect(auth_url)

def spotify_callback(request):
    sp_oauth = SpotifyOAuth(
        client_id=settings.SPOTIFY_CLIENT_ID,
        client_secret=settings.SPOTIFY_CLIENT_SECRET,
        redirect_uri=settings.SPOTIFY_REDIRECT_URI,
    )
    code = request.GET.get('code')
    token_info = sp_oauth.get_access_token(code)
    
    # Save token to user's session
    request.session['spotify_token'] = token_info
    return redirect('profile')  # Redirect to profile after auth