# 目的  
本記事の目的はjmockit 1.48について調査した際のメモです。  
  
**ドキュメント**  
http://jmockit.github.io/index.html  
  
**ソースコード**  
https://github.com/jmockit/jmockit1  
  
**JavaDoc**  
https://repo1.maven.org/maven2/org/jmockit/jmockit/1.48/jmockit-1.48-javadoc.jar  
  
**検証環境**  
java version "1.8.0_202"  
Eclipse IDE for Enterprise Java Developers.  
Version: 2019-03 (4.11.0)  
Build id: 20190314-1200  
JUnit4  
  
# jmockitとは  
xUnitを使用して単体テストを行う場合、依存する部品が問題になってテストが困難な場合があります。  
![image.png](/image/e45ace66-7f22-8d37-37d2-627af6f58f12.png)  
  
たとえば、以下のようなケースです。  
・依存する部品で任意の内容をテスト対象に返すのが困難な場合  
　※たとえばHDDの容量不足というエラーを出力する必要がある試験の場合  
・依存する部品を利用すると別の試験で副作用が発生する場合  
　※たとえばデーターベースの特定のテーブルを全て削除するような試験を行う場合  
・依存する部品がまだ完成していない場合  
　※たとえばテスト対象のプログラムと依存する部品が並行で開発されている場合。  
  
こういったケースの場合に、依存する部品の代わりにjmockitで作成したメソッドを利用することで単体テストを容易にします。  
  
![image.png](/image/4e8e549b-3615-6a2a-a100-2781a428c2ab.png)  
  
jmockitを使用することで、依存する部品の代わりにテストに都合のいい値をテスト対象に渡したり、依存する部品がどのようにテスト対象から呼び出されたかを記録し、検証することが可能になります。  
  
# 簡単な使用方法  
(1)以下からJarをダウンロードしてプロジェクトから参照する。  
https://mvnrepository.com/artifact/org.jmockit/jmockit  
  
あるいはMavenの場合は以下をpom.xmlに追加する  
  
```xml
<!-- https://mvnrepository.com/artifact/org.jmockit/jmockit -->
<dependency>
    <groupId>org.jmockit</groupId>
    <artifactId>jmockit</artifactId>
    <version>1.48</version>
    <scope>test</scope>
</dependency>
```  
  
(2)JUnitのテストケースを追加する  
  
```java
package jmockittest;

import static org.junit.Assert.*;

import org.junit.Test;

import mockit.Mock;
import mockit.MockUp;

public class SimpleTest {

	@Test
	public void test() {
        new MockUp<java.lang.Math>() {
        	@Mock
        	public double random() {
        		// 常に2.5を返すrandom()メソッド
        		return 2.5;
        	}
        };
		assertEquals(2.5, Math.random(), 0.1);
		assertEquals(2.5, Math.random(), 0.1);
	}

}
```  
  
(3)junit実行時の実行構成にて、VM引数に「-javaagent:jmockit-1.48.jar」を付与して実行する。  
![image.png](/image/15f06a4d-3daa-532d-e547-50fbb6da7038.png)  
  
![image.png](/image/4235cbf0-758b-1118-0cba-c04dfb5a65e9.png)  
  
実行方法の詳細は下記を参照：  
http://jmockit.github.io/tutorial/Introduction.html#runningTests  
  
  
## トラブルシュート  
### initializationErrorが発生する場合  
**事象**  
![image.png](/image/2ebe8221-b48d-94c9-8053-9766e9e113bf.png)  
  
**エラートレース**  
  
```
java.lang.Exception: Method testVerifications should have no parameters
	at org.junit.runners.model.FrameworkMethod.validatePublicVoidNoArg(FrameworkMethod.java:76)
	at org.junit.runners.ParentRunner.validatePublicVoidNoArgMethods(ParentRunner.java:155)
// 略
	at org.eclipse.jdt.internal.junit.runner.RemoteTestRunner.main(RemoteTestRunner.java:209)

```  
  
**原因**  
VM引数に「-javaagent:jmockit-1.48.jar」が付与されていない。  
  
### クラスパスの順番が重要？あるいはRunWithを使用する必要があるのか？  
ビルドのクラスパスをjmockit→junitの順番で行うことが重要であるという記載がたまにあります。  
https://stackoverflow.com/questions/32817982/jmockit-wasnt-properly-initialized?rq=1  
  
おそらく、これは現バージョンでは問題にならない、あるいはVM引数に「-javaagent:jmockit-X.XX.jar」が付与されていないことが原因と考えられます。  
  
また、ビルドのクラスパスの順番の別解に、「@RunWith(JMockit.class)」を使用するという方法があるらしいですが、少なくとも1.48時点では、この属性は存在しません。  
  
https://github.com/jmockit/jmockit1/issues/554  
  
# jmockitの使い方  
## Mocking  
Mocking はテスト対象のクラスをその依存関係（の一部）から分離するメカニズムを提供します。  
モック化されたインスタンスを作成するには@Mocked/@Injectable/@Capturingアノテーションを使用します。  
モック化されたインスタンスは[Expectations](#expectations)で期待する動作を設定したり、[Verifications](#verifications)でモック化されたインスタンスがどのように実行されたかを検証可能です。  
  
### @Mockedアノテーション  
テストケースのメソッドのパラメータまたはテストケースのクラスのフィールドとして@Mockedアノテーションを使用してモック化を行うことが可能です。@Mockedアノテーションを使用した場合、それを使用するテストの期間は同じ型のインスタンスは全てモック化されます。  
  
なお、プリミティブ型と配列型を除き、任意の型をモック化可能です。  
  
では以下のクラスをモックオブジェクトとして使用する方法を考えてみます。  
  
**テスト対象**  
  
```java
package SampleProject;

public class Hoge001 {
	public int hoge(int x, int y) {
		return x + y;
	}
	public String hoge(String x) {
		return "test" + x;
	}
}

```  
  
**Mockedの使用例**  
  
```java
package jmockittest;

import static org.junit.Assert.*;

import org.junit.Test;

import SampleProject.Hoge001;
import mockit.Expectations;
import mockit.Mocked;

public class Test001 {
	// モックを使用しない場合...
	@Test
	public void test0() {
		Hoge001 hoge = new Hoge001();
		assertEquals(11, hoge.hoge(5,6));
		assertEquals("testxxx", hoge.hoge("xxx"));
	}

	// テストメソッドのパラメータとして指定することで、モック化されたインスタンスを作成できます
	@Test
	public void test1(@Mocked Hoge001 mock) {
		new Expectations() {{
			// hogeがx=5, y = 6で呼ばれたら1回目は99を返す
			mock.hoge(5,6);
			result  = 99;
		}};
		// Expectationsでメソッドのresultを指定した場合は、その値が取得される
		assertEquals(99, mock.hoge(5,6));
		// Expectationsでメソッドのresultを指定されていない場合は、初期値(null)となる
		assertEquals(null, mock.hoge("xxx"));

		// @Mockedを使用した場合、そのテストの期間は、すべての該当のインスタンスがモック化される
		Hoge001 hoge = new Hoge001();
		assertEquals(99, hoge.hoge(5,6));
		assertEquals(null, hoge.hoge("xxx"));

	}
}

```  
  
test0()はモック化しない場合のテストケースになっており、test1()はパラメータに@Mockedを使用したテストケースになっています。  
test1()のテストケースの間は、Hoge001のインスタンスは全てモック化されてたインスタンスとなります。  
  
#### テストケースで直接作成されていない場合もモックになることを確認  
テストケース内で直接インスタンスを作成していない場合もモック化されることを以下のテストで確認します。  
  
**テスト対象**  
Hoge001のインスタンスを作成して利用するHoge002をテスト対象とします。  
  
```java
package SampleProject;

public class Hoge002 {
	public int test(int x , int y) {
		Hoge001 hoge1 = new Hoge001();
		return hoge1.hoge(x*2, y*2);
	}
}
```  
  
**テストコード**  
  
```java
package jmockittest;

import static org.junit.Assert.*;

import org.junit.Test;

import SampleProject.Hoge001;
import SampleProject.Hoge002;
import mockit.Expectations;
import mockit.Mocked;

public class Test001_3 {

	// テストメソッドのパラメータとして指定することで、モック化されたインスタンスを作成できます
	@Test
	public void test1(@Mocked Hoge001 mock) {
		new Expectations() {{
			// hogeがx=10, y = 12で呼ばれたら1回目は99を返す
			mock.hoge(10,12);
			result  = 99;
		}};
		Hoge002 hoge2 = new Hoge002();
		assertEquals(99, hoge2.test(5,6));
	}
}

```  
  
このテストケースを実行すると、Hoge002で作成したHoge001がモック化されているものであると確認できます。  
  
#### クラスのフィールドに@Mockedを使用したケース  
クラスのフィールドに@Mockedを使用した場合、クラスのテスト全てで対象のクラスがモック化されます。  
  
**テストコード**  
  
```java
package jmockittest;

import static org.junit.Assert.*;

import org.junit.Test;

import SampleProject.Hoge001;
import SampleProject.Hoge002;
import mockit.Expectations;
import mockit.Mocked;

public class Test001_2 {

	// テストクラスのフィールドとして指定することで、モック化されたインスタンスをそれぞれのテストケースで利用できます
	@Mocked
	private Hoge001 fieldMocked;
	@Test
	public void test1() {
		new Expectations() {{
			fieldMocked.hoge(anyInt, anyInt);
			result = 100;
		}};
		assertEquals(100, fieldMocked.hoge(1,2));
	}
	@Test
	public void test2() {
		new Expectations() {{
			// hogeがx=10, y = 12で呼ばれたら1回目は99を返す
			fieldMocked.hoge(10,12);
			result  = 99;
		}};
		Hoge002 hoge2 = new Hoge002();
		assertEquals(99, hoge2.test(5,6));
	}
}
```  
  
#### カスケードされたモック  
多くの異なるオブジェクトを使用して提供される機能があるとします。たとえば「obj1.getObj2(...).getYetAnotherObj().doSomething(...)」のような呼び出しがあることは珍しくありません。  
この場合のモックの例を見てみましょう。  
  
以下の例ではmock.getDepend1().output()といったオブジェクトを返すメソッドにおいてモック化がされるか確認するコードになっています。  
  
**テスト対象のクラス**  
  
```java
package SampleProject;

public class Depend001 {
	private String prefix;
	public Depend001(String p) {
		this.prefix = p;
	}
	public String output(String msg) {
		return this.prefix + msg;
	}
}
```  
  
```java
package SampleProject;

public class Hoge003 {
	private Depend001 d1;
	public Depend001 d2;
	public Hoge003() {

	}

	public Hoge003(Depend001 depend1, Depend001 depend2) {
		this.d1 = depend1;
		this.d2 = depend2;
	}

	public String output() {
		String ret = "";
		ret = ret + this.d1.output("test1") + "\n";
		ret = ret + this.d2.output("test2") + "\n";
		return ret;
	}
	public Depend001 getDepend1() {
		return this.d1;
	}
}

```  
  
**テストコード**  
  
```java
package jmockittest;

import static org.junit.Assert.*;

import org.junit.Test;

import SampleProject.Hoge003;
import mockit.Expectations;
import mockit.Mocked;

public class Test002 {
	@Test
	public void test1(@Mocked Hoge003 mock) {
		new Expectations() {{
			mock.getDepend1().output(anyString);
			result  = "abcde";
		}};
		assertEquals("abcde", mock.getDepend1().output("abc"));
	}

}
```  
  
上記のサンプルのように、枝葉のDepend001を明示的にモック化しなくても、大元のHoge003クラスをモック化することで目的のメソッドの期待する動作を変更することが確認できました。  
  
### @Injectableアノテーション  
@Mockedアノテーションと同様にモック化を行うためのアノテーションですが、@Mockedアノテーションとの違いはモックを１つのインスタンスに制限することです。  
また、@Testedアノテーションとと組み合わせることで、テスト対象オブジェクトへの自動注入に使用することができます。  
  
### @Mockedアノテーションとの違い  
@Mockedアノテーションと@Injectableアノテーションの違いを確認するために、@Mockedアノテーションで使用したテストコードを@Injectableに変更して確認をしてみます。  
  
```java
package jmockittest;

import static org.junit.Assert.*;

import org.junit.Test;

import SampleProject.Hoge001;
import mockit.Expectations;
import mockit.Injectable;

public class Test004 {

	// テストメソッドのパラメータとして指定することで、モック化されたインスタンスを作成できます
	@Test
	public void test1(@Injectable Hoge001 mock) {
		new Expectations() {{
			// hogeがx=5, y = 6で呼ばれたら1回目は99を返す
			mock.hoge(5,6);
			result  = 99;
		}};
		// Expectationsでメソッドのresultを指定した場合は、その値が取得される
		assertEquals(99, mock.hoge(5,6));
		// Expectationsでメソッドのresultを指定されていない場合は、初期値(null)となる
		assertEquals(null, mock.hoge("xxx"));

		// @Mockedを使用した場合とことなり、すべての該当のインスタンスがモック化されるわけではない。
		Hoge001 hoge = new Hoge001();
		assertEquals(11, hoge.hoge(5,6));
		assertEquals("testxxx", hoge.hoge("xxx"));

	}
}
```  
  
@Mockedアノテーションを使用した場合、テストの期間中は対象のクラスのインスタンスを作成するたびにモック化されたものとなりましたが、@Injectableを使用することでモック化されるインスタンスを１つに制限していることが確認できます。  
  
#### @Testedアノテーションに対する注入  
@Testedアノテーションで指定したテスト対象のオブジェクトにモックを注入するサンプルを確認してみます。  
@Testedで指定したテスト対象のオブジェクトのコンストラクタの引数に注入する方法と、テスト対象のフィールドに注入する方法があります。  
  
**コンストラクタの引数に注入する方法**  
以下はHoge003(Depend001 depend1, Depend001 depend2) のコンストラクタの引数であるdepend1とdepend2を指定する例です。  
  
```java
package jmockittest;

import static org.junit.Assert.*;

import org.junit.Test;

import SampleProject.Depend001;
import SampleProject.Hoge003;
import mockit.Expectations;
import mockit.Injectable;
import mockit.Tested;

public class Test003 {
	@Tested
	Hoge003 target;

	@Injectable
	Depend001 depend1;

	@Injectable
	Depend001 depend2;

	@Test
	public void test1() {
		new Expectations() {{
			depend1.output(anyString);
			result  = "abcde";
			depend2.output(anyString);
			result  = "xxxxx";
		}};
		assertEquals("abcde\nxxxxx\n", target.output());
	}

}

```  
  
**フィールドに注入する方法**  
以下はHoge003オブジェクトのd1,d2フィールドに注入するサンプルになります。  
  
```java
package jmockittest;

import static org.junit.Assert.*;

import org.junit.Test;

import SampleProject.Depend001;
import SampleProject.Hoge003;
import mockit.Expectations;
import mockit.Injectable;
import mockit.Tested;

public class Test003B {
	@Tested
	Hoge003 target;

	@Injectable
	Depend001 d1;

	@Injectable
	Depend001 d2;

	@Test
	public void test1() {
		new Expectations() {{
			d1.output(anyString);
			result  = "abcde";
			d2.output(anyString);
			result  = "xxxxx";
		}};
		assertEquals("abcde\nxxxxx\n", target.output());
	}
}
```  
  
##### プリミティブ型のフィールドやコンストラクトに注入を行う方法  
@Injectableアノテーションのvalue要素を使用することで、@Testedアノテーションで指定したテスト対象のプリミティブ型のフィールドやコンストラクトに注入を行うことが可能です。  
  
```java
package jmockittest;

import org.junit.Test;

import SampleProject.Depend001;
import mockit.Injectable;
import mockit.Tested;

public class Test005 {
	@Tested
	Depend001 tested;

	@Test
	public void test1(@Injectable("abc") String p) {
		// 以下を出力
		// abcaaa
		System.out.println(tested.output("aaa"));
	}
	@Test
	public void test2(@Injectable("abc") String prefix) {
		// 以下を出力
		// abcbbb
		System.out.println(tested.output("bbb"));
	}
}

```  
  
test1はテスト対象のオブジェクトのコンストラクタ引数pに指定して注入をおこなっており、test2はテスト対象のオブジェクトのフィールドprefixを指定して注入をしています。  
  
##### @Testedアノテーションのオプション要素  
  
|タイプ|名前|オプションの要素と説明|規定値|  
|:-----|:-----|:-----|:-----|  
|boolean|availableDuringSetup|テストされたクラスが、テストセットアップメソッド（つまり、@ Beforeまたは@BeforeMethodとして注釈が付けられたメソッド）の実行前にインスタンス化および初期化されるか、それらの後に初期化されるかを示します。|false|  
|boolean|fullyInitialized|注入に適格なテスト済みオブジェクトの各非最終フィールドに値を割り当てる必要があることを示します。Springを使用している場合での使いどころは次のページで記載されています。https://stackoverflow.com/questions/25856210/injecting-only-some-properties-mocking-others |false|  
|boolean|global|テスト対象クラスの単一の名前付きインスタンスを作成して、テスト実行全体で使用するかどうかを示します。|false|  
|String|value|テストするフィールド/パラメーターのタイプがストリング、プリミティブまたはラッパータイプ、数値タイプ、または列挙タイプの場合、リテラル値を指定します。|""|  
  
**availableDuringSetupとglobalを検証するテストコード**  
  
```java
package jmockittest;

import org.junit.Before;
import org.junit.Test;

import SampleProject.Hoge001;
import mockit.Tested;

public class Test007 {
	@Tested(availableDuringSetup=true, global=true)
	Hoge001 tested;

	@Before
	public void before()
	{
		// null以外　availableDuringSetupがfalseだとnullになる
		System.out.println("before:" + tested);
	}

	@Test
	public void test1() {
		// null以外
		System.out.println("test1:" + tested);
	}
	@Test
	public void test2() {
		// null以外 test1と同じオブジェクトが使われていることが確認できる
		System.out.println("test2:" + tested);
	}
}
```  
  
  
### @Capturingアノテーション  
@Capturingアノテーションを使用することで既定クラスやインターフェイスに対してモック化を行いうことが可能です。  
下記のサンプルは、個々の実装クラスではなく、インターフェイスに対してモック化されたメソッドを作成するサンプルになっています。  
  
```java
package jmockittest;

import static org.junit.Assert.*;

import org.junit.Test;

import mockit.Capturing;
import mockit.Expectations;

public class Test006 {
	public interface Service { int doSomething(); }
	final class ServiceImpl implements Service { public int doSomething() { return 1; } }

	public final class TestedUnit {
	   private final Service service1 = new ServiceImpl();
	   private final Service service2 = new Service() { public int doSomething() { return 2; } };

	   public int businessOperation() {
	      return service1.doSomething() + service2.doSomething();
	   }
	}

	// インターフェイスや既定クラスに対してモックを作成する
	@Test
	public void test1(@Capturing Service anyService) {
	      new Expectations() {{ anyService.doSomething(); returns(3, 4); }};

	      int result = new TestedUnit().businessOperation();

	      assertEquals(7, result);
	}
}

```  
  
### Expectations  
Expectationsは特定のテストに関連するモックオブジェクトに対して期待する動作を設定します。  
  
#### 期待値を設定する  
Expectations中にはモックオブジェクトのメソッドをどのパラメータを指定したら、どの値を返すかを指定できます。  
下記の例では「String hoge(String)」と「int hoge(int, int)」メソッドを実行した際にどのような値を返すかを設定した例になります。  
  
```java
package jmockittest;

import static org.junit.Assert.*;

import org.junit.Test;

import SampleProject.Hoge001;
import mockit.Delegate;
import mockit.Expectations;
import mockit.Mocked;

public class Test008 {

	// Expectationsでメソッドのresultを指定した場合は、その値が取得されることを確認
	@Test
	public void test1(@Mocked Hoge001 mock) {
		new Expectations() {{
			mock.hoge("test");
			result = "abcde";

			mock.hoge(5,6);
			result  = 99;
			result = 100;
			result = 101;

		}};
		//　mock.hoge("test")を実行した際の期待値を取得
		assertEquals("abcde", mock.hoge("test"));


		//　mock.hoge(5,6)を実行した際の期待値を取得
		// Expectationsで設定した1つめの値が取得
		assertEquals(99, mock.hoge(5,6));
		// Expectationsで設定した2つめの値が取得
		assertEquals(100, mock.hoge(5,6));
		// Expectationsで設定した3つめの値が取得
		assertEquals(101, mock.hoge(5,6));
		// Expectationsで設定した最後の値が取得
		assertEquals(101, mock.hoge(5,6));
		// Expectationsで設定した最後の値が取得
		assertEquals(101, mock.hoge(5,6));

		// 引数が異なる場合は初期値となる
		assertEquals(0, mock.hoge(7,6));
	}
}
```  
  
##### returnsで記載する例  
複数のresultはreturnsで以下のように、まとめて記載することも可能です。  
  
```java
		new Expectations() {{
			mock.hoge("test");
			result = "abcde";

			mock.hoge(5,6);
			returns(99, 100, 101);

		}};
```  
  
#### 引数の柔軟な指定方法  
先の例では特定の引数の値を受け付けたときのみ戻り値を返すようにしていましたが、any～やwith～を引数に指定することで引数の値を柔軟に設定することができます。  
  
  
##### anyフィールドの使用  
Expectationsには任意のあたいをあらわすいくつかのanyフィールドが存在します。  
  
|type|name|  
|:---|:---|  
|Object|any|  
|Boolean|anyBoolean|  
|Byte|anyByte|  
|Character|anyChar|  
|Double|anyDouble|  
|Float|anyFloat|  
|Integer|anyInt|  
|Long|anyLong|  
|Short|anyShort|  
|String|anyString|  
  
anyフィールドを利用した例は以下のようになります。  
  
```java
	@Test
	public void test1_1(@Mocked Hoge001 mock) {
		new Expectations() {{
			mock.hoge(anyString);
			result = "abcde";

			mock.hoge(anyInt, anyInt);
			result  = 99;

		}};
		//　mock.hoge("test")を実行した際の期待値を取得
		assertEquals("abcde", mock.hoge("test"));
		assertEquals("abcde", mock.hoge("hogehoget"));


		//　mock.hoge(5,6)を実行した際の期待値を取得
		assertEquals(99, mock.hoge(5,6));
		assertEquals(99, mock.hoge(99,1234));
	}
```  
  
  
###### 固定の引数の値と任意の引数の値を組み合わせる  
固定の引数の値と任意の引数の値を組み合わせることもできます。下記の例ではhoge(5,6)の場合は10を返して、それ以外の場合は99を返すモックメソッドを作ります。  
  
```java
	@Test
	public void test1_2(@Mocked Hoge001 mock) {
		new Expectations() {{
			mock.hoge(5,6);
			result = 10;

			mock.hoge(anyInt, anyInt);
			result  = 99;

		}};

		//　mock.hoge(5,6)を実行した際の期待値を取得
		assertEquals(10, mock.hoge(5,6));
		assertEquals(99, mock.hoge(99,1234));
	}
```  
  
任意の引数の値と組み合わせる場合は、固定値を先に記載してください。  
  
##### withメソッドの利用  
with～メソッドを使用することで、Expectationsで指定したモックメソッドとして一致するかどうかの判断を柔軟におこなうことが可能です。  
  
|メソッド|説明|  
|:------|:----|  
|with(Delegate<? super T> objectWithDelegateMethod)|引数が一致したかどうかをデリゲートメソッドを用いて判定します。デリゲートメソッドの戻り値がtrueである場合、一致したことを意味します|  
|withEqual(T arg)|指定された値がモック実行時の引数に一致するか確認します。通常は、この方法は使用しないで、目的の引数の値を渡す方法を使用してください。|  
|withEqual(double value, double delta)|deltaで指定した値に近い場合に一致したものとします|  
|withEqual(float value, double delta)|deltaで指定した値に近い場合に一致したものとします|  
|withAny(T arg)|anyBoolean、anyByte、anyChar、anyDouble、anyFloat、anyInt、anyLong、anyShort、anyString、anyを使用することを検討してください。|  
|withNotEqual(T arg)|指定した値以外の場合、一致したものとします|  
|withNotNull()|指定した値がNULL以外の場合、一致したものとします|  
|withNull()|指定した値がNULLの場合、一致したものとします|  
|withInstanceOf(Class<T> argClass)|指定されたクラスのインスタンスであることを確認します。|  
|withInstanceLike(T object)|指定されたオブジェクトと同じクラスのインスタンスであることを確認します。withInstanceOf(object.getClass()) と同等になります|  
|withSameInstance(T object)|まったく同じインスタンスであることを確認します|  
|withPrefix(T text)|特定の文字が含まれた場合、一致したものとみなします|  
|withSubstring(T text)|先頭が指定した文字に一致した場合、一致したものとみなします|  
|withSuffix(T text)|末尾が指定した文字に一致した場合、一致したものとみなします|  
|withMatch(T regex)|正規表現で一致するかどうかを指定できます|  
  
###### withでデリゲートメソッドを使用した例  
withでデリゲートメソッドを使用することでメソッドでモックの引数が一致するかどうかの判定を行うことが可能です。  
  
```java
	@Test
	public void test1_4(@Mocked Hoge001 mock) {
		new Expectations() {{
			mock.hoge(with(new Delegate<Integer>() {
				@Mock boolean validate(int value) {
					return value >= 0;
				}
			}),anyInt);
			result = 99;
		}};


		// xがプラスなのでモックで設定した値に一致する
		assertEquals(99, mock.hoge(1,2));
		// xがマイナスなのでモックで設定した値に一致しない
		assertEquals(0, mock.hoge(-1,2));
	}
```  
  
###### withEqualを使用した例  
基本的にwithEqualを使用するよりリテラルをそのまま使用した方がいいです。しかし、浮動小数点を使用する場合はwithEqualを使用した方がいいでしょう。  
  
```java
	class testWithEqual {
		int test1(double v) {
			return 1000;
		}
		int test2(int v) {
			return 2000;
		}
	}

	@Test
	public void test_withEqual1(@Mocked testWithEqual mock) {
		new Expectations() {{
			mock.test2(withEqual(100));
			result = 99;
		}};
		// 一致する　mock.test2(100)と同じ
		assertEquals(99, mock.test2(100));
		// 一致しない
		assertEquals(0, mock.test2(101));
	}
	@Test
	public void test_withEqual2(@Mocked testWithEqual mock) {
		new Expectations() {{
			mock.test1(withEqual(100, 1));
			result = 99;
		}};
		// 一致する
		assertEquals(99, mock.test1(100.0));
		assertEquals(99, mock.test1(101.0));
		assertEquals(99, mock.test1(99.0));
		// 一致しない
		assertEquals(0, mock.test1(101.1));
		assertEquals(0, mock.test1(98.99));
	}

```  
  
###### withInstanceOf,withInstanceOf,withSameInstanceの例  
withInstanceOf,withInstanceOf,withSameInstanceを使用することで特定のインスタンスと一致するかどうかを確認することが可能です。  
  
```java
	class classA {
	}
	class classB {
	}
	class classX  {
		public int method1(Object obj) {
			return 999;
		}
	}

	@Test
	public void test_withInst1(@Mocked classX mock) {
		new Expectations() {{
			mock.method1(withInstanceOf(classA.class));
			result = 99;
		}};
		// 一致する
		{
			classA obj = new classA();
			assertEquals(99, mock.method1(obj));
		}

		// 一致しない
		{
			classB obj = new classB();
			assertEquals(0, mock.method1(obj));
		}
	}

	@Test
	public void test_withInst2(@Mocked classX mock) {
		new Expectations() {{
			classA objA = new classA();
			mock.method1(withInstanceLike(objA));
			result = 99;
		}};
		// 一致する
		{
			classA obj = new classA();
			assertEquals(99, mock.method1(obj));
		}

		// 一致しない
		{
			classB obj = new classB();
			assertEquals(0, mock.method1(obj));
		}
	}
	@Test
	public void test_withInst3(@Mocked classX mock) {
		classA obj1 = new classA();
		new Expectations() {{
			mock.method1(withSameInstance(obj1));
			result = 99;
		}};
		// 一致する
		{
			assertEquals(99, mock.method1(obj1));
		}

		// 一致しない
		{
			classA obj2 = new classA();
			assertEquals(0, mock.method1(obj2));
		}
	}
```  
  
###### withPrefix,withSubstring,withSuffix,withMatchの例  
withPrefix,withSubstring,withSuffix,withMatchを用いることで文字列の一部が一致するかどうかを調べることが可能です。  
  
```java
	@Test
	public void test_withString1(@Mocked Hoge001 mock) {
		new Expectations() {{
			mock.hoge(withPrefix("abc"));
			result = "test";
		}};

		// 以下は一致する
		assertEquals("test", mock.hoge("abc"));
		assertEquals("test", mock.hoge("abcAA"));

		// 以下は一致しない
		assertEquals(null, mock.hoge("AAabc"));
		assertEquals(null, mock.hoge("AabcA"));
		assertEquals(null, mock.hoge("xx"));
	}

	@Test
	public void test_withString2(@Mocked Hoge001 mock) {
		new Expectations() {{
			mock.hoge(withSuffix("abc"));
			result = "test";
		}};

		// 以下は一致する
		assertEquals("test", mock.hoge("abc"));
		assertEquals("test", mock.hoge("AAabc"));

		// 以下は一致しない
		assertEquals(null, mock.hoge("abcAA"));
		assertEquals(null, mock.hoge("AabcA"));
		assertEquals(null, mock.hoge("xx"));
	}
	@Test
	public void test_withString3(@Mocked Hoge001 mock) {
		new Expectations() {{
			mock.hoge(withSubstring("abc"));
			result = "test";
		}};

		// 以下は一致する
		assertEquals("test", mock.hoge("abc"));
		assertEquals("test", mock.hoge("abcAA"));
		assertEquals("test", mock.hoge("AAabc"));
		assertEquals("test", mock.hoge("AabcA"));

		// 以下は一致しない
		assertEquals(null, mock.hoge("xx"));
	}
	@Test
	public void test_withString4(@Mocked Hoge001 mock) {
		new Expectations() {{
			mock.hoge(withMatch("[0-9]+"));
			result = "test";
		}};

		// 以下は一致する
		assertEquals("test", mock.hoge("1234"));

		// 以下は一致しない
		assertEquals(null, mock.hoge("xxx"));
	}
```  
  
#### インスタンスの作成のされ方でモックメソッドを分ける方法  
Expectationsにてインスタンスの作成のされ方でモックメソッドを分けることが可能です。  
以下の例では「new TestA(10)」を実行して作成したインスタンスにのみモックメソッドを適用するサンプルを示します。  
  
```java
	class TestA {
		public TestA(int x) {

		}
		public int hoge() {
			return 99999;
		}
	}

	@Test
	public void test8(@Mocked TestA mock) {
		new Expectations() {{
			TestA t1 = new TestA(10);
			t1.hoge();
			result = 10;

		}};

		{
			TestA obj = new TestA(10);
			assertEquals(10, obj.hoge());
		}
		{
			TestA obj = new TestA(99);
			assertEquals(0, obj.hoge());
		}
	}
```  
  
#### 例外を発生させる方法  
モックメソッドの処理中に例外を発生させることができます。  
以下の例ではhoge()メソッド実行中にIllegalArgumentExceptionを発生させます。  
  
```java
	// Expectationsでメソッドの例外を返す例
	@Test
	public void test2(@Mocked Hoge001 mock) {
		new Expectations() {{
			mock.hoge(5,6);
			result = 99;
			result = new IllegalArgumentException("test");
		}};
		// Expectationsで設定した1つめの値が取得
		assertEquals(99, mock.hoge(5,6));
		try {
			// Expectationsで設定した2つめの値が取得
			mock.hoge(5,6);
			fail();

		} catch (IllegalArgumentException ex) {
			assertEquals("test", ex.getMessage());
		}
	}
```  
  
#### 実行回数を確認する  
Expectationsでtimes,maxTImes,minTimesを指定することでメソッドの実行回数を指定することが可能です。  
  
|Field|Description|  
|:----|:----------|  
|tiems|実行中に何回メソッドが呼び出されるかを指定します。これと異なる回数、呼び出された場合、エラーとなります。|  
|maxTimes|呼び出されるメソッドの最大回数を指定します。これを上回る回数、呼び出された場合エラーとなります。|  
|minTimes|呼び出されるメソッドの最小回数を指定します。これを下回る回数しか呼び出されない場合エラーとなります。|  
  
  
```java
	@Test
	public void test4_1(@Mocked Hoge001 mock) {
		new Expectations() {{
			mock.hoge(anyInt, anyInt);
			result  = 99;
			times = 3;

		}};
		assertEquals(99, mock.hoge(5,6));
		assertEquals(99, mock.hoge(99,1234));
		assertEquals(99, mock.hoge(3,6));
	}
	// この試験はMissing 2 invocations  が発生してエラーとなります
	@Test
	public void test4_2(@Mocked Hoge001 mock) {
		new Expectations() {{
			mock.hoge(anyInt, anyInt);
			result  = 99;
			times = 3;

		}};
		assertEquals(99, mock.hoge(3,6));
	}

	// この試験はUnexpected invocation が発生してエラーとなります
	@Test
	public void test4_3(@Mocked Hoge001 mock) {
		new Expectations() {{
			mock.hoge(anyInt, anyInt);
			result  = 99;
			times = 3;

		}};
		assertEquals(99, mock.hoge(5,6));
		assertEquals(99, mock.hoge(99,1234));
		assertEquals(99, mock.hoge(3,6));
		assertEquals(99, mock.hoge(3,6));
	}

	@Test
	public void test5_1(@Mocked Hoge001 mock) {
		new Expectations() {{
			mock.hoge(anyInt, anyInt);
			result  = 99;
			minTimes = 3;

		}};
		assertEquals(99, mock.hoge(5,6));
		assertEquals(99, mock.hoge(99,1234));
		assertEquals(99, mock.hoge(3,6));
	}

	// この試験はMissing 2 invocations  が発生してエラーとなります
	@Test
	public void test5_2(@Mocked Hoge001 mock) {
		new Expectations() {{
			mock.hoge(anyInt, anyInt);
			result  = 99;
			minTimes = 3;

		}};
		assertEquals(99, mock.hoge(3,6));
	}
	@Test
	public void test5_3(@Mocked Hoge001 mock) {
		new Expectations() {{
			mock.hoge(anyInt, anyInt);
			result  = 99;
			minTimes = 3;

		}};
		assertEquals(99, mock.hoge(5,6));
		assertEquals(99, mock.hoge(99,1234));
		assertEquals(99, mock.hoge(3,6));
		assertEquals(99, mock.hoge(3,6));
	}
	@Test
	public void test6_1(@Mocked Hoge001 mock) {
		new Expectations() {{
			mock.hoge(anyInt, anyInt);
			result  = 99;
			maxTimes = 3;

		}};
		assertEquals(99, mock.hoge(5,6));
		assertEquals(99, mock.hoge(99,1234));
		assertEquals(99, mock.hoge(3,6));
	}
	@Test
	public void test6_2(@Mocked Hoge001 mock) {
		new Expectations() {{
			mock.hoge(anyInt, anyInt);
			result  = 99;
			maxTimes = 3;

		}};
		assertEquals(99, mock.hoge(3,6));
	}

	// この試験はUnexpected invocation が発生してエラーとなります
	@Test
	public void test6_3(@Mocked Hoge001 mock) {
		new Expectations() {{
			mock.hoge(anyInt, anyInt);
			result  = 99;
			maxTimes = 3;

		}};
		assertEquals(99, mock.hoge(5,6));
		assertEquals(99, mock.hoge(99,1234));
		assertEquals(99, mock.hoge(3,6));
		assertEquals(99, mock.hoge(3,6));
	}
```  
  
#### Delegateを利用したresultのカスタム指定  
モックメソッド実行時に引数に基づいて、モックで返す結果を変更したい場合はDeglegateを使用します。  
下記の例では入力引数の2倍を加えた値を返すモックメソッドを作成しています。  
  
```java
	@Test
	public void test7(@Mocked Hoge001 mock) {
		new Expectations() {{
			mock.hoge(anyInt,anyInt);
			result= new Delegate<Integer>() {
				@SuppressWarnings("unused")
				int aDelegateMethod(int x, int y) {
					return x * 2 + y * 2;

		        }
		    };
		}};
		// Expectationsで設定した1つめの値が取得
		assertEquals(22, mock.hoge(5,6));
	}

```  
  
##### Invocationの使用  
Delegateのメソッドの最初のパラメータとしてInvocationを使用することが可能です。  
Invocationは下記のゲッターを提供しています。  
  
|メソッド|説明|  
|:-------------------|:-----------|  
|getInvocationCount()|呼び出し回数|  
|getInvocationIndex()|現在の呼び出しIndexを取得|  
|getInvokedArguments()|呼び出しに使用した引数を取得|  
|getInvokedInstance()|現在の呼び出しのインスタンス。staticメソッドの場合はnullとなる|  
|getInvokedMember()|呼び出しのメソッド/コンストラクタを取得|  
|proceed(Object... replacementArguments)|実際のメソッド/コンストラクタを実行します|  
  
  
```java
	@Test
	public void testDelegate2(@Mocked Hoge001 mock) {
		new Expectations() {{
			mock.hoge(anyInt,anyInt);
			result= new Delegate<Integer>() {
				@SuppressWarnings("unused")
				int aDelegateMethod(Invocation inv ,int x, int y) {
					System.out.println("--------------------------------");
					// 呼び出し回数
					System.out.format("Invocation getInvocationCount %d \n", inv.getInvocationCount());
					// 現在の呼び出しのインデックス
					System.out.format("Invocation getInvocationIndex() %d \n", inv.getInvocationIndex());
					// 引数を取得
					System.out.println("getInvokedArguments");
					for(Object obj : inv.getInvokedArguments()) {
						System.out.println(obj);
					}
					// インスタンスを取得
					System.out.format("Invocation getInvokedInstance() %s \n", inv.getInvokedInstance().toString());
					// 実際のメソッドを取得
					System.out.format("Invocation getInvokedMember() %s \n", inv.getInvokedMember().toString());
					// 実際のメソッドの実行が可能。
					System.out.format("Invocation  proceed %s \n", inv.proceed().toString());
					// 引数を改ざんして実際のメソッドを実行可能
					System.out.format("Invocation  proceed %s \n", inv.proceed(5,6).toString());
					return 0;
		        }
		    };
		}};
		// Expectationsで設定した1つめの値が取得
		Hoge001 a = new Hoge001();
		Hoge001 b = new Hoge001();
		a.hoge(5,6);
		a.hoge(45,63);
		b.hoge(99,100);
	}
```  
  
上記を実行したコンソールログは以下のようになります。  
  
```
--------------------------------
Invocation getInvocationCount 1 
Invocation getInvocationIndex() 0 
getInvokedArguments
5
6
Invocation getInvokedInstance() SampleProject.Hoge001@2a2d45ba 
Invocation getInvokedMember() public int SampleProject.Hoge001.hoge(int,int) 
Invocation  proceed 11 
Invocation  proceed 11 
--------------------------------
Invocation getInvocationCount 2 
Invocation getInvocationIndex() 1 
getInvokedArguments
45
63
Invocation getInvokedInstance() SampleProject.Hoge001@2a2d45ba 
Invocation getInvokedMember() public int SampleProject.Hoge001.hoge(int,int) 
Invocation  proceed 108 
Invocation  proceed 11 
--------------------------------
Invocation getInvocationCount 3 
Invocation getInvocationIndex() 2 
getInvokedArguments
99
100
Invocation getInvokedInstance() SampleProject.Hoge001@675d3402 
Invocation getInvokedMember() public int SampleProject.Hoge001.hoge(int,int) 
Invocation  proceed 199 
Invocation  proceed 11 
```  
  
#### オブジェクトの一部をモック化する  
すべてのメソッドでなく一部のみをモック化するには以下のようにExpectationsにオブジェクトを渡します。  
  
```java
	@Test
	public void test10() {
		Hoge001 hoge = new Hoge001();
		new Expectations(hoge) {{
			hoge.hoge(5,6);
			result = 99;
		}};
		// モックの結果を返す
		assertEquals(99, hoge.hoge(5,6));
		
		// 実際のメソッドを実行する
		assertEquals(3, hoge.hoge(1,2));
		assertEquals("testabc", hoge.hoge("abc"));

	}
```  
  
### Verifications  
Verifications、VerificationsInOrder、FullVerificationsを使用することでモックオブジェクトがどのように呼び出されたかを明示的に検証することが可能です。  
  
```java
	@Test
	public void test_v1(@Mocked Hoge001 mock) {
		mock.hoge(1,2);
		mock.hoge(2,3);
		mock.hoge(4,5);

		//
		new Verifications() {{
			mock.hoge(anyInt,anyInt);
			times = 3;
			mock.hoge(anyString);
			times = 0;
		}};
		// Verificationsは順番の違いや余計な呼び出しについては合格と見なします
		new Verifications() {{
			mock.hoge(4,5);
			mock.hoge(1,2);
		}};
	}
	@Test
	public void test_v2(@Mocked Hoge001 mock) {
		mock.hoge(1,2);
		mock.hoge(2,3);
		mock.hoge(4,5);

		// VerificationsInOrderは順番が異なるとエラーになります
		/*
		new VerificationsInOrder() {{
			mock.hoge(4,5);
			mock.hoge(1,2);
		}};
		*/
		new VerificationsInOrder() {{
			mock.hoge(1,2);
			mock.hoge(4,5);
		}};
	}
	@Test
	public void test_v3(@Mocked Hoge001 mock) {
		mock.hoge(1,2);
		mock.hoge(2,3);
		mock.hoge(4,5);

		// FullVerificationsでは余計な呼び出しがされているとエラーになります
		/*
		new FullVerifications() {{
			mock.hoge(1,2);
			mock.hoge(4,5);
		}};
		*/
		new FullVerifications() {{
			mock.hoge(1,2);
			mock.hoge(2,3);
			mock.hoge(4,5);
		}};
		// 順番はことなっていても合格となります
		new FullVerifications() {{
			mock.hoge(4,5);
			mock.hoge(2,3);
			mock.hoge(1,2);
		}};
	}
```  
  
##### withCaptureを使用した検証の例  
withCaptureでどのようなパラメータが与えられたインスタンスをListで取得できます。  
  
```java
	// withCaptureでパラメータを確認する例
	@Test
	public void test_v4(@Mocked Hoge001 mock) {
		mock.hoge(1,2);
		mock.hoge(2,3);
		mock.hoge(4,5);

		//
		new Verifications() {{
			List<Integer> argXList = new ArrayList<Integer>();
			List<Integer> argYList = new ArrayList<Integer>();
			mock.hoge(withCapture(argXList),withCapture(argYList));
			assertEquals(3, argXList.size());
			assertEquals(3, argYList.size());

			assertEquals(1, (int)argXList.get(0));
			assertEquals(2, (int)argXList.get(1));
			assertEquals(4, (int)argXList.get(2));

			assertEquals(2, (int)argYList.get(0));
			assertEquals(3, (int)argYList.get(1));
			assertEquals(5, (int)argYList.get(2));

		}};
	}

	// withCaptureでインスタンスの作成を確認する例
	class Person {
		public Person(String name , int age) {
		}
	}
	@Test
	public void test_v5(@Mocked Person mockPerson) {
		new Person("Joe", 10);
		new Person("Sara", 15);
		new Person("Jack", 99);

		//
		new Verifications() {{
			List<Person> created = withCapture(new Person(anyString, anyInt));
			assertEquals(3, created.size());

		}};
	}
```  
  
## Faking API  
Faking APIはFakeの実装の作成のサポートを提供します。 通常、Fakeは、Fakeされるクラス内のいくつかのメソッドやコンストラクタをターゲットにし、他のほとんどのメソッドやコンストラクタは変更されません。  
  
### public/protectedメソッドのFake  
以下の例ではProc1とProc2が存在するクラスのProc1のみFakeしている例です。  
  
```java
package jmockittest;

import static org.junit.Assert.*;

import org.junit.Test;

import mockit.Mock;
import mockit.MockUp;

public class FakeTest {
	class ClassA {
		protected String Proc1() {
			return "...Proc1";
		}
		public String Proc2() {
			return  "Proc2:" + this.Proc1();
		}

	}
	@Test
	public void test1() {
        new MockUp<ClassA>() {

        	@Mock
        	String Proc1() {
        		System.out.print("Proc1");
        		return "xxx";
        	}
        };
        ClassA obj = new ClassA();
        assertEquals("Proc2:xxx", obj.Proc2());
	}
}
```  
  
### Private メソッドのFake  
1.48では無理。以下のようなエラーが出る。  
  
```
java.lang.IllegalArgumentException: Unsupported fake for private method ClassA#Proc1()Ljava/lang/String; found
	at jmockittest.FakeTest$1.<init>(FakeTest.java:22)
	at jmockittest.FakeTest.test1(FakeTest.java:22)

```  
  
おそらく、以前はできていてできなくなった模様。  
https://github.com/jmockit/jmockit1/issues/605  
  
  
### Staticメソッドの例  
StaticメソッドのFakeは可能です。  
下記の例はjava.lang.Math.randomで常に固定値を返す例になります。  
  
```java
	@Test
	public void test() {
        new MockUp<java.lang.Math>() {
        	@Mock
        	public double random() {
        		// 常に2.5を返すrandom()メソッド
        		return 2.5;
        	}
        };
		assertEquals(2.5, Math.random(), 0.1);
		assertEquals(2.5, Math.random(), 0.1);
	}
```  
  
### finailが指定されているメソッドのFakeは作成できるか？  
作成可能でした。  
  
```java
	class ClassB {
		final protected String Proc1() {
			return "...Proc1";
		}
		public String Proc2() {
			return  "Proc2:" + this.Proc1();
		}

	}
	@Test
	public void test3() {
        new MockUp<ClassB>() {

        	@Mock
        	String Proc1() {
        		System.out.print("Proc1");
        		return "xxx";
        	}
        };
        ClassB obj = new ClassB();
        assertEquals("Proc2:xxx", obj.Proc2());
	}
```  
  
### Fakeクラス内の特別なメソッド  
Fakeクラス内で特別なメソッドとして\$init,\$clinit,\$adviceが存在します。  
\$initはコンストラクタをターゲットとしています。  
\$clinitは静的初期化子を対象としています。  
\$adviceはターゲットのクラスの全てのメソッドをあらわします。  
  
**テスト対象**  
  
**ClassC.java**  
```java:ClassC.java
package SampleProject;

public class ClassC {
	public static int sx;
	private int x;
	static {
		sx = 999;
	}
	public ClassC(int x) {
		this.x = x;
	}

	public String Proc1() {
		System.out.format("ClassC Proc1 %d %d\n", sx, this.x);
		return "...Proc1";
	}

}
```  
  
**テストコード**  
  
```java
	@Test
	public void test4() {
        new MockUp<ClassC>() {
        	@Mock
        	void $clinit() {
        		// ClassCのスタティック初期化が動いていないことを確認
        		assertEquals(0, ClassC.sx);
        	}

        	@Mock
        	void $init(int x) {
        		assertEquals(100, x);
        	}

        	@Mock
        	Object $advice(Invocation inv) {
				return "test";
        	}
        };
        ClassC obj = new ClassC(100);
        assertEquals("test", obj.Proc1());

	}
```  
  
### Fakeメソッドの特別なパラメータ  
Fakeメソッドの最初のパラメータに[Invocation](#invocationの使用)を使用することが可能です。  
これを使用して現在時刻にたいして固定値を返すサンプルを下記に示します。  
  
```java
	@Test
	public void testTime() {
		Calendar nowCalendar = Calendar.getInstance();
		System.out.println("現在日時 : " + nowCalendar.getTime());
        new MockUp<Calendar>() {
        	@Mock
        	Calendar getInstance(Invocation inv) {
        		Calendar cal = inv.proceed();
        		cal.set(Calendar.YEAR, 2018);
        		cal.set(Calendar.MONTH, 0);
        		cal.set(Calendar.DAY_OF_MONTH, 1);
        		cal.set(Calendar.HOUR, 22);
        		cal.set(Calendar.MINUTE, 32);
        		cal.set(Calendar.SECOND, 12);
        		cal.set(Calendar.MILLISECOND, 512);
        		return cal;
        	}
        	@Mock
        	Calendar getInstance(Invocation inv, TimeZone zone, Locale aLocale) {
        		Calendar cal = inv.proceed();
        		cal.set(Calendar.YEAR, 2018);
        		cal.set(Calendar.MONTH, 0);
        		cal.set(Calendar.DAY_OF_MONTH, 1);
        		cal.set(Calendar.HOUR, 22);
        		cal.set(Calendar.MINUTE, 32);
        		cal.set(Calendar.SECOND, 12);
        		cal.set(Calendar.MILLISECOND, 512);
        		return cal;
        	}
        };
        final Calendar c = Calendar.getInstance();
		SimpleDateFormat sdf = new SimpleDateFormat("yyyyMMddHHmmssSSS");
        assertEquals("20180102103212512", sdf.format(c.getTime()));

	}
```  
  
## カバレッジの計測  
実行構成でVMの引数を与えることでカバレッジの計測結果を出力することができます。  
  
```
-Dcoverage-output=html -Dcoverage-srcDirs=..\SampleProject\src
```  
  
![image.png](/image/b55cd26c-6bef-b7af-484d-ec6135e02324.png)  
  
![image.png](/image/e2f4a6bb-3ac8-aaf1-ea0a-962adbe2383a.png)  
  
![image.png](/image/d10a9acc-94bc-d9e7-fc1d-eeca29fc1641.png)  
  
  
その他引数は下記を参照してください。  
http://jmockit.github.io/tutorial/CodeCoverage.html  
  
アンドキュメントな動作として「-Dcoverage-output=xml」とするとXMLを出力するようです。  
  
# まとめ  
ここまで調べてなんですが、GitHub上のprivate methodまわりの議論や更新履歴の廃止履歴を観るに、完全で完璧な理想的なテスト環境にいない場合、ちょっと使うのにリスクがある感じがします。  
  
なお、以下でpowermock+mockitoも調べてみました。  
  
**powermock-mockito2-2.0.2を使ってみる**  
https://github.com/mima3/note/blob/master/powermock-mockito2-2.0.2を使ってみる.md  
