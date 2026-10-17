import os
import psycopg2
from psycopg2.extras import RealDictCursor

# app.py でインポートされている DATABASE_URL
DATABASE_URL = os.environ.get(
    "DATABASE_URL",
    f"postgresql://{os.environ.get('DB_USER', os.environ.get('USER'))}@{os.environ.get('DB_HOST', 'localhost')}:{os.environ.get('DB_PORT', '5432')}/{os.environ.get('DB_NAME', 'bookgram_db')}"
)

def get_db_connection():
    try:
        conn = psycopg2.connect(
            DATABASE_URL,
            cursor_factory=RealDictCursor
        )
        return conn
    except Exception as e:
        print(f"❌ データベース接続エラー: {e}")
        return None

def test_connection():
    conn = get_db_connection()
    if conn:
        print("✅ PostgreSQL への接続に成功しました！")
        conn.close()
    else:
        print("❌ 接続に失敗しました。")

if __name__ == "__main__":
    test_connection()