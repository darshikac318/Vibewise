// FIXED Camera Manager - Single popup, no image storage
console.log('Camera.js loaded - Privacy-focused version');

let video = null;
let canvas = null;
let stream = null;
let authCheckInProgress = false; // Prevent duplicate checks

// Initialize camera on page load
document.addEventListener('DOMContentLoaded', function() {
    console.log('DOM loaded, initializing camera manager');
    
    video = document.getElementById('video');
    canvas = document.getElementById('canvas');
    
    if (!video) console.error('Video element not found!');
    if (!canvas) console.error('Canvas element not found!');
    
    // Setup start detection button
    const startBtn = document.getElementById('startDetectionBtn');
    if (startBtn) {
        console.log('Start detection button found');
        startBtn.addEventListener('click', async function(e) {
            e.preventDefault();
            e.stopPropagation(); // Prevent event bubbling
            console.log('Start detection clicked');
            
            // ⚠️ SINGLE AUTH CHECK - No double popup
            if (!await checkAuthenticationOnce()) {
                return; // STOP if not authenticated
            }
            
            showCameraSection();
            startCamera();
        });
    }
    
    // Setup detect mood button
    const detectBtn = document.getElementById('detectButton');
    if (detectBtn) {
        detectBtn.addEventListener('click', async function() {
            console.log('Detect mood clicked');
            
            // Quick check without popup
            if (!await quickAuthCheck()) {
                stopCamera();
                return;
            }
            
            detectMood();
        });
    }
    
    // Setup stop camera button
    const stopBtn = document.getElementById('stopCamera');
    if (stopBtn) {
        stopBtn.addEventListener('click', function() {
            console.log('Stop camera clicked');
            stopCamera();
        });
    }
});

/**
 * ⚠️ SINGLE AUTH CHECK - Prevents double popup
 */
async function checkAuthenticationOnce() {
    // Prevent multiple simultaneous checks
    if (authCheckInProgress) {
        console.log('Auth check already in progress, waiting...');
        return false;
    }
    
    authCheckInProgress = true;
    console.log('🔒 Checking authentication (single check)...');
    
    try {
        if (!window.authManager) {
            console.error('❌ Auth manager not available!');
            showMessage('Please refresh the page and try again.', 'error');
            authCheckInProgress = false;
            return false;
        }
        
        // Check authentication status
        console.log('Checking authentication status from server...');
        const isAuthenticated = await window.authManager.checkAuthStatus();
        
        if (!isAuthenticated) {
            console.log('❌ USER NOT AUTHENTICATED');
            
            // Single login prompt
            const message = '🎵 Spotify Login Required\n\n' +
                          'You need to connect with Spotify to use VibeWise mood detection.\n\n' +
                          'Click OK to login now.';
            
            if (confirm(message)) {
                sessionStorage.setItem('autoStartCamera', 'true');
                sessionStorage.setItem('returnTo', window.location.pathname);
                window.location.href = '/login/';
            }
            
            authCheckInProgress = false;
            return false;
        }
        
        console.log('✅ USER AUTHENTICATED');
        authCheckInProgress = false;
        return true;
        
    } catch (error) {
        console.error('❌ Authentication check error:', error);
        showMessage('Failed to verify authentication.', 'error');
        authCheckInProgress = false;
        return false;
    }
}

/**
 * Quick auth check without popup (for subsequent actions)
 */
async function quickAuthCheck() {
    try {
        if (!window.authManager) return false;
        
        const response = await fetch('/api/spotify/status/', {
            credentials: 'same-origin',
            cache: 'no-cache'
        });
        
        const data = await response.json();
        
        if (!data.connected) {
            showMessage('Session expired. Please login again.', 'error');
            setTimeout(() => window.location.href = '/login/', 1500);
            return false;
        }
        
        return true;
    } catch (error) {
        console.error('Quick auth check error:', error);
        return false;
    }
}

function showCameraSection() {
    console.log('Showing camera section');
    const cameraSection = document.getElementById('cameraSection');
    if (cameraSection) {
        cameraSection.style.display = 'block';
        cameraSection.scrollIntoView({ behavior: 'smooth' });
    }
}

async function startCamera() {
    console.log('Starting camera...');
    
    try {
        stream = await navigator.mediaDevices.getUserMedia({
            video: {
                width: { ideal: 640 },
                height: { ideal: 480 },
                facingMode: 'user'
            },
            audio: false
        });
        
        console.log('✅ Camera access granted');
        
        if (video) {
            video.srcObject = stream;
            await video.play();
            console.log('Video playing');
            
            const videoContainer = document.getElementById('videoContainer');
            if (videoContainer) {
                videoContainer.style.display = 'block';
            }
            
            const stopBtn = document.getElementById('stopCamera');
            if (stopBtn) {
                stopBtn.style.display = 'inline-block';
            }
            
            showMessage('Camera started successfully!', 'success');
        }
        
    } catch (error) {
        console.error('Camera error:', error);
        
        let errorMessage = 'Failed to access camera. ';
        if (error.name === 'NotAllowedError') {
            errorMessage += 'Please allow camera access in your browser.';
        } else if (error.name === 'NotFoundError') {
            errorMessage += 'No camera found on your device.';
        } else {
            errorMessage += error.message;
        }
        
        showMessage(errorMessage, 'error');
    }
}

function stopCamera() {
    console.log('Stopping camera');
    
    if (stream) {
        stream.getTracks().forEach(track => {
            track.stop();
            console.log('Track stopped:', track.kind);
        });
        stream = null;
    }
    
    if (video) {
        video.srcObject = null;
    }
    
    const videoContainer = document.getElementById('videoContainer');
    if (videoContainer) {
        videoContainer.style.display = 'none';
    }
    
    const stopBtn = document.getElementById('stopCamera');
    if (stopBtn) {
        stopBtn.style.display = 'none';
    }
    
    showMessage('Camera stopped', 'info');
}

function captureFrame() {
    console.log('Capturing frame');
    
    if (!video || !canvas) {
        console.error('Video or canvas not available');
        return null;
    }
    
    canvas.width = video.videoWidth;
    canvas.height = video.videoHeight;
    
    const context = canvas.getContext('2d');
    context.drawImage(video, 0, 0, canvas.width, canvas.height);
    
    // Convert to base64 (temporary, not saved)
    const imageData = canvas.toDataURL('image/jpeg', 0.8);
    console.log('✅ Frame captured (NOT saved, privacy-protected)');
    
    return imageData;
}

async function detectMood() {
    console.log('Detecting mood...');
    
    try {
        // Quick auth check
        if (!await quickAuthCheck()) {
            stopCamera();
            throw new Error('Session expired. Please login again.');
        }
        
        // Capture frame (not saved to storage)
        const imageData = captureFrame();
        
        if (!imageData) {
            throw new Error('Failed to capture image');
        }
        
        showLoading(true);
        
        const csrfToken = getCsrfToken();
        console.log('CSRF token:', csrfToken ? 'Present' : 'Missing');
        
        // Send to backend (backend will NOT save image)
        console.log('Sending request to /api/mood/detect/');
        const response = await fetch('/api/mood/detect/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': csrfToken
            },
            credentials: 'same-origin',
            body: JSON.stringify({
                image: imageData,
                save_image: false // ⚠️ IMPORTANT: Don't save image
            })
        });
        
        console.log('Response status:', response.status);
        
        if (response.status === 401) {
            stopCamera();
            throw new Error('Session expired. Please login again.');
        }
        
        const data = await response.json();
        console.log('Response data:', data);
        
        if (response.ok) {
            displayMoodResult(data);
            
            console.log('Detection complete, stopping camera...');
            showMessage('Mood detected! Camera stopped.', 'success');
            
            setTimeout(() => {
                stopCamera();
            }, 1000);
            
        } else {
            throw new Error(data.error || 'Failed to detect mood');
        }
        
    } catch (error) {
        console.error('Detection error:', error);
        showMessage('Error: ' + error.message, 'error');
        
        if (error.message.includes('login') || error.message.includes('Session expired')) {
            setTimeout(() => {
                window.location.href = '/login/';
            }, 2000);
        }
    } finally {
        showLoading(false);
    }
}

function displayMoodResult(result) {
    console.log('Displaying mood result:', result);
    
    const moodEmojis = {
        'happy': '😊', 'sad': '😢', 'angry': '😠', 'neutral': '😐',
        'surprised': '😲', 'fear': '😨', 'disgust': '🤢', 'excited': '🤩',
        'confident': '😎', 'motivated': '💪', 'dancing': '💃', 'romantic': '😍',
        'peaceful': '😌', 'energetic': '⚡', 'melancholic': '🥺', 'playful': '😜'
    };
    
    const emoji = moodEmojis[result.mood] || '😊';
    const confidence = (result.confidence * 100).toFixed(1);
    
    const resultContainer = document.getElementById('moodResult');
    if (resultContainer) {
        resultContainer.innerHTML = `
            <div style="text-align: center; padding: 2rem; background: var(--bg-secondary); border-radius: 12px; margin-top: 2rem;">
                <div style="font-size: 5rem; margin-bottom: 1rem;">${emoji}</div>
                <h3 style="font-size: 2rem; margin-bottom: 0.5rem;">
                    ${result.mood.charAt(0).toUpperCase() + result.mood.slice(1)}
                </h3>
                <p style="font-size: 1.2rem; color: var(--text-secondary); margin-bottom: 1rem;">
                    Confidence: ${confidence}%
                </p>
                <div style="background: var(--bg-tertiary); height: 8px; border-radius: 4px; overflow: hidden; margin-bottom: 1.5rem;">
                    <div style="background: var(--primary-color); height: 100%; width: ${confidence}%; transition: width 0.3s;"></div>
                </div>
                <p style="font-size: 0.9rem; color: var(--text-secondary); margin-bottom: 1rem;">
                    🔒 Your image was processed privately and not saved
                </p>
                <button onclick="createPlaylistForMood('${result.mood}')" class="btn-primary">
                    🎵 Create Personalized Playlist
                </button>
            </div>
        `;
        resultContainer.style.display = 'block';
    }
}

function createPlaylistForMood(mood) {
    console.log('Creating playlist for mood:', mood);
    
    showLoading(true);
    showMessage('Creating your personalized playlist...', 'info');
    
    const csrfToken = getCsrfToken();
    
    fetch('/api/spotify/create_playlist/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': csrfToken
        },
        credentials: 'same-origin',
        body: JSON.stringify({ mood: mood })
    })
    .then(response => {
        if (response.status === 401) {
            throw new Error('Session expired. Please login again.');
        }
        return response.json();
    })
    .then(data => {
        console.log('Playlist created:', data);
        
        if (data.playlist) {
            showMessage(`✅ Playlist created successfully!`, 'success');
            
            const moodResult = document.getElementById('moodResult');
            if (moodResult) {
                const genresText = data.genres_used ? data.genres_used.join(', ') : 'your favorites';
                moodResult.innerHTML += `
                    <div style="margin-top: 2rem; padding: 2rem; background: var(--bg-tertiary); border-radius: 12px; border: 2px solid var(--primary-color);">
                        <h3 style="margin-bottom: 1rem;">🎵 Your Personalized Playlist</h3>
                        <p style="font-size: 1.1rem; margin-bottom: 1rem;">
                            <strong>${data.playlist.name}</strong>
                        </p>
                        <p style="color: var(--text-secondary); margin-bottom: 1.5rem;">
                            ${data.message || `Based on ${genresText}`}
                        </p>
                        <a href="${data.spotify_url}" target="_blank" class="btn-primary" style="display: inline-block; text-decoration: none;">
                            Open in Spotify
                        </a>
                    </div>
                `;
            }
        } else {
            throw new Error(data.error || 'Failed to create playlist');
        }
    })
    .catch(error => {
        console.error('Playlist creation error:', error);
        showMessage('Failed to create playlist: ' + error.message, 'error');
        
        if (error.message.includes('login') || error.message.includes('Session expired')) {
            setTimeout(() => {
                window.location.href = '/login/';
            }, 2000);
        }
    })
    .finally(() => {
        showLoading(false);
    });
}

function showLoading(isLoading) {
    const detectBtn = document.getElementById('detectButton');
    const loadingIndicator = document.getElementById('loadingIndicator');
    
    if (detectBtn) {
        detectBtn.disabled = isLoading;
        detectBtn.textContent = isLoading ? 'Detecting...' : 'Detect Mood';
    }
    
    if (loadingIndicator) {
        loadingIndicator.style.display = isLoading ? 'block' : 'none';
    }
}

function showMessage(message, type = 'info') {
    console.log(type.toUpperCase() + ':', message);
    
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
        max-width: 350px;
    `;
    notification.textContent = message;
    
    document.body.appendChild(notification);
    
    setTimeout(() => {
        notification.style.animation = 'slideOut 0.3s ease';
        setTimeout(() => {
            if (document.body.contains(notification)) {
                document.body.removeChild(notification);
            }
        }, 300);
    }, 4000);
}

function getCsrfToken() {
    const cookies = document.cookie.split(';');
    for (let cookie of cookies) {
        const [name, value] = cookie.trim().split('=');
        if (name === 'csrftoken') {
            return decodeURIComponent(value);
        }
    }
    
    const csrfInput = document.querySelector('[name=csrfmiddlewaretoken]');
    if (csrfInput) {
        return csrfInput.value;
    }
    
    const csrfMeta = document.querySelector('meta[name="csrf-token"]');
    if (csrfMeta) {
        return csrfMeta.content;
    }
    
    console.warn('CSRF token not found');
    return '';
}

// Add CSS animations
const style = document.createElement('style');
style.textContent = `
    @keyframes slideIn {
        from { transform: translateX(400px); opacity: 0; }
        to { transform: translateX(0); opacity: 1; }
    }
    @keyframes slideOut {
        from { transform: translateX(0); opacity: 1; }
        to { transform: translateX(400px); opacity: 0; }
    }
`;
document.head.appendChild(style);

console.log('✅ Camera manager ready (privacy-protected, single popup)');