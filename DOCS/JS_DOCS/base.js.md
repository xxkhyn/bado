# 📜 `static/js/base.js` 完全解説

**役割**: どのページを開いても必ず読み込まれる、「アプリの基本機能」を管理するファイルです。

## 🔍 コード解説

### ① Service Workerの登録 (PWAの入り口)
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

### ② アバターメニューの制御 (UI)
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

### ③ スマホ用メニューの連携
スマホ画面下にある「マイページ」ボタンを押した時、実は**PC版の右上アイコンをクリックしたことにしています** (`btn.click()`)。これによって、スマホ専用の処理をわざわざ書かずに済み、コード量を減らしています。
