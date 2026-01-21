# 📜 JavaScript コード完全解剖マニュアル

フロントエンドの実装詳細について、ファイルごとに **「どこに・何が・なぜ書かれているか」** を徹底解説します。
面接官に「このコードは何をしているの？」と指差されても即答できるレベルの深さでまとめました。

---

## 📂 目次
1.  [**`static/js/base.js`**](#1-staticjsbasejs-共通動作) - 全ページ共通のUIとPWA
2.  [**`static/js/calendar.js`**](#2-staticjscalendarjs-カレンダーロジック) - カレンダーの核心部分
3.  [**`static/js/home_calendar.js`**](#3-staticjshome_calendarjs-トップページ用) - 簡易カレンダー
4.  [**`static/sw.js`**](#4-staticswjs-service-worker) - アプリ化の裏方 (PWA)

---

## 1. `static/js/base.js` (共通動作)
**役割**: どのページを開いても必ず読み込まれる、「アプリの基本機能」を管理するファイルです。

### 🔍 コード解説
#### ① Service Workerの登録 (PWAの入り口)
```javascript
document.addEventListener('DOMContentLoaded', () => {
    if ('serviceWorker' in navigator) { // ブラウザが対応しているかチェック
        const swUrl = document.body.dataset.swUrl;
        if (swUrl) {
            navigator.serviceWorker.register(swUrl) // sw.js を起動！
                .then(...)
        }
    }
    // ...
```
*   **ポイント**: Webページが開かれた瞬間に、「裏方さん(`sw.js`)」を呼び出しています。これが無いとアプリ化もキャッシュも動きません。

#### ② アバターメニューの制御 (UI)
```javascript
    const btn = document.getElementById('avatarBtn');
    const menu = document.getElementById('userMenu');
    // ...
        document.addEventListener('click', () => { // 画面のどこかをクリックしたら
            if (menu.style.display === 'block') {
                menu.style.display = 'none';   // メニューを閉じる
            }
        });
```
*   **ポイント**: よくある「メニューを開いたまま他の場所を触ったら、メニューが閉じない」というイライラを防ぐため、**`document`全体にクリックイベント**を仕掛けています。地味ですがUX(使い勝手)に効く工夫です。

#### ③ スマホ用メニューの連携
スマホ画面下にある「マイページ」ボタンを押した時、実は**PC版の右上アイコンをクリックしたことにしています** (`btn.click()`)。これによって、スマホ専用の処理をわざわざ書かずに済み、コード量を減らしています。

---

## 2. `static/js/calendar.js` (カレンダーロジック)
**役割**: カレンダー画面の**「脳みそ」**です。ここが一番コード量が多く、複雑です。

### 🔍 コード解説

#### ① CSRF対策 (セキュリティ)
```javascript
function getCookie(name) { ... }
const csrftoken = getCookie('csrftoken');
```
*   **解説**: Djangoにデータを送信するとき、「私は部外者じゃありません」という**通行手形(トークン)**が必要です。それをCookieから取り出しています。

#### ② モーダルの表示 (`openModal`)
カレンダーの日付をクリックした時に呼ばれる関数です。
```javascript
function openModal(payload) {
    // ...
    if (payload.id && !currentCanManage) {
        // 編集権限がない場合、保存・削除ボタンを消す
        saveBtn.style.display = 'none';
        delBtn.style.display = 'none';
        // 入力フォームも無効化(disabled)する
        fTitle.disabled = true;
        // ...
    }
    // ...
}
```
*   **面接アピール**: 「フロントエンドでも権限チェックを行い、**編集できない人はボタンごと非表示にする**ことで、誤操作を防ぐ親切な設計にしています」

#### ③ サーバーとの通信 (`saveBtn.onclick`)
```javascript
saveBtn.onclick = async () => {
    // 1. 入力チェック (バリデーション)
    if (!startISO) { alert('開始時刻を入力してください'); return; }
    
    // 2. データ送信 (Fetch API)
    const res = await fetch(url, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': csrftoken // ここで通行手形を見せる
        },
        body: JSON.stringify(payload)
    });
    // ...
};
```
*   **技術ポイント**: 画面遷移させずにデータを送る **Ajax (非同期通信)** を使っています。昔ながらの `<form>` 送信だと画面が真っ白になりますが、これならスマホアプリのようにヌルヌル動きます。

#### ④ 参加ボタンの即時反映 (`toggleAttendance`)
```javascript
updateAttendBtn(data.attending); // ボタンの色を変える
attendCount.textContent = `${data.count}名`; // 人数を書き換える
```
*   サーバーから「OK」が返ってきた瞬間、**ページを再読み込みせずに** JavaScriptだけで画面を書き換えています。これが「サクサク感」の正体です。

---

## 3. `static/js/home_calendar.js` (トップページ用)
**役割**: `FullCalendar` という**外部ライブラリ**を使って、トップページにカレンダーを表示するための設定ファイルです。

### 🔍 コード解説
```javascript
    var calendar = new FullCalendar.Calendar(calendarEl, {
        initialView: 'dayGridMonth',
        locale: 'ja',
        events: '/events-json/', // ここから予定データを取ってくる
        // ...
```
*   **違い**: `calendar.js` は**全部自作**のカレンダーですが、こちらはライブラリを使っています。
*   **理由**: トップページは「見るだけ」がメインなので、手軽に綺麗なカレンダーが出せるライブラリを採用しました。（使い分けの工夫）

---

## 4. `static/sw.js` (Service Worker)
**役割**: アプリ化 (PWA) のための**「裏方さん」**です。画面には出ませんが、最強の仕事をしています。

### 🔍 コード解説

#### ① インストール時のキャッシュ (Install Event)
```javascript
const urlsToCache = [ '/', '/static/css/style.css', ... ];

self.addEventListener('install', event => {
    // 指定したファイルをスマホの中に保存(キャッシュ)する
    event.waitUntil(caches.open(CACHE_NAME).then(cache => cache.addAll(urlsToCache)));
});
```
*   **効果**: これにより、2回目以降は画像やCSSをダウンロードしなくて済むので、**表示速度が爆速**になります。

#### ② 通信の横取り (Fetch Event)
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

---

## 💡 面接での勝ちパターン
これらのファイルについて聞かれたら、こう答えてください。

> 「JavaScriptは、単に動きをつけるだけでなく、**ユーザーの体験(UX)** を損なわないように設計しました。
> 例えば、**誤操作防止のために権限がないボタンは隠したり**、
> **Fetch APIを使って画面遷移なしでデータを保存したり**、
> **Service Workerでオフライン時の挙動まで考慮**しています。」
