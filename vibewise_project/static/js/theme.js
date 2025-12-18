// WORKING Theme System - Tested and Fixed
console.log('🎨 Theme System Loading...');

(function() {
    'use strict';
    
    const THEME_KEY = 'vibeWiseTheme';
    const themes = ['dark', 'light', 'soft', 'girly', 'cool'];
    const icons = ['🌙', '☀️', '🌸', '💖', '🌊'];
    const names = ['Dark', 'Light', 'Soft Vibes', 'Girly Pop', 'Cool Vibes'];
    
    // Get current theme from localStorage
    function getCurrentTheme() {
        try {
            const saved = localStorage.getItem(THEME_KEY);
            if (saved && themes.includes(saved)) {
                return saved;
            }
        } catch (e) {
            console.error('Error reading theme:', e);
        }
        return 'dark';
    }
    
    // Save theme to localStorage
    function saveTheme(theme) {
        try {
            localStorage.setItem(THEME_KEY, theme);
            console.log('✅ Theme saved:', theme);
        } catch (e) {
            console.error('Error saving theme:', e);
        }
    }
    
    // Apply theme to page
    function applyTheme(theme) {
        if (!themes.includes(theme)) {
            theme = 'dark';
        }
        
        // Apply to html and body
        document.documentElement.setAttribute('data-theme', theme);
        document.body.setAttribute('data-theme', theme);
        
        // Update all theme icons
        document.querySelectorAll('.theme-icon').forEach(icon => {
            const index = themes.indexOf(theme);
            icon.textContent = icons[index] || '🌙';
        });
        
        console.log('🎨 Theme applied:', theme);
    }
    
    // Toggle to next theme
    function toggleTheme() {
        const current = getCurrentTheme();
        const currentIndex = themes.indexOf(current);
        const nextIndex = (currentIndex + 1) % themes.length;
        const nextTheme = themes[nextIndex];
        
        console.log(`🔄 Toggle: ${current} → ${nextTheme}`);
        
        // Save and apply new theme
        saveTheme(nextTheme);
        applyTheme(nextTheme);
        
        // Show notification
        showNotification(`Theme: ${names[nextIndex]}`);
    }
    
    // Show theme change notification
    function showNotification(message) {
        // Remove existing notification
        const existing = document.querySelector('.theme-notification');
        if (existing) existing.remove();
        
        // Create new notification
        const notif = document.createElement('div');
        notif.className = 'theme-notification';
        notif.textContent = message;
        notif.style.cssText = `
            position: fixed;
            bottom: 80px;
            right: 20px;
            background: var(--primary-color);
            color: white;
            padding: 12px 20px;
            border-radius: 8px;
            box-shadow: 0 4px 12px rgba(0,0,0,0.3);
            z-index: 10000;
            font-weight: 500;
            animation: slideIn 0.3s ease;
        `;
        
        document.body.appendChild(notif);
        
        // Remove after 2 seconds
        setTimeout(() => {
            notif.style.animation = 'slideOut 0.3s ease';
            setTimeout(() => notif.remove(), 300);
        }, 2000);
    }
    
    // Initialize theme system
    function init() {
        console.log('🎨 Initializing theme system...');
        
        // Apply current theme immediately
        const currentTheme = getCurrentTheme();
        applyTheme(currentTheme);
        
        // Setup toggle buttons
        document.querySelectorAll('.theme-toggle').forEach(button => {
            button.addEventListener('click', (e) => {
                e.preventDefault();
                e.stopPropagation();
                toggleTheme();
            });
        });
        
        // Listen for storage changes (other tabs)
        window.addEventListener('storage', (e) => {
            if (e.key === THEME_KEY && e.newValue) {
                console.log('🔄 Theme changed in another tab:', e.newValue);
                applyTheme(e.newValue);
            }
        });
        
        // Reapply on page show (back/forward)
        window.addEventListener('pageshow', () => {
            const theme = getCurrentTheme();
            applyTheme(theme);
        });
        
        console.log('✅ Theme system ready');
    }
    
    // Apply theme immediately (before page renders)
    const initialTheme = getCurrentTheme();
    applyTheme(initialTheme);
    
    // Initialize when DOM is ready
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }
    
    // Export global function
    window.toggleTheme = toggleTheme;
    
    // Add animation styles
    if (!document.querySelector('#theme-animations')) {
        const style = document.createElement('style');
        style.id = 'theme-animations';
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
    }
    
})();

console.log('✅ Theme system loaded');