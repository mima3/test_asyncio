このドキュメントは下記のようなGitサーバーの環境を構築するためのメモである。  
  
|種別|OS |  
|:---|:--|  
|サーバー|Debian|  
|クライアント|Windows7|  
  
# Gitのインストール  
  
## Debian側  
  
```
apt-get install git
```  
  
以降,gitコマンドが使用できる。  
  
## Windows側  
MSysGitを下記からインストールする。  
http://msysgit.github.io/  
  
Git Bashがインストールされ、そこからGitコマンドが操作可能。  
![git.png](/image/8173a8da-738e-6b1a-3a82-475b6b531531.png)  
  
# Gitoliteのインストール  
Gitoliteはユーザー管理やアクセス管理を行うためのツールである。  
https://github.com/sitaramc/gitolite  
  
以下にその導入手順を説明する。  
  
1. Debian側でGitoliteを動作させるためのgitユーザを作成する。  
  
```
adduser git
```  
  
２. Gitoliteの管理を行うためのユーザを作成する。クライアント側で公開キーと秘密キーを作成する。GitBashで以下のコマンドを実行する。  
  
```
$ssh-keygen -t rsa
Generating public/private rsa key pair.
Enter file in which to save the key (/c/Users/xxxx/.ssh/id_rsa): admin
Enter passphrase (empty for no passphrase):
Enter same passphrase again:
Your identification has been saved in admin.
Your public key has been saved in admin.pub.
The key fingerprint is:
1f:98:a4:47:16:bd:d9:9f:ea:97:6e:37:50:38:29:dd xxxx@xxxx-PC
```  
  
これによりカレントディレクトリに以下のファイルが作成される。  
  
|名前|説明|  
|:---|:---|  
|admin|秘密キー|  
|admin.pub|公開キー|  
  
３．クライアント側の「.ssh」フォルダを作成する。  
  
下記のフォルダが存在するか、なければ作成する。  
C:\Users\ユーザ名\.ssh  
  
先ほど作成してadmin,admin.pubを.sshフォルダにコピーする。  
  
また以下のようなconfigファイルを作成する  
  
**config**  
```text:config
Host debian
	User git
	Hostname debian
	Port 22
	Identityfile ~/.ssh/admin
```  
  
|名前|説明|  
|:---|:---|  
|Host|接続時に使用する名前|  
|User|ログインユーザ名|  
|Hostname|GitサーバーのIPまたはホスト名|  
|Port|上記のポート番号|  
|Identityfile|秘密鍵へのパス|  
  
４．サーバー側に「git」ユーザーでログインして、同ユーザがアクセスできる場所に２.で作成した公開鍵をコピーする。  
  
５．サーバー側で「git」ユーザでgitoliteのソースコードのダウンロードする。  
  
```
git clone git://github.com/sitaramc/gitolite gitolite-source
```  
  
６．インストール先のフォルダを作成して、インストールを行う  
  
```
mkdir -p $HOME/bin
gitolite-source/install -to $HOME/bin
```  
  
７．「~/.ssh/authorized_keys」 が空であるか、存在しないこと。  
  
８．gitolite のセットアップを行う  
  
```
$HOME/bin/gitolite setup -pk admin.pub

WARNING: /home/git/.ssh/authorized_keys missing; creating a new one
    (this is normal on a brand new install)
```  
  
９．クライアント側でgitolite-adminを取得する  
  
```
$ git clone git@debian:gitolite-admin
Cloning into 'gitolite-admin'...
Enter passphrase for key '/c/Users/xxxx/.ssh/admin':★２で入力したpassphrase を入力する
remote: Counting objects: 39, done.
remote: Compressing objects: 100% (34/34), done.
remote: Total 39 (delta 2), reused 0 (delta 0)
Receiving objects: 100% (39/39), 5.57 KiB | 0 bytes/s, done.
Resolving deltas: 100% (2/2), done.
Checking connectivity... done.

```  
  
gitolite-adminフォルダが作成されている。  
このフォルダには２つフォルダが含まれている。  
  
confフォルダは管理するリポジトリとユーザの情報を設定するファイルが存在する。  
keydirフォルダには、認証対象のユーザの公開鍵を格納する。  
  
ユーザの管理やリポジトリの追加はすべて、このgitolite-adminリポジトリを更新することで行う。  
  
## testingリポジトリの確認  
gitolite-adminの初期設定にはtestingリポジトリが用意されている。  
ここではadminユーザでtestingリポジトリを操作してみる。  
  
１．testingリポジトリの取得  
  
```
$ git clone ssh://debian/testing
Cloning into 'testing'...
Enter passphrase for key '/c/Users/xxx/.ssh/admin':★adminのパスフレーズを入力
warning: You appear to have cloned an empty repository.
Checking connectivity... done.
```  
  
ここでtestingという空のリポジトリが作られる。  
  
２.いつものgitの操作のようにファイルを追加してローカルにコミットする  
  
```
$cd testing
$vim test.txt
$git add test.txt
$git commit -m "first commit"
```  
  
３．サーバー側に反映させる。  
  
```
$ git push origin master
Enter passphrase for key '/c/Users/xxxx/.ssh/admin':★adminのパスフレーズを入力
Counting objects: 3, done.
Writing objects: 100% (3/3), 218 bytes | 0 bytes/s, done.
Total 3 (delta 0), reused 0 (delta 0)
To ssh://debian/testing
 * [new branch]      master -> master
```  
  
# リポジトリの追加とユーザの追加  
ここではリポジトリの追加と、ユーザの追加の方法を説明する。  
  
１．クライアント側でadminの時と同様にaliceというユーザを作成して、その公開鍵をadminを操作する端末にコピーする。  
  
２．admin側でalice.pubをgitolite-admin/keydirにコピーする。  
  
３．admin側でgitolite-admin/conf/gitolite.confを編集する  
  
**gitolite.conf**  
```text:gitolite.conf
repo gitolite-admin
    RW+     =   admin

repo testing
    RW+     =   @all

repo sample
    RW+    =    admin
    RW+    =    alice

```  
  
この例ではsampleというリポジトリを新たに作成して、adminとaliceに読み書きの権限を付与している。  
  
４．admin側でgitolite-adminのローカルリポジトリをコミットする。  
  
```
$git add conf
$git add keydir
$git commit -m "add sample rep"
```  
  
５．サーバー側を更新する  
  
```
$ git push origin master
Enter passphrase for key '/c/Users/xxxx/.ssh/admin':★adminのパスフレーズを入力
```  
  
６．aliceの端末でリポジトリを取得する。  
  
```
git clone ssh://debian/sample
```  
  
# 参考  
ここでは必要最小限の情報しか記述していない。  
さらなる詳細は下記を参考の事。  
  
 __4.8 Git サーバー - Gitolite__   
http://git-scm.com/book/ja/Git-%E3%82%B5%E3%83%BC%E3%83%90%E3%83%BC-Gitolite  
https://github.com/sitaramc/gitolite  
http://gitolite.com/gitolite/#contact  
