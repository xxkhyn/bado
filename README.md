

# 必要な環境（共通）

* Git
* Python 3.13（※今あなたの環境が3.13なので合わせるのが安全）
* pip（Python同梱）
* 仮想環境ツール（標準の `venv` でOK）
* Google Cloud（OAuth クライアントID/Secret を取得する用）
* エディタ（VS Code 推奨）

# プロジェクト依存パッケージ

`requirements.txt` をリポジトリに入れて、全員これでインストール：

```txt
Django==5.2.5
django-allauth==65.0.2
python-dotenv==1.0.1
```

> すでに allauth を使っているので固定しておくのが吉。追加ライブラリが増えたらここに追記。

# 秘密情報（.env）

全員がローカルで持つ `.env` ファイル（コミットしない）。リポジトリにはテンプレートとして **`.env.example`** を置いておくと親切。

**`.env.example`（配布用）**

```env
DJANGO_SECRET_KEY=replace_me
DJANGO_DEBUG=True
DJANGO_ALLOWED_HOSTS=127.0.0.1,localhost

GOOGLE_CLIENT_ID=replace_me.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=replace_me
SITE_ID=1
```

各自これをコピーして `.env` を作って値を埋める：

```bash
cp .env.example .env   # Windows PowerShellなら: copy .env.example .env
```

# settings.py に .env を読む設定

すでに直書きしていた `SECRET_KEY` などは .env から読むように変更（みんな同じ設定にできる）：

```python
# circle_app/settings.py の先頭で
from pathlib import Path
import os
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")

SECRET_KEY = os.getenv("DJANGO_SECRET_KEY", "insecure-dev-key")  # dev fallback
DEBUG = os.getenv("DJANGO_DEBUG", "True") == "True"
ALLOWED_HOSTS = os.getenv("DJANGO_ALLOWED_HOSTS", "127.0.0.1,localhost").split(",")

SITE_ID = int(os.getenv("SITE_ID", "1"))

# allauth用（管理画面に入力でもOKだが、将来ENVで管理したいときのため）
SOCIALACCOUNT_PROVIDERS = {
    "google": {
        "APP": {
            "client_id": os.getenv("GOOGLE_CLIENT_ID", ""),
            "secret": os.getenv("GOOGLE_CLIENT_SECRET", ""),
            "key": "",
        }
    }
}
```

> 既に Admin → Social applications に登録済みならそれでも動く。ENVに切り替える場合は Admin の登録を削るか、上記 APP 設定を優先するように合わせてね（上の方法だとコード側で固定できる）。

# Google Cloud 側の設定（全員共通）

代表者が 1 回だけ作ればOK（同じ Client ID/Secret を全員の `.env` に配布）：

1. Google Cloud Console → 「OAuth 同意画面」作成（外部/内部どちらでもよい、ローカル用途ならテストユーザーにチーム全員のアドレスを追加）
2. 「認証情報」→「OAuth 2.0 クライアントID」作成（アプリの種類：**ウェブアプリ**）
3. **承認済みのリダイレクトURI** に以下を登録

   * `http://127.0.0.1:8000/accounts/google/login/callback/`
   * `http://localhost:8000/accounts/google/login/callback/`
4. 発行された **クライアントID** と **クライアントシークレット** を `.env` に記入
5. （Adminで管理する方式にするなら）Django管理画面 → Social applications → Google → クライアントID/Secret を入力、Sites で「example.com」ではなく **example.com を外して** 現在の Site（id=1）を選択。

# 全員のセットアップ手順（クローン後の流れ）

```bash
git clone https://github.com/xxkhyn/bado.git
cd bado

# 仮想環境
python -m venv .venv
# Windows:
.venv\Scripts\activate
# macOS/Linux:
# source .venv/bin/activate

# 依存インストール
pip install -r requirements.txt

# 環境ファイル作成
copy .env.example .env   # (macOS/Linuxは cp)
# → .env を開いて各自の値をセット（少なくとも SECRET_KEY と GoogleのID/Secret）

# DB初期化
python manage.py migrate

# 管理ユーザー（必要なら）
python manage.py createsuperuser

# 起動
python manage.py runserver
```

# .gitignore（リポジトリに置く）

```gitignore
# Python
__pycache__/
*.py[cod]

# DB (SQLite を共有しないなら除外)
*.sqlite3

# venv
.venv/

# Django 静的/メディア（開発中は生成物）
/static/
/media/

# 環境ファイル
.env
```

> SQLite を「共有したい」なら `*.sqlite3` の除外を外す。ただし基本は各自ローカルで持つ方が安全。

# 推奨（任意）の開発ツールを揃える

* **VS Code 拡張**：Python、Pylance
* **コード整形・Lint**（全員同じ動きにしたいとき）

  * `pip install black ruff pre-commit`
  * `pre-commit` を入れて `black`/`ruff` フックを設定しておくと、コミット時に自動整形できる

# よくあるつまずき

* Google のリダイレクトURIが一致していない → 401/invalid\_request
* `.env` を作っていない / 値が空 → allauth で `DoesNotExist`
* `ALLOWED_HOSTS` が空のまま → 本番やトンネルURLでアクセス不可
* `SITE_ID` がズレている → allauth のサイト紐付けエラー

---

ここまでリポジトリに **`requirements.txt`** と **`.env.example`** を追加してコミットしておけば、メンバーは迷わず同じ環境を再現できるよ。追加で README の雛形も要るなら、すぐ出すよ！
