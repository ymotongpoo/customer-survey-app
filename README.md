# 顧客調査アプリケーション

顧客からのフィードバックを収集するためのシンプルなウェブアプリケーションです。

## 機能

- ユーザー登録・ログイン機能
- アンケート作成・管理
- 回答結果の可視化
- 共有可能なアンケートリンク

## 技術スタック

- Python 3.8+
- Flask (Webフレームワーク)
- SQLAlchemy (ORM)
- SQLite (データベース)
- Chart.js (グラフ表示)

## プロジェクト構成

```
├── app.py                  # アプリケーションファクトリー
├── config.py               # 設定ファイル
├── init_db.py              # データベース初期化スクリプト
├── requirements.txt        # 依存関係
└── src/                    # ソースコードディレクトリ
    ├── extensions.py       # Flaskの拡張機能
    ├── models/             # データモデル
    ├── routes/             # ルート定義
    ├── static/             # 静的ファイル
    └── templates/          # テンプレート
```

## セットアップと実行方法

### セットアップ

1. リポジトリをクローン:
   ```
   git clone <repository-url>
   cd customer-survey-app
   ```

2. 仮想環境を作成して有効化:
   ```
   python -m venv venv
   source venv/bin/activate  # Linuxの場合
   venv\Scripts\activate     # Windowsの場合
   ```

3. 依存関係をインストール:
   ```
   pip install -r requirements.txt
   ```

4. 環境変数を設定:
   ```
   cp .env.example .env
   # .envファイルを編集して適切な値を設定
   ```

### データベースの初期化

アプリケーションを初めて実行する前に、データベースを初期化します:

```
python init_db.py
```

これにより、SQLiteデータベースが作成され、テーブルが作成されます。また、デモユーザーとサンプルアンケートも追加されます。

### アプリケーションの実行

Flaskアプリケーションを起動します:

```
flask run
```

または、直接 `app.py` を実行することもできます:

```
python app.py
```

ブラウザで http://127.0.0.1:5000 にアクセスすると、アプリケーションのホームページが表示されます。

### ログイン

初期データベースにはデモユーザーが含まれています:
- メールアドレス: demo@example.com
- パスワード: password123

このアカウントでログインするか、新しいアカウントを登録してアプリケーションを使用できます。

## 使用方法

1. アカウントを登録してログイン
2. ダッシュボードからアンケートを作成
3. 作成したアンケートの共有リンクをコピー
4. リンクを顧客に共有して回答を収集
5. ダッシュボードから結果を確認

## トラブルシューティング

1. **データベースエラー**: データベースに問題がある場合は、`instance` ディレクトリを削除して `python init_db.py` を再実行してください。

2. **ポートの競合**: デフォルトのポート（5000）が使用中の場合は、以下のように別のポートを指定できます:
   ```
   flask run --port=5001
   ```

3. **依存関係の問題**: 依存関係のインストールに問題がある場合は、仮想環境を作成して再試行することをお勧めします:
   ```
   python -m venv venv
   source venv/bin/activate  # Linuxの場合
   venv\Scripts\activate     # Windowsの場合
   pip install -r requirements.txt
   ```