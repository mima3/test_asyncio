## 概要  
Crossfilterはブラウザ上で大きな多変量データを扱うためのJavaScriptのライブラリです。  
素早く、グループ化やフィルタリング、データの集約がおこなえます。  
Crossfilter自体には、独自のUIはないので、D3.jsなどの可視化ライブラリと併用してください。  
  
 **GitHub**   
https://github.com/square/crossfilter  
  
 **Crossfilter Tutorial**   
http://blog.rusty.io/2012/09/17/crossfilter-tutorial/  
  
## 用語説明  
 **fact** 、 **dimension** 、 **measure** について説明します。  
  
 **「週にどれだけの注文を処理するか？」** という問題を想像してください。  
  
処理したすべての注文について週ごとにグループ化し、週ごとの注文数を計算することで表すことができるでしょう。  
  
この場合、各注文については「fact」といいます。  
  
週は「dimension」になります。これはあなたがどのようにデータをスライスしたかの方法になります。  
  
注文数は「measure」になります。それは、あなたが計算したい値です。  
  
では今度は、 **「週ごと、店員ごとにどれだけの売り上げがあるの？」** という問題を想像してください。  
  
再び「facts」を格納して、今度は２つの「dimension」を使います。週と店員です。そして最後に「measure」は注文毎の価格になります。  
  
  
## FactをCrossfilterに設定する  
FactをCrosfilterに設定するには、以下のようにJSONデータを指定する。  
  
```js
var payments = crossfilter([
  {date: "2011-11-14T16:17:54Z", quantity: 2, total: 190, tip: 100, type: "tab"},
  {date: "2011-11-14T16:20:19Z", quantity: 2, total: 190, tip: 100, type: "tab"},
  {date: "2011-11-14T16:28:54Z", quantity: 1, total: 300, tip: 200, type: "visa"},
  {date: "2011-11-14T16:30:43Z", quantity: 2, total: 90, tip: 0, type: "tab"},
  {date: "2011-11-14T16:48:46Z", quantity: 2, total: 90, tip: 0, type: "tab"},
  {date: "2011-11-14T16:53:41Z", quantity: 2, total: 90, tip: 0, type: "tab"},
  {date: "2011-11-14T16:54:06Z", quantity: 1, total: 100, tip: 0, type: "cash"},
  {date: "2011-11-14T16:58:03Z", quantity: 2, total: 90, tip: 0, type: "tab"},
  {date: "2011-11-14T17:07:21Z", quantity: 2, total: 90, tip: 0, type: "tab"},
  {date: "2011-11-14T17:22:59Z", quantity: 2, total: 90, tip: 0, type: "tab"},
  {date: "2011-11-14T17:25:45Z", quantity: 2, total: 200, tip: 0, type: "cash"},
  {date: "2011-11-14T17:29:52Z", quantity: 1, total: 200, tip: 100, type: "visa"}
]);
```  
  
## 総計の計算  
factから総計を求めます。  
まず、すべてのデータを１つのグループにまとめてから、reduceCount()を使用して次のようにします。  
  
```js
console.log("Count: " + payments.groupAll().reduceCount().value()) ;
// Count: 12
```  
  
もし、特定の属性で計算をしたい場合、例えば、totalの合計を求める場合は、reduceSum()を使用します。  
  
```js
console.log("Sum: " + payments.groupAll().reduceSum(function(fact) { return fact.total; }).value());
//  Sum: 1720
```  
  
実は、reduceCount(),reduceSum()はreduce()という関数を用いて実装されています。つまり、reduce()を独自に実装することで、独自の計算がおこなえます。  
  
下記の例では、レコード数とtotalの合計を取得しています。  
  
```js
console.log(payments.groupAll().reduce(
  function add(p, v) {
    ++p.count;
    p.total += v.total;
    return p;
  }, 
  function remove(p, v) {
    --p.count;
    p.total -= v.total;
    return p;
  }, 
  function init() {
    return {count: 0, total: 0};;
  }
).value());

//  Object {count: 12, total: 1720}
```  
  
init()では、集計開始時の初期値を指定します。  
add()では、グループにデータが加わった場合の計算、  
remove()では、グループからデータが外れた場合の計算を行います。  
  
addやremoveは実際にデータを追加、削除した時だけでなく、filterによってデータが外れた場合も実行されます。  
  
add,removeの引数pは集計値、vはfactのオブジェクトになります。  
  
  
## フィルタをかける  
### 単一のdimensionに対する条件でフィルター  
たとえば、typeが"tab"のデータの数とtotalの合計を求める場合を考えます。  
  
この場合は、typeのdimensionを作成後、そのdimensionに対してフィルターをかけます。  
  
```js
var paymentsByType = payments.dimension(function(d) { return d.type; });
paymentsByType.filter('tab');
```  
  
ここでフィルターを指定することにより、paymentsByTypeオブジェクト上で計算した場合を除き、集計時にフィルターが掛かることが確認できます。たとえば先と同じく、個数とtotalの合計をもとめてみます。  
  
  
```js
console.log("Count: " + payments.groupAll().reduceCount().value()) ;
console.log("Sum: " + payments.groupAll().reduceSum(function(fact) { return fact.total; }).value());

// Count: 8
// Sum: 920
```  
  
このように、集計した場合に、「type==tab」のデータについてのみ計算されることが確認できます。  
  
### 複数のdimensionに対する条件でフィルター  
フィルターは同時に複数指定することも可能です。  
次の例では「type==tab」という条件に加えて、「tip==0」という条件を指定しましょう。  
この場合は、新しくtipsのdimensionを作成後、フィルタをかけることになります。  
  
  
```js
var paymentsByType = payments.dimension(function(d) { return d.type; });
paymentsByType.filter('tab');
var paymentsByTip = payments.dimension(function(d) { return d.tip; });
paymentsByTip.filter(0);
console.log("Count: " + payments.groupAll().reduceCount().value()) ;
console.log("Sum: " + payments.groupAll().reduceSum(function(fact) { return fact.total; }).value());

//Count: 6
//Sum: 540
```  
  
このように、dimensionを作成することにより、フィルターを追加が行えます。  
  
しかし、dimensionの作成は高価です。それゆえ、32個までしかdimensionの作成はサポートされていません。  
もし、これ以上のdimensionを作成したい場合はdispose関数で作成済みのdimensionを始末してから、作成してください。  
  
```js
var ds=[]
for (var i = 0; i < 33; ++i) {
  var d = payments.dimension(function(d) { return d.type; });
  d.dispose(); // これをはずすとエラーになる。
}
```  
### フィルターの解除方法  
指定したフィルターを解除するには、filterAll()を使用します。  
  
```js
var paymentsByType = payments.dimension(function(d) { return d.type; });
paymentsByType.filter('tab');
console.log("Count: " + payments.groupAll().reduceCount().value()) ;
console.log("Sum: " + payments.groupAll().reduceSum(function(fact) { return fact.total; }).value());
// Count: 8
// Sum:920

paymentsByType.filterAll()
console.log("Count: " + payments.groupAll().reduceCount().value()) ;
console.log("Sum: " + payments.groupAll().reduceSum(function(fact) { return fact.total; }).value());
// Count: 12
// Sum:1720
```  
  
この例ではfilterAll()後に、先に指定したフィルターの条件が外れて集計されていることが確認できます。  
  
### フィルター条件の種類  
先の例では一致するか否かの条件でのみフィルターをかけていました。  
crossfilterは以下のように、範囲を指定して条件を指定できます。  
  
```js
var paymentsByTip = payments.dimension(function(d) { return d.tip; });
paymentsByTip.filter([100,200]);
console.log("Count: " + payments.groupAll().reduceCount().value()) ;
console.log("Sum: " + payments.groupAll().reduceSum(function(fact) { return fact.total; }).value());

//Count: 3
//Sum: 580
```  
  
この場合はtipが100以上で200より小さいデータのみ抽出しています。  
  
また、このフィルター条件については、関数で指定することができます。  
  
```js
var paymentsByTip = payments.dimension(function(d) { return d.tip; });
paymentsByTip.filterFunction( function(d) {
  return (d >= 100 && d < 200);
});
console.log("Count: " + payments.groupAll().reduceCount().value()) ;
console.log("Sum: " + payments.groupAll().reduceSum(function(fact) { return fact.total; }).value());

```  
  
## グループ化  
グループ化を行うには、グループ化をする属性に対するdimensionを作成し、それに対してグループ化を行います。  
  
```js
var paymentsByType = payments.dimension(function(d) { return d.type; });
var gp = paymentsByType.group();
console.log('グループごとの数');
var countMeasure = gp.reduceCount();
var ret = countMeasure.all()
for (var i = 0; i < ret.length ;++i) {
  console.log(ret[i]);
}
// グループごとの数
// Object {key: "cash", value: 2}
// Object {key: "tab", value: 8}
// Object {key: "visa", value: 2}
```  
  
dimension.group()にて、特定のdimensionに対するグループ化を行いgroupオブジェクトを作成します。  
  
```js
var gp = paymentsByType.group();
```  
  
次に、作成したグループに対して、集計を行いmesureを求めます。  
  
```js
var countMeasure = gp.reduceCount();
```  
  
mesureには集計結果が格納されていますが、これを取得するには、all()を使用します。これにより、配列として全てのデータが取得できます。  
  
```js
var ret = countMeasure.all()
for (var i = 0; i < ret.length ;++i) {
  console.log(ret[i]);
}
```  
  
all()の代わりにtop()を用いることで指定の件数を大きいもの順から取得することができます。  
  
```js
var ret = countMeasure.top(gp.size())
for (var i = 0; i < ret.length ;++i) {
  console.log(ret[i]);
}
// Object {key: "tab", value: 8}
// Object {key: "visa", value: 2}
// Object {key: "cash", value: 2}
```  
  
### 複数の属性によるグループ化  
複数の属性を指定してグループ化することも可能です。  
以下の例ではtype, quantity毎の合計を取得します。  
  
```js
var dim = payments.dimension(function(d) { return [d.type, d.quantity]; });
var m = dim.group().reduceSum(
  function(d) { return d.total; }
);
var ret = m.all();
for (var i = 0; i < ret.length ;++i) {
  console.log('key:', ret[i]['key'],'value:', ret[i]['value']);
}
```  
  
```結果
key: ["cash", 1] value: 100
key: ["cash", 2] value: 200
key: ["tab", 2] value: 920
key: ["visa", 1] value: 500
```  
  
## フィルタの落とし穴  
フィルターを書けたdimensionオブジェクトで計算を行うとフィルターが掛からない状態になります。  
  
```js
var paymentsByType = payments.dimension(function(d) { return d.type; });
paymentsByType.filter('tab');
var ret = paymentsByType.group().reduceCount().all();
for (var i = 0; i < ret.length ;++i) {
  console.log(ret[i]);
}
// Object {key: "cash", value: 2}
// Object {key: "tab", value: 8}
// Object {key: "visa", value: 2}
```  
  
「type==tab」でフィルターを掛けているのに、cash,visaに数値が計上されています。これはフィルターを掛けたオブジェクト上で計算を行った場合にフィルターが解除されるためです。  
  
もし、期待した動作をしたい場合は、別のdimensionオブジェクトで計算する必要があります。  
  
```js
var paymentsByType = payments.dimension(function(d) { return d.type; });
paymentsByType.filter('tab');
var paymentsByType2 = payments.dimension(function(d) { return d.type; });
var ret = paymentsByType2.group().reduceCount().all();
for (var i = 0; i < ret.length ;++i) {
  console.log(ret[i]);
}
// Object {key: "cash", value: 0}
// Object {key: "tab", value: 8}
// Object {key: "visa", value: 0}
```  
  
## 作成済みのcrossfilterにfactを追加、削除をする  
crossfilterにデータを追加するには、addメソッドを使用します  
  
```js
console.log("Count: " + payments.size()) ;
payments.add(
   [
     {date: "2011-11-15T17:29:52Z", quantity: 1, total: 200, tip: 100, type: "visa"},
     {date: "2011-11-15T17:29:52Z", quantity: 1, total: 200, tip: 150, type: "cash"}
   ]
);
console.log("Count: " + payments.size()) ;
//Count: 12
//Count: 14
```  
  
削除する場合はフィルターで削除対象のデータを選択後、remove()を実行します。  
  
```js
console.log("Count: " + payments.size()) ;

var paymentsByType = payments.dimension(function(d) { return d.type; });
paymentsByType.filter('tab');
payments.remove();
console.log("Count: " + payments.size()) ;
//Count: 14
//Count: 6

```  
