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

### Databaseの非同期の実験

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