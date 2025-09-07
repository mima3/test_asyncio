# AsyncIOの検証

## 概要
このリポジトリはPythonのAsyncIOの実験を行うものである
実験には以下が動作する環境が存在すること。

- docker
- pipenv

また実験は以下の環境で作成したものである。

**マシン環境：**
macOS 15.4.1
2 GHz クアッドコアIntel Core i5
16 GB 3733 MHz LPDDR4X

## 事前知識

- [A Conceptual Overview of asyncio](https://docs.python.org/ja/3.13/howto/a-conceptual-overview-of-asyncio.html#a-conceptual-overview-of-asyncio)
- [import asyncio: Learn Python's](https://www.youtube.com/watch?v=Xbl7XjFYsN4&list=PLhNSoGM2ik6SIkVGXWBwerucXjgP1rHmB)
- [Python Concurrency with asyncio](https://www.amazon.co.jp/dp/1617298662)

## 実験対象のダミーの外部リソースの起動

```bash
cd docker
# 開始時
docker compose up
```

- postgres
  - postgres16のDBコンテナを起動する
- mysql
  - mysql8のDBコンテナを起動する
- wiremock
  - ダミーのRESTAPIを提供するサーバーを作る
  - GET /hello/{id} で値を返す
    - レスポンス時間は1秒から4秒

## 実験環境のPython環境の構築

**環境をインストール**

```bash
cd py313
pipenv install --dev
```

**環境を消す場合**

```bash
cd py313
pipenv --rm
```

### REST APIの実行の実験

**httpxを使用してREST APIを実行するサンプル**  

このサンプルはhttpxを非同期に実行するサンプルです。
同時実行数は10で制限しています。

```
pipenv run python rest/test_httpx.py
```

**requestsを同期的に実行するサンプル**  

このサンプルはrequestsを同期的にに実行するサンプルです。

```
pipenv run python rest/test_requests_sync.py
```

**requestsを非同期的に実行するサンプル**  

このサンプルは同期的に動くrequestsをasyncio.to_threadを用いて非同期的に動作させるサンプルです。
同時実行数は10で制限しています。

```
pipenv run python rest/test_requests_async.py
```

### Databaseの非同期の実験
この試験はMySQLとPostgressに同時に操作を行う実験になっています。

使用ライブラリ
- SQLAlchemy
- [asyncpg](https://github.com/MagicStack/asyncpg)
  - Postgressの非同期ライブラリ
- [asyncmy](https://github.com/long2ice/asyncmy)
  - MySQLの非同期ライブラリ。[aiomysql](https://github.com/aio-libs/aiomysql)もあるが最終コミットが2023年

**dbを構築**  

```py
pipenv run python -m db.init_db
```


**クエリの実験**  

```
pipenv run python -m db.query_db
```

**dbを削除**  

```py
pipenv run python db.truncate_db
```