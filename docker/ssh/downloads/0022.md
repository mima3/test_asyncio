このドキュメントではフックの説明と、フックの挙動を検証するための方法とその結果を記述する。  
  
  
# フックの説明  
Gitは特定のコマンドが実行された場合に、スクリプトを起動させることができる。  
そのスクリプトは.git/hooks フォルダに特定の名称で作成することで実行される。  
  
# 検証プログラム  
検証環境は以下の通り  
Debian7.0  
git version 1.7.10.4  
  
フックの動作を検証するために、各フックスクリプトに下記を記述する。  
  
```
# !/bin/sh
logger "********************************************"
logger ${0##*/}
logger "param $*"
logger "param cont $#"
logger "input..."
while read i; do
  logger ${i}
done
```  
  
後は下記のコマンドでsyslogを監視しながらgitの操作を行う  
  
```
tail -f /var/log/messages
```  
  
これにより、フックスクリプトの発生順と、パラメータ、標準入力の検証が行える。  
  
# フックの確認  
## commitコマンドのフック  
commitコマンドのフックの実行順序は以下の通りである。  
  
1.commit コマンド  
2.pre-commitスクリプト実行  
3.デフォルトのログメッセージの準備  
4.prepare-commit-msgスクリプト実行  
5.コミットメッセージ入力用のエディタ起動  
6.commit-msgスクリプト実行  
7.コミットの作成  
8.post-commitスクリプト実行  
9.--amendで実行した場合はpost-rewriteスクリプト実行  
  
### pre-commit  
「git commit」によって呼び出される。commitコマンドに「--no-verify」オプションをつけると呼び出されない。  
  
引数は存在しない。  
0以外の終了コードでコマンドを中断する。  
  
### prepare-commit-msg  
「git commit」によって呼び出される。デフォルトログメッセージの準備が終わった後、そしてエディターが起動する前に呼ばれる。  
  
最大で３つの引数をとる。  
第一引数はコミットメッセージを保存したファイルへのパス  
第二引数はコミットのタイプである。  
  
|Type|説明|  
|:---|:---|  
|なし|オプションなし|  
|message|-m, -Fオプションがある場合|  
|template|-tオプションなどでテンプレートが指定された場合|  
|merge|mergeによるコミットの場合|  
|squash|--squash オプションでブランチのコミットをまとめた場合|  
|commit|-c, -C ,--amendをオプションとして使用した場合。この場合、第三引数にSHA-1が与えられる|  
  
0以外の終了コードでコマンドを中断する。  
  
### commit-msg  
「git commit」によって呼び出される。commitコマンドに「--no-verify」オプションをつけると呼び出されない。  
  
１つの引数を取る  
第一引数は現在のコミットメッセージを保存した一時ファイルへのパスになる。  
  
0以外の終了コードでコマンドを中断する。  
  
### post-commit  
「git commit」によって呼び出される。  
引数は存在しない。  
コミットを作成したあとに呼ばれ、このスクリプトはgit commit に影響を与えない。  
通常、commitの通知に使用される。  
  
### post-rewrite  
「git commit --amend」や「git rebase」などでコミットログの書き換えが発生された場合に実行される。  
  
引数は１つのみで、amend または　rebaseとなる。  
  
また標準入力から以下のデータを取得できる。  
  
```
<old-sha1> SP <new-sha1> [ SP <extra-info> ] LF
```  
  
extra-infoはコマンド依存。これが空の場合、前のSPも省略される。  
  
このスクリプトはgit commit に影響を与えない。  
  
## am コマンドのフック  
git format-patch で作ったパッチを git am で適用する際に実行されるフックの順番は以下のとおりになる。  
  
1. git am コマンド実行  
2. applypatch-msgスクリプト実行  
3. パッチが適用される  
4. pre-applypatchスクリプト実行  
5. コミットの作成  
6. post-applypatchスクリプト実行  
  
このamコマンドでコミットが作成されても、commit用のフックスクリプトは実行されない。  
デフォルトのapplypatch-msgなどは、コミット用のフックスクリプトを実装するサンプルになっている。  
  
### applypatch-msg  
「git am」コマンド実行時に呼び出される。  
引数を一つとり、それはミットメッセージを含む一時ファイル名になる。  
0以外の終了コードでコマンドを中断する。  
  
### pre-applypatch  
「git am」コマンド実行時に呼び出される。  
パッチが適用されたのちに、コミットを作成する前に、呼び出される。  
引数は存在しない。  
0以外の終了コードでコマンドを中断する。  
  
### post-applypatch  
「git am」コマンド実行時に呼び出される。  
パッチが適用され、コミットが作成されたのちに呼び出される。  
引数は存在しない。  
このスクリプトは「git am」の結果に影響を与えない。  
通常は通知に用いられる。  
  
## rebaseコマンドのフック  
rebaseコマンドを実行する前にpre-rebaseスクリプトが実行される。  
  
その後、次のフックスクリプトが実行されていた。  
1.post-checkoutスクリプト実行  
2.applypatch-msgスクリプト実行  
3.pre-applypatchスクリプト実行  
4.post-applypatchスクリプト実行  
5.post-rewriteスクリプト実行  
  
2～4はコミットの数だけ複数回。  
  
  
### pre-rebase  
rebaseコマンドを実行する前にpre-rebaseスクリプトが実行される。  
  
引数として最大２つ取る。  
第一引数は再配置先のブランチ名  
第二引数は再配置をするブランチ名で、現在ブランチの場合はブランクになる。  
  
0以外の終了コードでコマンドを中断する。  
  
  
## checkoutコマンドのフック  
checkoutコマンドが完了した時にpost-checkoutスクリプトを実行する。  
  
### post-checkout  
このスクリプトはcheckoutコマンドでワークツリーが更新された後に実行される。  
次の３つの引数を取る。  
第１引数　変更前のHEADのSHA  
第２引数　変更後のHEADのSHA  
第３引数　ブランチの変更があったかどうかのフラグ 1:変更あり 0:なし  
  
このスクリプトはコマンドの結果に影響を与えない。  
  
## mergeコマンドのフック  
mergeコマンドを実行した場合、次の順番でフックメッセージが発生する  
  
1. prepare-commit-msgスクリプト実行  
2. コミットメッセージの入力  
3. コミットの完了  
4. post-mergeスクリプト実行  
  
### post-merge  
meregeコマンドが完了されたら実行される。  
このスクリプトはsquashマージかどうかの引数を１つだけ与える。  
このスクリプトはコマンドの結果に影響を与えない。  
  
## pushコマンドのフック  
  
クライアントサイド  
1. push コマンドを実行  
2. pre-push スクリプトを実行  
  
リモート側  
1. クライアントからのpushを受信  
2. pre-receiveスクリプトを実行  
3. ブランチ単位でそれぞれ一度ずつupdateスクリプトを実行  
4. push処理が完了  
5. post-receiveスクリプトを実行  
6. post-updateスクリプトを実行  
  
### pre-push  
pushを実行する前にクライアントで実行されるフックスクリプト  
未検証。  
Version 1.8.2 から。  
  
### pre-receive  
pushを受信したらリモート上で実行されるスクリプト。  
このスクリプトは引数を取らない。  
しかし、プッシュされた参照のリストを標準入力から受け取る。  
0以外の終了コードでコマンドを中断する。  
  
### update  
pushを実行した場合update はブランチ単位でそれぞれ一度ずつリモート上で実行される。  
3つの引数をとる。  
第一引数：関連する参照名　例：refs/heads/master  
第二引数：Push前の参照のオブジェクトのSHA  
第三引数：新しい参照のSHA  
  
0以外の終了コードでコマンドを中断する  
  
### post-receive  
pushが完了したらリモート上で一度だけ呼ばれる。  
引数はないが、標準入力からpre-receiveと同じ情報が取得できる。  
このスクリプトはコマンドの結果に影響を与えない。  
  
このスクリプト中の標準出力（echo)の結果はクライアントに返される。  
  
```post-receive
echo  ECHO POST RECEIVE
```  
  
```client
root@debian:/share/testgit/hooktest_clone# git push origin test3:master
Counting objects: 5, done.
Compressing objects: 100% (3/3), done.
Writing objects: 100% (3/3), 279 bytes, done.
Total 3 (delta 2), reused 0 (delta 0)
Unpacking objects: 100% (3/3), done.
remote: ECHO POST RECEIVE <<<<< remoteからのメッセージ
To /share/testgit/hooktest
   a8e54a0..437df47  test3 -> master
root@debian:/share/testgit/hooktest_clone#
```  
  
### post-update  
すべての参照が実行されたあとにリモート上で呼び出される。  
このスクリプトの引数は可変引数となっており、実際に更新された参照(ex. refs/heads/master)が与えられる。  
このスクリプトはコマンドの結果に影響を与えない。  
  
このスクリプト中の標準出力（echo)の結果はクライアントに返される。  
  
# 参考  
[7.3 Git のカスタマイズ - Git フック](http://git-scm.com/book/ja/Git-%E3%81%AE%E3%82%AB%E3%82%B9%E3%82%BF%E3%83%9E%E3%82%A4%E3%82%BA-Git-%E3%83%95%E3%83%83%E3%82%AF "7.3 Git のカスタマイズ - Git フック")  
[githooks(5) Manual Page](http://git-scm.com/docs/githooks "githooks(5) Manual Page")  
