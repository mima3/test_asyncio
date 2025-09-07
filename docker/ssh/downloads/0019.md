# はじめに  
2019/11時点でGithubにある[WYSIWYG](https://github.com/topics/wysiwyg?o=desc&s=stars)タグでスターが多いライブラリを調べてみます。  
  
# Quill  
## 概要  
**Github**  
https://github.com/quilljs/quill  
  
**Demo**  
https://quilljs.com/  
![image.png](/image/43809db5-3c34-c035-6a5b-8bbe758cdb93.png)  
  
・テーブルの作成はできないようです(ver2.x用にテーブル追加のプラグインはある）  
・クリップボードを経由して画像のアップロードが可能です。  
・[highlight.jsを使用してコードブロックのハイライトが可能のようです](https://quilljs.com/docs/modules/syntax/)  
  
**対象ブラウザ**  
![image.png](/image/db7e19c5-f96b-ac27-2fb6-2a388bcb840a.png)  
IEは非推奨のようです。  
  
**ライセンス**  
BSD 3-clause  
  
## サンプル  
### 1.3.7のサンプル  
  
```html
<!doctype html>
<html>
  <head>
    <meta charset="utf-8">
    <title>Test Quill</title>
    <!-- highlight.js を使う場合はquillの前に参照する-->
    <link rel="stylesheet"
          href="http://cdn.jsdelivr.net/gh/highlightjs/cdn-release@9.16.2/build/styles/default.min.css">
    <script src="http://cdn.jsdelivr.net/gh/highlightjs/cdn-release@9.16.2/build/highlight.min.js"></script>

    <link href="https://cdn.quilljs.com/1.3.7/quill.snow.css" rel="stylesheet">
    <script src="https://cdn.quilljs.com/1.3.7/quill.js"></script>



  </head>
  <body>


<!-- Create the editor container -->
<div id="editor">
  <p>Hello World!</p>
</div>
<button id="btnContent">コンテンツ取得</button>
<button id="btnImage">イメージの挿入</button>
<button id="btnDisable">編集可能/不可能</button>

<script>
var Delta = Quill.import('delta');
const quill = new Quill('#editor', {
  theme: 'snow',
  modules: {
    syntax : true,              // Include syntax module
    // https://quilljs.com/docs/modules/toolbar/
    toolbar : [
      ['bold', 'italic', 'underline', 'strike'],
      [{ 'color': [] }, { 'background': [] }], 
      ['link', 'image'] ,
      ['code-block']
    ]
  }
});

document.getElementById('btnContent').addEventListener('click', function() {
  console.log(quill.getContents());
});

document.getElementById('btnImage').addEventListener('click', function() {
  // このあたりを工夫すればクリップボードからの画像貼り付け等ができそう・・
  console.log(quill.getSelection(true).index);
  quill.insertEmbed(quill.getSelection(true).index, 'image', 'https://www.google.com/images/branding/googlelogo/1x/googlelogo_color_272x92dp.png');
});

let enableEditor = false;
document.getElementById('btnDisable').addEventListener('click', function() {
  quill.enable(enableEditor);
  enableEditor = !enableEditor;
  console.log(enableEditor);
});


/**
 * ペーストのイベント追加例
 */
quill.root.addEventListener("paste", function (t) {
  console.log('paste');
  console.log(t);
  return true;
} , false);


</script>
  </body>
</html>
```  
  
### 拡張モジュール  
#### 画像の貼り付けについて  
quill-image-drop-and-paste  
https://github.com/chenjuneking/quill-image-drop-and-paste  
  
![image.png](/image/97ba3475-efe9-e837-110f-942969bb686f.png)  
  
quill-image-drop-and-pasteはどうも以下のように修正しないと動作しないようです。  
export.ImageDropAndPasteを使用しているが、設定していないので替わりにImageDropAndPasteを設定する。  
  
```js
(function(){var exports={};
"use strict";Object.defineProperty(exports,"__esModule",{value:true});var _createClass=function(){function e(e,t){for(var a=0;a<t.length;a++){var n=t[a];n.enumerable=n.enumerable||false;n.configurable=true;if("value"in n)n.writable=true;Object.defineProperty(e,n.key,n)}}return function(t,a,n){if(a)e(t.prototype,a);if(n)e(t,n);return t}}();function _classCallCheck(e,t){if(!(e instanceof t)){throw new TypeError("Cannot call a class as a function")}}var ImageDropAndPaste=function(){function e(t){var a=arguments.length>1&&arguments[1]!==undefined?arguments[1]:{};_classCallCheck(this,e);this.quill=t;this.options=a;this.handleDrop=this.handleDrop.bind(this);this.handlePaste=this.handlePaste.bind(this);this.quill.root.addEventListener("drop",this.handleDrop,false);this.quill.root.addEventListener("paste",this.handlePaste,false)}_createClass(e,[{key:"handleDrop",value:function e(t){var a=this;t.preventDefault();if(t.dataTransfer&&t.dataTransfer.files&&t.dataTransfer.files.length){if(document.caretRangeFromPoint){var n=document.getSelection();var i=document.caretRangeFromPoint(t.clientX,t.clientY);if(n&&i){n.setBaseAndExtent(i.startContainer,i.startOffset,i.startContainer,i.startOffset)}}this.readFiles(t.dataTransfer.files,function(e,t){if(typeof a.options.handler==="function"){a.options.handler(e,t)}else{a.insert.call(a,e,t)}},t)}}},{key:"handlePaste",value:function e(t){var a=this;if(t.clipboardData&&t.clipboardData.items&&t.clipboardData.items.length){this.readFiles(t.clipboardData.items,function(e,t){if(typeof a.options.handler==="function"){a.options.handler(e,t)}else{a.insert(e,t)}},t)}}},{key:"readFiles",value:function e(t,a,n){[].forEach.call(t,function(e){var t=e.type;if(!t.match(/^image\/(gif|jpe?g|a?png|svg|webp|bmp)/i))return;n.preventDefault();var i=new FileReader;i.onload=function(e){a(e.target.result,t)};var r=e.getAsFile?e.getAsFile():e;if(r instanceof Blob)i.readAsDataURL(r)})}},{key:"insert",value:function e(t,a){var n=(this.quill.getSelection()||{}).index||this.quill.getLength();this.quill.insertEmbed(n,"image",t,"user")}}]);return e}();exports.default=ImageDropAndPaste;
window.Quill.register('modules/imageDropAndPaste',ImageDropAndPaste)})(); // export.ImageDropAndPaste->ImageDropAndPaste

```  
  
```html
<!doctype html>
<html>
  <head>
    <meta charset="utf-8">
    <title>Test Quill</title>
    <link href="https://cdn.quilljs.com/1.3.7/quill.snow.css" rel="stylesheet">
    <script src="https://cdn.quilljs.com/1.3.7/quill.js"></script>
    
    <script src="quill-image-drop-and-paste-master/quill-image-drop-and-paste.min.js" type="text/javascript"></script>
    
  </head>
  <body>
<button id="btnContent">コンテンツ取得</button>
<br>
クリップボードからイメージをbase64で張り付けている。
<!-- Create the editor container -->
<div id="editor">
  <p>Hello World!</p>
</div>

<script>

const quill = new Quill('#editor', {
  theme: 'snow',
  modules: {
    imageDropAndPaste : true
  }
});
document.getElementById('btnContent').addEventListener('click', function() {
  console.log(quill.getContents());
});
</script>
  </body>
</html>
```  
  
#### テーブル操作  
##### quilljs-table  
quilljs-table  
https://github.com/dost/quilljs-table  
  
![image.png](/image/aa4153da-1716-bca4-01e0-107aaa13ef92.png)  
  
サンプルを見る限り、テーブルの削除や列、行の削除がGUIからできそうにないです。  
最終コミット日が2017年。  
  
#### quilljs-table  
quilljs-table  
https://github.com/volser/quill-table-ui  
  
quilljs v2.0.0-dev.3が必要になります。  
最終更新日は2019年10月25日です。  
  
テーブルの操作は以下のようなイメージになります。  
![image.png](/image/70a027d5-0272-4d55-76e7-a9ef0087da54.png)  
  
```html
<!doctype html>
<html>
  <head>
    <meta charset="utf-8">
    <title>Test Quill</title>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/quill/2.0.0-dev.3/quill.min.js" type="text/javascript"></script>
    <link href="https://cdnjs.cloudflare.com/ajax/libs/quill/2.0.0-dev.3/quill.snow.min.css" rel="stylesheet">
    
    <script src="https://unpkg.com/quill-table-ui@1.0.5/dist/umd/index.js" type="text/javascript"></script>
    <link href="https://unpkg.com/quill-table-ui@1.0.5/dist/index.css" rel="stylesheet">
    
  </head>
  <body>
<button id="btnContent">コンテンツ取得</button>
<button id="btnTable">テーブル追加</button>
<br>
クリップボードからイメージをbase64で張り付けている。
<!-- Create the editor container -->
<div id="editor">
  <p>Hello World!</p>
</div>

<script>

Quill.register({
  'modules/tableUI': quillTableUI.default
}, true);

const quill = new Quill('#editor', {
  theme: 'snow',
  modules: {
    table: true,
    tableUI: true,
  }
});
document.getElementById('btnContent').addEventListener('click', function() {
  console.log(quill.getContents());
});
document.getElementById('btnTable').addEventListener('click', function() {
  let table = quill.getModule('table');
  console.log(table);
  table.insertTable(3, 3);
});


</script>
  </body>
</html>
```  
  
  
## メモ  
2019/11/28時点の最終リリースはバージョン1.3.7です。  
2.0の開発が進められていますが、そのマイルストーンは不透明なものとなっています。  
https://github.com/quilljs/quill/issues/2435  
  
moduleを実装することで拡張機能が作れる模様。  
  
  
# trix  
**Github**  
https://github.com/basecamp/trix  
  
**Demo**  
https://trix-editor.org/  
![image.png](/image/e47104e2-c484-0437-d4ff-862c44de8279.png)  
  
  
**対象ブラウザ**  
IE 11以降をサポートしているようです。  
https://github.com/basecamp/trix/issues/173  
  
  
**ライセンス**  
MIT License  
  
## サンプル  
  
```javascript
<!doctype html>
<html>
  <head>
    <meta charset="utf-8">
    <title>Test Trix</title>
    <link rel="stylesheet" type="text/css" href="trix.css">
    <script type="text/javascript" src="trix.js"></script>
  </head>
  <body>


<!-- Create the editor container -->
<trix-editor class="trix-content">サンプル</trix-editor>

<button id="btnContent">コンテンツ取得</button>
<button id="btnSave">セーブ</button>
<button id="btnLoad">ロード</button>

<script>
document.getElementById('btnContent').addEventListener('click', function() {
  var element =  document.querySelector("trix-editor");
  console.log(element.editor.getDocument());
  console.log(element.editor.getDocument().toString());
});

// エディタの内容はJSON化して保存と読み込みが可能
document.getElementById('btnSave').addEventListener('click', function() {
  var element =  document.querySelector("trix-editor");
  localStorage["editorState"] = JSON.stringify(element.editor);
});

document.getElementById('btnLoad').addEventListener('click', function() {
  var element =  document.querySelector("trix-editor");
  element.editor.loadJSON(JSON.parse(localStorage["editorState"]));
});

// イベントの確認
addEventListener("trix-attachment-add", function(event) {
  // 添付ファイルや画像を追加するとこのイベントが実行される
  // 以下のコードを参考にfileuploadとかができそう
  // https://trix-editor.org/js/attachments.js
  console.log('trix-attachment-add');
  console.log(event.attachment);
});
addEventListener("trix-attachment-remove", function(event) {
  // 添付ファイルや画像を削除するとこのイベントが実行される
  console.log('trix-attachment-remove');
  console.log(event.attachment);
});

addEventListener("trix-change", function(event) {
  // 内容が変化した場合実行
  console.log('trix-change');
  console.log(event);
});



</script>
  </body>
</html>
```  
  
  
## メモ  
学習コストは低いと思われる。  
※最低限の動作確認はtrix-editorタグを作ってtrix.jsを読み込むだけでいい。  
  
テーブルをサポートする予定はない。  
https://github.com/basecamp/trix/issues/539  
  
コードブロックはあるが強調表示はサポートしていない。  
![image.png](/image/75a9bafe-3163-6102-5b14-909c5d45397b.png)  
  
拡張とかはできなさそう。  
  
# MediumEditor  
medium.comインラインエディターツールバーのクローン  
  
**Github**  
https://github.com/yabwe/medium-editor  
  
**Demo**  
http : //yabwe.github.io/medium-editor/  
![image.png](/image/3fc8c278-f5ea-45ec-438d-4e6b4bb01082.png)  
  
画像の貼り付けやコードブロックはなさそう。  
  
  
**対象ブラウザ**  
![image.png](/image/800d1a22-d64d-040f-3019-01645ad4c0e3.png)  
IEをサポートしている  
  
  
**ドキュメント**  
https://github.com/yabwe/medium-editor/wiki  
  
**ライセンス**  
MIT  
  
## サンプル  
### 単純な例  
  
```html
<!doctype html>
<html>
  <head>
    <meta charset="utf-8">
    <title>Test Trix</title>
    <script src="http://cdn.jsdelivr.net/npm/medium-editor@latest/dist/js/medium-editor.min.js"></script>
    <link rel="stylesheet" href="http://cdn.jsdelivr.net/npm/medium-editor@latest/dist/css/medium-editor.min.css" type="text/css" media="screen" charset="utf-8">
  </head>
  <body>

<div class="editable"></div>
<button id="btnSave">セーブ</button>
<button id="btnLoad">ロード</button>
<script>
var editor = new MediumEditor('.editable', {
    placeholder: {
        text: 'テキストを入力してください',
        hideOnClick: true
    },
    toolbar: {
        /* These are the default options for the toolbar,
           if nothing is passed this is what is used */
        allowMultiParagraphSelection: true,
        buttons: ['bold', 'italic', 'underline', 'anchor', 'h2', 'h3', 'quote'],
        diffLeft: 0,
        diffTop: -10,
        firstButtonClass: 'medium-editor-button-first',
        lastButtonClass: 'medium-editor-button-last',
        relativeContainer: null,
        standardizeSelectionStart: false,
        static: false,
        /* options which only apply when static is true */
        align: 'center',
        sticky: false,
        updateOnEmptySelection: false
    }
});

document.getElementById('btnSave').addEventListener('click', function() {
  console.log(editor.getContent());
  localStorage["medium"] = editor.getContent();
});
document.getElementById('btnLoad').addEventListener('click', function() {
  console.log(editor.getContent());
  editor.setContent(localStorage["medium"]);
});
</script>
  </body>
</html>
```  
  
### MediumEditor Tables  
テーブルの作成を行うプラグインです。  
Jqueryに依存しています。  
  
**GitHub**  
https://github.com/yabwe/medium-editor-tables  
  
**demo**  
https://yabwe.github.io/medium-editor-tables/  
  
![tablemedium.gif](/image/5c79efaa-50f0-efd5-cba4-460819b2e0a2.gif)  
  
```html
<!doctype html>
<html>
  <head>
    <meta charset="utf-8">
    <title>Test Medium</title>
    <link rel="stylesheet" href="http://cdn.jsdelivr.net/npm/medium-editor@latest/dist/css/medium-editor.min.css" type="text/css" media="screen" charset="utf-8">

    <!-- medium-editor-tables.js が使用している -->
    <script src="https://code.jquery.com/jquery-3.4.1.min.js"></script>

    <script src="http://cdn.jsdelivr.net/npm/medium-editor@latest/dist/js/medium-editor.min.js"></script>
    <script type="text/javascript" src="lib/js/medium-editor-tables.js"></script>

    <link rel="stylesheet" href="lib/css/medium-editor-tables.css" />
    
  </head>
  <body>

    <div class="editable"></div>

<script>
  var editor = new MediumEditor('.editable', {
    toolbar: {
      buttons: [
        'bold',
        'italic',
        'table'
      ]
    },
    extensions: {
      table: new MediumEditorTable()
    }
  });
</script>
  </body>
</html>
```  
  
### jQuery insert plugin for MediumEditor  
画像やYoutubeやTwitterなどの埋め込みが可能なプラグインです。  
Jqueryに依存します。  
  
**Github**  
https://github.com/orthes/medium-editor-insert-plugin  
  
**demo**  
https://linkesch.com/medium-editor-insert-plugin/  
  
  
![tablemedium3.gif](/image/376ea51b-5739-0e70-6ac8-ce4b9d62fea9.gif)  
  
  
  
  
```html
<!doctype html>
<html>
  <head>
    <meta charset="utf-8">
    <title>Test Medium</title>
    <link href="http://netdna.bootstrapcdn.com/font-awesome/4.0.3/css/font-awesome.css" rel="stylesheet">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/medium-editor-insert-plugin/2.5.0/css/medium-editor-insert-plugin-frontend.min.css" />
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/medium-editor-insert-plugin/2.5.0/css/medium-editor-insert-plugin.min.css" />
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/medium-editor/5.23.3/css/medium-editor.min.css" />


    <!-- medium-editor-tables.js が使用している -->
    <script src="https://cdnjs.cloudflare.com/ajax/libs/jquery/3.3.1/jquery.min.js"></script>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/handlebars.js/4.0.12/handlebars.runtime.min.js"></script>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/jquery-sortable/0.9.13/jquery-sortable-min.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/jquery.ui.widget@1.10.3/jquery.ui.widget.js"></script>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/jquery.iframe-transport/1.0.1/jquery.iframe-transport.min.js"></script>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/blueimp-file-upload/9.28.0/js/jquery.fileupload.min.js"></script>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/medium-editor/5.23.3/js/medium-editor.min.js"></script>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/medium-editor-insert-plugin/2.5.0/js/medium-editor-insert-plugin.min.js"></script>

  </head>
  <body>

    <div class="editable"></div>
<button id="btnSave">セーブ</button>
<button id="btnLoad">ロード</button>
<script>
  var editor = new MediumEditor('.editable', {
    toolbar: {
      buttons: [
        'bold',
        'italic',
        'table'
      ]
    }
  });
  $('.editable').mediumInsert({
      editor: editor
  });
document.getElementById('btnSave').addEventListener('click', function() {
  console.log(editor.getContent());
  localStorage["medium"] = editor.getContent();
});
document.getElementById('btnLoad').addEventListener('click', function() {
  console.log(editor.getContent());
  editor.setContent(localStorage["medium"]);
});
</script>
  </body>
</html>
```  
  
## メモ  
Medium Editorのライブラリ自体はJavaScriptのみで外部のライブラリに依存していない。  
しかし、その拡張機能がJQueryに依存している。  
  
任意の拡張機能が作成可能。  
https://github.com/yabwe/medium-editor/blob/master/src/js/extensions/README.md  
  
# Pell  
もっともサイズの小さいWYSIWYGライブラリで他のライブラリに依存しません。  
  
**GitHub**  
https://github.com/jaredreich/pell  
  
**Demo**  
https://jaredreich.com/pell/  
画像はURL指定して表示。  
Link等でダイアログを表示する際はブラウザのメッセージボックスを使用している  
  
![image.png](/image/9a05f333-921d-14a1-9624-8d357571727c.png)  
  
  
**対象ブラウザ**  
![image.png](/image/58879047-7f02-d94f-8d4a-e22f9f529607.png)  
かなり古いブラウザでも動作するようです。  
  
**ライセンス**  
MIT  
  
## メモ  
軽量であるのが売り。  
テーブル機能はなさそう。  
また拡張機能等はなさそう。  
  
# Editor.js  
**GitHub**  
https://github.com/codex-team/editor.js  
  
**Demo**  
https://editorjs.io/  
  
![image.png](/image/2577b404-db57-3cc5-5e64-e97c5dfda7e1.png)  
  
・表、画像のアップロードをサポートしている。  
・ツールバーは表示されずに、必要な時にポップアップが出る  
  
**対象ブラウザ**  
![image.png](/image/0f7d5381-4eb8-a970-f0a9-8efafb1c6170.png)  
  
IEは対象外の模様  
※すくなくともデモサイトはIE11で動作しない  
  
**ドキュメント**  
https://github.com/codex-team/editor.js/tree/bcdfcdadbc444921aee62b38516329cda3c96a70/docs  
  
  
**ライセンス**  
Apache License 2.0  
寄付を受け付けている  
https://opencollective.com/editorjs  
  
## サンプル  
  
```html
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>Editor.js example</title>
  <link href="https://fonts.googleapis.com/css?family=PT+Mono" rel="stylesheet">
  <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no" />
</head>
<body>
  <div class="ce-example">
    <div class="ce-example__content _ce-example__content--small">
      <div id="editorjs"></div>

      <button id="saveButton">
        editor.save()
      </button>
      <button id="loadButton">
        editor.load()
      </button>
    </div>
  </div>

  <!-- Load Tools -->
  <!--
   You can upload Tools to your project's directory and use as in example below.
   Also you can load each Tool from CDN or use NPM/Yarn packages.
   Read more in Tool's README file. For example:
   https://github.com/editor-js/header#installation
   -->
  <script src="https://cdn.jsdelivr.net/npm/@editorjs/header@latest"></script><!-- Header -->
  <script src="https://cdn.jsdelivr.net/npm/@editorjs/simple-image@latest"></script><!-- Image -->
  <script src="https://cdn.jsdelivr.net/npm/@editorjs/delimiter@latest"></script><!-- Delimiter -->
  <script src="https://cdn.jsdelivr.net/npm/@editorjs/list@latest"></script><!-- List -->
  <script src="https://cdn.jsdelivr.net/npm/@editorjs/checklist@latest"></script><!-- Checklist -->
  <script src="https://cdn.jsdelivr.net/npm/@editorjs/quote@latest"></script><!-- Quote -->
  <script src="https://cdn.jsdelivr.net/npm/@editorjs/code@latest"></script><!-- Code -->
  <script src="https://cdn.jsdelivr.net/npm/@editorjs/embed@latest"></script><!-- Embed -->
  <script src="https://cdn.jsdelivr.net/npm/@editorjs/table@latest"></script><!-- Table -->
  <script src="https://cdn.jsdelivr.net/npm/@editorjs/link@latest"></script><!-- Link -->
  <script src="https://cdn.jsdelivr.net/npm/@editorjs/warning@latest"></script><!-- Warning -->

  <script src="https://cdn.jsdelivr.net/npm/@editorjs/marker@latest"></script><!-- Marker -->
  <script src="https://cdn.jsdelivr.net/npm/@editorjs/inline-code@latest"></script><!-- Inline Code -->

  <!-- Load Editor.js's Core -->
  <script src="./dist/editor.js"></script>

  <!-- Initialization -->
  <script>
    /**
     * To initialize the Editor, create a new instance with configuration object
     * @see docs/installation.md for mode details
     */
    var initObj = {
      /**
       * Wrapper of Editor
       */
      holder: 'editorjs',
      /**
       * Tools list
       */
      tools: {
        /**
         * Each Tool is a Plugin. Pass them via 'class' option with necessary settings {@link docs/tools.md}
         */
        header: {
          class: Header,
          inlineToolbar: ['link'],
          config: {
            placeholder: 'Header'
          },
          shortcut: 'CMD+SHIFT+H'
        },
        /**
         * Or pass class directly without any configuration
         */
        image: {
          class: SimpleImage,
          inlineToolbar: ['link'],
        },
        list: {
          class: List,
          inlineToolbar: true,
          shortcut: 'CMD+SHIFT+L'
        },
        checklist: {
          class: Checklist,
          inlineToolbar: true,
        },
        quote: {
          class: Quote,
          inlineToolbar: true,
          config: {
            quotePlaceholder: 'Enter a quote',
            captionPlaceholder: 'Quote\'s author',
          },
          shortcut: 'CMD+SHIFT+O'
        },
        warning: Warning,
        marker: {
          class:  Marker,
          shortcut: 'CMD+SHIFT+M'
        },
        code: {
          class:  CodeTool,
          shortcut: 'CMD+SHIFT+C'
        },
        delimiter: Delimiter,
        inlineCode: {
          class: InlineCode,
          shortcut: 'CMD+SHIFT+C'
        },
        linkTool: LinkTool,
        embed: Embed,
        table: {
          class: Table,
          inlineToolbar: true,
          shortcut: 'CMD+ALT+T'
        },
      },
      /**
       * This Tool will be used as default
       */
      // initialBlock: 'paragraph',
      /**
       * Initial Editor data
       */
      data: {
      },
      onReady: function(){
      },
      onChange: function() {
        console.log('something changed');
      }
    };
    var editor = new EditorJS(initObj);
    /**
     * Saving example
     */
    const saveButton = document.getElementById('saveButton');
    const loadButton = document.getElementById('loadButton');

    saveButton.addEventListener('click', function () {
      editor.save().then((savedData) => {
        console.log(savedData);
        localStorage["editJs"] = JSON.stringify(savedData);
      });
    });
    loadButton.addEventListener('click', function () {
      let data = JSON.parse(localStorage["editJs"]);
      console.log(data);
      editor.render(data);
    });
  </script>
</body>
</html>
```  
  
## メモ  
IEは動作しない  
undo機能は2019/11/28時点では自前でやる必要があるっぽい。  
https://github.com/codex-team/editor.js/issues/518  
  
# CKEditor5  
Gitのスター順で並べると上位5位にでてきませんが、バージョンごとにプロジェクトが分かれているっぽいので累計すると、結構使われているように見えます。  
公式ページを見ると累計で27.500.000+のダウンロードが行われているそうです。  
  
**GitHub**  
https://github.com/ckeditor/ckeditor5  
  
**Demo**  
https://ckeditor.com/ckeditor-5/demo/  
  
**ライセンス**  
GNU General Public License Version 2 or later.  
  
商用ライセンスがある。  
https://ckeditor.com/pricing/#null  
  
## メモ  
この中ではデモが一番、使い易かったので、金が豊富にあるならコレがよさそう。  
  
  
# まとめ  
色々調べましたが、結局、一長一短ある感じがします。  
その上で個人的にはコードのハイライトが簡単に使えそうなQuillか、学習コストの低そうなtrixがよさそうに見えます。  
  
  
  
  
