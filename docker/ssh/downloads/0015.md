LMQ(Lightweight Message Queue)はErlangで実装したHTTP経由で使用できるメッセージキューです。  
以下のようにLMQが動作している端末に別の端末からHTTP POSTによりメッセージを追加、別の端末でHTTP-GETによりキューのデータを取得することができます。  
![lmq.png](/image/8a4b2fbe-532b-4d5f-1566-b28438742f09.png)  
  
また、次のように、2つ以上のLMQをしようして冗長化が可能です。  
![lmq.png](/image/7075f4c9-31ce-0070-1e59-697395fd3aa0.png)  
  
このLMQにより、HTTPプロトコルを用いたプロセス間通信や、端末間の通信を容易に分散化させることが可能になります。つまり、設計しだいで、スケーリングが可能なシステムを構築することが容易になると期待できます。  
  
このソフトウェアのライセンスはThe MIT License (MIT)となっています。  
詳細は下記を参照してください。  
https://github.com/iij/lmq  
  
# Debianでのインストール  
１．前提条件としてGitをインストールしておいてください。  
これはlmqのmakeに使用します。  
  
２. Erlangをインストールします。  
　ソースコードを以下からダウンロードします。今回は17.1を利用しました。  
http://www.erlang.org/download.html  
  
３．解凍したフォルダで次の作業を行います。  
  
```
./configure
make install
```  
  
４．erlコマンドが使えることを確認します。  
  
```
root@debian:/share/otp_src_17.1# erl
Erlang/OTP 17 [erts-6.1] [source] [64-bit] [async-threads:10] [hipe] [kernel-poll:false]

Eshell V6.1  (abort with ^G)
1> 1+1.
2
```  
  
５．LMQを取得し、makeします。  
  
```
git clone https://github.com/iij/lmq.git
cd lmq
make rel
```  
  
この時以下のようなエラーがでるかもしれません。  
  
 __Cannot update the ref 'HEAD' というエラー__   
```
ERROR: cmd /q /c git checkout -q origin/master failed with error: 128 and output:
error: Couldn't set HEAD
fatal: Cannot update the ref 'HEAD'.

make: *** [deps] Error 1
```  
  
この場合は、lmq/deps中のいづれかが、git clone後のcheckoutに失敗しています。  
手動で、check outしましょう。  
  
※再現しないので、おそらく、実験環境の問題だと思います。  
  
  
 __ERROR: OTP release 17 does not match required regex R15|R16 というエラー__   
msgpack_rpc/rebar.configがR16までしか認めていないせいです。  
  
以下のように修正してmakeしなおせばビルドができるでしょう。  
  
```
 R15|R16|17
```  
  
※現状では対応済みのようです。  
  
  
６．LMQをmakeするとrel/lmq/bin/lmqが作成されています。  
  
次のコマンドを実行してlmqを起動します  
  
```
rel/lmq/bin/lmq start
```  
  
７．メッセージキューの登録は次の通り  
  
```
root@debian:~/lmq# curl -i -XPOST localhost:9980/messages/myqueue -H 'content-type: text/plain' -d 'ゆっくりしていってね'
HTTP/1.1 200 OK
connection: keep-alive
server: Cowboy
date: Sun, 03 Aug 2014 20:25:35 GMT
content-length: 14
content-type: application/json

{"accum":"no"}
```  
  
  
８．メッセージキューの取得は次の通り  
  
```
root@curl -i localhost:9980/messages/myqueue
HTTP/1.1 200 OK
connection: keep-alive
server: Cowboy
date: Sun, 03 Aug 2014 20:25:53 GMT
content-length: 30
content-type: text/plain
x-lmq-queue-name: myqueue
x-lmq-message-id: f26f95a1-7b6b-48c3-b18d-9184fb6796f2
x-lmq-message-type: normal

ゆっくりしていってね
```  
  
メッセージキューを取得した場合、x-lmq-message-idが取得できます。  
メッセージに応じた処理を行い、その成否を返します。  
  
```
curl -i -XPOST 'localhost:9980/messages/myqueue/f26f95a1-7b6b-48c3-b18d-9184fb6796f2?reply=ack'
```  
  
replyは以下のいづれかを指定してください。  
ack: 処理が正常に終了 -> メッセージをキューから削除  
nack: 処理が継続できなくなった -> メッセージをキューに戻す  
ext: 処理に時間がかかっている -> メッセージの処理可能時間を延長  
  
# Windowsでインストール（失敗）  
結論から言います。  
現時点ではLMQをインストールすることは不可能そうです。  
lmqが依存するjsonxのmakeに失敗しました。  
このライブラリのビルドで失敗しているケースが他にもあるようなので、現状動作しないとみていいでしょう。  
https://github.com/5HT/n2o/issues/13  
  
  
  
## インストールに失敗した方法  
環境：  
Winsows7 64bit Home Premium.  
  
１．以下からWindowsのインストーラを取得する。  
http://www.erlang.org/download.html  
  
２．インストール後、システム環境設定で「C:\Program Files (x86)\erl6.1\bin」にパスが通るようにする。  
  
  
３．gitとmakeが使えないとlmqがインストールできないので、msysGitをインストールする。  
http://msysgit.github.io/  
  
このページの下の方のDownloadを選択すること。（上の方だとGit for WindowsでGit以外のmakeなどができない）  
  
![lmq.png](/image/e5525f4e-3290-99b3-445d-cb1f4e589a58.png)  
  
もし、インストール中にmsgfmtでエラーが出たら、「LOCALE=C」を実行後、再度、「make install」を行う  
https://groups.google.com/forum/#!msg/msysgit/noypkk5XzAI/ol1o2oK1wqsJ  
  
４．あとは、debianと同様にlmqをインストールする。  
ただし、現状は以下のようなエラーが発生する。  
  
```
==> Entering directory `c:/Users/username/git/lmq/deps/jsonx'
==> jsonx (compile)
Compiling c_src/jsonx.c
c_src/jsonx.c:1: warning: -fPIC ignored for target (all code is position independent)
In file included from c_src/jsonx.c:4:
c_src/jsonx.h:3:21: error: erl_nif.h: No such file or directory
In file included from c_src/jsonx.c:4:
c_src/jsonx.h:10: error: expected specifier-qualifier-list before 'ERL_NIF_TERM'
c_src/jsonx.h:31: error: expected '=', ',', ';', 'asm' or '__attribute__' before 'decode_nif'
c_src/jsonx.h:32: error: expected '=', ',', ';', 'asm' or '__attribute__' before 'encode_nif'
In file included from c_src/jsonx.c:4:
c_src/jsonx.h:66: error: expected specifier-qualifier-list before 'ERL_NIF_TERM'
c_src/jsonx.h:72: error: expected specifier-qualifier-list before 'ErlNifBinary'
c_src/jsonx.h: In function 'enc_fields_base':
c_src/jsonx.h:86: error: 'EncEntry' has no member named 'records_cnt'
c_src/jsonx.h: At top level:
c_src/jsonx.h:138: error: expected specifier-qualifier-list before 'ERL_NIF_TERM'
c_src/jsonx.h:149: error: expected '=', ',', ';', 'asm' or '__attribute__' before '*' token
c_src/jsonx.h: In function 'ukeys_size':
c_src/jsonx.h:156: error: 'ERL_NIF_TERM' undeclared (first use in this function)
c_src/jsonx.h:156: error: (Each undeclared identifier is reported only once
c_src/jsonx.h:156: error: for each function it appears in.)
c_src/jsonx.h: In function 'keys_base':
c_src/jsonx.h:161: warning: implicit declaration of function 'ukeys_base'
c_src/jsonx.c: At top level:
c_src/jsonx.c:7: error: expected ')' before '*' token
c_src/jsonx.c:19: error: expected ')' before '*' token
c_src/jsonx.c:59: error: expected ')' before '*' token
c_src/jsonx.c:64: error: expected ')' before '*' token
c_src/jsonx.c:69: error: expected ')' before '*' token
c_src/jsonx.c:75: error: expected '=', ',', ';', 'asm' or '__attribute__' before 'make_encoder_resource_nif'
c_src/jsonx.c:152: error: expected '=', ',', ';', 'asm' or '__attribute__' before 'make_decoder_resource_nif'
c_src/jsonx.c:223: error: expected '=', ',', ';', 'asm' or '__attribute__' before 'nif_funcs'
c_src/jsonx.c:232: warning: data definition has no type or storage class
c_src/jsonx.c:232: warning: type defaults to 'int' in declaration of 'ERL_NIF_INIT'
c_src/jsonx.c:232: warning: parameter names (without types) in function declaration
cc: /DWIN32: No such file or directory
cc: /D_WINDOWS: No such file or directory
cc: /D_WIN32: No such file or directory
cc: /DWINDOWS: No such file or directory
cc: Files: No such file or directory
cc: (x86)/erl6.1/lib/erl_interface-3.7.17/include: No such file or directory
cc: Files: No such file or directory
cc: (x86)/erl6.1/erts-6.1/include: No such file or directory
ERROR: cmd /q /c cc -c /Wall /DWIN32 /D_WINDOWS /D_WIN32 /DWINDOWS -g -Wall -fPIC  -Ic:/Program Files (x86)/erl6.1/lib/erl_interface-3.7.17/include -I
c_src/jsonx.c:1: warning: -fPIC ignored for target (all code is position independent)
In file included from c_src/jsonx.c:4:
c_src/jsonx.h:3:21: error: erl_nif.h: No such file or directory
In file included from c_src/jsonx.c:4:
c_src/jsonx.h:10: error: expected specifier-qualifier-list before 'ERL_NIF_TERM'
c_src/jsonx.h:31: error: expected '=', ',', ';', 'asm' or '__attribute__' before 'decode_nif'
c_src/jsonx.h:32: error: expected '=', ',', ';', 'asm' or '__attribute__' before 'encode_nif'
In file included from c_src/jsonx.c:4:
c_src/jsonx.h:66: error: expected specifier-qualifier-list before 'ERL_NIF_TERM'
c_src/jsonx.h:72: error: expected specifier-qualifier-list before 'ErlNifBinary'
c_src/jsonx.h: In function 'enc_fields_base':
c_src/jsonx.h:86: error: 'EncEntry' has no member named 'records_cnt'
c_src/jsonx.h: At top level:
c_src/jsonx.h:138: error: expected specifier-qualifier-list before 'ERL_NIF_TERM'
c_src/jsonx.h:149: error: expected '=', ',', ';', 'asm' or '__attribute__' before '*' token
c_src/jsonx.h: In function 'ukeys_size':
c_src/jsonx.h:156: error: 'ERL_NIF_TERM' undeclared (first use in this function)
c_src/jsonx.h:156: error: (Each undeclared identifier is reported only once
c_src/jsonx.h:156: error: for each function it appears in.)
c_src/jsonx.h: In function 'keys_base':
c_src/jsonx.h:161: warning: implicit declaration of function 'ukeys_base'
c_src/jsonx.c: At top level:
c_src/jsonx.c:7: error: expected ')' before '*' token
c_src/jsonx.c:19: error: expected ')' before '*' token
c_src/jsonx.c:59: error: expected ')' before '*' token
c_src/jsonx.c:64: error: expected ')' before '*' token
c_src/jsonx.c:69: error: expected ')' before '*' token
c_src/jsonx.c:75: error: expected '=', ',', ';', 'asm' or '__attribute__' before 'make_encoder_resource_nif'
c_src/jsonx.c:152: error: expected '=', ',', ';', 'asm' or '__attribute__' before 'make_decoder_resource_nif'
c_src/jsonx.c:223: error: expected '=', ',', ';', 'asm' or '__attribute__' before 'nif_funcs'
c_src/jsonx.c:232: warning: data definition has no type or storage class
c_src/jsonx.c:232: warning: type defaults to 'int' in declaration of 'ERL_NIF_INIT'
c_src/jsonx.c:232: warning: parameter names (without types) in function declaration
cc: /DWIN32: No such file or directory
cc: /D_WINDOWS: No such file or directory
cc: /D_WIN32: No such file or directory
cc: /DWINDOWS: No such file or directory
cc: Files: No such file or directory
cc: (x86)/erl6.1/lib/erl_interface-3.7.17/include: No such file or directory
cc: Files: No such file or directory
cc: (x86)/erl6.1/erts-6.1/include: No such file or directory

make: *** [compile] Error 1
```  
  
  
# まとめ  
DebianやMacなどでは、LMQの導入は難しくはないでしょう。  
  
しかし、WindowsではLMQを動作させるのは無理、もしくは、困難です。もしかしたらCygwinでは行えるかもしれませんが、仮にできてもライセンス的に配布にリスクがあるので当方では無理です。  
  
Windows以外のサーバーでメッセージキューを配置するという前提ならば、十分活用のチャンスはあると思います。  
  
