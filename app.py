from flask import Flask, request, redirect, url_for, render_template_string
from db import DATABASE_URL
import psycopg2
from psycopg2.extras import RealDictCursor

app = Flask(__name__)


def get_db_connection():
    return psycopg2.connect(DATABASE_URL, cursor_factory=RealDictCursor)


# --------------------------------------------------
# 1. トップページ（一覧表示 ＋ 新規登録）
# --------------------------------------------------
@app.route("/", methods=["GET", "POST"])
def index():
    conn = get_db_connection()
    cur = conn.cursor()

    if request.method == "POST":
        title = request.form.get("title")
        author = request.form.get("author")
        status = request.form.get("status")
        rating = request.form.get("rating")

        if title:
            cur.execute(
                """
                INSERT INTO books (title, author, status, rating)
                VALUES (%s, %s, %s, %s)
                """,
                (
                    title,
                    author if author else None,
                    status if status else "積読",
                    int(rating) if rating else None
                )
            )
            conn.commit()
            cur.close()
            conn.close()
            return redirect(url_for("index"))

    cur.execute("SELECT * FROM books ORDER BY created_at DESC")
    books = cur.fetchall()
    cur.close()
    conn.close()

    html_template = """
    <!DOCTYPE html>
    <html lang="ja">
    <head>
        <meta charset="UTF-8">
        <title>book-log-app</title>
        <style>
            body { font-family: sans-serif; margin: 30px; line-height: 1.6; background-color: #f9f9f9; color: #333; }
            .container { max-width: 900px; margin: 0 auto; background: #fff; padding: 25px; border-radius: 8px; box-shadow: 0 2px 5px rgba(0,0,0,0.1); }
            h1, h2 { border-bottom: 2px solid #eee; padding-bottom: 8px; }
            form { display: grid; gap: 12px; margin-bottom: 30px; }
            label { font-weight: bold; font-size: 0.9em; }
            input[type="text"], select { width: 100%; padding: 8px; border: 1px solid #ccc; border-radius: 4px; box-sizing: border-box; }
            button { background-color: #007bff; color: white; border: none; padding: 10px 15px; border-radius: 4px; cursor: pointer; font-weight: bold; }
            button:hover { background-color: #0056b3; }
            .btn-edit { background-color: #28a745; color: white; padding: 5px 10px; border-radius: 4px; text-decoration: none; font-size: 0.85em; font-weight: bold; }
            .btn-edit:hover { background-color: #218838; }
            .btn-delete { background-color: #dc3545; color: white; border: none; padding: 5px 10px; border-radius: 4px; cursor: pointer; font-size: 0.85em; font-weight: bold; }
            .btn-delete:hover { background-color: #c82333; }
            table { width: 100%; border-collapse: collapse; margin-top: 10px; }
            th, td { border: 1px solid #ddd; padding: 10px; text-align: left; }
            th { background-color: #f2f2f2; }
            .status-badge { display: inline-block; padding: 2px 8px; border-radius: 12px; font-size: 0.85em; background: #e0e0e0; }
            .action-cell { display: flex; gap: 8px; align-items: center; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>📚 book-log-app</h1>

            <h2>新しい本を登録</h2>
            <form method="POST">
                <div>
                    <label>タイトル（必須）:</label>
                    <input type="text" name="title" required placeholder="例: 独習Python">
                </div>
                <div>
                    <label>著者名:</label>
                    <input type="text" name="author" placeholder="例: 山田太郎">
                </div>
                <div>
                    <label>ステータス:</label>
                    <select name="status">
                        <option value="積読">積読</option>
                        <option value="読書中">読書中</option>
                        <option value="読了">読了</option>
                    </select>
                </div>
                <div>
                    <label>評価 (1〜5):</label>
                    <select name="rating">
                        <option value="">未評価</option>
                        <option value="5">⭐⭐⭐⭐⭐ (5)</option>
                        <option value="4">⭐⭐⭐⭐ (4)</option>
                        <option value="3">⭐⭐⭐ (3)</option>
                        <option value="2">⭐⭐ (2)</option>
                        <option value="1">⭐ (1)</option>
                    </select>
                </div>
                <button type="submit">登録する</button>
            </form>

            <h2>登録済みの本一覧 ({{ books|length }}冊)</h2>
            {% if books %}
            <table>
                <thead>
                    <tr>
                        <th>ID</th>
                        <th>タイトル</th>
                        <th>著者</th>
                        <th>ステータス</th>
                        <th>評価</th>
                        <th>更新日時</th>
                        <th>操作</th>
                    </tr>
                </thead>
                <tbody>
                    {% for book in books %}
                    <tr>
                        <td>{{ book.id }}</td>
                        <td><strong>{{ book.title }}</strong></td>
                        <td>{{ book.author or '-' }}</td>
                        <td><span class="status-badge">{{ book.status }}</span></td>
                        <td>{{ '⭐' * book.rating if book.rating else '-' }}</td>
                        <td><small>{{ book.updated_at.strftime('%Y-%m-%d %H:%M') }}</small></td>
                        <td class="action-cell">
                            <a href="/edit/{{ book.id }}" class="btn-edit">編集</a>
                            <form action="/delete/{{ book.id }}" method="POST" style="margin:0;" onsubmit="return confirm('本当に削除しますか？');">
                                <button type="submit" class="btn-delete">削除</button>
                            </form>
                        </td>
                    </tr>
                    {% endfor %}
                </tbody>
            </table>
            {% else %}
            <p>まだ登録されている本はありません。</p>
            {% endif %}
        </div>
    </body>
    </html>
    """
    return render_template_string(html_template, books=books)


# --------------------------------------------------
# 2. 編集・更新画面
# --------------------------------------------------
@app.route("/edit/<int:book_id>", methods=["GET", "POST"])
def edit_book(book_id):
    conn = get_db_connection()
    cur = conn.cursor()

    if request.method == "POST":
        title = request.form.get("title")
        author = request.form.get("author")
        status = request.form.get("status")
        rating = request.form.get("rating")

        if title:
            cur.execute(
                """
                UPDATE books
                SET title = %s,
                    author = %s,
                    status = %s,
                    rating = %s,
                    updated_at = CURRENT_TIMESTAMP
                WHERE id = %s
                """,
                (
                    title,
                    author if author else None,
                    status,
                    int(rating) if rating else None,
                    book_id
                )
            )
            conn.commit()
            cur.close()
            conn.close()
            return redirect(url_for("index"))

    cur.execute("SELECT * FROM books WHERE id = %s", (book_id,))
    book = cur.fetchone()
    cur.close()
    conn.close()

    if not book:
        return "書籍が見つかりません", 404

    edit_template = """
    <!DOCTYPE html>
    <html lang="ja">
    <head>
        <meta charset="UTF-8">
        <title>書籍の編集 - book-log-app</title>
        <style>
            body { font-family: sans-serif; margin: 30px; background-color: #f9f9f9; color: #333; }
            .container { max-width: 600px; margin: 0 auto; background: #fff; padding: 25px; border-radius: 8px; box-shadow: 0 2px 5px rgba(0,0,0,0.1); }
            form { display: grid; gap: 12px; margin-top: 20px; }
            label { font-weight: bold; font-size: 0.9em; }
            input[type="text"], select { width: 100%; padding: 8px; border: 1px solid #ccc; border-radius: 4px; box-sizing: border-box; }
            .btn-save { background-color: #28a745; color: white; border: none; padding: 10px; border-radius: 4px; cursor: pointer; font-weight: bold; }
            .btn-back { display: inline-block; margin-top: 15px; color: #6c757d; text-decoration: none; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>✏️ 書籍情報の編集</h1>
            <form method="POST">
                <div>
                    <label>タイトル（必須）:</label>
                    <input type="text" name="title" value="{{ book.title }}" required>
                </div>
                <div>
                    <label>著者名:</label>
                    <input type="text" name="author" value="{{ book.author or '' }}">
                </div>
                <div>
                    <label>ステータス:</label>
                    <select name="status">
                        <option value="積読" {% if book.status == '積読' %}selected{% endif %}>積読</option>
                        <option value="読書中" {% if book.status == '読書中' %}selected{% endif %}>読書中</option>
                        <option value="読了" {% if book.status == '読了' %}selected{% endif %}>読了</option>
                    </select>
                </div>
                <div>
                    <label>評価 (1〜5):</label>
                    <select name="rating">
                        <option value="" {% if not book.rating %}selected{% endif %}>未評価</option>
                        <option value="5" {% if book.rating == 5 %}selected{% endif %}>⭐⭐⭐⭐⭐ (5)</option>
                        <option value="4" {% if book.rating == 4 %}selected{% endif %}>⭐⭐⭐⭐ (4)</option>
                        <option value="3" {% if book.rating == 3 %}selected{% endif %}>⭐⭐⭐ (3)</option>
                        <option value="2" {% if book.rating == 2 %}selected{% endif %}>⭐⭐ (2)</option>
                        <option value="1" {% if book.rating == 1 %}selected{% endif %}>⭐ (1)</option>
                    </select>
                </div>
                <button type="submit" class="btn-save">更新する</button>
            </form>
            <a href="/" class="btn-back">← 一覧に戻る</a>
        </div>
    </body>
    </html>
    """
    return render_template_string(edit_template, book=book)


# --------------------------------------------------
# 3. 削除処理
# --------------------------------------------------
@app.route("/delete/<int:book_id>", methods=["POST"])
def delete_book(book_id):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM books WHERE id = %s", (book_id,))
    conn.commit()
    cur.close()
    conn.close()
    return redirect(url_for("index"))


if __name__ == "__main__":
    app.run(debug=True, port=5000)