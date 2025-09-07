# まえがき  
以前、[こんな記事](https://github.com/mima3/note/blob/master/RPA九人衆による「ｱｶﾈﾁｬﾝｶﾜｲｲﾔｯﾀ」の自動化.md)を書いたことがあります。  
色々な方法でWindowsのGUIの自動操作を行う方法を記載しましたが、PowerShellで**画像認識**を利用した自動操作については逃げました。  
  
今回は宿題として残っていたPowerShellとOpenCVを使用して画像認識での自動操作を行ってみます。  
  
考え方としてはスクリーンキャプチャした内容をMatに変換して[Template Matching](https://opencv-python-tutroals.readthedocs.io/en/latest/py_tutorials/py_imgproc/py_template_matching/py_template_matching.html)を行うだけです。  
  
  
  
# OpenCVの.NET用のラッパー  
OpenCVには.NET用のラッパーとしてOpenCvSharpが存在します。  
https://github.com/shimat/opencvsharp/releases  
  
このライブラリをNugetまたは上記のページからダウンロードしてください。  
注意点として、ネイティブのDLLを使うことになるので32bit、64bitのどちらのプロセスで動作しているか、意識してDLLを利用してください。  
  
## C#のサンプル  
VisualStudio 2019の.NET Framework4.0で作成したサンプルは以下のようになります。  
  
```csharp
using OpenCvSharp;
using System;
using System.Collections.Generic;
using System.Drawing;
using System.Runtime.InteropServices;
using System.Windows.Forms;

namespace OpenCv
{
    public class GuiAuto
    {
        // https://culage.hatenablog.com/entry/20130611/1370876400
        [DllImport("user32.dll")]
        extern static uint SendInput(uint nInputs, INPUT[] pInputs, int cbSize);

        [StructLayout(LayoutKind.Sequential)]
        struct INPUT
        {
            public int type;
            public MOUSEINPUT mi;
        }

        [StructLayout(LayoutKind.Sequential)]
        struct MOUSEINPUT
        {
            public int dx;
            public int dy;
            public int mouseData;
            public int dwFlags;
            public int time;
            public IntPtr dwExtraInfo;
        }

        const int MOUSEEVENTF_LEFTDOWN = 0x0002;
        const int MOUSEEVENTF_LEFTUP = 0x0004;

        static public void Click()
        {
            //struct 配列の宣言
            INPUT[] input = new INPUT[2];
            //左ボタン Down
            input[0].mi.dwFlags = MOUSEEVENTF_LEFTDOWN;
            //左ボタン Up
            input[1].mi.dwFlags = MOUSEEVENTF_LEFTUP;
            //イベントの一括生成
            SendInput(2, input, Marshal.SizeOf(input[0]));
        }

        static public void Move(int x, int y)
        {
            var pt = new System.Drawing.Point(x, y);
            System.Windows.Forms.Cursor.Position = pt;
        }

        public class TemplateResult
        {
            public int TargetWidth { set; get; }
            public int TargetHeight { set; get; }

            public List<OpenCvSharp.Point> MatchList { set; get; }

            public TemplateResult()
            {
                this.MatchList = new List<OpenCvSharp.Point>();
            }
        }



        static public TemplateResult MatchTemplate(int ScreenNo, string targetPath, double threshold) 
        {
            TemplateResult result = new TemplateResult();
            var screen = Screen.AllScreens[ScreenNo];

            Bitmap bitmap = new Bitmap(screen.Bounds.Width, screen.Bounds.Height);
            Graphics graphics = Graphics.FromImage(bitmap as Image);
            graphics.CopyFromScreen(screen.Bounds.X, screen.Bounds.Y, 0, 0, bitmap.Size);

            using (var targetImg = Cv2.ImRead(targetPath))
            using (var img = OpenCvSharp.Extensions.BitmapConverter.ToMat(bitmap))
            using (var img3ch = img.CvtColor(ColorConversionCodes.BGRA2BGR))
            {
                result.TargetWidth = targetImg.Width;
                result.TargetHeight = targetImg.Height;

                var tmplRet = img3ch.MatchTemplate(targetImg, TemplateMatchModes.CCoeffNormed);
                double minVal, maxVal;
                OpenCvSharp.Point minLoc, maxLoc;
                tmplRet.MinMaxLoc(out minVal, out maxVal, out minLoc, out maxLoc);
                Mat thresholdRet = tmplRet.Threshold(threshold, 1.0, ThresholdTypes.Tozero);
                while (true)
                {
                    thresholdRet.MinMaxLoc(out minVal, out maxVal, out minLoc, out maxLoc);
                    if (maxVal < threshold)
                    {
                        break;
                    }
                    result.MatchList.Add(maxLoc);
                    thresholdRet.FloodFill(maxLoc, 0);
                }
            }
            return result;
        }

        static public bool ClickImg(int ScreenNo, string targetPath, double threshold, int offsetX, int offsetY)
        {
            TemplateResult tmplRet = MatchTemplate(ScreenNo, targetPath, threshold);
            if (tmplRet.MatchList.Count == 0)
            {
                return false;
            }
            var screen = Screen.AllScreens[ScreenNo];

            Move(screen.Bounds.X + tmplRet.MatchList[0].X, screen.Bounds.Y + tmplRet.MatchList[0].Y);
            Click();
            return true;
        }
        static public bool ClickImg(int ScreenNo, string targetPath, double threshold)
        {
            TemplateResult tmplRet = MatchTemplate(ScreenNo, targetPath, threshold);
            if (tmplRet.MatchList.Count == 0)
            {
                return false;
            }
            var screen = Screen.AllScreens[ScreenNo];

            Move(screen.Bounds.X + tmplRet.MatchList[0].X + tmplRet.TargetWidth/ 2, screen.Bounds.Y + tmplRet.MatchList[0].Y + tmplRet.TargetHeight / 2);
            Click();
            return true;
        }
    }

    class Program
    {


        static void Main(string[] args)
        {
            Console.ReadLine();
            var targetPath = @"target.bmp";
            GuiAuto.ClickImg(0, targetPath, 0.75);
        }
    }
}
```  
  
このサンプルはスクリーン上に存在するtarget.bmpの画像を検索してクリックするものとなっています。  
やっている内容としてはOpenCvのチュートリアルの[Template Matching](https://opencv-python-tutroals.readthedocs.io/en/latest/py_tutorials/py_imgproc/py_template_matching/py_template_matching.html)と似たようなことです。  
MatchTemplateは複数の類似画像の位置を取得できるようにFloodFillを実施してループしていますが、常に最も一致した画像だけを取得するならループは不要です。  
  
あとは、取得した位置をもとにマウスを移動してクリックしています。  
なお、マルチディスプレイを考慮しているので、ClickImgのScreenNoを変更することで別のスクリーンを検索することが可能です。  
  
スクリーン上の画像の取得は.NETのよくあるキャプチャ処理で、取得したBitmapオブジェクトはOpenCvSharp.Extensions.BitmapConverter.ToMatで行っています。  
  
OpenCvSharpは.NET2.0でも動作するのですが、どうも.NET2.0ではOpenCvSharp.Extensions.dllを提供していないようです。  
自前で[BitmapConvert.cs](https://github.com/shimat/opencvsharp/blob/master/src/OpenCvSharp.Extensions/BitmapConverter.cs)と同様な処理を実装すればできるかもしれませんが、.NET3.5までは簡単にできましたが、.NET2.0ではうまくいきませんでした。  
  
## PowerShell 5.1の例  
Windows10 Home + PowerShell5.1でもC#と同様のことが行えます。  
  
まず、DLLを以下のように配置します。  
![image.png](/image/add7285c-125b-c9b8-aadc-6ff1833a61c3.png)  
  
OpenCvSharpExtern.dllは使用するPowerShellがx86の場合はx86,x64の場合はx64を使用してください。  
  
次に以下のようなスクリプトを記述して実行します。  
  
```powershell
$source = @"
using OpenCvSharp;
using System;
using System.Collections.Generic;
using System.Drawing;
using System.Runtime.InteropServices;
using System.Windows.Forms;
public class GuiAuto
{
    // https://culage.hatenablog.com/entry/20130611/1370876400
    [DllImport("user32.dll")]
    extern static uint SendInput(uint nInputs, INPUT[] pInputs, int cbSize);

    [StructLayout(LayoutKind.Sequential)]
    struct INPUT
    {
        public int type;
        public MOUSEINPUT mi;
    }

    [StructLayout(LayoutKind.Sequential)]
    struct MOUSEINPUT
    {
        public int dx;
        public int dy;
        public int mouseData;
        public int dwFlags;
        public int time;
        public IntPtr dwExtraInfo;
    }

    const int MOUSEEVENTF_LEFTDOWN = 0x0002;
    const int MOUSEEVENTF_LEFTUP = 0x0004;

    static public void Click()
    {
        //struct 配列の宣言
        INPUT[] input = new INPUT[2];
        //左ボタン Down
        input[0].mi.dwFlags = MOUSEEVENTF_LEFTDOWN;
        //左ボタン Up
        input[1].mi.dwFlags = MOUSEEVENTF_LEFTUP;
        //イベントの一括生成
        SendInput(2, input, Marshal.SizeOf(input[0]));
    }

    static public void Move(int x, int y)
    {
        var pt = new System.Drawing.Point(x, y);
        System.Windows.Forms.Cursor.Position = pt;
    }

    public class TemplateResult
    {
        public int TargetWidth { set; get; }
        public int TargetHeight { set; get; }

        public List<OpenCvSharp.Point> MatchList { set; get; }

        public TemplateResult()
        {
            this.MatchList = new List<OpenCvSharp.Point>();
        }
    }

    static public TemplateResult MatchTemplate(int ScreenNo, string targetPath, double threshold) 
    {
        TemplateResult result = new TemplateResult();
        var screen = Screen.AllScreens[ScreenNo];

        Bitmap bitmap = new Bitmap(screen.Bounds.Width, screen.Bounds.Height);
        Graphics graphics = Graphics.FromImage(bitmap as Image);
        graphics.CopyFromScreen(screen.Bounds.X, screen.Bounds.Y, 0, 0, bitmap.Size);

        using (var targetImg = Cv2.ImRead(targetPath))
        using (var img = OpenCvSharp.Extensions.BitmapConverter.ToMat(bitmap))
        using (var img3ch = img.CvtColor(ColorConversionCodes.BGRA2BGR))
        {
            result.TargetWidth = targetImg.Width;
            result.TargetHeight = targetImg.Height;

            var tmplRet = img3ch.MatchTemplate(targetImg, TemplateMatchModes.CCoeffNormed);
            double minVal, maxVal;
            OpenCvSharp.Point minLoc, maxLoc;
            tmplRet.MinMaxLoc(out minVal, out maxVal, out minLoc, out maxLoc);
            Mat thresholdRet = tmplRet.Threshold(threshold, 1.0, ThresholdTypes.Tozero);
            while (true)
            {
                thresholdRet.MinMaxLoc(out minVal, out maxVal, out minLoc, out maxLoc);
                if (maxVal < threshold)
                {
                    break;
                }
                result.MatchList.Add(maxLoc);
                thresholdRet.FloodFill(maxLoc, 0);
            }
        }
        return result;
    }

    static public bool ClickImg(int ScreenNo, string targetPath, double threshold, int offsetX, int offsetY)
    {
        TemplateResult tmplRet = MatchTemplate(ScreenNo, targetPath, threshold);
        if (tmplRet.MatchList.Count == 0)
        {
            return false;
        }
        var screen = Screen.AllScreens[ScreenNo];

        Move(screen.Bounds.X + tmplRet.MatchList[0].X, screen.Bounds.Y + tmplRet.MatchList[0].Y);
        Click();
        return true;
    }
    static public bool ClickImg(int ScreenNo, string targetPath, double threshold)
    {
        TemplateResult tmplRet = MatchTemplate(ScreenNo, targetPath, threshold);
        if (tmplRet.MatchList.Count == 0)
        {
            return false;
        }
        var screen = Screen.AllScreens[ScreenNo];

        Move(screen.Bounds.X + tmplRet.MatchList[0].X + tmplRet.TargetWidth/ 2, screen.Bounds.Y + tmplRet.MatchList[0].Y + tmplRet.TargetHeight / 2);
        Click();
        return true;
    }
}
"@
$dllPath = Split-Path $MyInvocation.MyCommand.Path
Set-Item Env:Path "$Env:Path;$dllPath"

Write-Host $currentDir
$assemblies = @(
    "$dllPath\OpenCVSharp.dll", 
    "$dllPath\OpenCvSharp.Extensions.dll", 
    "System.Runtime", 
    "System.Windows.Forms", 
    "System.Drawing"
)
Add-Type -TypeDefinition $source -ReferencedAssemblies $assemblies
Add-Type -Path "$dllPath\OpenCVSharp.dll"
Add-Type -Path "$dllPath\OpenCVSharp.Extensions.dll"
[GuiAuto]::ClickImg(0, "C:\dev\ps\opencv\target.bmp", 0.75)

```  
  
## 実行結果  
**target.bmp**  
![image.png](/image/b7a70a12-8508-aca9-cc99-82f96af81534.png)  
  
  
**画面の状態**  
![image.png](/image/7e8910ad-915a-dc08-5bd9-375970002dcc.png)  
  
  
## 初期状態のWindows7のPowerShellでできないか？  
難しいです。  
理由として初期状態のWindows7では.NET3.5とPowerShell2.0が入っていますが、このPowerShell2.0はどんな新しい.NET Frameworkが入っていても.NET2.0を使用してしまいます。  
  
**PowerShellでdllを読み込む際の注意点**  
https://qiita.com/icoxfog417/items/e0d29bed109071888f19  
  
このため、[BitmapConvert.cs](https://github.com/shimat/opencvsharp/blob/master/src/OpenCvSharp.Extensions/BitmapConverter.cs)と同様の処理が、うまく実装できませんでした。  
  
やるなら、.NET Framework3.5でコマンドラインツールを作成して、PowerShellから呼び出す用な形になると思います（当然、起動時にオーバーヘッドがかかります）  
  
# まとめ  
画像認識とかいうと難しく考えがちですが、OpenCvを利用すれば、わりと簡単に画像を利用した自動操作を自前でつくれます。  
ただし、あまり古すぎる環境だと辛いです。  
