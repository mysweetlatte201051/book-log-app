from flask import Flask, render_template_string
from db import DATABASE_URL
import psycopg2

app = Flask(__name__)


# トップページの設定
@app.route("/")
def home():
    db_status = "未確認"
    db_version = ""

    # DB接続テスト
    try:
        conn = psycopg2.connect(DATABASE_URL)
        cur = conn.cursor()
        cur.execute("SELECT version();")
        db_version = cur.fetchone()[0]
        cur.close()
        conn.close()
        db_status = "正常に接続されています ✅"
    except Exception as e:
        db_status = f"接続エラー: {e} ❌"

    # ブラウザに表示するHTML（簡易デザイン）
    html_template = """
    <!DOCTYPE html>
    <html lang="ja">
    <head>
        <meta charset="UTF-8">
        <title>book-log-app</title>
        <style>
            body { font-family: sans-serif; margin: 40px; line-height: 1.6; }
            .card { border: 1px solid #ccc; padding: 20px; border-radius: 8px; max-width: 600px; }
            .status { font-weight: bold; color: green; }
        </style>
    </head>
    <body>
        <h1>📚 book-log-app へようこそ！</h1>
        <div class="card">
            <h2>データベースステータス</h2>
            <p><strong>状態:</strong> <span class="status">{{ status }}</span></p>
            {% if version %}
            <p><small>{{ version }}</small></p>
            {% endif %}
        </div>
    </body>
    </html>
    """
    return render_template_string(html_template, status=db_status, version=db_version)


if __name__ == "__main__":
    # 開発用サーバー起動（ポート5000 / デバッグモードON）
    app.run(debug=True, port=5000)