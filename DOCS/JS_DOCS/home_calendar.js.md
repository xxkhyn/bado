# 📜 `static/js/home_calendar.js` 完全解説

**役割**: `FullCalendar` という**外部ライブラリ**を使って、トップページにカレンダーを表示するための設定ファイルです。

## 🔍 コード解説
```javascript
    var calendar = new FullCalendar.Calendar(calendarEl, {
        initialView: 'dayGridMonth',
        locale: 'ja',
        events: '/events-json/', // ここから予定データを取ってくる
        // ...
```
*   **違い**: `calendar.js` は**全部自作**のカレンダーですが、こちらはライブラリを使っています。
*   **理由**: トップページは「見るだけ」がメインなので、手軽に綺麗なカレンダーが出せるライブラリを採用しました。（使い分けの工夫）
