// Authentication Check - authCheck.js
console.log('Auth check loaded');

const AuthCheck = {
    async checkSpotifyConnection() {
        try {
            const response = await fetch('/api/spotify/status/', {
                credentials: 'same-origin'
            });
            
            const data = await response.json();
            return data.connected || false;
        } catch (error) {
            console.error('Error checking Spotify connection:', error);
            return false;
        }
    },
    
    async requireSpotifyLogin(callback) {
        const isConnected = await this.checkSpotifyConnection();
        
        if (!isConnected) {
            // Show modal or redirect to login
            this.showLoginRequired();
            return false;
        }
        
        // User is connected, execute callback
        if (callback) {
            callback();
        }
        return true;
    },
    
    showLoginRequired() {
        const message = 'Spotify login required to use VibeWise!\n\nWould you like to login now?';
        
        if (confirm(message)) {
            // Save current page to return after login
            sessionStorage.setItem('returnTo', window.location.pathname);
            sessionStorage.setItem('autoStartCamera', 'true');
            
            // Redirect to login
            window.location.href = '/login/';
        }
    },
    
    checkAutoStart() {
        const autoStart = sessionStorage.getItem('autoStartCamera');
        const returnTo = sessionStorage.getItem('returnTo');
        
        if (autoStart === 'true' && window.location.pathname === '/') {
            // Clear flags
            sessionStorage.removeItem('autoStartCamera');
            sessionStorage.removeItem('returnTo');
            
            // Auto-start camera after a short delay
            setTimeout(() => {
                const startBtn = document.getElementById('startDetectionBtn');
                if (startBtn) {
                    console.log('Auto-starting camera after login');
                    startBtn.click();
                }
            }, 1000);
        }
    }
};

// Export globally
window.AuthCheck = AuthCheck;