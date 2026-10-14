import pytest
from app import app
from db import DATABASE_URL
from init_db import init_db
import psycopg2

@pytest.fixture
def client():
    # Flaskのテストモードを有効化
    app.config["TESTING"] = True

    # テスト開始前にテーブルが存在することを確認（なければ作成）
    init_db()

    with app.test_client() as client:
        # テスト実行前にテーブルをクリア（初期化）
        conn = psycopg2.connect(DATABASE_URL)
        cur = conn.cursor()
        cur.execute("TRUNCATE TABLE books RESTART IDENTITY;")
        conn.commit()
        cur.close()
        conn.close()

        yield client

        # テスト終了後のクリーンアップ（必要に応じて）
        conn = psycopg2.connect(DATABASE_URL)
        cur = conn.cursor()
        cur.execute("TRUNCATE TABLE books RESTART IDENTITY;")
        conn.commit()
        cur.close()
        conn.close()

# --------------------------------------------------
# 1. トップページの表示テスト（Read）
# --------------------------------------------------
def test_index_page(client):
    response = client.get("/")
    assert response.status_code == 200
    assert "book-log-app" in response.data.decode("utf-8")

# --------------------------------------------------
# 2. 書籍の新規登録テスト（Create）
# --------------------------------------------------
def test_add_book(client):
    # 本を1冊投稿
    post_data = {
        "title": "テスト用Python本",
        "author": "テスト著者",
        "status": "読書中",
        "rating": "4"
    }
    response = client.post("/", data=post_data, follow_redirects=True)
    assert response.status_code == 200

    # 画面上に投稿したデータが表示されているか検証
    html_content = response.data.decode("utf-8")
    assert "テスト用Python本" in html_content
    assert "テスト著者" in html_content
    assert "読書中" in html_content

# --------------------------------------------------
# 3. 書籍の更新テスト（Update）
# --------------------------------------------------
def test_update_book(client):
    # まずテストデータを1件挿入
    client.post("/", data={"title": "変更前の本", "status": "積読"}, follow_redirects=True)

    # ID:1 の書籍を更新
    update_data = {
        "title": "変更後の本",
        "author": "更新後の著者",
        "status": "読了",
        "rating": "5"
    }
    response = client.post("/edit/1", data=update_data, follow_redirects=True)
    assert response.status_code == 200

    # 一覧画面に更新内容が反映されているか検証
    html_content = response.data.decode("utf-8")
    assert "変更後の本" in html_content
    assert "読了" in html_content

# --------------------------------------------------
# 4. 書籍の削除テスト（Delete）
# --------------------------------------------------
def test_delete_book(client):
    # テストデータを1件挿入
    client.post("/", data={"title": "削除される本"}, follow_redirects=True)

    # ID:1 の書籍を削除
    response = client.post("/delete/1", follow_redirects=True)
    assert response.status_code == 200

    # 画面から削除されているか検証
    html_content = response.data.decode("utf-8")
    assert "削除される本" not in html_content
