# 🎯 サークルカレンダーアプリ (bado)

Django製のサークル用イベント管理アプリです。  
メンバーはイベントを登録し、「参加 / 解除」をトグルすることで出欠を管理できます。  
また、イベントごとの **参加者一覧をモーダル表示** で確認できます。

---

## 🚀 機能一覧

| 機能 | 説明 |
|------|------|
| ✅ イベント登録・削除 | カレンダーから予定を追加・削除できます |
| 👥 参加トグル機能 | 「参加 / 解除」ボタンで即時反映（Ajax） |
| 🧾 参加者一覧表示 | モーダル内に「参加者: N人」とスクロール可能な参加者一覧 |
| 🔐 ログインユーザ制御 | Django認証機能でユーザ別に操作制限 |
| 💾 SQLite3 データベース | ローカル開発用DB（本番環境ではPostgreSQL等に変更可） |

---

## 🛠️ 環境構築手順

### 1. リポジトリをクローン
```bash
git clone https://github.com/xxkhyn/bado.git
cd bado
2. 仮想環境を構築
（Windows PowerShellの場合）

bash
コードをコピーする
python -m venv .venv
.venv\Scripts\activate
（macOS / Linux の場合）

bash
コードをコピーする
python3 -m venv .venv
source .venv/bin/activate
3. 依存パッケージをインストール
bash
コードをコピーする
pip install -r requirements.txt
4. 環境変数を設定（任意）
必要に応じて .env ファイルを用意し、以下を設定してください：

ini
コードをコピーする
DEBUG=True
SECRET_KEY=任意の秘密鍵
ALLOWED_HOSTS=*
5. マイグレーション実行
bash
コードをコピーする
python manage.py migrate
6. 管理ユーザー作成
bash
コードをコピーする
python manage.py createsuperuser
7. 開発サーバ起動
bash
コードをコピーする
python manage.py runserver
サーバが起動したら、
➡️ http://127.0.0.1:8000/ にアクセス。
