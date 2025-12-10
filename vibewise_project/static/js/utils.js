// Utility functions for VibeWise
class Utils {
    // Format timestamp to readable string
    static formatTime(timestamp) {
        return new Date(timestamp).toLocaleString();
    }

    // Debounce function to limit API calls
    static debounce(func, delay) {
        let timeoutId;
        return (...args) => {
            clearTimeout(timeoutId);
            timeoutId = setTimeout(() => func.apply(this, args), delay);
        };
    }

    // Show notification to user
    static showNotification(message, type = 'info') {
        const notification = document.createElement('div');
        notification.className = `notification ${type}`;
        notification.textContent = message;
        
        document.body.appendChild(notification);
        
        setTimeout(() => {
            notification.remove();
        }, 3000);
    }

    // Validate email format
    static isValidEmail(email) {
        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        return emailRegex.test(email);
    }

    // Generate random ID
    static generateId() {
        return Date.now().toString(36) + Math.random().toString(36).substr(2);
    }

    // Get mood emoji
    static getMoodEmoji(mood) {
        const emojis = {
            happy: '😊',
            sad: '😢',
            angry: '😠',
            surprised: '😲',
            neutral: '😐',
            disgusted: '🤢',
            fearful: '😰'
        };
        return emojis[mood] || '😐';
    }

    // Local storage helpers
    static saveToStorage(key, data) {
        try {
            localStorage.setItem(key, JSON.stringify(data));
        } catch (error) {
            console.error('Error saving to localStorage:', error);
        }
    }

    static getFromStorage(key, defaultValue = null) {
        try {
            const data = localStorage.getItem(key);
            return data ? JSON.parse(data) : defaultValue;
        } catch (error) {
            console.error('Error reading from localStorage:', error);
            return defaultValue;
        }
    }

    // Theme management
    static setTheme(theme) {
        document.body.className = theme;
        this.saveToStorage('vibeWiseTheme', theme);
    }

    static loadTheme() {
        const savedTheme = this.getFromStorage('vibeWiseTheme', 'light');
        this.setTheme(savedTheme);
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

    // Format confidence percentage
    static formatConfidence(confidence) {
        return `${(confidence * 100).toFixed(1)}%`;
    }

    // Smooth scroll to element
    static scrollTo(elementId) {
        const element = document.getElementById(elementId);
        if (element) {
            element.scrollIntoView({ behavior: 'smooth' });
        }
    }

    // Copy text to clipboard
    static async copyToClipboard(text) {
        try {
            await navigator.clipboard.writeText(text);
            this.showNotification('Copied to clipboard!', 'success');
        } catch (error) {
            this.showNotification('Failed to copy', 'error');
        }
    }

    // Check if browser supports required features
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

// Initialize theme on load
document.addEventListener('DOMContentLoaded', () => {
    Utils.loadTheme();
    Utils.checkBrowserSupport();
});

window.Utils = Utils;

class MusicBackground {
  static init() {
    this.createNotes();
    window.addEventListener('resize', () => this.handleResize());
  }

  static createNotes() {
    // Clear existing notes
    document.querySelectorAll('.music-note').forEach(note => note.remove());

    // Number of notes based on screen size
    const noteCount = Math.floor(window.innerWidth / 50);
    const notes = ['♪', '♫', '♩', '♬', '♭', '♮', '♯'];
    const animations = ['falling-note', 'jumping-note', 'floating-note'];

    for (let i = 0; i < noteCount; i++) {
      const note = document.createElement('div');
      note.className = `music-note ${animations[Math.floor(Math.random() * animations.length)]}`;
      note.textContent = notes[Math.floor(Math.random() * notes.length)];
      
      // Random positioning
      note.style.left = `${Math.random() * 100}%`;
      note.style.top = `${Math.random() * 100}%`;
      note.style.fontSize = `${Math.random() * 20 + 16}px`;
      
      // Random animation duration variation
      const animDuration = note.className.includes('falling-note') 
        ? `${Math.random() * 10 + 10}s` 
        : note.className.includes('jumping-note') 
          ? `${Math.random() * 2 + 2}s`
          : `${Math.random() * 4 + 6}s`;
      note.style.animationDuration = animDuration;
      
      // Random delay
      note.style.animationDelay = `${Math.random() * 5}s`;
      
      document.body.appendChild(note);
    }
  }

  static handleResize() {
    // Debounce to avoid performance issues
    clearTimeout(this.resizeTimer);
    this.resizeTimer = setTimeout(() => this.createNotes(), 200);
  }
}

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
  MusicBackground.init();
});