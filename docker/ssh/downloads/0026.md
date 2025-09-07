# JsCoverの概要  
JSCoverは、JavaScriptプログラムのコードカバレッジを測定するツールです。  
Webブラウザで実行される前に、JavaScriptコードに計測用のコードを追加することによって機能します。  
  
JsCoverをHTTPサーバーとして起動させて、[QUnit](https://qunitjs.com/)のようにHTMLにテストコードを記載し、JavaScriptのカバレッジを計測することができます。  
  
![image.png](/image/47ed539a-979d-1973-0f5a-874d08fe0558.png)  
  
この際、サーバーと通信する箇所は[sinon](https://sinonjs.org/)などのモックを利用して、ダミーコードを用意するとテストが容易になります。  
  
また下記のようにプロキシサーバーとしてJsCoverを起動することも可能です。  
![image.png](/image/cb821343-5382-bcd8-6b8f-53cd0c73c5a5.png)  
  
詳細は下記を参照してください。  
https://tntim96.github.io/JSCover/manual/manual.xml  
  
  
# チュートリアル  
## 導入方法  
Java1.6以上を取得後、下記からダウンロードを行います。  
https://tntim96.github.io/JSCover/  
  
  
## HTTPサーバーでの実行例  
解凍後の「JSCover-X.X.X\target」中のJSCover-all.jarを下記のようなコマンドで実行することでJsCoverはHTTPサーバーとして起動します。  
  
```
java -jar target/dist/JSCover-all.jar -ws --document-root=doc/example --report-dir=target
```  
  
  
--document-rootにはhtmlやjsファイルが存在するディレクトリのルートパスを指定して、--report-dirにはカバレッジの計測結果が格納されるディレクトリを指定します。  
  
次に、ブラウザを用いて「[http://localhost:8080/jscoverage.html](http://localhost:8080/jscoverage.html)」にアクセスしてJSCover用の画面を表示します。  
  
![image.png](/image/900f5650-7f75-62c2-4ede-a228b7c3f26e.png)  
  
URLの入力ボックスに「[http://localhost:8080/index.html](http://localhost:8080/index.html)」を入力して「Open in frame」ボタンを押下します。  
  
![image.png](/image/76038567-0587-c2f8-690f-ab5071558a9e.png)  
  
これにより、フレーム内にテスト対象のページが表示されました。  
では、「Two」オプションを選択してみましょう。  
  
![image.png](/image/5fb9b4f8-bf0e-c970-b44b-38d92dacdb02.png)  
  
JavaScriptが実行されて画面が更新されます。  
この状態で、カバレッジを確認するには、「Summary」タブをクリックします。  
  
![image.png](/image/d37d3331-3de8-6735-9187-58db24f79d28.png)  
  
「Summary」画面では、File、Coverage、Branch、またはFunctionの列をクリックしてソート順を変更できます。  
カバーされていない行を確認するには「Show missing statements column」チェックボックスにチェックを付けます。  
![image.png](/image/c26ed44b-bf85-9b6f-ce7b-eef3a7582050.png)  
Missingという列が追加されて、カバーされていない行が表示されます。  
  
ソースコードを見るにはFile列のファイル名をクリックするか、Missing列の行番号をクリックします。その結果は以下のようになります。  
![image.png](/image/49cd20e3-a26e-c5e5-8d9d-db53c29d9834.png)  
  
カバーされた行は緑となり、カバーされていない行は赤になります。  
今回は「Two」オプションをクリックした場合の分岐のみが実行されていることがわかります。  
  
また、分岐においてどの条件が実行されたかを確認するには「info」ボタンを押下します。  
9行目をクリックすると以下のようなメッセージボックスが表示されます。  
![image.png](/image/8ade3c98-79bc-3bad-0820-b1116d0c1585.png)  
  
element.id=='radio1'がtrueになる条件をみたしていないと通知されます。  
  
カバレッジの計測結果を外部ファイルに保存するには「Store」タブを押下後、「Store Report」ボタンを押下することで「jscoverage.json」というファイル名で起動時に指定したレポート出力フォルダに出力されます。  
![image.png](/image/f493583c-a442-cf6a-0eaf-a9638dff295a.png)  
  
URLを再読み込みしても、JsCoverのサーバーが起動中はカバレッジは累積して計測されます。  
１から計測しなおしたい場合はJsCoverを再起動してください。  
  
## プロキシサーバーでの実行例  
HTTPサーバーで実行する場合、HTTPサーバーはJsCoverが提供したHTTPサーバになります。  
このためWebServerとのやりとりのコードをスタブに置き換えたりする必要があったり、JSPやASPXをHTMLに置き換えて実行する必要があります。  
  
なるべくテスト用のコードを記載せず、現在、動いている環境を利用して計測するにはJsCoverをプロキシサーバーとして起動します。  
  
```
java -jar C:\tool\JSCover-2.0.8\target\dist\JSCover-all.jar -ws --proxy --port=3128   --report-dir=C:\tool\JSCover-2.0.8\myfolder
```  
  
--proxyを付与することで、プロキシサーバーとして起動します。  
あとはブラウザのプロキシに「127.0.0.1:3128」を指定して手動で動かすか、下記のようにSeleniumで動作させることで、指定のウェブページをJsCoverのプロキシサーバー経由で計測することによりカバレッジが計測できるようになります。  
  
### C#のSeleniumによるカバレッジの取得例  
まずSelenium用のライブラリを取得します。  
![image.png](/image/951353c6-2d55-a9be-4109-8eaf5a5c90ed.png)  
  
以下の例は、指定のURLをプロキシ経由で開いてradio2をクリックしたのちに、カバレッジを取得する例です。  
  
```csharp
using OpenQA.Selenium;
using OpenQA.Selenium.Chrome;
using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Reflection;
using System.Text;
using System.Threading.Tasks;

namespace selenium_test
{
    class Program
    {
        static void Main(string[] args)
        {
            // Chrome
            var option = new ChromeOptions();
            option.Proxy = new Proxy();
            option.Proxy.Kind = ProxyKind.Manual;
            option.Proxy.IsAutoDetect = false;
            option.Proxy.HttpProxy = "127.0.0.1:3128";
            //option.Proxy.SslProxy = "127.0.0.1:3128";

            using (var chrome = new ChromeDriver(Path.GetDirectoryName(Assembly.GetEntryAssembly().Location), option))
            {
                Test(chrome);
                chrome.ExecuteScript("jscoverage_report();");
            }
        }

        static void Test(IWebDriver _webDriver)
        {
            // https://github.com/tntim96/JSCover-samples/blob/master/src/test/java/jscover/webdriver/proxy/WebDriverGeneralProxyTest.java
            _webDriver.Url = "http://tntim96.github.io/JSCover/example/";
            IWebElement element = _webDriver.FindElement(By.Id("radio2"));
            element.Click();
        }
    }
}
```  
  
Seleniumをプロキシ経由で動作させて、テスト用の操作終了後、JavaScriptの「jscoverage_report();」を実行することで、レポート用のディレクトリにJSONファイルが吐き出されます。  
  
## Jenkinsでのカバレッジの表示方法  
JSCoverで計測したレポートはJenkinsに表示させることも可能です。  
その手順は以下のようになります。  
  
(1)JenkinsのプラグインでCoberturaをインストールします。	  
![image.png](/image/9ece2ee8-f1b8-3d5d-9864-f1d5412fc9dc.png)  
  
(2)JSCoverのコマンドを用いて「jscoverage.json」から「cobertura-coverage.xml」を生成します。  
  
```
java -cp JSCover-all.jar jscover.report.Main --format=COBERTURAXML jscoverage.jsonのあるフォルダ JavaScriptのソースのあるフォルダ
```  
  
Jenkinsで使用する場合、「cobertura-coverage.xml」とJavaScriptのあるフォルダはワークスペース上に配置するようにした方がいいでしょう。  
  
(3)Jenkinsのジョブのビルド後イベントで「Cobertura カバレッジ・レポートの集計」を追加する  
![image.png](/image/22bdac05-7051-f49e-d9b4-55e822315f0a.png)  
  
(4)Jenkinsでビルドが成功するとカバレッジのレポートが作成されます。  
![image.png](/image/aa0c9d64-4474-d91d-153f-1e9ce57528d1.png)  
  
![image.png](/image/cfa3f1f3-a1cf-da1b-1384-7cffb5552586.png)  
  
  
![image.png](/image/08a53774-ba0f-4df2-8787-ed15bea3a211.png)  
  
## LocalStorageモード  
JsCover起動時に「--local-storage」を付与することで、ブラウザのローカルストレージにカバレッジ情報を記録することができます。これにより、JSCoverを再起動しても継続してカバレッジを収取しつづけることが期待できます。  
  
具体的にはページの切り替わりのタイミングでローカルストレージの「jscover」キーにカバレッジの情報を記録するような動きになります。  
  
詳細は下記を参考にしてください。  
https://tntim96.github.io/JSCover/manual/manual.xml#localStorage  
  
・  
# まとめ  
JSCoverを使用することでJavaScriptのカバレッジの計測が行えるようになりました。  
また、プロキシモードを用いることで既存のコードをテストコードを追加せずに、そのまま計測することも可能です。  
ただし、内部的には計測用にJavaScriptを置き換えているため、プロダクトコードをそのまま確認したいテストの場合に使用は控えたほうがよいです。（例：速度計測とかする場合）  
  
