# 📖 `core/views.py` 完全解説ガイド

このファイルは、アプリの「頭脳」にあたる部分です。
機能ごとにセクションが分かれているので、一つずつ解説します。

---

## 1. カレンダー表示 (`home`, `calendar_view`)

### `home(request)`
*   トップページ (`/`) にアクセスした時、自動的にカレンダー画面 (`calendar_view`) に転送します。

### `calendar_view(request)`
*   **役割**: カレンダー画面のHTMLを作る。
*   **処理の流れ**:
    1.  URLから「何年何月か」を取得（例: `?y=2025&m=10`）。
    2.  `calendar` ライブラリを使って、その月の「週ごとの日付リスト」を作ります。
    3.  **高速化の工夫**: その月に表示されるイベントだけを `Event.objects.filter(...)` で絞り込んで取得しています（全件取得すると重くなるため）。
    4.  HTMLテンプレート (`calendar.html`) にデータを入れて返します。

---

## 2. イベントAPI (`events_json`, `event_add`...)

### `events_json(request)`
*   **役割**: カレンダーに表示する「イベントデータ」をJSON形式で配るAPI。
*   **技術ポイント**: **N+1問題の解消**
    ```python
    Event.objects.annotate(attending_count=Count("attendances"))
    ```
    *   普通に書くと「イベント1つ取得」→「その参加者数を数えるSQLを発行」× イベント数分だけSQLが飛んでしまいます。
    *   `annotate` を使うことで、「イベント取得と同時に参加人数も数えておいて！」と1回のSQLで済ませています。

### `event_add`, `event_update`, `event_delete`
*   **役割**: イベントの作成・編集・削除。
*   **権限**: `@login_required` に加えて、関数の中で `if not request.user.is_staff...` とチェックし、管理者か運営メンバーしか操作できないようにガードしています。

---

## 3. 参加・不参加ボタン (`event_vote`, `votes_summary`)

### `event_vote(request)`
*   **役割**: 「参加する」ボタンを押した時の処理。
*   **ロジック**:
    *   「まだ参加してなければ作成」「既に参加してれば削除」というトグル動作をしています。
    *   **Optimistic UI (楽観的UI)**: 
        *   処理が終わったら、最新の「参加人数」と「参加者リスト(先頭10名)」をJSONで返します。
        *   JavaScript側はこれを受け取って、画面のリロードなしで数字だけ書き換えます。

---

## 4. QRコード出席 (`event_qr`, `event_checkin`)

### `event_qr(request)`
*   **役割**: 出席用のQRコード画像を生成して返す。
*   **仕組み**: `qrcode` ライブラリを使い、その場で `https://.../checkin/トークン/` というURLを画像化しています。

### `event_checkin(request)`
*   **役割**: QRコードが読み込まれた時の処理。
*   **重要ロジック**:
    ```python
    attendance.checked_in_at = timezone.now()
    ```
    *   ここで初めて「出席時刻」が書き込まれます。これが入っている人だけが「出席済」扱いになります。

---

## 5. モーダル・チーム分け (`attendees_list`, `team_division`)

### `attendees_list(request)`
*   **役割**: カレンダーの日付をクリックした時に出る「参加者一覧」のデータを返す。
*   **詳細情報**: 
    *   単に名前を返すだけでなく、`checked_in: true/false` というフラグも一緒に返しています。
    *   これで画面上に「✅ 出席済」「🎫 予約のみ」を出し分けています。

### `team_division(request)`
*   **役割**: その日の参加者をランダムにチーム分けする。
*   **アルゴリズム**:
    *   参加者リストをシャッフルし、ラウンドロビン（順番に1, 2, 3...と配る）方式で均等にチーム分けしています。

---

## 6. マイページ・メンバー管理 (`mypage`, `member_list`)

### `mypage(request)`
*   **役割**: 自分の参加履歴を表示。
*   **統計の正確さ**:
    ```python
    all_attendances.filter(checked_in_at__isnull=False).count()
    ```
    *   「予約しただけの数」ではなく「QRチェックインした数」をカウントして、正確な活動実績を表示しています。

---

**面接官へのアピールポイント:**
> 「`views.py` は機能が増えると肥大化しやすいので、コメントで見出しをつけて可読性を保ちました。また、N+1問題の対策(`annotate`, `select_related`)や、適切な権限チェック(`is_staff`)を徹底して、セキュリティとパフォーマンスを両立させました。」
