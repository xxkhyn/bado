# クローン
git clone https://github.com/<YOUR_NAME>/<REPO>.git
cd <REPO>

# 仮想環境
python -m venv .venv
.venv\Scripts\activate  # Windows（Mac/Linux: source .venv/bin/activate）

# 依存パッケージ
pip install -r requirements.txt

# .env を作る（各自ローカルで）
copy .env.example .env   # Windows（Mac/Linux: cp .env.example .env）
# .envを自分の値に編集（SECRET_KEY, Google OAuth など）

# マイグレーション & 管理ユーザー
python manage.py migrate
python manage.py createsuperuser

# 起動
python manage.py runserver
