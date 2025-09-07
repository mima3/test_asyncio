# CLRProfilerとは？  
CLRProfilerはマネージドアプリケーションの以下の挙動を解析するのに使用するアプリケーションです。  
  
調査が可能な項目には以下のような項目があります。  
・どこのメソッドが、どのオブジェクトをマネージヒープ上に割り当てているか？  
・マネージヒープ上で回収されずに残っているのはどのオブジェクトか？  
・何がオブジェクトを保持しているか？  
・アプリケーションが動作中にガベージコレクタがどのようなことをしているか？  
  
この結果がログファイルに保存され、CLRProfilerを使用することで対応するグラフを確認できます。  
  
後日、ログファイルを確認する場合には保存したログファイルのみで確認できます。シンボリックリンクなどは不要です。  
また、CLRProfilerはコマンドラインよりバッチモードでレポートをテキストファイルにして作成することが可能になっています。  
  
# クイックガイド  
１．CLRProfilerをダウンロードして、解凍します。  
http://clrprofiler.codeplex.com/  
  
２．次にプロファイルを行なう対象のアプリケーションを用意します。  
NET Framework2.0で以下のようなコンソールアプリケーションを作成したものとします。  
  
  
```csharp
using System;
using System.IO;

namespace CLRProfilerTest
{
    class Program
    {
        static void Main(string[] args)
        {
            int start = Environment.TickCount;
            for (int i = 0; i < 1000; i++)
            {
                string s = "";
                for (int j = 0; j < 100; j++)
                {
                    s += "Outer index = ";
                    s += i;
                    s += " Inner index = ";
                    s += j;
                    s += " ";
                }
            }
            Console.WriteLine("Program ran for {0} seconds",
            0.001 * (Environment.TickCount - start));
        }
    }
}
```  
  
３．CLRProfilerを起動します。  
CLRProfilerは２種類の実行ファイルが存在します。これは「32」というフォルダと「64」というフォルダにあります。  
プロファイル対象のアプリケーションが32ビットの場合は「32」というフォルダ中のCLRProfiler.exeを実行してください。もし、64ビットのアプリケーションをプロファイルする場合は「64」フォルダ中のCLRProfiler.exeを実行してください。  
  
![Profile.png](/image/4f54bc0d-8a54-2d6a-8886-bba545b5dd75.png)  
  
４．プロファイルの対象を選択  
すべてのチェックボックスをONにします。  
・Profiling active  
・Allocations  
・Calls  
  
このチェックボックスはプロファイリングを選択的に行うために使用します。多くの場合、プロファイルを行うアプリケーションの速度は劣化します。そういう場合にプロファイル対象の処理を行うまではプロファイリングの対象外にすることができます。  
  
次に、「Target CLR Version: 」を選択します。  
ここではプロファイル対象のCLRを以下のいづれかから選択できます。  
プロファイル対象のCLRを選択できます。以下のいずれかを選択してください。  
  
 __V4 Desktop CLR：__   
.NET Framework4以降を使用しているアプリケーションの場合に選択してください。  
  
 __V4 Core CLR：__   
Core CLRとはSilverlight用にスケーリングされたCLRです。  
  
 __V2 Desktop CLR：__   
.NET Framework3.5以前を使用しているアプリケーションの場合に選択してください。  
Attachなどの機能が一部、使用できなくなります。  
  
今回は. .NET Framework2.0で作成したアプリケーションが対象なので「V2 Desktop CLR」を選択することになります。  
  
つまり、次のようになります。  
![Profile.png](/image/172df9ef-6e5a-53f6-afb0-89986e8581e3.png)  
  
５．プロファイルの対象を選択して実行します。  
  
![Profile.png](/image/a056fe76-9634-bcc2-8ced-dda7d9dca188.png)  
  
「File」メニューの「Profile Application…」を選択するとファイルを選択するダイアログが開きます。  
ここでプロファイル対象のアプリケーションを選択して「開く」ボタンを押してください。  
プロファイルを行った場合、通常の動作より１０～１００倍遅くなることもあります。  
  
またWindows７以前で実行した場合、プロファイル中に下記のメッセージが表示されることがあります。  
  
![Profile.png](/image/0622f25e-a693-9034-df2c-f06e3091974b.png)  
  
これは、WindowsStoreAppのサポートの有無をチェックしており、Windows8より前のOSではサポートしていないため表示されるメッセージです。このメッセージはOKを押して無視してかまいません。  
  
６．Summaryの確認  
プロファイルが終了すると以下のSummaryダイアログが表示されます。  
  
![Profile.png](/image/bd2bfdee-0972-1cc7-11cc-8cb4f7a95a98.png)  
  
このSummaryダイアログから詳細の情報画面に遷移ができます。  
  
CLR Profileのメインダイアログの[File]->[Save Profile As]で今回のプロファイル結果をlogファイルとして保存ができます。保存したlogファイルはCLR Profilerで読み込む事が可能です。  
  
  
# 画面の説明  
## Summary ダイアログ  
プロファイル結果の要約を表示ます。また、CTRL+Vでサマリーの内容をクリップボードに転送します。  
  
|項目|説明|  
|:---|:---|  
|Heap Statistics|このグループではオブジェクトがアロケーションされて、プログラムがどのように保持しているかの統計情報を表示します。それぞれの項目はヒストグラムやコールグラフとして詳細を確認できます。|  
|Allocated bytes:|プログラムがアロケートしたすべてのオブジェクトのサイズです。CLRがプログラムのために割り当てたオブジェクトも含みます。|  
|Relocated bytes：|ガベージコレクタがプログラム実行中に移動したオブジェクトのサイズの合計です。|  
|Final Heap bytes:|プログラムの実行が終了した時にガベージコレクタヒープ中にあるすべてのオブジェクトのサイズです。これはもはや参照されていないが、ガベージコレクタによってクリーンアップされていないオブジェクトを含む場合がある。|  
|Objects finalized|Finalizerが実際に実行されたオブジェクトの数です。|  
|Critical objects finalized:|上記のサブカテゴリーです。.NET Framework 2.0では特別に重要なFinalizerをマークすることができます。たとえば、重要なシステムリソースをカプセル化したオブジェクトなどです。|  
  
### Garbage Collection Statistics  
このグループはプログラム実行中のガベージコレクションの発生数を世代別の統計を表示します。  
  
|項目|説明|  
|:---|:---|  
|Gen0 collections|世代0のガベージコレクションの発生|  
|Gen1 collections|世代1のガベージコレクションの発生|  
|Gen2 collections|世代2のガベージコレクションの発生|  
|induced collections|ガベージコレクタ以外のトリガーで発生。たとえば、アプリケーションから GC.Collectを実行した場合などが当てはまる。|  
  
### Garbage Collector Generation Sizes  
各世代とLarge Object Heapのサイズを表示する。  
これらの数字は実行終了時の状況とは異なる場合があり、プログラムの実行上の平均値であることに注意してください。  
  
### GC Handle Statistics  
作成、削除、生き残っているGCHandleの情報を提供する。  
「Allocation Graph」ボタンで調査が行える。  
  
### Profiling Statistics  
プロファイリング実行自体に関するイベントをまとめたもの。  
  
# コマンドラインからの実行  
コマンドラインから実行することもできる。  
パラメータの詳細は下記で調べることが可能  
  
```
CLRProfiler.exe -?
```  
  
# トラブルシュート  
## 実行するとエラーになる場合  
インターネットからダウンロードしたファイルにはブロックがかかっています。  
すべてのファイルにたいして、プロパティを開き「ブロックの解除」を行います。  
  
## アタッチするとエラーになる場合  
管理者権限で実行してください。  
  
# 参考  
  
How To 情報: CLR プロファイラの使用方法  
http://msdn.microsoft.com/ja-jp/library/ms979205.aspx  
  
CLR プロファイラのフォルダ内にある CLRProfiler.doc  
