/**
 * base.js
 * - Service Worker Registration
 * - Avatar Dropdown
 * - Mobile Menu
 */

document.addEventListener('DOMContentLoaded', () => {
    // Service Worker Registration
    if ('serviceWorker' in navigator) {
        const swUrl = document.body.dataset.swUrl;
        if (swUrl) {
            navigator.serviceWorker.register(swUrl)
                .then(reg => console.log('SW registered:', reg))
                .catch(err => console.log('SW registration failed:', err));
        }
    }

    // Avatar Dropdown
    const btn = document.getElementById('avatarBtn');
    const menu = document.getElementById('userMenu');
    if (btn && menu) {
        const toggle = () => {
            const open = menu.style.display === 'block';
            menu.style.display = open ? 'none' : 'block';
            btn.setAttribute('aria-expanded', (!open).toString());
        };
        btn.addEventListener('click', (e) => { e.stopPropagation(); toggle(); });
        menu.addEventListener('click', (e) => e.stopPropagation());
        document.addEventListener('click', () => {
            if (menu.style.display === 'block') {
                menu.style.display = 'none';
                btn.setAttribute('aria-expanded', 'false');
            }
        });
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape') {
                menu.style.display = 'none';
                btn.setAttribute('aria-expanded', 'false');
            }
        });
    }

    // Mobile Menu Trigger
    const mobileMenuBtn = document.getElementById('mobileMenuBtn');
    if (mobileMenuBtn && btn) {
        mobileMenuBtn.addEventListener('click', (e) => {
            e.preventDefault();
            btn.click(); // Simulate click on desktop avatar button
        });
    }
});
