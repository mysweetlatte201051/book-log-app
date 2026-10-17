import os
from flask import Flask, render_template, request, redirect, url_for
import psycopg2
from psycopg2.extras import RealDictCursor
from db import DATABASE_URL
from init_db import init_db
from flask import Flask, render_template, request, redirect, url_for, abort # abortを追加
from db import get_db_connection
from flask import jsonify, request

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "dev-secret-key")

# --- 404エラーハンドラー ---
@app.errorhandler(404)
def page_not_found(e):
    return render_template("404.html"), 404

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
    memo = request.form.get("memo", "").strip()

    rating_val = int(rating) if rating and rating.isdigit() else None

    if title:
        conn = get_db_connection()
        cur = conn.cursor()
        # ★ %s と 引数に memo or None を含める
        cur.execute(
            "INSERT INTO books (title, author, status, rating, memo) VALUES (%s, %s, %s, %s, %s);",
            (title, author or None, status, rating_val, memo or None)
        )
        conn.commit()
        cur.close()
        conn.close()

    return redirect(url_for("index"))

@app.route("/edit/<int:book_id>", methods=["GET", "POST"])
def edit_book(book_id):
    conn = get_db_connection()
    cur = conn.cursor()

    # 対象の書籍が存在するか確認
    cur.execute("SELECT * FROM books WHERE id = %s;", (book_id,))
    book = cur.fetchone()

    # 書籍が存在しない場合は 404 エラーを発生させる
    if not book:
        cur.close()
        conn.close()
        abort(404)

    if request.method == "POST":
        title = request.form.get("title", "").strip()
        author = request.form.get("author", "").strip()
        status = request.form.get("status", "積読")
        rating = request.form.get("rating")
        memo = request.form.get("memo", "").strip()

        rating_val = int(rating) if rating and rating.isdigit() else None

        if title:
            # memo = %s を追加し、プレースホルダーと変数の数を揃えます (計6個)
            cur.execute("""
                UPDATE books 
                SET title = %s, author = %s, status = %s, rating = %s, memo = %s, updated_at = CURRENT_TIMESTAMP
                WHERE id = %s;
            """, (title, author or None, status, rating_val, memo or None, book_id))
            conn.commit()

        cur.close()
        conn.close()
        return redirect(url_for("index"))

    cur.close()
    conn.close()

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

# ==============================================================================
# REST API エンドポイント
# ==============================================================================

# 1. 書籍一覧の取得 (GET /api/books)
@app.route("/api/books", methods=["GET"])
def api_get_books():
    keyword = request.args.get("keyword", "").strip()
    status = request.args.get("status", "").strip()

    conn = get_db_connection()
    cur = conn.cursor()

    query = "SELECT * FROM books WHERE 1=1"
    params = []

    if keyword:
        query += " AND (title ILIKE %s OR author ILIKE %s)"
        params.extend([f"%{keyword}%", f"%{keyword}%"])
    if status:
        query += " AND status = %s"
        params.append(status)

    query += " ORDER BY id DESC;"
    cur.execute(query, tuple(params))
    books = cur.fetchall()

    cur.close()
    conn.close()

    # datetime オブジェクトを文字列に変換してレスポンス
    formatted_books = []
    for b in books:
        book_dict = dict(b)
        if book_dict.get("created_at"):
            book_dict["created_at"] = book_dict["created_at"].strftime("%Y-%m-%d %H:%M:%S")
        if book_dict.get("updated_at"):
            book_dict["updated_at"] = book_dict["updated_at"].strftime("%Y-%m-%d %H:%M:%S")
        formatted_books.append(book_dict)

    return jsonify(formatted_books), 200


# 2. 指定した書籍の個別取得 (GET /api/books/<int:book_id>)
@app.route("/api/books/<int:book_id>", methods=["GET"])
def api_get_book(book_id):
    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute("SELECT * FROM books WHERE id = %s;", (book_id,))
    book = cur.fetchone()

    cur.close()
    conn.close()

    if not book:
        return jsonify({"error": "Book not found"}), 404

    book_dict = dict(book)
    if book_dict.get("created_at"):
        book_dict["created_at"] = book_dict["created_at"].strftime("%Y-%m-%d %H:%M:%S")
    if book_dict.get("updated_at"):
        book_dict["updated_at"] = book_dict["updated_at"].strftime("%Y-%m-%d %H:%M:%S")

    return jsonify(book_dict), 200


# 3. 新規書籍の追加 (POST /api/books)
@app.route("/api/books", methods=["POST"])
def api_create_book():
    data = request.get_json() or {}
    title = data.get("title", "").strip()

    if not title:
        return jsonify({"error": "Title is required"}), 400

    author = data.get("author", "").strip()
    status = data.get("status", "積読")
    rating = data.get("rating")
    memo = data.get("memo", "").strip()

    rating_val = int(rating) if rating and str(rating).isdigit() else None

    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute(
        """
        INSERT INTO books (title, author, status, rating, memo)
        VALUES (%s, %s, %s, %s, %s)
        RETURNING id;
        """,
        (title, author or None, status, rating_val, memo or None)
    )
    new_id = cur.fetchone()["id"]
    conn.commit()

    cur.close()
    conn.close()

    return jsonify({"message": "Book created", "id": new_id}), 201


# 4. 書籍情報の更新 (PUT /api/books/<int:book_id>)
@app.route("/api/books/<int:book_id>", methods=["PUT"])
def api_update_book(book_id):
    data = request.get_json() or {}
    title = data.get("title", "").strip()

    if not title:
        return jsonify({"error": "Title is required"}), 400

    author = data.get("author", "").strip()
    status = data.get("status", "積読")
    rating = data.get("rating")
    memo = data.get("memo", "").strip()

    rating_val = int(rating) if rating and str(rating).isdigit() else None

    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute("SELECT * FROM books WHERE id = %s;", (book_id,))
    if not cur.fetchone():
        cur.close()
        conn.close()
        return jsonify({"error": "Book not found"}), 404

    cur.execute(
        """
        UPDATE books
        SET title = %s, author = %s, status = %s, rating = %s, memo = %s, updated_at = CURRENT_TIMESTAMP
        WHERE id = %s;
        """,
        (title, author or None, status, rating_val, memo or None, book_id)
    )
    conn.commit()

    cur.close()
    conn.close()

    return jsonify({"message": "Book updated"}), 200


# 5. 書籍の削除 (DELETE /api/books/<int:book_id>)
@app.route("/api/books/<int:book_id>", methods=["DELETE"])
def api_delete_book(book_id):
    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute("SELECT * FROM books WHERE id = %s;", (book_id,))
    if not cur.fetchone():
        cur.close()
        conn.close()
        return jsonify({"error": "Book not found"}), 404

    cur.execute("DELETE FROM books WHERE id = %s;", (book_id,))
    conn.commit()

    cur.close()
    conn.close()

    return jsonify({"message": "Book deleted"}), 200

if __name__ == "__main__":
    app.run(debug=True, port=5000)