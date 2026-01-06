console.log('Main.js loaded');

function initializeTheme() {
    const savedTheme = localStorage.getItem('vibeWiseTheme') || 'dark';
    document.body.setAttribute('data-theme', savedTheme);
}

document.addEventListener('DOMContentLoaded', () => {
    console.log('Main initialization');
    initializeTheme();
});