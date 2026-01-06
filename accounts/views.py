from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.conf import settings
from .models import User, UserPreferences
import requests

def index(request):
    return render(request, 'index.html')

def about(request):
    return render(request, 'about.html')

def login_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        
        user = authenticate(request, username=email, password=password)
        
        if user is not None:
            login(request, user)
            messages.success(request, 'Login successful!')
            return redirect('dashboard')
        else:
            messages.error(request, 'Invalid email or password')
    
    return render(request, 'login.html')

def register_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    
    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        password = request.POST.get('password')
        password_confirm = request.POST.get('password_confirm')
        
        if password != password_confirm:
            messages.error(request, 'Passwords do not match')
            return render(request, 'register.html')
        
        if User.objects.filter(email=email).exists():
            messages.error(request, 'Email already exists')
            return render(request, 'register.html')
        
        try:
            user = User.objects.create_user(
                username=email,
                email=email,
                password=password,
                name=name
            )
            UserPreferences.objects.create(user=user)
            login(request, user)
            messages.success(request, 'Registration successful!')
            return redirect('dashboard')
        
        except Exception as e:
            messages.error(request, f'Registration failed: {str(e)}')
    
    return render(request, 'register.html')

@login_required
def dashboard(request):
    context = {
        'user': request.user,
        'spotify_connected': bool(request.user.spotify_access_token)
    }
    return render(request, 'dashboard.html', context)

def logout_view(request):
    if request.user.is_authenticated:
        user = request.user
        user.spotify_access_token = None
        user.spotify_refresh_token = None
        user.spotify_id = None
        user.save()
    
    logout(request)
    messages.success(request, 'Logged out successfully')
    return redirect('index')

def spotify_login(request):
    from urllib.parse import urlencode
    scope = 'user-top-read playlist-modify-public playlist-modify-private user-read-private user-read-email'
    params = {
        'client_id': settings.SPOTIFY_CLIENT_ID,
        'response_type': 'code',
        'redirect_uri': settings.SPOTIFY_REDIRECT_URI,
        'scope': scope,
        'show_dialog': 'false'
    }
    
    auth_url = f'https://accounts.spotify.com/authorize?{urlencode(params)}'
    return redirect(auth_url)

def spotify_callback(request):
    code = request.GET.get('code')
    error = request.GET.get('error')
    
    if error:
        messages.error(request, f'Spotify authorization failed: {error}')
        return redirect('index')
    
    if not code:
        messages.error(request, 'No authorization code received')
        return redirect('index')
    return render(request, 'spotify_callback.html', {'code': code})

@login_required
def profile(request):
    if request.method == 'POST':
        user = request.user
        user.name = request.POST.get('name', user.name)
        user.save()
        messages.success(request, 'Profile updated successfully')
        return redirect('profile')
    
    context = {
        'user': request.user
    }
    return render(request, 'profile.html', context)