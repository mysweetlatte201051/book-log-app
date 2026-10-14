import psycopg2
from db import DATABASE_URL


def init_db():
    try:
        conn = psycopg2.connect(DATABASE_URL)
        cur = conn.cursor()

        create_table_sql = """
        CREATE TABLE IF NOT EXISTS books (
            id SERIAL PRIMARY KEY,
            title VARCHAR(255) NOT NULL,
            author VARCHAR(100),
            status VARCHAR(20) DEFAULT '積読',
            rating INTEGER CHECK (rating >= 1 AND rating <= 5),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """

        cur.execute(create_table_sql)
        conn.commit()
        print("✅ 'books' テーブルの初期化に成功しました！")

        cur.close()
        conn.close()
    except Exception as e:
        print("❌ テーブル作成エラー:")
        print(e)
        raise e


if __name__ == "__main__":
    init_db()