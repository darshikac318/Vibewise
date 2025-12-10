// Complete Authentication System
console.log('Auth system loaded');

class AuthenticationManager {
    constructor() {
        this.isLoggedIn = false;
        this.userData = null;
        this.checkInProgress = false;
    }

    async init() {
        console.log('AuthManager initializing...');
        await this.checkAuthStatus();
        this.updateUI();
        this.setupEventListeners();
        
        // Force UI update after delay
        setTimeout(() => {
            console.log('Forcing UI update after delay');
            this.updateUI();
        }, 200);
    }

    async checkAuthStatus() {
        if (this.checkInProgress) {
            console.log('Auth check already in progress, waiting...');
            return this.isLoggedIn;
        }
        
        this.checkInProgress = true;
        
        try {
            console.log('Checking auth status...');
            const response = await fetch('/api/spotify/status/', {
                credentials: 'same-origin',
                cache: 'no-cache'
            });
            
            const data = await response.json();
            console.log('Auth status response:', data);
            
            if (data.connected && data.user) {
                this.isLoggedIn = true;
                this.userData = data.user;
                console.log('✓ User is logged in:', this.userData.name);
            } else {
                this.isLoggedIn = false;
                this.userData = null;
                console.log('✗ User is not logged in');
            }
            
            this.checkInProgress = false;
            return this.isLoggedIn;
        } catch (error) {
            console.error('Error checking auth status:', error);
            this.isLoggedIn = false;
            this.userData = null;
            this.checkInProgress = false;
            return false;
        }
    }

    updateUI() {
        console.log('Updating UI - isLoggedIn:', this.isLoggedIn);
        
        const loginNavItem = document.getElementById('loginNavItem');
        const profileNavItem = document.getElementById('profileNavItem');
        const userDisplay = document.getElementById('userNameDisplay');
        const logoutBtn = document.getElementById('logoutBtn');

        if (this.isLoggedIn && this.userData) {
            console.log('→ Showing logged-in UI');
            
            if (loginNavItem) {
                loginNavItem.style.display = 'none';
            }
            
            if (profileNavItem) {
                profileNavItem.style.display = 'block';
            }
            
            if (userDisplay) {
                userDisplay.textContent = this.userData.name || 'User';
                userDisplay.style.display = 'inline-block';
            }
            
            if (logoutBtn) {
                logoutBtn.style.display = 'inline-block';
            }
        } else {
            console.log('→ Showing logged-out UI');
            
            if (loginNavItem) {
                loginNavItem.style.display = 'block';
            }
            
            if (profileNavItem) {
                profileNavItem.style.display = 'none';
            }
            
            if (userDisplay) {
                userDisplay.style.display = 'none';
            }
            
            if (logoutBtn) {
                logoutBtn.style.display = 'none';
            }
        }
    }

    setupEventListeners() {
        const logoutBtn = document.getElementById('logoutBtn');
        if (logoutBtn) {
            logoutBtn.addEventListener('click', () => this.logout());
        }
    }

    async logout() {
        const confirmed = confirm('Are you sure you want to logout?\n\nYou can login with a different Spotify account after logout.');
        
        if (!confirmed) {
            console.log('Logout cancelled by user');
            return;
        }

        console.log('Logging out...');
        
        try {
            const csrfToken = this.getCsrfToken();
            console.log('CSRF Token:', csrfToken ? 'Present' : 'Missing');
            
            if (!csrfToken) {
                throw new Error('CSRF token not found. Please refresh and try again.');
            }
            
            const response = await fetch('/api/spotify/logout/', {
                method: 'POST',
                credentials: 'same-origin',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': csrfToken
                }
            });

            console.log('Logout response status:', response.status);
            
            const data = await response.json();
            console.log('Logout response data:', data);

            if (response.ok && data.success) {
                console.log('✓ Logged out successfully on server');
                
                // Clear local state
                this.isLoggedIn = false;
                this.userData = null;
                
                // Clear all storage
                sessionStorage.clear();
                localStorage.removeItem('vibeWiseCurrentUser');
                
                // Force page reload to clear everything
                console.log('Redirecting to homepage...');
                window.location.replace('/');
            } else {
                throw new Error(data.error || data.message || 'Logout failed on server');
            }
        } catch (error) {
            console.error('❌ Logout error:', error);
            alert(`Failed to logout: ${error.message}\n\nPlease try refreshing the page.`);
        }
    }

    async requireAuth() {
        // Always recheck auth status
        await this.checkAuthStatus();
        
        if (!this.isLoggedIn) {
            console.log('Auth required but user not logged in');
            const message = '🎵 Spotify Login Required\n\nYou need to connect with Spotify to use VibeWise mood detection.\n\nClick OK to login now.';
            if (confirm(message)) {
                sessionStorage.setItem('autoStartCamera', 'true');
                sessionStorage.setItem('returnTo', window.location.pathname);
                window.location.href = '/login/';
            }
            return false;
        }
        
        console.log('Auth check passed, user is logged in');
        return true;
    }

    getCsrfToken() {
        const cookies = document.cookie.split(';');
        for (let cookie of cookies) {
            const [name, value] = cookie.trim().split('=');
            if (name === 'csrftoken') {
                return decodeURIComponent(value);
            }
        }
        return '';
    }
}

// Spotify OAuth
function loginWithSpotify() {
    const clientId = 'f99dc779642f4540b550a3217ea7a4a6';
    const redirectUri = encodeURIComponent('http://127.0.0.1:8000/callback/');
    const scopes = encodeURIComponent('user-read-private user-read-email user-top-read playlist-read-private playlist-modify-public playlist-modify-private');
    
    const fromPage = window.location.pathname;
    if (fromPage === '/') {
        sessionStorage.setItem('autoStartCamera', 'true');
    }
    sessionStorage.setItem('returnTo', fromPage);
    
    const spotifyAuthUrl = `https://accounts.spotify.com/authorize?` +
        `client_id=${clientId}&` +
        `response_type=code&` +
        `redirect_uri=${redirectUri}&` +
        `scope=${scopes}&` +
        `show_dialog=true`;
    
    window.location.href = spotifyAuthUrl;
}

// Global instance
let authManager;

// Initialize on DOM load
document.addEventListener('DOMContentLoaded', async () => {
    console.log('DOM loaded, initializing auth manager');
    authManager = new AuthenticationManager();
    await authManager.init();
    window.authManager = authManager;
    console.log('Auth manager ready:', authManager.isLoggedIn);
});

window.loginWithSpotify = loginWithSpotify;