LiquidFunは流体とか軟体を扱うためのライブラリで、Box2dをベースに実装しています。  
基本的にC++で実装されていますが、JavaまたはJavaScriptからも使用できます。  
今回はAndroidからJavaでLiquidFunを利用する方法について説明します。  
  
![device-2015-03-26-191808.png](/image/9b02cacd-ad4b-edac-5b04-cb125f978b55.png)  
  
 **LiquidFunTest**  
https://www.youtube.com/watch?v=kAaiJtDYa9Q  
  
 **GitHub**   
https://github.com/mima3/LiquidFunTest  
  
JavaScriptで使いたい場合は下記を参考にしてください。  
  
 **流体とか軟体を扱えるLiquidFunをJavaScriptで100%利用する**   
http://qiita.com/mima_ita/items/3e903f89952aea07b924  
  
## Javaで使えるようにする  
以下からliquidfun-x.x.x.zipをダウンロードして任意のフォルダに解凍します。  
https://github.com/google/liquidfun/releases  
  
  
JavaからLiquidfunを使用するには、SWIGとAndroid NDKを使用してビルドをする必要があります。  
ここでは、Debian7を開発環境とします。  
  
### Android NDKのインストール方法  
以下から、適切なNDKをダウンロードします。  
https://developer.android.com/tools/sdk/ndk/index.html  
  
ダウンロード後に、「android-ndk-r10d-linux-x86_64.bin」を実行すると「android-ndk-r10d」というフォルダが作成されます。  
  
もしかしたら、「android-ndk-r10d-linux-x86_64.bin」実行時に下記のエラーが出るかもしれません。  
  
```
./android-ndk-r10d-linux-x86_64.bin: /lib/x86_64-linux-gnu/libc.so.6: version `GLIBC_2.14' not found (required by ./android-ndk-r10d-linux-x86_64.bin)
```  
  
この場合は、libc6が古いので下記のページを参考に更新してください。  
  
http://stackoverflow.com/questions/10863613/how-to-upgrade-glibc-from-version-2-13-to-2-15-on-debian  
  
### SWIGのインストール方法  
SWINGは、C/C++で記述されたプログラムを様々な言語に接続するためのツールです。  
Debianでは、apt-getでインストールすることができます。  
  
```
apt-get install swig
```  
  
あるいは、下記からソースコードを入手してビルドしてください。  
http://www.swig.org/download.html  
  
なお、3.0.5でビルドした場合エラーになります。  
その対応については次項で解説します。  
  
  
### LiquidFunのビルド  
liquidfun/Box2D/swigをビルドします。  
公式のドキュメントは下記のURLです。  
https://google.github.io/liquidfun/Building/html/md__building_android.html  
  
・・・がSWIGについて記述がないようですので、以下のようにやるといいでしょう。  
  
```
cd liquidfun/Box2D/swig
ndk-build APP_ABI=all
```  
  
これにより以下のファイルが作成されます。  
  
 **Javaのファイル**   
liquidfun/Box2D/swig/gen/com/google/fpl/liquidfun  
  
 **libliquidfun.so,libliquidfun_jni.so**   
liquidfun/Box2D/swig/libs  
soファイルはプラットフォーム毎に作成されます。  
  
#### SWIGでエラーが発生した場合  
3.0.5でビルドした場合、以下のエラーが発生しました。  
  
```
Processing nested classes...
Generating wrappers...
[armeabi-v7a] Compile++ arm  : liquidfun_jni <= liquidfun_wrap.cpp
jni/../gen/cpp/armeabi-v7a/liquidfun_wrap.cpp: In member function 'virtual void SwigDirector_Draw::DrawPolygon(const b2Vec2*, int32, const b2Color&)':
jni/../gen/cpp/armeabi-v7a/liquidfun_wrap.cpp:707:52: error: exception handling disabled, use -fexceptions to enable
       throw Swig::DirectorException(jenv, swigerror);
```  
  
この場合は、swig/jni/Android.mkに以下のフラグを追加します。  
  
```
LOCAL_CFLAGS += -fexceptions
```  
  
## AndroidStudio1.1でのNDKを利用する  
### AndroidStudioの設定  
AndroidStudio1.0と基本的に同じです。  
  
 **Android NDK Sample with Android Studio 1.0**   
http://qiita.com/abekatsu/items/31459d11284623277668  
  
  
1.local.propertyを修正します。  
  
```
ndk.dir=C\:\\tool\\android-ndk-r10d
```  
  
今回は、AndroidStudioの外部でビルドしたので、この設定は不要かもしれません。  
  
  
2.Module.appのbuild.gradleの修正  
  
``` build.gradle
apply plugin: 'com.android.application'

android {
    compileSdkVersion 21
    buildToolsVersion "21.1.2"

    defaultConfig {
        applicationId "jp.ne.needtec.liquidfuntest"
        minSdkVersion 10
        targetSdkVersion 21
        versionCode 1
        versionName "1.0"
    }
    buildTypes {
        release {
            minifyEnabled false
            proguardFiles getDefaultProguardFile('proguard-android.txt'), 'proguard-rules.pro'
        }
    }
    sourceSets.main {
        jniLibs.srcDir 'src/main/libs'
        jni.srcDirs = []
        //jni.srcDirs = ['src/main/jni'] //disable automatic ndk-build call
    }
    productFlavors {

        'armeabi' {
            flavorDimension "abi"
            ndk {
                abiFilter "armeabi"
            }
        }

        'armeabi-v7a' {
            flavorDimension "abi"
            ndk {
                abiFilter "armeabi-v7a"
            }
        }

        'arm64-v8a' {
            flavorDimension "abi"
            ndk {
                abiFilter "arm64-v8a"
            }
        }

        'mips' {
            flavorDimension "mips"
            ndk {
                abiFilter "mips"
            }
        }

        'mips64' {
            flavorDimension "mips64"
            ndk {
                abiFilter "mips64"
            }
        }

        'x86' {
            flavorDimension "abi"
            ndk {
                abiFilter "x86"
            }
        }

        'x86_64' {
            flavorDimension "abi"
            ndk {
                abiFilter "x86_64"
            }
        }

        'fat' {
            flavorDimension "abi"

        }
    }

    project.ext.versionCodes = ['armeabi':1,
                                'armeabi-v7a':2,
                                'arm64-v8a':3,
                                'mips':5,
                                'mips64':6,
                                'x86':8,
                                'x86_64':9] //versionCode digit for each supported ABI, with 64bit>32bit and x86>armeabi-*

    // make per-variant version code
    applicationVariants.all { variant ->
        // assign different version code for each output
        variant.outputs.each { output ->
            output.versionCodeOverride =
                    project.ext.versionCodes.get(output.getFilter(com.android.build.OutputFile.ABI), 0) * 1000000 + defaultConfig.versionCode
        }
    }
}

dependencies {
    compile fileTree(dir: 'libs', include: ['*.jar'])
    compile 'com.android.support:appcompat-v7:21.0.3'
}
```  
  
sourceSetsでjniをおくフォルダを指定するのと、productFlavorsでプラットフォームごとのビルドを行えるようにします。  
  
3.libliquidfun.so,libliquidfun_jni.soのコピー  
Debianで作成した「liquidfun/Box2D/swig/libs」からAndroidStudioのフォルダ「\AndroidStudioProjects\LiquidFunTest\app\src\main\libs」にコピーします。  
  
4.swigで作成したJavaファイルのコピー  
Debianで作成した「liquidfun/Box2D/swig/gen/com/google/fpl/liquidfun」からAndroidStudioのフォルダ「\AndroidStudioProjects\LiquidFunTest\app\src\main\java」にコピーします。  
  
### コードの例  
以下のように、Liquidfunのオブジェクトの操作が行えます。  
  
```java
import com.google.fpl.liquidfun.World;
world = new World(0, -10);
```  
  
その他のサンプルは下記を参照してください。  
https://github.com/mima3/LiquidFunTest/blob/master/app/src/main/java/jp/ne/needtec/liquidfuntest/MainRenderer.java  
  
  
### 実行方法  
実行するプラットフォームごとに異なるapkを使用することに注意してください。  
たとえば、VMPalyer + Android-x86を使用している場合は「Build Variants」で「x86Debug」を選択して実行します。  
  
![AndroidExe1.png](/image/fae6d590-ad46-5066-d82e-ab35b9247c09.png)  
  
あるいは、SO-02G XPERIAで実行する場合は、「Build Variants」で「armeabiDebug」を選択して実行します。  
  
## まとめ  
ここではLiquidFunをAndroidで動作させる方法について解説しました。  
これにより、流体を利用した表現を行うことが可能になります。  
  
しかしながら、デフォルトのJavaで使用できる関数はC++でサポートされている関数の一部にすぎません。  
必要に応じて、b2Settings.swigなどを修正する必要があります。  
