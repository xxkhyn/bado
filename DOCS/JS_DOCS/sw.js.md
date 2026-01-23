# 📜 `static/sw.js` (Service Worker) 完全解説

**役割**: アプリ化 (PWA) のための**「裏方さん」**です。画面には出ませんが、最強の仕事をしています。

## 🔍 コード解説

### ① インストール時のキャッシュ (Install Event)
```javascript
const urlsToCache = [ '/', '/static/css/style.css', ... ];

self.addEventListener('install', event => {
    // 指定したファイルをスマホの中に保存(キャッシュ)する
    event.waitUntil(caches.open(CACHE_NAME).then(cache => cache.addAll(urlsToCache)));
});
```
*   **効果**: これにより、2回目以降は画像やCSSをダウンロードしなくて済むので、**表示速度が爆速**になります。

### ② 通信の横取り (Fetch Event)
```javascript
self.addEventListener('fetch', event => {
    event.respondWith(
        fetch(event.request).catch(() => {
            // ネットが繋がらない時は、保存しておいたキャッシュを返す
            return caches.match(event.request);
        })
    );
});
```
*   **面接アピール**: 「**オフライン対応**も実装しました。電波が悪い場所でも、キャッシュを使って最低限の画面は表示されるようにしてあります」
