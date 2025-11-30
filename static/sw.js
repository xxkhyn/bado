// Basic Service Worker
const CACHE_NAME = 'bado-v1';
const urlsToCache = [
  '/',
  '/static/css/style.css',
  '/static/images/icon.png'
];

self.addEventListener('install', event => {
  event.waitUntil(
    caches.open(CACHE_NAME)
      .then(cache => cache.addAll(urlsToCache))
  );
});

self.addEventListener('fetch', event => {
  event.respondWith(
    fetch(event.request).catch(() => {
      return caches.match(event.request);
    })
  );
});
