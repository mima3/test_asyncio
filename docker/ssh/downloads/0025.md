# まえがき  
JavaScriptで2ファイルのテキストの差分を確認するためのDiff用ライブラリについて調べます。  
  
# difflib  
![image.png](/image/1b4e6a1b-c5f4-8501-d9bf-dbe930f99fbe.png)  
  
**GitHub:**  
https://github.com/cemerick/jsdifflib  
  
**デモサイト**  
http://cemerick.github.io/jsdifflib/demo.html  
  
## サンプルコード  
  
```javascript
<!DOCTYPE html>
<html>
    <head>
        <meta charset="utf-8"/>
<link rel="stylesheet" href="diffview.css">
<script src="difflib.js"></script>
<script src="diffview.js"></script>
<script id="src1" type="sourcecode">
function b() {
  console.log('TESTdddddddddddddddddddddddddddddddddddddddddddddddddddddddddsfafdasdfffffffffffffffffffffffffff0');
  console.log('TEST');
  console.log('TEST1');
}
</script>
<script id="src2" type="sourcecode">
function b() {
  console.log('TEST');
  console.log('TEST2xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx');
  console.log('TEST3');
}
</script>
<!-- End Matomo Code -->
    </head>
    <body>
        <div id="output"></div>
        <script  type="text/javascript">
          const src1 = document.getElementById('src1').innerText;
          const src2 = document.getElementById('src2').innerText;

          var base = difflib.stringAsLines(src1);
          var newtxt = difflib.stringAsLines(src2);
                   
          // create a SequenceMatcher instance that diffs the two sets of lines
          var sm = new difflib.SequenceMatcher(base, newtxt);

          // get the opcodes from the SequenceMatcher instance
          // opcodes is a list of 3-tuples describing what changes should be made to the base text
          // in order to yield the new text
          var opcodes = sm.get_opcodes();
          var contextSize = 0;
          document.getElementById('output').append(diffview.buildView({
              baseTextLines: base,
              newTextLines: newtxt,
              opcodes: opcodes,
              // set the display titles for each resource
              baseTextName: "Base Text",
              newTextName: "New Text",
              contextSize: contextSize,
              viewType: 1 // 0にするとbaseとnewTextが別の列になります
          }));

          
        </script>
    </body>
</html>
```  
  
## 使用感  
・シンプルで使い易いですが、細かい調整はできないようです。（たとえば文字レベルでの差分の表示は現時点でできない）  
・積極的な開発はおこなわれていないようです。  
・BSDライセンスです。  
  
# prettydiff  
![image.png](/image/047a855a-7e76-1592-fff0-99bebb87da27.png)  
  
**GitHub**  
https://github.com/prettydiff/prettydiff/  
  
**デモ**  
https://prettydiff.com/  
  
**ドキュメント**  
https://prettydiff.com/documentation.xhtml  
  
## サンプル  
  
```javascript
<!DOCTYPE html>
<html>
    <head>
        <meta charset="utf-8"/>
<script src="prettydiff/js/browser.js"></script>
<link href="prettydiff/css/index.css" media="all" rel="stylesheet" type="text/css"/>

<script id="src1" type="sourcecode">
function b() {
  console.log('TESTdddddddddddddddddddddddddddddddddddddddddddddddddddddddddsfafdasdfffffffffffffffffffffffffff0');
  console.log('TEST');
  console.log('TEST1');
}
</script>
<script id="src2" type="sourcecode">
function b() {
  console.log('TEST');
  console.log('TEST2xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx');
  console.log('TEST3');
}
</script>
<!-- End Matomo Code -->
    </head>
    <body>
        <div class="white" id="prettydiff"></div>
        <script  type="text/javascript">
          const src1 = document.getElementById('src1').innerText;
          const src2 = document.getElementById('src2').innerText;

// integrate into the browser
let output     = "",
    prettydiff = window.prettydiff,
    options    = window.prettydiff.options;
options.source_label = "修正前";
options.source = src1;
options.diff_label = "修正後";
options.diff = src2;
options.diff_format = "html";

options.mode = "diff";
options.language = "auto";
options.lexer = "text";
options.wrap = 10;
options.diff_view = 'inline'; // 'sidebyside'で別の列で表示
output         = prettydiff();
console.log(output);
          document.getElementById('prettydiff').innerHTML = output;
// You can include the Pretty Diff code in any way that is convenient,
// whether that is using an HTML script tag or concatenating the
// js/browser.js code with your other code.

        </script>
    </body>
</html>
```  
  
## 使用感  
・ブラウザで使用するbrowser.jsは[npmでインストール後、tscコマンドで作成されます](https://github.com/prettydiff/prettydiff#local-install-for-development)  
・[さまざまなオプションがあります](https://github.com/prettydiff/prettydiff/blob/master/options.md)  
・ライセンスは[CC0](https://github.com/prettydiff/prettydiff/blob/master/license)  
  
# mergely  
![image.png](/image/1c7c723c-ebb5-a46c-2747-8289b63e694c.png)  
  
**GitHub**  
https://github.com/wickedest/Mergely  
  
**デモ**  
http://www.mergely.com/  
  
## サンプル  
  
```javascript
<!DOCTYPE html>
<html>
    <head>
        <meta charset="UTF-8" />
        <title>DIFF</title>
<script src="https://ajax.googleapis.com/ajax/libs/jquery/3.2.1/jquery.min.js"></script>
<script src="https://cdnjs.cloudflare.com/ajax/libs/codemirror/5.32.0/codemirror.min.js"></script>
<link rel="stylesheet" media="all" href="https://cdnjs.cloudflare.com/ajax/libs/codemirror/5.32.0/codemirror.css" />
<script src="https://cdnjs.cloudflare.com/ajax/libs/codemirror/5.32.0/addon/search/searchcursor.min.js"></script>
<script src="mergely/libs/mergely.js" type="text/javascript"></script>
<link rel="stylesheet" media="all" href="mergely/libs/mergely.css" />
    </head>

<script id="src1" type="sourcecode">
function b() {
  console.log('TESTdddddddddddddddddddddddddddddddddddddddddddddddddddddddddsfafdasdfffffffffffffffffffffffffff0');
  console.log('TEST');
  console.log('TEST1');
}
</script>
<script id="src2" type="sourcecode">
function b() {
  console.log('TEST');
  console.log('TEST2xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx');
  console.log('TEST3');
}
</script>


<body>
<div class="mergely-full-screen-8">
  <div class="mergely-resizer">
    <div id="mergely"></div>
  </div>
</div>

        <script>
$(document).ready(function () {
	$('#mergely').mergely({
		wrap_lines : true,
		cmsettings: { 
			readOnly: false,
			lineNumbers: true
		},
		lhs: function(setValue) {
			setValue(document.getElementById('src1').innerText);
		},
		rhs: function(setValue) {
			setValue(document.getElementById('src2').innerText);
		}
	});
});
        </script>
</body>

    </body>
</html>
```  
  
## 使用感  
・依存ライブラリが多い(JQuery,codemirror)  
・codemirrorがエディタ用のライブラリなので、修正したテキストの差分がすぐ確認できる  
・ライセンスはGNU LGPL v3.0  
  
# まとめ  
・差分を表示するだけならprettydiffがよさそうです。  
・マージなどの編集が必要ならmergelyになるでしょうが、JQueryに依存しています。  
・2ファイルを入力とするのでなく、diffの結果を入力としてHTML表示するなら[diff2html](https://github.com/rtfpessoa/diff2html)も使えそうです。  
・なお、画像の差分をとるなら[js-imagediff](https://github.com/HumbleSoftware/js-imagediff)が使えそうでした（未検証）  
  
  
# 参考  
**JavaScript based diff utility [closed]**  
https://stackoverflow.com/questions/3053587/javascript-based-diff-utility  
