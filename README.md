# 📚 book-log-app (書籍管理Webアプリケーション)

Python / Flask および PostgreSQL を用いて構築した、読書状況や感想メモを管理するためのWebアプリケーションです。
開発プロセスの透明化、品質担保のための自動テスト（CI/CD）、および技術知見のドキュメント化を意識して構築しています。

---

## 🛠 技術スタック

* **Backend:** Python 3.12, Flask
* **Database:** PostgreSQL (`psql`)
* **Testing:** pytest
* **CI/CD:** GitHub Actions
* **Frontend:** HTML5, CSS3, Jinja2 Template

---

## ✨ 主な機能

* **書籍情報の登録・編集・削除 (CRUD)**
  * タイトル、著者、ステータス（積読 / 読書中 / 読了）、5段階評価、詳細メモ
* **検索・フィルタリング機能**
  * PostgreSQL の `ILIKE` 検索による部分一致検索
* **データベースマイグレーション**
  * `init_db.py` による冪等性（繰り返し実行可能）を担保した安全なDB初期化
* **自動テスト＆CI構築**
  * `pytest` によるエンドポイントおよびDB操作の検証
  * GitHub Actions によるコミットごとの自動テスト実行

---

## 📝 技術解説記事・実績 (Qiita)

本リポジトリの開発過程で得たトラブルシューティングや設計に関する知見を Qiita にて公開しています。

* **Qiita 執筆記事:**
  * [【Flask / PostgreSQL】Webアプリ開発と自動テスト追従の実践記録](https://qiita.com/) *(※実際の記事URLを貼り付けてください)*
* **主な実績:**
  * 初速での LGTM および ストック（後で読む保存）を獲得
  * 有志による「Qiita いいねランキング自動更新記事」にランクイン・選出
  * 他ユーザーの技術記事からの参照・引用リンクを獲得

---

## 🚀 ローカル環境での起動方法

1. **リポジトリのクローン**
   ```bash
   git clone [https://github.com/YOUR_USERNAME/book-log-app.git](https://github.com/YOUR_USERNAME/book-log-app.git)
   cd book-log-app

2. **依存パッケージのインストール**

   ```Bash
   pip install -r requirements.txt

3. **データベースの初期化**

   ```Bash
   python init_db.py
   
4. **アプリケーションの起動**

   ```Bash
   python app.py

5. **テストの実行**

   ```Bash
   pytest test_app.py -v