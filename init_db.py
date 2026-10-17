import psycopg2
from db import get_db_connection


def init_db():
    conn = get_db_connection()
    cur = conn.cursor()

    # テーブル作成
    cur.execute("""
        CREATE TABLE IF NOT EXISTS books (
            id SERIAL PRIMARY KEY,
            title VARCHAR(255) NOT NULL,
            author VARCHAR(255),
            status VARCHAR(50) DEFAULT '積読',
            rating INT CHECK (rating >= 1 AND rating <= 5),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    """)

    # memo カラムが存在しない場合のみ追加
    cur.execute("""
        ALTER TABLE books ADD COLUMN IF NOT EXISTS memo TEXT;
    """)

    conn.commit()
    cur.close()
    conn.close()
    print("Database initialized successfully.")


if __name__ == "__main__":
    init_db()