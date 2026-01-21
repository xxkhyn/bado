# 🐍 Pythonファイル徹底解説 (初心者向け)

「これ何語？」レベルからでも面接で説明できるよう、**コードの読み方** を中心に解説します。

---

## � Pythonコードの基本ルール

まずは、どのファイルにも出てくる「共通の書き方」を覚えましょう。

*   **`import ...` / `from ... import ...`**:
    *   **意味**: 「道具箱を取り出す」
    *   **例**: `from django.db import models` → djangoのdb機能から `models` という道具を使えるようにする。
*   **`class Xxx(Yyy):`**:
    *   **意味**: 「原本(Yyy)をコピーして、新しい機能(Xxx)を作る」
    *   **例**: `class Event(models.Model):` → Django標準のモデル機能をコピーして、`Event` という独自データを作る。
*   **`def xxx(request):`**:
    *   **意味**: 「処理のまとまり（関数）を作る」
    *   **例**: `def calendar_view(request):` → 「カレンダー表示」という名前の処理を定義する。

---

## 📂 1. `core/models.py` (データの設計図)

「どんなデータを保存するか」を決めている場所です。Excelの「列名」を決めるイメージです。

### コードの読み方
```python
class Event(models.Model):
    # ユーザーと紐付ける (ForeignKey = 別のテーブルのIDを入れる)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    
    # タイトル (CharField = 短い文字)
    title = models.CharField(max_length=255)
    
    # 開始日時 (DateTimeField = 日付と時間)
    # db_index=True: これがあると検索が爆速になる魔法
    start = models.DateTimeField(db_index=True)
```
*   **面接ポイント**: 「`ForeignKey` は『誰が作ったか』を記録する紐付けです」「`db_index=True` をつけて検索を速くしました」と言えればOKです。

---

## 📂 2. `core/views.py` (アプリの動作)

「ページを表示する」「データを計算する」など、アプリの**メインの動き**が書かれています。

### コードの読み方 (カレンダー表示)
```python
# @login_required: 「ログインしてる人しか使っちゃダメ」という門番
@login_required
def calendar_view(request):
    # データベースから検索 (SQLの WHERE にあたる)
    # 「開始日が start_dt 以上、かつ 終了日が end_dt 以下」のデータを取得
    qs = Event.objects.filter(start__gte=start_dt, start__lte=end_dt)
    
    # HTMLファイルを表示する (データ qs を一緒に渡す)
    return render(request, "core/calendar.html", {"events": qs})
```
*   **`request`**: ユーザーからの「これ見せて」という要求データ。
*   **`render`**: 「HTMLを作ってブラウザに返す」命令。

### コードの読み方 (チェックイン機能)
```python
def event_checkin(request, event_id):
    # データを新規作成、既にあれば取得 ( 便利機能: get_or_create )
    attendance, created = EventAttendance.objects.get_or_create(...)

    # created が True なら「今初めて作った＝初参加」
    if created:
        print("出席しました！")
    else:
        print("もう出席済みです")
```

---

## 📂 3. `core/urls.py` (案内所)

URLとプログラム(`views.py`)を繋ぐ場所です。

### コードの読み方
```python
urlpatterns = [
    # ブラウザで '/calendar' にアクセスしたら -> views.calendar_view を動かす
    path("calendar/", views.calendar_view, name="calendar"),
    
    # '<int:event_id>' は「ここに数字が入るよ」という意味
    # 例: /checkin/123/ -> event_id=123 として受け取る
    path("checkin/<int:event_id>/", views.event_checkin, name="event_checkin"),
]
```

---

## 📂 4. `circle_app/settings.py` (各種設定)

アプリ全体の「環境設定」です。

### コードの読み方
```python
# データベースの設定
DATABASES = {
    'default': {
        # 'conn_max_age': DBとの電話を600秒間切りません（高速化）
        'conn_max_age': 600, 
    }
}

# インストールされたアプリ (coreアプリもここで登録)
INSTALLED_APPS = [
    'django.contrib.admin',
    'core',  # ← 自分で作ったアプリ
]
```

---

## 📂 5. その他のファイル

*   **`manage.py`**:
    *   これを直接書き換えることはありません。コマンド (`python manage.py ...`) を使うための入り口です。
*   **`requirements.txt`**:
    *   「買い物リスト」です。`Django==5.0` のように、必要なライブラリ名だけが書いてあります。Pythonのコードではありません。
