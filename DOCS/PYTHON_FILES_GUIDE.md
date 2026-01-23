# 🐍 Pythonコード詳細解説書 (操作連動版)

「**どのボタンを押したら、どのコードが動くのか**」をファイルごとに徹底解説します。
面接で「この機能はどう動いていますか？」と聞かれたら、このチャートを思い浮かべてください。

---

## 📂 1. `core/views.py` (アプリの動作・メイン)

**役割**: ユーザーの操作を受け取り、画面を返す「司令塔」です。

### 📅 シナリオA: 「カレンダー画面を開く」
1.  **操作**: ユーザーがブラウザで `/calendar/` にアクセス。
2.  **トリガー**: `urls.py` が `views.calendar_view` を呼び出す。
3.  **処理コード (`calendar_view` 関数)**:
    ```python
    @login_required  # ① ログインしていない人はログイン画面へ飛ばす
    def calendar_view(request):
        # ② 今月の1日と末日を計算する
        today = timezone.localtime()
        start_date = today.replace(day=1)
        end_date = ...
        
        # ③ データベースからイベントを検索 (インデックス検索で高速！)
        # 「開始日が start_date 以上、かつ終了日が end_date 以下」
        events = Event.objects.filter(start__gte=start_date, start__lte=end_date)
        
        # ④ HTMLを表示 ('events' という名前でデータを渡す)
        return render(request, "core/calendar.html", {"events": events})
    ```

### ✅ シナリオB: 「参加ボタンを押す」
1.  **操作**: カレンダー上の「参加」ボタンをクリック。
2.  **トリガー**: JavaScript が裏で `/event/vote/123/` へ通信 (Fetch API)。
3.  **処理コード (`event_vote` 関数)**:
    ```python
    @login_required
    def event_vote(request, event_id):
        # ① 指定されたイベントを探す
        event = get_object_or_404(Event, id=event_id)
        
        # ② 「参加記録」を作る、または取得する (get_or_create)
        attendance, created = EventAttendance.objects.get_or_create(
            event=event, user=request.user
        )
        
        # ③ Toggle処理 (あれば削除、なければ作成)
        if not created:
            attendance.delete()  # キャンセル
            action = "removed"
        else:
            action = "added"     # 参加
            
        # ④ 結果をJSONで返す (画面遷移させないため)
        return JsonResponse({"status": "success", "action": action})
    ```

### 📷 シナリオC: 「QRコードでチェックイン」
1.  **操作**: カメラでQRコードを読み取る (`/event/checkin/123/`)。
2.  **処理コード (`event_checkin` 関数)**:
    ```python
    def event_checkin(request, event_id):
        # ① 参加記録を取得 (なければ作る)
        attendance, created = EventAttendance.objects.get_or_create(...)
        
        # ② 出席時間を記録 (ここが重要！)
        # まだチェックインしていなければ、現在時刻を書き込む
        if not attendance.checked_in_at:
            attendance.checked_in_at = timezone.now()
            attendance.save()
            msg = "出席しました！"
        else:
            msg = "既に出席済みです"
            
        # ③ メッセージを表示
        return render(request, "core/checkin_result.html", {"message": msg})
    ```

---

## 📂 2. `core/models.py` (データ設計図)

**役割**: データの「形」と「ルール」を定義します。

### 🗓️ Event (イベント情報)
```python
class Event(models.Model):
    # 編・集・削などの操作で「誰がやったか」を知るためにUserと紐付け
    user = models.ForeignKey(User, ...) 
    
    # 検索を高速にするため db_index=True を設定
    # 理由: カレンダーで「日付ごとの検索」が頻発するから
    start = models.DateTimeField(db_index=True)
```

### 🙋 EventAttendance (参加/出席管理)
```python
class EventAttendance(models.Model):
    event = models.ForeignKey(Event, ...)
    user = models.ForeignKey(User, ...)
    
    # ★ここがポイント！
    # 「参加ボタンを押しただけ」なら Null (空)
    # 「QRコードを読んだ」なら 時間が入る
    checked_in_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        # 「同じ人が同じイベントに2回参加登録できない」というルール
        unique_together = ('event', 'user')
```

---

## 📂 3. `core/forms.py` (入力フォーム)

**役割**: ユーザーが入れたデータをチェックする関所です。

### 👤 ProfileForm (役職変更)
**シナリオ**: ユーザーが「運営」になりたい時だけ「合言葉」を求める。

```python
class ProfileForm(forms.ModelForm):
    def clean(self):
        # ① ユーザーが入力したデータを取り出す
        cleaned_data = super().clean()
        role = cleaned_data.get('role')
        secret = cleaned_data.get('secret_code')
        
        # ② チェックロジック
        # 「もし運営(Officer)を選んだのに、合言葉が間違っていたらエラー」
        if role == 'officer' and secret != settings.OFFICER_SECRET_CODE:
            raise forms.ValidationError("合言葉が違います！")
```

---

## 📂 4. `circle_app/settings.py` (全体設定)

**役割**: アプリの心臓部設定。

### ⚡ パフォーマンス設定
```python
DATABASES = {
    'default': {
        # 重要: データベースへの接続を600秒(10分)維持する
        # これがないと、毎回SSL接続を行ってしまい通信が遅くなる
        'conn_max_age': 600,
    }
}
```

---

## 📂 5. `core/tests.py` (テストコード)

**役割**: バグがないか自動で確認するロボット。

### 🧪 EventSharingTest
**シナリオ**: 一般メンバーが、運営の作ったイベントを見られるか？
```python
def test_member_can_see_officer_event(self):
    # ① 運営ユーザーでイベントを作る
    self.client.force_login(self.officer_user)
    Event.objects.create(...)
    
    # ② 一般メンバーに切り替える
    self.client.force_login(self.member_user)
    
    # ③ カレンダーページを開く
    response = self.client.get('/calendar/')
    
    # ④ 判定: 画面にイベント名が表示されているか？
    self.assertContains(response, "テストイベント")
```
