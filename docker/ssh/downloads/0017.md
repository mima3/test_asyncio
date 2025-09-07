# Excel VBAコーディング ガイドライン案  
  
ここで記述する内容はあくまでガイドライン、指針の案にすぎない。この規約を守るためにコードを作るのでなく、よいコードを作るためのガイドラインにすぎない。このガイドラインがよいコードを作るのに障害になる場合は、ガイドラインを変えるか、ガイドラインを使用しない。  
  
つまり、このガイドラインは必要に応じて、変更されることがある。  
  
もし、ガイドラインを考える場合、VB6の規約が参考になる。  
[Visual Basic Coding Conventions](http://msdn.microsoft.com/en-us/library/aa240822(VS.60).aspx "Visual Basic Coding Conventions")  
  
  
  
## 宣言について  
### 変数の宣言を強制する  
モジュールの先頭に下記の構文を記述して型の宣言を強制すること。  
  
```vb
Option Explicit
```  
  
この宣言は下記の手順で自動で作成することもできる。  
  
1. 【ツール】→【オプション】  
2. 【編集】のタブを選択  
3. 【変数の宣言を強制する】をチェックする。  
  
#### 理由  
変数名の記述ミスがあった場合、コンパイル時にそのミスを検知できる。  
  
### 暗黙の型は使用しない  
VBAで変数の型を指定しない場合、Variant型として扱われる。  
暗黙型の例：  
  
```vb
Dim A ' Aは Variant型になる
```  
  
また、型変換を行う場合はCStrなどの変換関数を使用して暗黙の型変換はおこなわないこと。  
  
#### 理由  
可読性を上げる  
  
  
### 一行で複数の宣言を行う場合、それぞれに型を明示すること。  
VBAでは一行で複数の型は指定できるが、暗黙の型にならないようにすること。  
  
悪い例：  
  
```vb
Dim UserMin, UserMax As Integer
```  
  
この場合、Variant型のUserMinとInteger型のUserMaxが作成される。  
両方をInteger型にしたい場合、下記のようにすること。  
  
正しい例：  
  
```vb
Dim UserMin As Integer , UserMax As Integer
```  
  
### スコープは明示すること  
関数、変数ともにPublic/Privateを明示すること。  
省略した場合はPublicになるが、省略は禁止する。  
なおGlobalは使用を行わないこと。  
  
#### 理由  
省略時に他のプログラミング言語経験者が混乱しやすいのでスコープは明示する必要がある。  
  
### スコープはなるべく小さくする  
関数内の変数ですむ場合は、それで済ます。  
Private変数ですむ場合はそれで済ます。  
クラスモジュールの変数は、なるべく関数を経由すべきだが、Public変数も認めてもよい。  
標準モジュールのPublic変数は基本的に使用しないこと。  
  
#### 理由  
変更時のリスクを減らすため  
  
  
### 変更の可能性のあるマジックナンバーはConstで宣言すること。  
「よくわからない数字だが、とにかく動く、まるで魔法のようだ」という皮肉から下記のような物をマジックナンバーという。  
  
```vb
    If l > 1024 Then
        MsgBox "上限エラー"
    End If
```  
  
これは下記のようなConstを用いた定数に置き換えること  
  
```vb
    Const MAX_LENGTH As Long = 1024
    If l > MAX_LENGTH Then
        MsgBox "上限エラー"
    End If
```  
  
#### 理由  
可読性をあげること。  
変更が発生した場合の変更を１か所にするため。  
  
この理由のため、直角三角形の公式などでは、変更の可能性もなく、数値の方が可読性が高いので、定数を使用しない。  
  
## 変数について  
### Integer型の使用は避ける  
VB6ならびにVBAのIntger型は16bitである。  
メモリ節約の意図がない限りLong型を使用すること。  
  
#### 理由  
通常32bitOSのIntは32bitとして扱われることが多いため、混乱を抱かせる。  
また、パフォーマンス的にLong型より若干落ちる。この説明は下記を参照のこと。  
[MSDN The Integer, Long, and Byte Data Types](http://msdn.microsoft.com/en-us/library/aa164754%28office.10%29.aspx "MSDN The Integer, Long, and Byte Data Types")  
  
### 変数の初期化を明示的に行う  
VB6やVBAでは規定の初期値があるが、なるべく明示的に初期化を行うこと。  
クラスモジュールを使用した場合は、Class_Initializeにて全てのメンバ変数の初期化を行う。  
  
### 変数の宣言と同時のNewは禁止  
宣言と同時にNewを行った場合：（禁止例）  
  
```vb
Dim reimu As New clsYukkuri
reimu.name = "ゆっくり霊夢"　' ここでインスタンスを生成
```  
  
後でNewを行った場合：（正しい例）  
  
```vb
Dim reimu As clsYukkuri
Set reimu = New clsYukkuri ' ここでインスタンスを生成
reimu.name = "ゆっくり霊夢"
```  
  
以下の理由により、変数宣言と同時のNewは行わない。  
インスタンスの作成のタイミングを制御できなくなり、予期しないバグを発生する可能性がある  
オブジェクトが使用されるたびにインスタンスの有無をチェックするのでオーバーヘッドがある  
  
#### 解説  
変数と同時にNewを行った場合、最初にオブジェクトにアクセスした場合にインスタンスが生成される。  
これは、インスタンスの生存期間がプログラマの意図しないものになる可能性があることを表す。以下のサンプルはその例になる。  
  
```vb
    Dim reimu As New clsYukkuri
    reimu.Name = "れいむ"
    Call reimu.TakeItEasy
    Set reimu = Nothing
    If reimu Is Nothing Then ' Nothingチェックした時点でインスタンスが作成されてしまう
        Debug.Print "削除されている"
    End If
```  
  
また、オブジェクトにアクセスするたびに存在チェックを行うので当然パフォーマンスも落ちる。  
下記の動画で、これらのパフォーマンスについての計測を行っている。  
[オプーナとゆっくりのExcelVBA講座 その11 「クラスモジュール」](http://www.nicovideo.jp/watch/sm20715025 "オプーナとゆっくりのExcelVBA講座 その11 「クラスモジュール」")  
  
#### 参考  
[MSDN クラスの新しいインスタンスを作成する](http://msdn.microsoft.com/ja-jp/library/cc376291.aspx "MSDN クラスの新しいインスタンスを作成する")  
  
[MSDN Dim x As New MyClass](http://msdn.microsoft.com/ja-jp/library/dd297716.aspx  
 "MSDN Dim x As New MyClass")  
  
## 配列について  
### 配列の最大と最小は明示する  
VBAの配列の範囲はCなどと違う。  
  
```vb
Dim buf() As String
ReDim buf(2) As String
```  
  
上記のような指定の場合、Cなどはbuf(0)～(1)までしか使用できない。VBAの場合、デフォルトでは(0)～(2)まで使用できる。  
Cなどと同じ範囲にしたい場合、下記のようにとりうる範囲を明示する。  
  
```vb
Dim buf() As String
ReDim buf(0 To 1) As String
```  
  
また、VBAは下記のコードで配列のデフォルトの最小値を変更できる。  
  
```vb
Option Base 0 ' 添え字の最小値は常時０
```  
  
もし、配列の最小値を明示しない場合、コードを移植した場合に正常に動作しない可能性が発生する。  
  
このように、多言語経験者に余計な混乱を与えないため、Toを用いて配列の最小範囲、最大範囲は明示すること。  
  
### 配列の大きさが頻繁に変更される場合、Collectionを使用する  
Collectionを用いることで、配列を使用するより容易に要素の追加、削除を行うことができる。  
Collectionは配列と異なり、別の型も格納できる。  
  
```vb
Public Sub CollectionTest001()
   Dim cll As New Collection

   Call cll.Add("オプーナ")
   Call cll.Add(CDate("2008/1/3 3:32"))
   Call cll.Add(CLng(23432))
   Call cll.Add("すぺらんかー")

   Dim vData As Variant
   For Each vData In cll
       Debug.Print TypeName(vData) & ":" & vData
   Next
   Set cll = Nothing
End Sub
```  
  
また、以下のように連想配列としても使用可能だ。  
  
```vb
Public Sub CollectionTest002()
   Dim cll As New Collection

   Call cll.Add("りんご", "赤")
   Call cll.Add("みかん", "黄")
   Call cll.Add("ぶどう", "紫")
   Dim vData As Variant
   Debug.Print "(1)-------------------------"
   ' 値の列挙
   For Each vData In cll
       Debug.Print TypeName(vData) & ":" & vData
   Next

   Debug.Print "-------------------------"
   ' キーに赤を指定することによりりんごが表示
   Debug.Print cll.Item("赤")


   Debug.Print "(2)-------------------------"
   ' キーを指定して黄を削除
   Call cll.Remove("黄")
   ' 値の列挙
   For Each vData In cll
       Debug.Print TypeName(vData) & ":" & vData
   Next

   Set cll = Nothing
End Sub
```  
  
なお、Collectionにはキーの存在チェックはサポートしていないので、On Error Gotoでエラートラップするキーの存在チェック用の関数を自前で実装する。  
  
#### 別解  
Scripting.Dictionaryを使用する。  
キーの存在チェックはあるが、参照設定またはCreateObjectが必要なので使用には注意。  
  
## 関数について  
### 関数の引数のキーワードを明示化する  
VBAの関数では参照渡しと値渡しの２種類が存在するので、これを明示すること。  
  
参照渡しの例：  
  
```vb
Sub ShowUser( ByRef User As String )
```  
  
値渡しの例:  
  
```vb
Sub ShowUser( ByVal User As String )
```  
  
#### 理由  
明示を行わない場合、関数の呼び出し方によって参照渡し、値渡しが決定される。 混乱の原因になりやすい。  
  
```vb
dim lVal as long
SubA lVal           '参照渡しになる
SubA(lVal)          '値渡しになる
Call SubA(lVal)     '参照渡しになる
Call SubA((lVal))   '値渡しになる
```  
  
  
参照渡しの場合、引数で与えたパラメータが更新される可能性がある。  
  
```vb
Dim a As String
a = "abc"
ShowUser( a ) ' ByRefの場合
' この時点でaの値は"abc"とは限らない
```  
  
### 構造体や<del>オブジェクト</del>、大きな文字列を関数に渡す場合は参照渡しとして、それ以外は値渡とする  
  
構造体や<del>オブジェクト</del>配列はそもそも参照渡しでしか関数に渡せないので、参照渡しとする。  
また、大きい文字列を渡す場合は参照渡しとする。  
それ以外は、値渡しとする。  
  
#### 理由  
大きなサイズの文字<del>オブジェクト</del>を値渡しで扱うとコピーにリソースを消費してしまうので、参照渡しの方が望ましい。  
それ以外の場合、関数内で引数の変更が行われても呼び出し元に悪影響を与えない値渡しの方が安全である。  
  
## 演算  
### 文字の結合には&演算子を使用する  
文字の結合は+演算子でも可能であるが、&演算子を使用すること。  
  
#### 理由  
+演算子の場合、演算対象に数字が混ざった場合、計算を行ってしまうため。  
  
### Round関数の丸め処理の違いに注意する。  
VBA の Round 関数は、Excel のワークシート関数 Round は挙動が異なる。  
Excel のワークシート関数 Round は、"算術型" の丸め処理を行う。この "算術型" 丸め処理では ".5" は常に切り上げらる。  
  
これに対して VBA の Round 関数は "銀行型" の丸め処理を行う。"銀行型" の丸め処理の場合は ".5" は、結果が偶数になるように丸め処理が行われ、切り上げられることも、切り捨てられることもある。  
  
VBA と Excel の Round 関数の違いは、以下の表のようになる。  
  
|数値|算術型|銀行型|  
|:---|:-----|:-----|  
| 1.5|     2|     2|  
| 2.5|     3|     2|  
| 3.5|     4|     4|  
| 4.5|     5|     4|  
| 5.5|     6|     6|  
| 6.5|     7|     6|  
  
Excel のワークシート関数と一貫性のある Round 関数をVBA内で使用したい場合は、以下の例のように Applicationプロパティを使用する。  
  
```vb
x = Application.Round(y ,0)
```  
  
この例では、y に 8.5 を代入すると 9 を返す  
  
#### 参考  
[丸めを行うカスタム プロシージャを実装する方法](http://support.microsoft.com/kb/196652/ja "丸めを行うカスタム プロシージャを実装する方法")  
[[OFFXP]VBAのRound関数について](http://support.microsoft.com/kb/418216/ja "[OFFXP]VBAのRound関数について")  
  
  
### 剰余の計算でMod演算子とMod数式の結果が違う  
VBAのMod演算子とExcelのサポートしているMod数式の計算結果は異なる。  
  
Mod演算子の例  
  
```vb
Debug.print 10 Mod -3
```  
  
Mod数式の例  
  
```vb
=Mod(10, -3)
```  
  
計算結果：  
  
| A | B |Mod演算子|Mod数式|  
|:--|:--|:--------|:------|  
| 10|  3|        1|      1|  
| 10| -3|        1|     -2|  
|-10|  3|       -1|      2|  
|-10| -3|       -1|     -1|  
  
もしVBAでMod数式と同じ結果が欲しい場合は、下記のようにする。  
  
```
Function fmod(ByVal a As Double, _
                     ByVal b As Double)
    fmod = a - b * Int(a / b)
End Function
```  
  
#### 参考  
[MSDN MOD 関数、Mod 演算子は異なる値を返す](http://support.microsoft.com/kb/141178 "MSDN MOD 関数、Mod 演算子は異なる値を返す")  
  
### 誤差が発生して困る計算にはCurrency型またはDecimalを用いる  
Single型、Double型の演算では誤差が発生する。  
  
浮動小数点の演算で誤差がでる例：  
  
```vb
Public Sub test()
    Dim a As Double
    Dim i As Long
    For i = 1 To 10
        a = a + 0.1
    Next i
    Debug.Assert a = 1 ' NG
End Sub
```  
  
上記のコードを正常に動作させるには次のように変更する  
  
例：通貨型（固定小数点）で計算する  
  
```vb
'Dim a As Double
Dim a As Currency
```  
  
例：Decimal型として扱う  
  
```vb
    Dim a As Variant
    Dim i As Long
    For i = 1 To 10
        a = a + CDec(0.1)
    Next i
    Debug.Assert a = 1
```  
  
### Fix、Int関数では浮動小数点レジスタの精度が影響するので変数に格納してから計算する。  
  
Int,Fix関数は、その実行タイミングで計算結果が変わるので注意を払って使用すること。  
  
```vb
    Dim a As Double
    Dim b As Double
    a = Fix(0.6 * 10)
    Debug.Print a '5
    
    b = 0.6 * 10
    b = Fix(b)
    Debug.Print b '6
```  
  
これはInt,Fix関数のバグなどではなく、浮動小数点レジスタの精度が影響している。  
浮動小数点レジスタの精度がDobule型のものより高いため、計算結果が異なってしまう。  
これをさけるには、FixやIntを実行する前にCDblでキャストするか、変数に代入してから行うと、浮動小数点レジスタの精度の違いによる誤差はでなくなる。  
  
参考：[VBAのFixやIntの計算誤差は浮動小数点レジスタの精度がかかわっている](http://qiita.com/mima_ita/items/cc3973ef68d26d79e9c7 "VBAのFixやIntの計算誤差は浮動小数点レジスタの精度がかかわっている")  
  
## 制御処理  
### 判定文は全ての判定処理が実行されることに注意する  
下記のような判定文があった場合、A()でFalseがかえってもB()も実行される  
  
```vb
IF A("TEST") = True And B("TEST") = True Then
End IF
```  
  
このため、B()が処理時間のかかる処理の場合は以下のようにする。  
  
```vb
IF A("TEST") = True Then
  IF B("TEST") = True
  End If
End IF
```  
  
また、下記のように一行で、インスタンスの有無と、インスタンスの使用を行う判定文を記述した場合アプリケーションエラーとなる。  
  
```vb
IF Not A Is  Nothing And A.Test("TEST") = True Then
End IF
```  
  
### With ～ End With の途中で抜けない  
エラーが発生する可能性があるので、下記のようなコードは禁止  
  
```vb
With hoge
.A = 2
.B = 3
Exit Sub
End With
```  
  
### 終了条件のGOTOは認める  
VBAにはtry-catch-finallyが存在しないので、終了処理の共通化のためのGOTOは認める。  
  
```vb
Dim a as Object
Set a = new Hoge
   If Not a.Test Then
      Goto Finish
   End If
   Call a.Test2

Finish:
  a.Finish()
       Set a = Nothing
```  
  
### 深さを減らすようにする  
タブの深さを減らすような制御構造にする  
  
修正前：  
  
```vb
If A = True Then
  X = False
Else
  For i = 0 To 100
    If Z = 3 Then
      Call Hoge
    End if
  Next i
End If
X = True
```  
  
修正後：  
  
```vb
If A = True Then
  X = False
  Exit Function
End If
For i = 0 To 100
  If Z = 3 Then
    Call Hoge
  End if
Next i
X = True
```  
  
## 環境依存  
なるべく多くの環境で動作することを目指す場合、以下のようなことに注意すること。  
  
### 参照設定やCreateObjectの使用は慎重に行う。  
動作環境が指定できない場合、参照設定で指定されたCOMなどが存在しないで、正常に動作しない場合がある。  
  
動作環境を慎重に考慮する。  
  
### XLAの使用は慎重に行う。  
XLAを用いることで、異なるワークブックで処理の共通化が可能である。  
しかし、特定のXLAが存在しなければ、動作しなくなるということは忘れてはいけない。  
  
### 日本語の変数や関数名は使用しない  
日本語の変数名を宣言できるが、他の地域で使用することを考えた場合、使用してはいけない。  
  
### Date型は日付リテラルで指定する。  
Date型に文字を入力した場合、その解釈は地域によって異なることになる。  
  
```vb
  Dim a As Date
  a = "12/1/1 12:0:0"
  Debug.Print a
```  
  
この実行結果は日本と米国で異なる。  
日本では「2012/1/1 12:00」と解釈するが、米国では「2001/1/12 12:00」と解釈する。  
  
これらを避けるため、日付リテラルとして指定すること。  
以下のように入力すると・・・  
  
```vb
a = #12/1/1 12:0:0#
```  
  
VBEが以下のように変換してくれる。  
  
```vb
a = #12/1/2001 12:00:00 PM#
```  
  
### DLLの呼び出しの際に32bit,64bitプロセスのいづれかであるか注意する。  
Declare 句を用いる事でDLLを使用できるが、32bitか64bitか常に考えて使用すること。  
  
32ビットプロセスのExcelからは64bitのDLLは使用できないし、64ビットプロセスのExcelから32bitのDLLは使用できない。  
  
「Win64」という条件付きコンパイル定数の使用を検討すること。  
  
## よくあるトラブルと対策  
### 実行前に必ず保存する  
VBAはコンパイル時に保存されない。  
プログラムを実行してプロセスが異常終了した場合、その成果物はすべて消える。  
  
そのため、VBAを実行する前は必ず保存をすること。  
  
### 終了ボタンを押してから再実行すること。  
デバッグなどを行っている場合、必ず終了ボタンを押してから再開すること。  
標準モジュールのモジュールレベルの変数はプログラムが中断しただけでは初期化されない。終了ボタンをおして初めて初期化される。  
  
### メモリ不足が頻発する場合は、ワークブックを作り直す  
特別にメモリを使うプログラムでないのにVBAの実行でメモリ不足が頻発する場合、ワークブックを作り直してみる。  
  
Excel2003の時は、行の挿入と削除を繰り返すとゴミデータが蓄積されて上記のような事態に遭遇する場合があった。  
  
  
## Excel VBA固有のガイドライン  
### WorkBookを明示する  
WorkBookの指定方法には下記の方法がある。  
  
```vb
ActiveWorkbook.Sheets(1).Cells(1, 1).Value = "TEST"      ' 1　アクティブのワークブックの操作
Workbooks("Book1").Sheets(1).Cells(1, 1).Value = "TEST"  ' 2　Book1の操作
ThisWorkbook.Sheets(1).Cells(1, 1).Value = "TEST"        ' 3　マクロを含むブックの操作
```  
  
なにも指定しない場合はActiveWorkbookに対して操作を行っている。  
  
ActiveWorkbookにすると、コードの成否はマクロ実行前、またはマクロ実行中のユーザの操作に依存することになる。  
このため、どのワークブックに対して処理を行うか明示しておいた方が望ましい。  
  
### WorkSheetを明示する  
シートの選択を省略した場合、暗黙的にActiveSheetになる。  
  
ユーザーがシートを切り替える可能性があるので、指定のシートを操作させたい場合は、必ずシート名を指定すること。  
  
```vb
Sheet("HOGE").Cells(1,1).Value = 5 ' OK
ActiveSheet.Cells(1,1).Value = 5 ' OK
Cells(1,1).Value = 5 ' NG
```  
  
### 規定のプロパティは使用禁止  
いくつかのオブジェクトでは既定のプロパティが用意されているが、省略は禁止とする。  
  
```vb
Cells(1,1)=5  ' NG
Cells(1,1).Value = 5 ' OK
```  
  
既定のプロパティを省略すると意図した動作にならない場合がある。以下の例では、選択したセルをDebug.Printして、その内容を書き換えようとしている。  
  
```vb
    Dim c As Variant
    For Each c In ActiveSheet.Range(Selection.Address)
        Debug.Print c
        c = "test"
    Next c
```  
  
この例では、Debug.printは表示されるが、セルの内容は書き変わらない。  
  
Valueを明示しておけば、この問題は発生しない  
  
```vb
    Dim c As Variant
    For Each c In ActiveSheet.Range(Selection.Address)
        Debug.Print c.Value
        c.Value = "test"
    Next c
```  
  
### 速度を求める場合、画面の更新を行わない  
画面の更新を中止することにより、計算途中の無駄な描画を省き速度をあげることができる。  
  
画面の更新を中止する例:  
  
```vb
Dim i As Integer, j As Integer
Application.ScreenUpdating = False
For i = 1 To 100
   For j = 1 To 10
       Cells(j + 54, 18).Select
       Selection.Value = j
   Next j
Next i
Application.ScreenUpdating = True
```  
  
### 意味のないSelectを使用しない  
セルの選択は速度に影響を与えるので不要な選択はしない。  
  
Selectを使用している例：  
  
```vb
Dim i As Integer, j As Integer
For i = 1 To 100
   For j = 1 To 10
       Cells(j + 53, 4).Select
       Selection.Value = j
   Next j
Next i
```  
  
Selectを使用しない例：  
  
```vb
Dim k As Integer, l As Integer
For k = 1 To 100
   For l = 1 To 10
       Cells(l + 53, 5).Value = l
   Next l
Next k
```  
  
Selectを使用しない例では5倍以上速度が改善される。  
  
### シートのアクセスに配列を使用するとパフォーマンスは改善する  
ワークシートを直接操作するより、配列を経由した方が速い。ただし、メモリの使用量には注意する。  
  
直接操作の例：  
  
```vb
Dim i As Long, j As Long, buf As Long
For i = 1 To 10000
   For j = 1 To 100
       buf = Cells(i + 80, j + 2).Value
   Next j
Next i
```  
  
配列の例：  
  
```vb
Dim i As Long, j As Long, buf As Long, C() As Variant
Let C = Range("C81:CX10080").Value
For i = 1 To 10000
   For j = 1 To 100
       buf = C(i, j)
   Next j
Next i
```  
  
配列を使用すると14倍以上速度が改善された。  
ただし、配列を使用することにより、メモリを余分に使用する副作用については下記を参照。  
  
[配列を経由したセルの値設定の副作用](http://needtec.exblog.jp/21549244/ "配列を経由したセルの値設定の副作用")  
  
  
  
  
### クリップボードを使用するCopyは使用しない  
Copyには２種類の方法があるが、特にクリップボードを経由する方法は使用禁止。  
直接コピーする方法もなるべく避ける。  
  
クリップボードを使用する例：  
  
```vb
wkSheet.Rows("1:3").Copy
wkSheet.Cells(4, 1).Select
wkSheet.Paste
```  
  
直接コピーする例：  
  
```vb
wkSheet.Rows("1:3").Copy Destination:=Cells(4, 1)
```  
  
クリップボードを経由すると速度に悪影響を与える。  
  
また、直接コピーするコードの場合でもクリップボードの中身はクリアされるため、ユーザの操作に影響を与える。  
