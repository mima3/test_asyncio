本ドキュメントではGitPrepを使用してプライベートなGitHubのようなサイトを構築する方法について記述する。  
  
# 環境  
Debian7  
Perl v5.14.2  
  
# インストール方法  
１．下記のサイトからZIPをダウンロード  
https://github.com/yuki-kimoto/gitprep  
  
２．Debianでフォルダを展開して、下記のシェルスクリプトを実行  
  
```
./setup.sh
```  
  
このときのログを次のコマンドで確認できる。  
  
```
vi setup/build.log
```  
  
今回は下記の項目がエラーとなった。  
  
```
FAIL Failed to fetch distribution Validator-Custom-0.22
FAIL Failed to fetch distribution Params-Check-0.36
FAIL Failed to fetch distribution Module-Load-Conditional-0.54
FAIL Failed to download http://backpan.perl.org/authors/id/D/DA/DAGOLDEN/Perl-OSType-1.003.tar.gz
FAIL Failed to fetch distribution IPC-Cmd-0.80
```  
  
インストールに失敗したモジュールを自前でインストールする。  
  
```
 perl cpanm Validator::Custom
 perl cpanm Params::Check
 perl cpanm Module::Load::Conditional
 perl cpanm Perl::OSType
 perl cpanm IPC::Cmd
```  
  
３．gitprepを起動する  
  
```
./gitprep
```  
  
以降、以下のようなURLでアクセスが可能になる。  
http://debian:10020/  
  
なお、WebServerをとめるには下記のコマンドを実行する。  
  
```
./gitprep --stop
```  
  
# gitprepの使い方  
## 管理ユーザの登録  
１．初回に下記のアドレスにアクセスすると管理用のユーザのパスワードの登録を求められる。  
  
http://debian:10020/  
![git2.png](/image/e1fcd299-bea2-e488-a48d-9b4d496d607c.png)  
  
  
２．管理ユーザの登録に成功すると次のようなメッセージが表示される。  
  
![git5.png](/image/847a4e4b-ee29-50c9-767d-1c6133028f1c.png)  
  
## 通常ユーザの登録  
１．画面右上の「Sign in」を入力して今登録した管理ユーザでログインする。  
管理ユーザではユーザの作成は行えるが、リポジトリの作成は行えない。  
  
２．Usersを押すとユーザを登録する画面に遷移できる。  
![git5.png](/image/13770656-784e-10e8-7722-283c58ea45aa.png)  
  
![git5.png](/image/1caea9a2-5c8f-ac72-de48-cef46843f4d1.png)  
  
３．ユーザ登録画面で下記のように「alice」と「Joe」を追加したものとする。  
![git5.png](/image/0f38de02-336f-8cc3-1309-f4d94013ee3d.png)  
  
以降、alice,Joeでログインが可能になる。  
  
## リポジトリの追加  
１．aliceでログインをする。  
  
![git5.png](/image/e5f73bb1-351f-31c9-5a48-a2d8c6056554.png)  
  
管理ユーザとことなり、「Create Repogitory」のメニューが追加されていることがわかる。  
  
２．必要な情報を入力して「testproject」を登録する。  
![git4.png](/image/6d36d6d8-ccd2-c101-4d15-c6150d8b233d.png)  
  
３．作成に成功すると、リポジトリ―の操作例が表示される。  
![git5.png](/image/824fa795-4d9c-8857-fa8c-0c33c1ed33bc.png)  
  
また、aliceのホームページには今追加した  
testprojectが表示される。  
![git4.png](/image/20767fc0-f752-b2a2-0e29-94c69c87ad78.png)  
  
４．クライアントで作成したtestprojectを操作してみる。  
  
```
# リポジトリを作成する
$ mkdir testproject
$ cd testproject
$ git init

# READMEの追加
$ vim README
// なんらかのファイルを作成

$ git add README
warning: CRLF will be replaced by LF in README.
The file will have its original line endings in your working directory.

# ファイルをコミット
$ git commit -m "first commit"
[master (root-commit) 4802d3e] first commit
warning: CRLF will be replaced by LF in README.
The file will have its original line endings in your working directory.
 1 file changed, 2 insertions(+)
 create mode 100644 README

# リモートサーバーの登録
$ git remote add origin http://debian:10020/alice/testproject.git
XXX@XXXX-PC ~/git/testproject (master)

# リモートサーバーにpush
$ git push -u origin master
Username for 'http://debian:10020': alice
Password for 'http://alice@debian:10020': <<< aliceのパスワード
Counting objects: 3, done.
Writing objects: 100% (3/3), 216 bytes | 0 bytes/s, done.
Total 3 (delta 0), reused 0 (delta 0)
To http://debian:10020/alice/testproject.git
 * [new branch]      master -> master
Branch master set up to track remote branch master from origin.
```  
  
## リポジトリに作業者を追加する。  
１．aliceでtestprojectを開いて、「Settings」ボタンを押す  
![git4.png](/image/3ff51d0a-0b9d-f8e5-c1dd-47846702b3cd.png)  
  
２．Collaboratorsを押下する。  
![git4.png](/image/20c3a7e9-7388-a90c-b31d-b49926bc3a0d.png)  
  
３．「joe」を入力して追加する。  
![git4.png](/image/2b55370c-99c8-a0b8-9118-1aa425bff7f5.png)  
  
４．以降「joe」がtestprojectへの操作を行える。  
  
```
$ git clone http://debian:10020/alice/testproject.git
$ cd testproject
$ vim README
$ git add README
$ git commit -m "Joe Commit"
$ git push -u origin master
Username for 'http://debian:10020': joe
Password for 'http://joe@debian:10020': << joeのパスワード
```  
  
  
# その他留意点  
・gitprep/gitprep.confでタイムゾーンやgitのパスなどの各種項目を変更できる。  
  
・adminのパスワードを忘れたり、変更したくなったら、gitprep/gitprep.confのreset_password=1を設定するといい。  
  
・apache経由でもできるらしいが、以下のエラーが出たので諦めた  
https://github.com/yuki-kimoto/gitprep/issues/52  
  
# 参考  
http://d.hatena.ne.jp/perlcodesample/20130421/1366536119  
  
https://github.com/yuki-kimoto/gitprep  
