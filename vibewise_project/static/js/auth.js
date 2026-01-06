// WORKING Authentication System with Logout
console.log('🔐 Auth system loading...');

class AuthManager {
    constructor() {
        this.isLoggedIn = false;
        this.userData = null;
    }

    async init() {
        console.log('🔐 Initializing auth...');
        await this.checkAuthStatus();
        this.updateUI();
        this.setupEventListeners();
        console.log('✅ Auth ready');
    }

    async checkAuthStatus() {
        try {
            const response = await fetch('/api/spotify/status/', {
                credentials: 'same-origin',
                cache: 'no-cache'
            });
            
            const data = await response.json();
            
            if (data.connected && data.user) {
                this.isLoggedIn = true;
                this.userData = data.user;
                console.log('✅ Logged in:', data.user.name);
            } else {
                this.isLoggedIn = false;
                this.userData = null;
                console.log('❌ Not logged in');
            }
            
            return this.isLoggedIn;
        } catch (error) {
            console.error('Auth check error:', error);
            this.isLoggedIn = false;
            this.userData = null;
            return false;
        }
    }

    updateUI() {
        const loginNav = document.getElementById('loginNavItem');
        const profileNav = document.getElementById('profileNavItem');
        const userDisplay = document.getElementById('userNameDisplay');
        const logoutBtn = document.getElementById('logoutBtn');

        if (this.isLoggedIn && this.userData) {
            // Logged in - show profile, hide login
            if (loginNav) loginNav.style.display = 'none';
            if (profileNav) profileNav.style.display = 'block';
            if (userDisplay) {
                userDisplay.textContent = this.userData.name || 'User';
                userDisplay.style.display = 'inline-block';
            }
            if (logoutBtn) logoutBtn.style.display = 'inline-block';
        } else {
            // Logged out - show login, hide profile
            if (loginNav) loginNav.style.display = 'block';
            if (profileNav) profileNav.style.display = 'none';
            if (userDisplay) userDisplay.style.display = 'none';
            if (logoutBtn) logoutBtn.style.display = 'none';
        }
    }

    setupEventListeners() {
        // Setup logout button
        const logoutBtn = document.getElementById('logoutBtn');
        if (logoutBtn) {
            // Remove old listeners
            const newBtn = logoutBtn.cloneNode(true);
            logoutBtn.parentNode.replaceChild(newBtn, logoutBtn);
            
            // Add new listener
            newBtn.addEventListener('click', () => {
                console.log('🚪 Logout clicked');
                this.logout();
            });
        }
    }

    async logout() {
        const confirmed = confirm('Are you sure you want to logout?');
        
        if (!confirmed) {
            console.log('Logout cancelled');
            return;
        }

        console.log('🚪 Logging out...');
        
        try {
            const csrfToken = this.getCsrfToken();
            
            if (!csrfToken) {
                throw new Error('CSRF token not found');
            }
            
            const response = await fetch('/api/spotify/logout/', {
                method: 'POST',
                credentials: 'same-origin',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': csrfToken
                }
            });

            const data = await response.json();
            console.log('Logout response:', data);

            if (response.ok && data.success) {
                console.log('✅ Logout successful');
                
                // Clear local state
                this.isLoggedIn = false;
                this.userData = null;
                
                // Clear storage
                sessionStorage.clear();
                localStorage.removeItem('vibeWiseCurrentUser');
                
                // Show success message
                this.showMessage('Logged out successfully', 'success');
                
                // Redirect to home after 1 second
                setTimeout(() => {
                    window.location.href = '/';
                }, 1000);
            } else {
                throw new Error(data.error || 'Logout failed');
            }
        } catch (error) {
            console.error('❌ Logout error:', error);
            this.showMessage('Logout failed: ' + error.message, 'error');
        }
    }

    async requireAuth() {
        await this.checkAuthStatus();
        
        if (!this.isLoggedIn) {
            console.log('Auth required');
            const message = 'Please login with Spotify to use this feature.\n\nClick OK to login now.';
            if (confirm(message)) {
                sessionStorage.setItem('autoStartCamera', 'true');
                sessionStorage.setItem('returnTo', window.location.pathname);
                window.location.href = '/login/';
            }
            return false;
        }
        
        return true;
    }

    getCsrfToken() {
        // Try cookie first
        const cookies = document.cookie.split(';');
        for (let cookie of cookies) {
            const [name, value] = cookie.trim().split('=');
            if (name === 'csrftoken') {
                return decodeURIComponent(value);
            }
        }
        
        // Try meta tag
        const meta = document.querySelector('meta[name="csrf-token"]');
        if (meta) {
            return meta.getAttribute('content');
        }
        
        // Try hidden input
        const input = document.querySelector('input[name="csrfmiddlewaretoken"]');
        if (input) {
            return input.value;
        }
        
        return null;
    }

    showMessage(message, type = 'info') {
        const notification = document.createElement('div');
        notification.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            padding: 1rem 1.5rem;
            background: ${type === 'error' ? '#ff6b6b' : type === 'success' ? '#1db954' : '#42a5f5'};
            color: white;
            border-radius: 8px;
            z-index: 10000;
            font-weight: 500;
            box-shadow: 0 4px 12px rgba(0,0,0,0.2);
            animation: slideIn 0.3s ease;
        `;
        notification.textContent = message;
        
        document.body.appendChild(notification);
        
        setTimeout(() => {
            notification.style.animation = 'slideOut 0.3s ease';
            setTimeout(() => notification.remove(), 300);
        }, 3000);
    }
}

// Spotify OAuth function
function loginWithSpotify() {
    const clientId = 'f99dc779642f4540b550a3217ea7a4a6';
    const redirectUri = encodeURIComponent('http://127.0.0.1:8000/callback/');
    
    const scopes = encodeURIComponent([
        'user-read-private',
        'user-read-email',
        'user-top-read',
        'playlist-read-private',
        'playlist-modify-public',
        'playlist-modify-private',
        'user-library-read',
        'user-read-recently-played',
    ].join(' '));
    
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
    
    console.log('🎵 Redirecting to Spotify...');
    window.location.href = spotifyAuthUrl;
}

// Make globally available
window.loginWithSpotify = loginWithSpotify;

// Initialize auth manager
let authManager = null;

if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', async () => {
        authManager = new AuthManager();
        await authManager.init();
        window.authManager = authManager;
    });
} else {
    authManager = new AuthManager();
    authManager.init().then(() => {
        window.authManager = authManager;
    });
}

console.log('✅ Auth system loaded');