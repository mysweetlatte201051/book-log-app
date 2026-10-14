import os
from flask import Flask, render_template, request, redirect, url_for
import psycopg2
from psycopg2.extras import RealDictCursor
from db import DATABASE_URL
from init_db import init_db

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "dev-secret-key")

# アプリ起動時に DB テーブルが存在するか確認
init_db()

def get_db_connection():
    return psycopg2.connect(DATABASE_URL, cursor_factory=RealDictCursor)

@app.route("/")
def index():
    keyword = request.args.get("keyword", "").strip()
    status = request.args.get("status", "").strip()

    conn = get_db_connection()
    cur = conn.cursor()

    # 基本となる SQL クエリ
    sql = "SELECT * FROM books WHERE 1=1"
    params = []

    # キーワード検索（タイトルまたは著者名にマッチ）
    if keyword:
        sql += " AND (title ILIKE %s OR author ILIKE %s)"
        params.extend([f"%{keyword}%", f"%{keyword}%"])

    # ステータス絞り込み
    if status:
        sql += " AND status = %s"
        params.append(status)

    sql += " ORDER BY id DESC;"

    cur.execute(sql, params)
    books = cur.fetchall()
    cur.close()
    conn.close()

    return render_template("index.html", books=books, keyword=keyword, status=status)

@app.route("/add", methods=["POST"])
def add_book():
    title = request.form.get("title")
    author = request.form.get("author")
    status = request.form.get("status")
    rating = request.form.get("rating")

    rating_val = int(rating) if rating and rating.isdigit() else None

    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute(
        """
        INSERT INTO books (title, author, status, rating)
        VALUES (%s, %s, %s, %s);
        """,
        (title, author, status, rating_val)
    )
    conn.commit()
    cur.close()
    conn.close()
    return redirect(url_for("index"))

@app.route("/edit/<int:book_id>", methods=["GET", "POST"])
def edit_book(book_id):
    conn = get_db_connection()
    cur = conn.cursor()

    if request.method == "POST":
        title = request.form.get("title")
        author = request.form.get("author")
        status = request.form.get("status")
        rating = request.form.get("rating")

        rating_val = int(rating) if rating and rating.isdigit() else None

        cur.execute(
            """
            UPDATE books
            SET title = %s, author = %s, status = %s, rating = %s, updated_at = CURRENT_TIMESTAMP
            WHERE id = %s;
            """,
            (title, author, status, rating_val, book_id)
        )
        conn.commit()
        cur.close()
        conn.close()
        return redirect(url_for("index"))

    # GET リクエスト時（編集画面の表示）
    cur.execute("SELECT * FROM books WHERE id = %s;", (book_id,))
    book = cur.fetchone()
    cur.close()
    conn.close()

    if not book:
        return "書籍が見つかりません", 404

    return render_template("edit.html", book=book)

@app.route("/delete/<int:book_id>", methods=["POST"])
def delete_book(book_id):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM books WHERE id = %s;", (book_id,))
    conn.commit()
    cur.close()
    conn.close()
    return redirect(url_for("index"))

if __name__ == "__main__":
    app.run(debug=True, port=5000)