// Global Theme Management - theme.js
console.log('Theme manager loaded');

const ThemeManager = {
    themes: ['dark', 'light', 'high-contrast', 'colorful', 'neon'],
    icons: ['🌙', '☀️', '🔳', '🌈', '⚡'],
    
    init() {
        this.loadTheme();
        this.setupToggleButton();
    },
    
    loadTheme() {
        const savedTheme = localStorage.getItem('vibeWiseTheme') || 'dark';
        this.applyTheme(savedTheme);
    },
    
    applyTheme(theme) {
        document.body.setAttribute('data-theme', theme);
        localStorage.setItem('vibeWiseTheme', theme);
        this.updateIcon(theme);
    },
    
    updateIcon(theme) {
        const icon = document.querySelector('.theme-icon');
        if (icon) {
            const themeIndex = this.themes.indexOf(theme);
            if (themeIndex >= 0) {
                icon.textContent = this.icons[themeIndex];
            }
        }
    },
    
    toggle() {
        const currentTheme = document.body.getAttribute('data-theme') || 'dark';
        const currentIndex = this.themes.indexOf(currentTheme);
        const nextIndex = (currentIndex + 1) % this.themes.length;
        const nextTheme = this.themes[nextIndex];
        
        this.applyTheme(nextTheme);
    },
    
    setupToggleButton() {
        const toggleBtn = document.querySelector('.theme-toggle');
        if (toggleBtn) {
            toggleBtn.addEventListener('click', () => this.toggle());
        }
    }
};

// Global toggle function for inline onclick
function toggleTheme() {
    ThemeManager.toggle();
}

// Initialize on DOM load
document.addEventListener('DOMContentLoaded', () => {
    ThemeManager.init();
});

// Export for use in other modules
window.ThemeManager = ThemeManager;
window.toggleTheme = toggleTheme;