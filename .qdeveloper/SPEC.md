新しいPythonコードを作成するときは、以下のガイダンスを使用してください。

- WebフレームワークとしてFlaskを使う
- Flaskのアプリケーションファクトリーパターンに従う
- コンフィギュレーションに環境変数を使う
- データベース操作のためにFlask-SQLAlchemyを実装する

次のようなプロジェクト構成にする。

├── src
├── src/static/
├── src/models/
├── src/routes/
├── src/templates/
├── src/extensions.py
├ app.py
├ requirements.txt