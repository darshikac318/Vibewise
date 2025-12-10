// Main.js - Simple initialization
console.log('Main.js loaded');

// Theme functionality
function initializeTheme() {
    const savedTheme = localStorage.getItem('vibeWiseTheme') || 'dark';
    document.body.setAttribute('data-theme', savedTheme);
}

// Initialize when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    console.log('Main initialization');
    initializeTheme();
});