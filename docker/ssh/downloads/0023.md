# はじめに  
最近ますます、以下の記事のようにIE死すべき慈悲はないという時代になってまいりました。  
  
**新Edgeブラウザ登場に伴うIEサポート終了についてチームのコンセンサスを得るためのシンプルなテンプレ**  
https://qiita.com/uupaa/items/ad1f0f64191dbec56889  
  
今回はIEが本当に死んだ場合、なにが困るかを考えてみようと思います。  
  
  
# 検証環境  
・Windows10  
・Edge Beta Version 77.0.235.25 (Official build) beta (64-bit)  
　※アンインストールも再インストールもさせないEdgeですが、Beta版は上書きでインストールしていないので、飽きたらBeta版をアンインストールすることで元にもどせました。  
・VisualStudio2019  
  
# 検討項目  
  
 - 外部からの自動操作  
 - ClickOnceの実行  
 - WindowsFormへの埋め込み  
 - ShowModalDialogの使用  
 - ActiveXの使用  
 - XBAPの使用  
  
## 外部からの自動操作  
ブラウザを外部から自動操作する際に大きく3つの方法が考えられると思います。  
  
・Seleniumで自動実行する  
・InternetExploreのCOMを利用する  
・UiPathなどのRPAツールを使う  
  
### Seleniumで自動実行する  
すでに新Edge用のWebDriverが公開されているようなので、おそらくは問題なく移行できると思います。  
https://developer.microsoft.com/en-us/microsoft-edge/tools/webdriver/  
  
### InternetExploreのCOMを使う。  
これは一切の外部ツールを使わずにブラウザを自動操作できる方法でした。  
仮に旧Edgeだったとしても以下の方法で無理やりInternet Explorer_Serverを取得して動かすことが可能でした。  
  
**VBAでInternetExplore上のJavaScriptを無理やり動かすよ！**  
https://github.com/mima3/note/blob/master/VBAでInternetExplore上のJavaScriptを無理やり動かすよ！.md  
  
当然、新Edgeでは動作しません。  
**すなわち、ダウンロード禁止縛り環境ではブラウザの自動操作はできなくなります。**  
  
#### （補足：UiAutomationで代替できないか？）  
Inspectで新EdgeのGoogle開いているページを解析したところ以下のようになります。  
![image.png](/image/9fef1e27-f084-28c5-fcf0-760302a3a7f2.png)  
ControlTypeがちゃんと設定されているのでボタン押下ぐらいはUiAutomationで操作可能かもしれません。  
ただ、HTMLの構造の解析は難しいと思うので基本、外部ツールなしで自動操作は厳しいと思います。  
  
### UiPathなどのRPAツール  
UiPathで自動操作をする場合、Chromeの拡張機能をインストールしていたと思います。  
この拡張機能とUiPathが連携してブラウザの自動操作を行っています。  
  
実は新EdgeになるとChromeの拡張がそのまま使えるようなので、恐らく、ChromeをサポートしているRPAツールは対応してもらえる可能性が高いと思います。  
ユーザ側の対応作業としてはアクティビティの置き換えと各RPA端末に拡張機能をインストールするという工数くらいでしょう。  
  
**新Microsoft EdgeはChrome拡張機能をサポート - 阿久津良和のWindows Weekly Report**  
https://news.mynavi.jp/article/20190402-800458/  
  
  
## ClickOnceの実行  
ClickOnceは.NETで作成したバイナリをWebに配置しておき、ブラウザがクリックすると、配布、実行してくれるという仕組みです。  
この機能はIE11,ならびに旧Edgeで動作します。  
  
残念ながら、新EdgeについてはEdge Beta Version 77の段階では正常に実行できませんでした。  
  
ただし、下記のブログを見る限り2019 10月に対応するような旨がかかれているので将来的には解消されそうです。  
  
**[What we're hearing from you](https://techcommunity.microsoft.com/t5/Discussions/What-we-re-hearing-from-you/m-p/811931?ranMID=24542&ranEAID=je6NUbpObpQ&ranSiteID=je6NUbpObpQ-IjeaeLYGG3YAGIIEGxxSNg&epi=je6NUbpObpQ-IjeaeLYGG3YAGIIEGxxSNg&irgwc=1&OCID=AID2000142_aff_7593_1243925&tduid=(ir__19oa1xfwk0kfrlkrkk0sohzx0m2xgxdntqhm6a1a00)(7593)(1243925)(je6NUbpObpQ-IjeaeLYGG3YAGIIEGxxSNg)()&irclickid=_19oa1xfwk0kfrlkrkk0sohzx0m2xgxdntqhm6a1a00)**  
  
>Planned to be addressed in the Canary channel in October 2019:  
>  
> - Inking on PDFs  
> - When you sign-in to the browser, your sign-in profile picture will accurately be kept up to date.  
> - When you have more than one profile, better handling for opening links and attachments in the appropriate profile.  
> - An option to set your own photos as the background image on the New Tab Page  
> - Enable search in the extensions store  
> - A bug fix for users who receive an “Administrator Mode Detected” notification (advising them to close and relaunch the browser in non-administrator mode) each time they launch Edge  
> - ClickOnce deployment of Windows applications from web pages  
   
## WindowsFormへの埋め込み  
IE11ならびに旧EdgeではMicrosoft.Toolkit.Wpf.UI.Controls.WebView"や"Microsoft.Toolkit.Forms.UI.Controls.WebView"を使用することで以下のように.NETの画面にブラウザを埋め込めます。  
  
![image.png](/image/aa20e37f-20dc-2644-48c2-0e743cd4de85.png)  
  
以下のページによると最近まではIEのみでEdgeは埋め込めなかったようです。  
  
**WPFやWindowsフォームでEdgeのWebViewを使うには？［Windows 10 1803以降］**  
https://www.atmarkit.co.jp/ait/articles/1807/04/news017.html#winform  
  
今後、新Edgeになったとき、この機能が使えるかどうか、経過を見る必要があるでしょう。  
  
## showModalDialogの使用  
IE11では呼び出し元の画面を触らせないように新規Windowを表示するため、showModalDialogがjavascriptから使用できていました。  
しかし、時代はかわり、この機能は非推奨となり、旧Edgeでもサポートしないと明言しています。  
  
**"showModalDialog" is not working in IE Edge**  
https://developer.microsoft.com/en-us/microsoft-edge/platform/issues/18235925/  
  
  
何らかの方法に置き換える必要があり,StackOverflowでは以下のようなやり方が紹介されています。  
  
**showModalDialog alternative?**  
https://stackoverflow.com/questions/24400388/showmodaldialog-alternative  
  
どう対応するかと、画面数しだいですが、地味にテスト工数がかなりかかると思います。  
  
## ActiveXの使用  
ブラウザからファイルやレジストリの操作をActiveXで行っているデンジャラスなシステムもありますが、それらは動かなくなります。  
  
基本、ブラウザでそんな物騒な操作をさせていることがおかしいわけなので、これを機に設計を見直したほうがいいと思いますが、どうしても、これを置き換えるというなら、拡張機能を作ってローカルのEXEと通信する方法が考えられます。  
  
### Chromeの拡張機能であるNative Messageを使用した回避案  
Chromeの拡張機能、また、それが動作する新EdgeではNative Messageという機能を使用して端末上のEXEと通信をすることが可能です。  
  
**Native Messaging**  
https://developer.chrome.com/apps/nativeMessaging  
  
**Chrome Native Messaging Example**  
https://medium.com/@svanas/chrome-native-messaging-example-5cf8f91cdce6  
  
**C# native host with Chrome Native Messaging**  
https://stackoverflow.com/questions/30880709/c-sharp-native-host-with-chrome-native-messaging  
  
端末上のEXEとブラウザ上からやり取りできるのであれば、ActiveXと勝るとも劣らない無茶なことが可能です。  
  
今回は以下のようなEXEと通信するChromeの拡張機能が新IEでも使用できるか検証しました。  
  
![image.png](/image/58f825b0-acc2-48f0-15a7-732750ebb27e.png)  
  
  
ContentScriptは以下のようになります。  
ページ読み込み時にボタンを作成し、このボタンが動作したらbackgroundにメッセージを送信します。  
また、backgroundからのメッセージをonMessageで処理します。  
  
backgroundの処理は以下のようになります。  
  
**content.js**  
```javascript:content.js
window.addEventListener("load", function(event) {
  var button=document.createElement("button");
  button.innerText = "ボタン";
  button.id = "btnExtContents";
  document.body.appendChild(button); 
  button.addEventListener("click", function() {
    window.sendMessage('click');
  });
}, false);

window.sendMessage = function sendMessage(message) {
  chrome.runtime.sendMessage(message); 
};

chrome.runtime.onMessage.addListener(function(message) {
  console.log('onMessage...');
  console.log(message);
  alert(JSON.stringify(message));
});
```  
  
window.sendMessageという関数をここで定義していますが、元のページのJavaScriptからは実行できませんでした。  
そのため、元ページでは以下のようにクリックイベントを実行する必要があります。  
  
```javascript
document.getElementById('btnExtContents').click();
```  
  
引数が必要ならば適当な要素に格納しておくといいでしょう。  
  
  
backgroundのスクリプトは下記のようになります。  
content_scriptsからのメッセージをNativeメッセージでEXEに渡し、  
Exeから受信したメッセージをcontent_scriptsに渡します。  
  
  
**background.js**  
```javascript:background.js

var port = null;
chrome.runtime.onMessage.addListener(function(message, sender) {
  console.log(message);
  if (!port) {
    var hostName = "com.google.chrome.example.echo";
    port = chrome.runtime.connectNative(hostName);
    port.onMessage.addListener( function (rcv) {
      console.log('onNativeMessage');
      console.log(rcv);
      chrome.tabs.sendMessage(sender.tab.id ,rcv);
    });
    port.onDisconnect.addListener( function () {
      console.log('onDisconnect');
      port = null;
    });
  }
  port.postMessage({"text": message});
});

```  
  
EXEと拡張機能の通信は標準入力と標準出力で行います。  
先頭4バイトに送受信のバイト数を入力し、その後に文字列をJSON形式で格納します。  
EXEの実装はどのプログラミング言語でおこなってもいいですが、JSONの取り扱いと、バイナリの取り扱いが楽なものを選択した方がよいでしょう。  
  
  
ChromeとEdge Beta Version 77.0.235.25 でローカルのExeと通信できた拡張機能のサンプルを以下に置きます。  
https://github.com/mima3/hello_sample  
  
### WebScoketを使用した回避案  
下記の方法でもネイティブアプリと通信できそうです。  
  
**Webアプリの限界を超える方法**  
https://qiita.com/tekka/items/1bf440ccd50bb4171886  
  
**Webアプリの限界を超える方法(セキュリティ編)～ActiveXを葬る～**  
https://qiita.com/tekka/items/d9f6fd2e30c1f778b5aa  
  
ようするにユーザーのマシンに立てたWebSocketサーバーと通信してしまおうという考えです。  
  
  
## XBAPの使用  
IEではXBAPを使用することでブラウザに.NETで作った画面を埋め込むことができました。  
またセキュリティの設定によってはファイル操作でもレジストリの操作でもできました。  
  
![image.png](/image/4f5c73df-1488-964c-b30b-283877af4cf8.png)  
  
これに関しては旧Edgeの時点でXBAPのサポートはしないと言い切っています。  
https://stackoverflow.com/questions/31895766/xbap-support-in-ie-edge  
  
代替はないとおもいます。  
ClickOnceかブラウザいずれかに倒して実装するかなさそうです…いずれにせよ完全に作り直しだと思いますが。  
  
  
## HTAの使用  
[HTA](https://docs.microsoft.com/ja-jp/previous-versions/technical-document/ms536496(v=vs.85)?redirectedfrom=MSDN)を使用するとInternetExploreの機能を利用してスタンドアローンのGUIを作成することができます。（Electronのような感じ）  
  
![image.png](/image/7f0c29ca-c52c-d13e-a3f5-ac960a9f0e37.png)  
  
**test.hta**  
```html:test.hta
<html>
<head>
 <title>ボタンをおすのです</title>
</title>
<body>
  <input type="button" name="buttonA" value="ボタン" onClick="buttonA()"/>

<script language="VBScript">
  sub buttonA
    MsgBox "わっふる"
  End Sub

</script>
</body>
</html>
```  
  
IEが亡くなった場合、この機能も必然的につかえなくなるので、拡張子htaで画面を開いている場合は改修が必要になると考えられます。  
  
# IEモードによる延命  
ここまではIEが完全に死んだ場合を考えてみましたが、慈悲深いマイクロソフトはIEモードという延命処置を用意してくれています。  
https://docs.microsoft.com/en-us/deployedge/edge-ie-mode  
  
  
このモードになることでActiveXすらもサポートしますが、**IE11またはMicrosoft Edge F12開発者ツールをサポートしない**ので、開発時にたぶん苦労します。  
  
~~…Console.logすら使えないとこで、うまく実装できるイメージがまったくわかん。~~  
  
  
# まとめ  
どういう対応になっても地獄しかみえないので心当たりのある方は、震えて眠りましょう。  
