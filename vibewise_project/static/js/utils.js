// Simple Utility Functions - NO THEME HANDLING
console.log('🔧 Utils loading...');

class Utils {
    // Format timestamp
    static formatTime(timestamp) {
        return new Date(timestamp).toLocaleString();
    }

    // Debounce function
    static debounce(func, delay) {
        let timeoutId;
        return (...args) => {
            clearTimeout(timeoutId);
            timeoutId = setTimeout(() => func.apply(this, args), delay);
        };
    }

    // Show notification
    static showNotification(message, type = 'info') {
        const notification = document.createElement('div');
        notification.className = `notification ${type}`;
        notification.textContent = message;
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
        `;
        
        document.body.appendChild(notification);
        
        setTimeout(() => notification.remove(), 3000);
    }

    // Validate email
    static isValidEmail(email) {
        return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email);
    }

    // Generate random ID
    static generateId() {
        return Date.now().toString(36) + Math.random().toString(36).substr(2);
    }

    // Get mood emoji
    static getMoodEmoji(mood) {
        const emojis = {
            happy: '😊', sad: '😢', angry: '😠', surprised: '😲',
            neutral: '😐', disgusted: '🤢', fearful: '😰'
        };
        return emojis[mood] || '😐';
    }

    // Device detection
    static isMobile() {
        return window.innerWidth <= 768 || 
           /Android|webOS|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini/i.test(navigator.userAgent);
    }

    static hasCamera() {
        return navigator.mediaDevices && navigator.mediaDevices.getUserMedia;
    }

    // Error handling
    static handleError(error, context = '') {
        console.error(`Error in ${context}:`, error);
        this.showNotification(`Error: ${error.message}`, 'error');
    }

    // Format confidence
    static formatConfidence(confidence) {
        return `${(confidence * 100).toFixed(1)}%`;
    }

    // Smooth scroll
    static scrollTo(elementId) {
        const element = document.getElementById(elementId);
        if (element) {
            element.scrollIntoView({ behavior: 'smooth' });
        }
    }

    // Copy to clipboard
    static async copyToClipboard(text) {
        try {
            await navigator.clipboard.writeText(text);
            this.showNotification('Copied!', 'success');
        } catch (error) {
            this.showNotification('Failed to copy', 'error');
        }
    }

    // Check browser support
    static checkBrowserSupport() {
        const requirements = {
            camera: navigator.mediaDevices && navigator.mediaDevices.getUserMedia,
            localStorage: typeof Storage !== 'undefined',
            canvas: document.createElement('canvas').getContext,
            es6: typeof Symbol !== 'undefined'
        };

        const unsupported = Object.entries(requirements)
            .filter(([feature, supported]) => !supported)
            .map(([feature]) => feature);

        if (unsupported.length > 0) {
            this.showNotification(`Browser doesn't support: ${unsupported.join(', ')}`, 'error');
            return false;
        }

        return true;
    }
}

// Music Background
class MusicBackground {
    static init() {
        this.createNotes();
        window.addEventListener('resize', () => this.handleResize());
    }

    static createNotes() {
        // Clear existing notes
        document.querySelectorAll('.music-note').forEach(note => note.remove());

        const noteCount = Math.floor(window.innerWidth / 50);
        const notes = ['♪', '♫', '♩', '♬'];
        const animations = ['falling-note', 'jumping-note', 'floating-note'];

        for (let i = 0; i < noteCount; i++) {
            const note = document.createElement('div');
            note.className = `music-note ${animations[Math.floor(Math.random() * animations.length)]}`;
            note.textContent = notes[Math.floor(Math.random() * notes.length)];
            
            note.style.left = `${Math.random() * 100}%`;
            note.style.top = `${Math.random() * 100}%`;
            note.style.fontSize = `${Math.random() * 20 + 16}px`;
            
            const animDuration = note.className.includes('falling-note') 
                ? `${Math.random() * 10 + 10}s` 
                : note.className.includes('jumping-note') 
                    ? `${Math.random() * 2 + 2}s`
                    : `${Math.random() * 4 + 6}s`;
            note.style.animationDuration = animDuration;
            note.style.animationDelay = `${Math.random() * 5}s`;
            
            document.body.appendChild(note);
        }
    }

    static handleResize() {
        clearTimeout(this.resizeTimer);
        this.resizeTimer = setTimeout(() => this.createNotes(), 200);
    }
}

// Initialize
document.addEventListener('DOMContentLoaded', () => {
    console.log('✅ Utils initialized');
    Utils.checkBrowserSupport();
    MusicBackground.init();
});

window.Utils = Utils;
console.log('✅ Utils loaded');