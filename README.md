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
- ssh_server
  - openssh-serverのコンテナを起動する
- localstack
  - localstackを起動してAWSのS3,SQS,dynamodbを擬似的にローカルで動かす

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

**requestsを同期的に実行するサンプル**  

このサンプルはrequestsを同期的にに実行するサンプルです。

```
pipenv run python -m rest.test_requests_sync
```

**requestsを非同期的に実行するサンプル**  

このサンプルは同期的に動くrequestsをasyncio.to_threadを用いて非同期的に動作させるサンプルです。  

```
pipenv run python -m rest.test_requests_async
```

この際、セマフォを用いて同時実行数の上限を5として実行する場合は以下のようになります。

```
pipenv run python -m rest.test_requests_async_with_semaphore
```


**httpxを使用してREST APIを実行するサンプル**  

このサンプルは[httpx](https://github.com/encode/httpx)を非同期に実行するサンプルです。  
httpx を使うとスレッド管理が不要になり、requestsに近い開発体験になります。

```
pipenv run python -m rest.test_httpx
```

この際、セマフォを用いて同時実行数の上限を5として実行する場合は以下のようになります。

```
pipenv run python -m rest.test_httpx_with_semaphore
```

REST APIには秒間の要求数の上限が要求されているケースがあります。
以下の例では[aiometer](https://github.com/florimondmanca/aiometer/tree/master)を使用して秒間の要求数を絞ったものになります。

```
pipenv run python -m rest.test_httpx_with_limit 
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

### SSHのファイル送受信の非同期処理

このサンプルはSSHサーバーとのファイルの送受信を実施するサンプルとなります。

使用ライブラリ
- [AsyncSSH](https://asyncssh.readthedocs.io/en/latest/index.html)


**ファイルの送受信のテスト**

ファイルをSSHからダウンロード後、追記を行いアップロードしなおす。

```
pipenv run python -m ssh.test_ssh
```


### AWSの非同期処理
[aioboto3](https://pypi.org/project/aioboto3/)を使用してS3へのファイルアップロードのサンプルを記載します。
[boto3](https://github.com/boto/boto3)と[aiobotocore](https://github.com/aio-libs/aiobotocore)のラッパーになっています。
またローカルファイルの操作は[aiofiles](https://pypi.org/project/aiofiles/)を使用して非同期化しています。

#### S3へのアップロードの操作例

docker/ssh/downloadsにあるファイルをlocalstackのmy-bucketパケットのincomeのしたにアップロードするサンプルです。

```
pipenv run python -m aws.test_s3_aioboto3 
```

localstackにアップロードしたファイルは以下のコマンドで確認できます。

```
curl http://localhost:4566/my-bucket/income/0010.md
```
