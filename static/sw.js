/**
 * Burme AI - PWA Service Worker
 * Handles offline functionality and caching
 */

const CACHE_NAME = 'burme-ai-v1';
const OFFLINE_URL = '/';

// Install event - cache core files
self.addEventListener('install', function(event) {
    event.waitUntil(
        caches.open(CACHE_NAME).then(function(cache) {
            return cache.addAll([
                '/',
                '/static/favicon.svg',
                '/static/manifest.json'
            ]);
        })
    );
    self.skipWaiting();
});

// Activate event - clean old caches
self.addEventListener('activate', function(event) {
    event.waitUntil(
        caches.keys().then(function(cacheNames) {
            return Promise.all(
                cacheNames.map(function(cacheName) {
                    if (cacheName !== CACHE_NAME) {
                        return caches.delete(cacheName);
                    }
                })
            );
        })
    );
    self.clients.claim();
});

// Fetch event - network first, fallback to cache
self.addEventListener('fetch', function(event) {
    // Skip non-GET requests
    if (event.request.method !== 'GET') return;
    
    // Skip chrome extensions and other non-http(s)
    if (!event.request.url.startsWith('http')) return;
    
    event.respondWith(
        fetch(event.request)
            .then(function(response) {
                // Clone response for caching
                var responseClone = response.clone();
                caches.open(CACHE_NAME).then(function(cache) {
                    cache.put(event.request, responseClone);
                });
                return response;
            })
            .catch(function() {
                // Fallback to cache
                return caches.match(event.request).then(function(response) {
                    if (response) return response;
                    // Return offline page for navigation
                    if (event.request.mode === 'navigate') {
                        return caches.match(OFFLINE_URL);
                    }
                });
            })
    );
});

// Handle push notifications (future)
self.addEventListener('push', function(event) {
    var data = event.data ? event.data.json() : {};
    var title = data.title || 'Burme AI';
    var options = {
        body: data.body || 'New notification',
        icon: '/static/favicon.svg',
        badge: '/static/favicon.svg',
        vibrate: [100, 50, 100],
        data: {
            dateOfArrival: Date.now(),
            primaryKey: data.id || 1
        }
    };
    event.waitUntil(
        self.registration.showNotification(title, options)
    );
});

// Handle notification click
self.addEventListener('notificationclick', function(event) {
    event.notification.close();
    event.waitUntil(
        clients.openWindow('/')
    );
});