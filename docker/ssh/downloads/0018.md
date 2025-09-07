# 目的  
この記事ではExcelVBAでバージョン管理を行う方法について説明する。  
以下のようにWinMergeの差分機能を用いることで、VBAの差分を表示することが可能である。  
![b0232065_21525328.png](/image/d7098654-2d42-05ac-863c-4ae61f493979.png)  
  
  
# 手順  
## WinMergeの準備  
  
1. [WinMerge](http://www.geocities.co.jp/SiliconValley-SanJose/8165/winmerge.html "WinMerge")のダウンロードを行う  
  
2. ダウンロードページより「Excelからテキストへの変換プラグイン」のExcelToText.sctをWinMergeのMergePluginsフォルダにコピーする。  
例："C:\Program Files\WinMerge\MergePlugins"  
3. WinMergeを起動してプラグインの自動展開を選択する  
![b0232065_21443344.png](/image/8b34a3c6-1464-f828-1b71-7c4e588dfc53.png)  
  
## Excelの準備  
### Excel 2003の場合  
1. Excelを起動  
2. [ツール]→[マクロ]→[セキュリティ]  
3. [信頼できる発行元タブ]を選択する。  
4. [Visual Basic プロジェクトへのアクセスを信頼する]にチェックを付与する。   
![b0232065_21472719.png](/image/1437da5a-e5ad-e138-be42-3bbbb1586913.png)  
  
### Excel 2010の場合  
1. Excelを起動  
2. 開発タブを選択して「マクロのセキュリティ」をクリックする  
![b0232065_21482034.png](/image/5dca0fea-3aa2-25f8-346f-b431716677aa.png)  
3. 「VBAプロジェクトオブジェクトモデルへのアクセスを信頼する」をONにする。  
![b0232065_21504100.png](/image/43420a03-d6da-e2be-678e-1bc71e1c7eba.png)  
  
## 構成管理ソフトの準備  
差分を外部プログラムを用いて行うようにする。  
  
### TrotoiseSVNの準備  
1. [TrotoiseSVN]→[設定]を表示する  
2. 差分ビュワーを選択してWinMergeを選択する。  
![b0232065_2155966.png](/image/69a2c992-390b-36b8-577e-9553eec3ce02.png)  
設定例：  
<code>  
C:\Program Files\WinMerge\WinMergeU.exe -e -x -ub -dl %bname -dr %yname %base %mine  
</code>  
  
# 別解  
Ariawaseを用いてファイルをテキストファイルに変更する。  
https://github.com/vbaidiot/Ariawase  
http://igeta-diary.blogspot.jp/2014/03/what-is-vbac.html  
  
build.batはsrcフォルダの内容をインポートしてXLSファイルを更新する。  
  
以下のコマンドでXLSの内容をエクスポートしてソースをテキストとして出力作成する  
  
```
cscript //nologo vbac.wsf decombine
```  
  
構成管理にテキストとしてソースコードを格納できることと、複数人が同時に１ファイルのソースを修正することができるのは強み。  
