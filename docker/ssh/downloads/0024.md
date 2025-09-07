Node.jsのexpressで使用するテンプレートエンジンである、Jadeで処理を共通化する方法を説明する。  
  
http://jade-lang.com/reference/  
  
# Includeによる共通化  
includeを用いることで外部ファイルを使用できる  
複数のファイルで共通する処理は別ファイルにまとめて、includeすればよい。  
与えられた変数はIncludeしたファイルでも使用できる。  
  
```message.jade
div#message(style='display:none')
  - for(var key in message) {
    div(id='#{key}') #{message[key]}
  -}
```  
  
```project.jade
// HTML
doctype html
html
  head
    title #{message.title}
    link(rel='stylesheet', href='/stylesheets/style.css')
    link(rel='stylesheet', href='/stylesheets/ui-lightness/jquery-ui-1.10.4.min.css')
    link(rel='stylesheet', href='/javascripts/lib/msgbox/msgBoxLight.css')
    script(type='text/javascript', src='/javascripts/lib/jquery-1.11.1.min.js')
    script(type='text/javascript', src='/javascripts/lib/jquery-ui-1.10.4.min.js')
    script(type='text/javascript', src='/javascripts/lib/msgbox/jquery.msgBox.js')
    script(type='text/javascript', src='/javascripts/src/ui_util.js')
    script(type='text/javascript', src='/javascripts/src/project.js')
  body
    h2 #{message.title}
    include message
```  
  
# mixinによる共通化  
同じファイル内で特定のブロックを繰り返したい場合は、mixinを使用するといい。  
mixinを使用する際に、引数を与えることができるので、それにより、各繰り返し要素の内容を変更できる。  
以下の例では追加用のダイアログと変更用のダイアログのHTMLを共通的に作成している。  
  
```sample.jade
// エディット用のダイアログ
// @param id DialogのID
mixin editDialog(dialogId, saveBtnId)
  div(id=dialogId, class='dialog', style='display:none')
    div #{message.projectName}
      input(type='text', name='projectName')#projectName
    div #{message.path}
      input(type='text', name='path')#inputPath
      button#addPath +
      button#deletePath -
    br
    select(multiple style="width:100%;")#selectPath
    br
    button(id=saveBtnId) #{message.saveBtn}

// HTML
doctype html
html
  head
    title #{message.title}
    link(rel='stylesheet', href='/stylesheets/style.css')
    link(rel='stylesheet', href='/stylesheets/ui-lightness/jquery-ui-1.10.4.min.css')
    link(rel='stylesheet', href='/javascripts/lib/msgbox/msgBoxLight.css')
    script(type='text/javascript', src='/javascripts/lib/jquery-1.11.1.min.js')
    script(type='text/javascript', src='/javascripts/lib/jquery-ui-1.10.4.min.js')
    script(type='text/javascript', src='/javascripts/lib/msgbox/jquery.msgBox.js')
    script(type='text/javascript', src='/javascripts/src/ui_util.js')
    script(type='text/javascript', src='/javascripts/src/project.js')
  body
    h2 #{message.title}
    +editDialog('dlgAddProject', 'btnAddProject')
    +editDialog('dlgEditProject', 'btnUpdateProject')
```  
