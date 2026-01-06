console.log('🎨 Theme System Loading...');

(function() {
    'use strict';
    
    const THEME_KEY = 'vibeWiseTheme';
    const themes = ['dark', 'light', 'soft', 'girly', 'cool'];
    const icons = ['🌙', '☀️', '🌸', '💖', '🌊'];
    const names = ['Dark', 'Light', 'Soft Vibes', 'Girly Pop', 'Cool Vibes'];
    
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
    
    function saveTheme(theme) {
        try {
            localStorage.setItem(THEME_KEY, theme);
            console.log('✅ Theme saved:', theme);
        } catch (e) {
            console.error('Error saving theme:', e);
        }
    }
    
    function applyTheme(theme) {
        if (!themes.includes(theme)) {
            theme = 'dark';
        }
        
        document.documentElement.setAttribute('data-theme', theme);
        document.body.setAttribute('data-theme', theme);
        
        document.querySelectorAll('.theme-icon').forEach(icon => {
            const index = themes.indexOf(theme);
            icon.textContent = icons[index] || '🌙';
        });
        
        console.log('🎨 Theme applied:', theme);
    }
    
    function toggleTheme() {
        const current = getCurrentTheme();
        const currentIndex = themes.indexOf(current);
        const nextIndex = (currentIndex + 1) % themes.length;
        const nextTheme = themes[nextIndex];
        
        console.log(`🔄 Toggle: ${current} → ${nextTheme}`);
        
        saveTheme(nextTheme);
        applyTheme(nextTheme);
        
        showNotification(`Theme: ${names[nextIndex]}`);
    }
    
    function showNotification(message) {
        const existing = document.querySelector('.theme-notification');
        if (existing) existing.remove();
        
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
        
        setTimeout(() => {
            notif.style.animation = 'slideOut 0.3s ease';
            setTimeout(() => notif.remove(), 300);
        }, 2000);
    }
    
    function init() {
        console.log('🎨 Initializing theme system...');
        
        const currentTheme = getCurrentTheme();
        applyTheme(currentTheme);
        
        document.querySelectorAll('.theme-toggle').forEach(button => {
            button.addEventListener('click', (e) => {
                e.preventDefault();
                e.stopPropagation();
                toggleTheme();
            });
        });
        
        window.addEventListener('storage', (e) => {
            if (e.key === THEME_KEY && e.newValue) {
                console.log('🔄 Theme changed in another tab:', e.newValue);
                applyTheme(e.newValue);
            }
        });
        
        window.addEventListener('pageshow', () => {
            const theme = getCurrentTheme();
            applyTheme(theme);
        });
        
        console.log('✅ Theme system ready');
    }
    
    const initialTheme = getCurrentTheme();
    applyTheme(initialTheme);
    
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }
    
    window.toggleTheme = toggleTheme;
    
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