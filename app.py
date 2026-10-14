from flask import Flask, request, redirect, url_for, render_template_string
from db import DATABASE_URL
import psycopg2
from psycopg2.extras import RealDictCursor

app = Flask(__name__)


def get_db_connection():
    conn = psycopg2.connect(DATABASE_URL, cursor_factory=RealDictCursor)
    return conn


@app.route("/", methods=["GET", "POST"])
def index():
    conn = get_db_connection()
    cur = conn.cursor()

    # POSTリクエスト（書籍の登録処理）
    if request.method == "POST":
        title = request.form.get("title")
        author = request.form.get("author")
        status = request.form.get("status")
        rating = request.form.get("rating")

        # 簡易バリデーション（タイトルは必須）
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

    # GETリクエスト（書籍一覧の取得）
    cur.execute("SELECT * FROM books ORDER BY created_at DESC")
    books = cur.fetchall()
    cur.close()
    conn.close()

    # HTMLテンプレート（登録フォーム ＋ 一覧表示）
    html_template = """
    <!DOCTYPE html>
    <html lang="ja">
    <head>
        <meta charset="UTF-8">
        <title>book-log-app</title>
        <style>
            body { font-family: sans-serif; margin: 30px; line-height: 1.6; background-color: #f9f9f9; color: #333; }
            .container { max-width: 800px; margin: 0 auto; background: #fff; padding: 25px; border-radius: 8px; box-shadow: 0 2px 5px rgba(0,0,0,0.1); }
            h1, h2 { border-bottom: 2px solid #eee; padding-bottom: 8px; }
            form { display: grid; gap: 12px; margin-bottom: 30px; }
            label { font-weight: bold; font-size: 0.9em; }
            input[type="text"], select { width: 100%; padding: 8px; border: 1px solid #ccc; border-radius: 4px; box-sizing: border-box; }
            button { background-color: #007bff; color: white; border: none; padding: 10px 15px; border-radius: 4px; cursor: pointer; font-weight: bold; }
            button:hover { background-color: #0056b3; }
            table { width: 100%; border-collapse: collapse; margin-top: 10px; }
            th, td { border: 1px solid #ddd; padding: 10px; text-align: left; }
            th { background-color: #f2f2f2; }
            .status-badge { display: inline-block; padding: 2px 8px; border-radius: 12px; font-size: 0.85em; background: #e0e0e0; }
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
                        <th>登録日時</th>
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
                        <td><small>{{ book.created_at.strftime('%Y-%m-%d %H:%M') }}</small></td>
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


if __name__ == "__main__":
    app.run(debug=True, port=5000)