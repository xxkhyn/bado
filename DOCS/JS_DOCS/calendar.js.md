# 📜 `static/js/calendar.js` 完全解説

**役割**: カレンダー画面の**「脳みそ」**です。ここが一番コード量が多く、複雑です。

## 🔍 コード解説

### ① CSRF対策 (セキュリティ)
```javascript
function getCookie(name) { ... }
const csrftoken = getCookie('csrftoken');
```
*   **解説**: Djangoにデータを送信するとき、「私は部外者じゃありません」という**通行手形(トークン)**が必要です。それをCookieから取り出しています。

### ② モーダルの表示 (`openModal`)
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

### ③ サーバーとの通信 (`saveBtn.onclick`)
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

### ④ 参加ボタンの即時反映 (`toggleAttendance` / `loadAttendance`)
```javascript
// loadAttendance の中身(一部抜粋)
if (user.checked_in) {
    // チェックイン済みなら緑のチェックマーク
    sp.innerHTML = `<span style="color:var(--accent-success)">✅</span> ${user.name}`;
} else {
    // 予約だけならチケットアイコン
    sp.innerHTML = `<span style="color:var(--text-muted)">🎫</span> ${user.name}`;
}
```
*   サーバーから送られてきた `checked_in` フラグを見て、**アイコンを出し分け**ています。これで「誰が実際に来たか」が一目でわかります。
*   サーバーから「OK」が返ってきた瞬間、**ページを再読み込みせずに** JavaScriptだけで画面を書き換えています。これが「サクサク感」の正体です。
