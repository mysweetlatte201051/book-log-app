import os
import psycopg2
from dotenv import load_dotenv

# .env ファイルの読み込み
load_dotenv()

# 環境変数から DATABASE_URL を取得（設定されていない場合はデフォルト値）
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://localhost:5432/bookgram_db")


def test_connection():
    try:
        # PostgreSQL への接続試行
        conn = psycopg2.connect(DATABASE_URL)
        cur = conn.cursor()

        # 簡易クエリを実行（PostgreSQLのバージョン取得）
        cur.execute("SELECT version();")
        db_version = cur.fetchone()

        print("✅ PostgreSQL への接続に成功しました！")
        print(f"データベースバージョン: {db_version[0]}")

        cur.close()
        conn.close()
    except Exception as e:
        print("❌ 接続エラーが発生しました:")
        print(e)


if __name__ == "__main__":
    test_connection()