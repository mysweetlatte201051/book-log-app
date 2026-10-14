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
    assert "書籍管理アプリ" in response.get_data(as_text=True)

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
    # 追加エンドポイントを / から /add に変更
    response = client.post("/add", data=post_data, follow_redirects=True)
    assert response.status_code == 200
    assert "テスト用Python本" in response.get_data(as_text=True)

# --------------------------------------------------
# 3. 書籍の更新テスト（Update）
# --------------------------------------------------
def test_update_book(client):
    # まずテストデータを1件挿入
    client.post("/add", data={"title": "変更前の本", "status": "積読"}, follow_redirects=True)

    # ID:1 の書籍を更新
    update_data = {
        "title": "変更後の本",
        "author": "更新後の著者",
        "status": "読了",
        "rating": "5"
    }
    response = client.post("/edit/1", data=update_data, follow_redirects=True)
    assert response.status_code == 200
    assert "変更後の本" in response.get_data(as_text=True)

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
    assert "削除される本" not in response.get_data(as_text=True)


# --------------------------------------------------
# 5. 検索テスト
# --------------------------------------------------
def test_search_books(client):
    # テスト用データを3件作成 (/add エンドポイントへ POST)
    client.post("/add", data={"title": "Python入門", "author": "山田太郎", "status": "読書中"}, follow_redirects=True)
    client.post("/add", data={"title": "Flask Web開発", "author": "佐藤花子", "status": "積読"}, follow_redirects=True)
    client.post("/add", data={"title": "SQL実践ガイド", "author": "山田太郎", "status": "読了"}, follow_redirects=True)

    # 1. キーワード「Python」で検索 ➔ 「Python入門」のみ表示されること
    response = client.get("/?keyword=Python")
    content = response.get_data(as_text=True)
    assert "Python入門" in content
    assert "Flask Web開発" not in content

    # 2. ステータス「積読」で絞り込み ➔ 「Flask Web開発」のみ表示されること
    response = client.get("/?status=積読")
    content = response.get_data(as_text=True)
    assert "Flask Web開発" in content
    assert "Python入門" not in content