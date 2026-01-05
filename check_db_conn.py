import sys
import os
import psycopg2
import dotenv

dotenv.load_dotenv('.env.prod')
DB_URL = os.environ.get("DATABASE_URL")

try:
    print(f"Attempting to connect to: {DB_URL.replace(DB_URL.split(':')[2].split('@')[0], '******') if DB_URL else 'None'}")
    conn = psycopg2.connect(DB_URL, connect_timeout=10)
    print("SUCCESS: Connected to database!")
    
    cur = conn.cursor()
    # Check simple query
    cur.execute("SELECT 1;")
    print(f"Connection check result: {cur.fetchone()[0]}")
    
    conn.close()
except Exception as e:
    print(f"FAILURE: Could not connect. Error: {e}")
    sys.exit(1)
