// Death2Data Service Worker — makes the site installable as a PWA
const CACHE_NAME = 'd2d-v1';
const PRECACHE = [
  '/',
  '/tools.html',
  '/tools/notebook.html',
  '/tools/sanitizer.html',
  '/tools/converter.html',
  '/tools/leak-score.html',
  '/story.html',
  '/favicon.svg'
];

// Install — cache core pages
self.addEventListener('install', (e) => {
  e.waitUntil(
    caches.open(CACHE_NAME)
      .then(cache => cache.addAll(PRECACHE))
      .then(() => self.skipWaiting())
  );
});

// Activate — clean old caches
self.addEventListener('activate', (e) => {
  e.waitUntil(
    caches.keys().then(keys =>
      Promise.all(keys.filter(k => k !== CACHE_NAME).map(k => caches.delete(k)))
    ).then(() => self.clients.claim())
  );
});

// Fetch — network first, cache fallback (privacy-first: don't cache API responses)
self.addEventListener('fetch', (e) => {
  const url = new URL(e.request.url);

  // Never cache API calls or external requests
  if (url.pathname.startsWith('/api') || url.origin !== location.origin) {
    return;
  }

  e.respondWith(
    fetch(e.request)
      .then(response => {
        // Cache successful HTML responses
        if (response.ok && e.request.method === 'GET') {
          const clone = response.clone();
          caches.open(CACHE_NAME).then(cache => cache.put(e.request, clone));
        }
        return response;
      })
      .catch(() => caches.match(e.request))
  );
});
