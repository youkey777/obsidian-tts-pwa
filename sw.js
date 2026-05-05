const CACHE_VERSION = 'obs-tts-v47';
const CACHE_ASSETS = [
  './',
  './index.html',
  './manifest.json',
  './icons/icon-192.png',
  './icons/icon-512.png'
];

self.addEventListener('install', event => {
  event.waitUntil(
    caches.open(CACHE_VERSION)
      .then(cache => cache.addAll(CACHE_ASSETS))
      .then(() => self.skipWaiting())
  );
});

self.addEventListener('activate', event => {
  event.waitUntil(
    caches.keys()
      .then(keys => Promise.all(
        keys.filter(k => k !== CACHE_VERSION).map(k => caches.delete(k))
      ))
      .then(() => self.clients.claim())
  );
});

self.addEventListener('fetch', event => {
  const url = new URL(event.request.url);
  // 同一オリジンのPOSTのみShareTargetとして処理（クロスオリジンAPI呼び出しは素通り）
  if (event.request.method === 'POST' && url.origin === self.location.origin) {
    event.respondWith(handleShareTarget(event.request));
    return;
  }
  if (event.request.method !== 'GET') return;
  event.respondWith(
    caches.match(event.request)
      .then(cached => cached || fetch(event.request)
        .catch(() => caches.match('./index.html'))
      )
  );
});

async function handleShareTarget(request) {
  const formData = await request.formData();
  const title = formData.get('title') || '';
  const text  = formData.get('text')  || '';
  const url   = formData.get('url')   || '';

  await storeSharedContent({ title, text, url, ts: Date.now() });

  const clients = await self.clients.matchAll({ type: 'window', includeUncontrolled: true });
  clients.forEach(client => {
    client.postMessage({ type: 'SHARE_TARGET', title, text, url });
  });

  return Response.redirect('./?shared=1', 303);
}

function storeSharedContent(data) {
  return new Promise((resolve, reject) => {
    const req = indexedDB.open('obs-tts-share', 1);
    req.onupgradeneeded = e => e.target.result.createObjectStore('pending');
    req.onsuccess = e => {
      const db = e.target.result;
      const tx = db.transaction('pending', 'readwrite');
      tx.objectStore('pending').put(data, 'latest');
      tx.oncomplete = () => { db.close(); resolve(); };
      tx.onerror = reject;
    };
    req.onerror = reject;
  });
}
