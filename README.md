# 🎯 bado (サークル活動管理アプリ)

badoは、サークル活動を効率的に管理するための包括的なWebアプリケーションです。  
イベントのスケジュール管理、出欠確認、月刊誌の共有などの機能を備え、PWA（Progressive Web Apps）に対応しているため、スマートフォンからもネイティブアプリのように快適に利用できます。

## 🚀 主な機能

### 📅 イベント管理
- **カレンダー表示**: 月ごとのイベントをカレンダー形式で一覧表示。
- **イベント作成・編集**: 日時、タイトル、説明などを設定してイベントを作成。
- **出欠管理**:
  - メンバーは「参加 / キャンセル」をワンタップで切り替え可能。
  - 参加者リストをリアルタイムで確認できます。
  - **QRコードチェックイン**: イベント当日はQRコードを使用したスムーズな出席確認が可能。

### 👥 ユーザー権限と認証
- **Googleログイン**: Googleアカウントを使用して安全かつ簡単にログインできます。
- **ロールベースアクセス制御**:
  - **Member (一般)**: イベント閲覧、出欠登録、月刊誌閲覧。
  - **Officer (運営)**: イベント作成・編集、月刊誌アップロード。
  - **Admin (管理者)**: 全機能へのアクセス、ユーザー管理。
  - ※運営権限への昇格は、秘密の合言葉（`OFFICER_SECRET_CODE`）を使用します。

### 📱 PWA (Progressive Web App) 対応
- モバイル端末のホーム画面に追加可能。
- アプリのような全画面表示とスムーズな操作感。
- オフライン時でも基本画面の表示が可能。

### 📖 月刊誌 (Magazine)
- PDF形式の活動報告や月刊誌をアプリ内で閲覧・共有可能。

---

## 🛠️ 技術スタック

- **Backend**: Python 3, Django 5.x
- **Database**: SQLite (開発用) / PostgreSQL (本番推奨)
- **Frontend**: HTML5, CSS3, JavaScript (Vanilla), PWA
- **Authentication**: django-allauth (Google OAuth)
- **Infrastructure**: Docker, WhiteNoise (静的ファイル配信)

---

## 🏁 環境構築手順 (ローカル開発)

### 1. リポジトリのクローン
```bash
git clone https://github.com/xxkhyn/bado.git
cd bado
```

### 2. 仮想環境の作成と有効化
**Windows (PowerShell)**
```powershell
python -m venv .venv
.venv\Scripts\activate
```

**macOS / Linux**
```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 3. 表存パッケージのインストール
```bash
pip install -r requirements.txt
```

### 4. 環境変数の設定
プロジェクトルートに `.env` ファイルを作成し、必要な変数を設定します（開発環境では省略時のデフォルト値が使用されるため、必須ではありませんが推奨します）。

**.env 例**
```ini
DEBUG=True
SECRET_KEY=your-secret-key
# 運営権限に昇格するための合言葉 (デフォルト: admin1234)
OFFICER_SECRET_CODE=secret123
# 本番環境設定 (Render等)
# DJANGO_ALLOWED_HOSTS=...
# DATABASE_URL=postgres://...
```

### 5. データベースのセットアップ
```bash
python manage.py migrate
```

### 6. 管理ユーザーの作成
```bash
python manage.py createsuperuser
```

### 7. サーバーの起動
```bash
python manage.py runserver
```
ブラウザで `http://127.0.0.1:8000/` にアクセスしてください。

---

## 🔑 Google認証のセットアップ (開発環境)

本アプリはログインにGoogle OAuthを使用します。開発環境でテストする場合：

1. `http://127.0.0.1:8000/admin/` にアクセスし、スーパーユーザーでログイン。
2. **Social Applications** (ソーシャルアカウント) セクションを開く。
3. 「Google」プロバイダを追加し、GCPコンソールで取得した `Client ID` と `Secret Key` を設定。
4. **Sites** セクションで `example.com` を `127.0.0.1:8000` に書き換えるか、新しいサイトを追加してSocial Appの設定と紐付けます。

---

## 🐳 Dockerでの起動

DockerおよびDocker Composeがインストールされている場合：

```bash
docker-compose up --build
```
※ `.env.prod` ファイルの設定を確認してください。
