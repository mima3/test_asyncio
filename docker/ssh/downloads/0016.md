# 概要  
この記事ではExcelVBAのソースコードからDoxygenを用いてドキュメントを出力する方法について記述する。  
  
# 前提知識  
## Doxygen とは？  
Doxygenはソースコードからドキュメントを生成することができる。  
http://www.doxygen.jp/  
  
デフォルトではC++、C、Java、Objective-C、Python、IDL (Corba、Microsoft 風)、Fortran、VHDL、PHP、C#などが対象である。  
  
また、INPUT_FILTERを用いることで、上記以外のプログラミング言語のドキュメントを生成することが可能だ。  
  
## VB6用のINPUT_FILTER  
VBAはVB6と仕様がほぼ同じなので、VB6用のINPUT_FILTERを用いることで、ドキュメントの作成が可能である。  
  
InputFilterには、いくつかの種類が存在している。  
  
・だらろぐ 「vbfilter.pyを改造してみた」  
http://r-satsuki.air-nifty.com/blog/2008/02/vbfilter_61f1.html  
  
・VbDoxygen  
https://code.google.com/p/doxy-filter/wiki/VbDoxygen  
  
  
上記の例は、いずれも、Pythonのコードになっており、動作させるにはPythonをインストールする必要がある。  
前者の方が解析の精度はよい。  
  
## InputFilterの使用方法  
ExcelVBAのコードを何らかの手段でエクスポートする。  
そのフォルダに対してDoxygenを実行することにより、ドキュメントを出力することができる。  
InputFilterを用いるには次の設定が必要である。  
  
 **Project:**   
  
|項目名         |設定値|  
|:--------------|:-----|  
|EXTENSION_MAPPING|frm=c<BR>cls=c<BR>bas=c|  
  
※Doxygen1.8.8以降はこのオプションがないと、クラスを認識しません。  
  
 **Input:**   
  
|項目名         |設定値|  
|:--------------|:-----|  
|INPUT_ENCORDING|CP932|  
|FILE_PATTERNS|\*.bas<BR>\*.cls<BR>\*.frm|  
|INPUT_FILTER|フルパスで指定すること<BR>python C:\work\code\VBA\Report\doc\vbfilter.py|  
  
## 制限事項  
VBFilterはVBのコードをC++のコードに変換してDoxygenに渡している。  
この時、関数の中までは、変換していないので、本来Doxygenで作成される関数のコールグラフなどは作成できない。  
つまり、使われていない関数の抽出などには使用できない。  
  
# 改善案  
上記の方法でもExcelVBAのコードをDoxygenのドキュメントとして出力することができる。  
  
しかし、以下の問題がある。  
・VbFilterを動作させるのにPythonをインストールせねばならない。  
・ExcelVBAからファイルの出力せねばならない。  
  
## PythonのコードをExe化する  
Pythonのコードはpy2exeを用いる事でexeに変換することができる。  
これにより、Pythonをインストールしていない端末でもVbFilterを使用できる。  
  
Python-izm exe変換 (py2exe)  
http://www.python-izm.com/contents/external/exe_conversion.shtml  
  
## ExcelVBAからファイルの出力  
VBSを用いてExcelからform,cls,basファイルを出力する方法を説明する  
  
1. 「VBAプロジェクトオブジェクトモデルへのアクセスを信頼する」をONにする。  
(1)開発タブを選択して「マクロのセキュリティ」をクリックする   
(2)「VBAプロジェクトオブジェクトモデルへのアクセスを信頼する」をONにする。  
  
2. 下記のようなVBS使用することでExcel中のソースコードを抽出できる。  
  
```
Option Explicit
Dim xl
Set xl = CreateObject("Excel.Application")
ExportExcelVBA "C:\\Users\\test\\Desktop\\VbaDoxygen\\Sample.xlsm", "C:\\Users\\test\\Desktop\\VbaDoxygen\\output\\src"

'* ExcelからVBAのコードを抽出する
'* @param[in] fileSrc Excelファイルのパス
'* @param[in] dirDst  ソースコードを出力する先
'*
Private Sub ExportExcelVBA(Byval fileSrc, Byval dirDst)
	Dim fso			' FileSystemObject
	Dim fo			' 出力ファイル
	Dim xl			' Excelオブジェクト
	Dim wbk			' ワークブック
	Dim cmp			' VBProject.VBComponents
	

	Dim sFormat		' 拡張子
	Dim fileDst 	' 保存先のファイル

	Set fso = CreateObject("Scripting.FileSystemObject")
	Set xl = CreateObject("Excel.Application")
	Set wbk = xl.Workbooks.Open(fileSrc)

	xl.DisplayAlerts = False

	On Error Resume Next

	For Each cmp In wbk.VBProject.VBComponents
		
		Select Case cmp.Type
			Case 1 
				sFormat = "bas"
			Case 2
				sFormat = "cls"
			case 100
				sFormat = "cls"
			Case 3
				sFormat = "frm"
			Case Else
				sFormat = "unkwon" & cmp.Type
		End Select
		If sFormat <> "" Then
			fileDst = dirDst + "\" + cmp.Name + "." + sFormat
			Set fo = fso.CreateTextFile(fileDst, True)
			
			If cmp.CodeModule.CountOfLines > 0 Then
				fo.WriteLine "Attribute VB_Name = """ & cmp.Name & """"
				fo.WriteLine cmp.CodeModule.Lines(1, cmp.CodeModule.CountOfLines)
			End If
			fo.WriteLine ""
			fo.Close
		End If
	Next

	wbk.Close
	Set wbk = Nothing
	xl.Quit
	Set xl = Nothing
	Set fo = Nothing
	Set fso = Nothing
End Sub
```  
  
もし64bitの端末で32bitのExcelを操作する場合は次のように実行する。  
  
```
C:\Windows\SysWOW64\CScript.exe test.vbs test.vbs
```  
  
それ以外は、下記のようにして実行するとよい。  
  
```
CScript test.vbs
```  
  
## ExcelVBAのDoxygen出力を容易にする方法  
  
![b0232065_3103513.png](/image/2fa6231b-0599-2b39-05be-7f95b730265c.png)  
  
上記の図のように、VBSを用いてCLSファイル、BASファイルなどを抽出する。  
そして、Doxygenの設定ファイルのテンプレートと、VBFilterのExe化したものを使用してDoxygenを実行する。  
  
これを容易にできるようにしたスクリプトは下記からダウンロードできる。  
https://github.com/mima3/VbaDoxygen  
  
__ファイルの説明:__  
  
|ファイル名|説明|  
|:---------|:---|  
|Sample.xlsm|テスト出力用のエクセルファイル|  
|python27.dll|VBFilter.exeを動かすのに必要|  
|w9xpopen.exe|VBFilter.exeを動かすのに必要|  
|vbfilter.exe|VBFilter.pyをpy2exeでExe化したもの|  
|doxyfile_template|Doxygenの設定ファイルのテンプレート。必要に応じて修正すること|  
|ExcelVBADoxygen.vbs|Excelからファイルを抽出してDoxygenを実行するスクリプト|  
  
  
次のように実行すればよい。  
  
```
C:\Windows\SysWOW64\CScript.exe ExcelVBADoxygen.vbs "C:\dev\VbaDoxygen\Sample.xlsm" "C:\dev\VbaDoxygen\output" "C:\Program Files\doxygen\bin\doxygen.exe"
```  
  
 __引数の説明：__  
  
第一引数：Excelのパス  
第二引数：出力フォルダ  
第三引数：doxygen.exeへのフルパス  
  
   
  
  
