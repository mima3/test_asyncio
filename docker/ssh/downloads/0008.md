# 前書き  
C#とPowerShellで色々なDBを操作してみます。  
環境は以下の通りです。  
  
**クライアントの環境**  
  
 - PowerShell 5.1(32bit)  
 - VisualStudio 2019 .NET Framework 4.7.2(32bit)  
  
**操作対象のDatabase**  
  
 - SQLite3  
 - MDB  
 - Ver 15.1 Distrib 5.5.60-MariaDB  
 - PostgreSQL 9.2.24  
 - Oracle12  
 - SQLServer2017  
   
**操作対象のテーブル**  
  
```sql
CREATE TABLE test_tbl
(
  user_name varchar(50),
  age integer
)
```  
  
# PowerShellのusingについて  
PowerShellでのusingを用いたリソースの解放処理が標準で存在していなかったので下記を利用する。  
  
**Dave Wyatt's Blog　Using-Object: PowerShell version of C#’s “using” statement.**  
https://davewyatt.wordpress.com/2014/04/11/using-object-powershell-version-of-cs-using-statement/  
  
```powershell
function Using-Object
{
    [CmdletBinding()]
    param (
        [Parameter(Mandatory = $true)]
        [AllowEmptyString()]
        [AllowEmptyCollection()]
        [AllowNull()]
        [Object]
        $InputObject,

        [Parameter(Mandatory = $true)]
        [scriptblock]
        $ScriptBlock
    )

    try
    {
        . $ScriptBlock
    }
    finally
    {
        if ($null -ne $InputObject -and $InputObject -is [System.IDisposable])
        {
            $InputObject.Dispose()
        }
    }
}
```  
  
# SQLite3  
外部ライブラリのSystem.Data.SQLiteを利用してデータベースの操作を行います。  
  
## 事前準備  
NuGetで下記をインストールする  
  
 - System.Data.SQLite.Core  
  
## C＃  
  
```csharp
using System;
using System.Data.SQLite;

namespace sqliteSample
{
    class Program
    {
        // https://www.ivankristianto.com/howto-make-user-defined-function-in-sqlite-ado-net-with-csharp/
        [SQLiteFunction(Name = "ToUpper", Arguments = 1, FuncType = FunctionType.Scalar)]
        public class ToUpper : SQLiteFunction
        {
            public override object Invoke(object[] args)
            {
                return args[0].ToString().ToUpper();
            }
        }

        static void Main(string[] args)
        {
            if (System.IO.File.Exists("database.db"))
            {
                System.IO.File.Delete("database.db");
            }
            using (var conn = new SQLiteConnection("Data Source=database.db; Version = 3; New = True; Compress = True; "))
            {
                conn.Open();
                
                using (var cmd = new SQLiteCommand("CREATE TABLE test_tbl(user_name varchar(50), age integer)", conn))
                {
                    cmd.ExecuteNonQuery();
                }

                using (var cmd = new SQLiteCommand())
                {
                    cmd.Connection = conn;
                    cmd.CommandText = "INSERT INTO test_tbl (user_name, age) VALUES (@user, @age)";
                    cmd.Parameters.Add(new SQLiteParameter("@user", "aa明日のジョー"));
                    cmd.Parameters.Add(new SQLiteParameter("@age", 17));
                    cmd.ExecuteNonQuery();
                }
                using (var cmd = new SQLiteCommand("SELECT user_name, age FROM test_tbl", conn))
                using (var reader = cmd.ExecuteReader())
                {
                    while (reader.Read())
                    {
                        Console.WriteLine("{0} {1}", reader.GetString(0), reader.GetInt32(1).ToString());
                    }
                }
                // トランザクション
                Console.WriteLine("=================================================");
                Console.WriteLine("トランザクション（ロールバック）");
                using (var tran = conn.BeginTransaction())
                {
                    using (var cmd = new SQLiteCommand())
                    {
                        cmd.Connection = conn;
                        cmd.CommandText = "INSERT INTO test_tbl (user_name, age) VALUES (@user, @age)";
                        cmd.Parameters.Add(new SQLiteParameter("@user", "bb丹下さくら"));
                        cmd.Parameters.Add(new SQLiteParameter("@age", 43));
                        cmd.ExecuteNonQuery();
                    }
                    tran.Rollback();

                }
                using (var cmd = new SQLiteCommand("SELECT user_name, age FROM test_tbl", conn))
                using (var reader = cmd.ExecuteReader())
                {
                    while (reader.Read())
                    {
                        Console.WriteLine("{0} {1}", reader.GetString(0), reader.GetInt32(1).ToString());
                    }
                }
                Console.WriteLine("=================================================");
                Console.WriteLine("トランザクション（コミット）");
                using (var tran = conn.BeginTransaction())
                {
                    using (var cmd = new SQLiteCommand())
                    {
                        cmd.Connection = conn;
                        cmd.CommandText = "INSERT INTO test_tbl (user_name, age) VALUES (@user, @age)";
                        cmd.Parameters.Add(new SQLiteParameter("@user", "bb丹下さくら"));
                        cmd.Parameters.Add(new SQLiteParameter("@age", 43));
                        cmd.ExecuteNonQuery();
                    }
                    tran.Commit();

                }
                using (var cmd = new SQLiteCommand("SELECT user_name, age FROM test_tbl", conn))
                using (var reader = cmd.ExecuteReader())
                {
                    while (reader.Read())
                    {
                        Console.WriteLine("{0} {1}", reader.GetString(0), reader.GetInt32(1).ToString());
                    }
                }


                Console.WriteLine("=================================================");
                Console.WriteLine("ユーザ定義関数");
                using (var cmd = new SQLiteCommand("SELECT ToUpper(user_name) FROM test_tbl", conn))
                using (var reader = cmd.ExecuteReader())
                {
                    while (reader.Read())
                    {
                        Console.WriteLine("{0}", reader.GetString(0));
                    }
                }
                conn.Close();
            }
            Console.ReadLine();
        }
    }
}

```  
  
## PowerShell  
~~C#と異なりユーザ定義関数の実行がうまく行きません。~~（コメント欄参考に実現しました）  
また、今回は調査外としましたが[PSSQLite](https://github.com/RamblingCookieMonster/PSSQLite)というライブラリがあります。  
System.Data.SQLite.dllをラップして使い易くしているようです。  
  
```powershell
using namespace System.Data.SQLite
Add-Type -Path 'System.Data.SQLite.dll'

$source = @"
using System.Data.SQLite;
[SQLiteFunction(Name = "ToUpper", Arguments = 1, FuncType = FunctionType.Scalar)]
public class ToUpper : SQLiteFunction
{
    public override object Invoke(object[] args)
    {
        return args[0].ToString().ToUpper();
    }
}

"@

Add-Type -TypeDefinition $source -ReferencedAssemblies ("C:\dev\ps\database\System.Data.SQLite.dll")


if (Test-Path C:\dev\ps\database\database.db) {
	Remove-Item C:\dev\ps\database\database.db
}
Using-Object ($conn = New-Object SQLiteConnection('Data Source=C:\dev\ps\database\database.db; Version = 3; New = True; Compress = True; ')) {
	$conn.Open()
	Using-Object ($cmd = New-Object SQLiteCommand('CREATE TABLE test_tbl(user_name varchar(50), age integer)', $conn)) {
		$cmd.ExecuteNonQuery() | Out-Null
	}
	Using-Object ($cmd = New-Object SQLiteCommand('INSERT INTO test_tbl (user_name, age) VALUES (@user, @age)', $conn)) {
		$param = New-Object SQLiteParameter("@user", "aa明日のジョー")
		$cmd.Parameters.Add( $param ) | Out-Null
		$param = New-Object SQLiteParameter("@age", 17)
		$cmd.Parameters.Add( $param ) | Out-Null
		$cmd.ExecuteNonQuery() | Out-Null
	}
	Using-Object ($cmd = New-Object SQLiteCommand("SELECT user_name, age FROM test_tbl", $conn)) {
		Using-Object ($reader = $cmd.ExecuteReader()){
		    while ($reader.Read())
		    {
		        Write-Host $reader.GetString(0)  $reader.GetInt32(1).ToString()
		    }
		}
	}

	Write-Host "================================================="
	Write-Host "トランザクション（ロールバック）"
	Using-Object ($tran = $conn.BeginTransaction()) {
		Using-Object ($cmd = New-Object SQLiteCommand('INSERT INTO test_tbl (user_name, age) VALUES (@user, @age)', $conn)) {
			$param = New-Object SQLiteParameter("@user", "bb丹下さくら")
			$cmd.Parameters.Add( $param ) | Out-Null
			$param = New-Object SQLiteParameter("@age", 43)
			$cmd.Parameters.Add( $param ) | Out-Null
			$cmd.ExecuteNonQuery() | Out-Null
		}
	    $tran.Rollback()
	}
	Using-Object ($cmd = New-Object SQLiteCommand("SELECT user_name, age FROM test_tbl", $conn)) {
		Using-Object ($reader = $cmd.ExecuteReader()){
		    while ($reader.Read())
		    {
		        Write-Host $reader.GetString(0)  $reader.GetInt32(1).ToString()
		    }
		}
	}

	Write-Host "================================================="
	Write-Host "トランザクション（コミット）"
	Using-Object ($tran = $conn.BeginTransaction()) {
		Using-Object ($cmd = New-Object SQLiteCommand('INSERT INTO test_tbl (user_name, age) VALUES (@user, @age)', $conn)) {
			$param = New-Object SQLiteParameter("@user", "bb丹下さくら")
			$cmd.Parameters.Add( $param ) | Out-Null
			$param = New-Object SQLiteParameter("@age", 43)
			$cmd.Parameters.Add( $param ) | Out-Null
			$cmd.ExecuteNonQuery() | Out-Null
		}
	    $tran.Commit()
	}
	Using-Object ($cmd = New-Object SQLiteCommand("SELECT user_name, age FROM test_tbl", $conn)) {
		Using-Object ($reader = $cmd.ExecuteReader()){
		    while ($reader.Read())
		    {
		        Write-Host $reader.GetString(0)  $reader.GetInt32(1).ToString()
		    }
		}
	}

	[SQLiteFunction]::RegisterFunction([ToUpper]) 
	Write-Host "================================================="
	Write-Host "ユーザ定義"
	Using-Object ($cmd = New-Object SQLiteCommand("SELECT ToUpper(user_name) FROM test_tbl", $conn)) {
		Using-Object ($reader = $cmd.ExecuteReader()){
		    while ($reader.Read())
		    {
		        Write-Host $reader.GetString(0) 
		    }
		}
	}

	$conn.Close()
}
 
```  
  
  
# MDB  
古いアクセスの拡張子であるMDBは実は32bitに限り、標準で操作可能です。  
COMオブジェクトのMicrosoft ADO Ext(ADOX)を利用してデータベースの作成とテーブルの作成を行います。  
.NETのSystem.Data.OleDbを利用してテーブルの操作を行います。  
  
## 事前準備  
C#の場合は、COMとして「Microsoft ADO Ext」を参照します。  
  
## C＃  
System.Data.OleDbはバインド変数に名前を付けることができないようです。  
  
**What's wrong with these parameters?**  
https://stackoverflow.com/questions/1216271/whats-wrong-with-these-parameters  
  
```csharp
using System;
using System.Data.OleDb;
using System.Runtime.InteropServices;

namespace mdbSample
{
    class Program
    {
        static void Main(string[] args)
        {
            string path = @"C:\dev\ps\database\test.mdb";
            string cnnStr = @"Provider=Microsoft.Jet.OLEDB.4.0; Data Source=" + path;
            if (System.IO.File.Exists(path))
            {
                System.IO.File.Delete(path);
            }
            // 32bitで動かす必要がある
            // https://www.c-sharpcorner.com/uploadfile/mahesh/using-adox-with-ado-net/
            // Microsoft ADO Ext 6.0
            var ct = new ADOX.Catalog();
            var createdObj = ct.Create(cnnStr);
            ADOX.Table tbl = new ADOX.Table();
            tbl.Name = "test_tbl";
            tbl.Columns.Append("user_name", ADOX.DataTypeEnum.adVarWChar, 50);
            tbl.Columns.Append("age", ADOX.DataTypeEnum.adInteger);
            ct.Tables.Append(tbl);
            createdObj.Close();
            Marshal.ReleaseComObject(createdObj);
            Marshal.ReleaseComObject(tbl);
            Marshal.ReleaseComObject(ct);

            using (var conn = new OleDbConnection(cnnStr))
            {
                conn.Open();
                using (var cmd = new OleDbCommand("INSERT INTO test_tbl (user_name, age) VALUES (?, ?)", conn))
                {
                    cmd.Parameters.AddWithValue("@user", "明日のジョー");
                    cmd.Parameters.AddWithValue("@age", 17);
                    cmd.ExecuteNonQuery();

                }
                using (var cmd = new OleDbCommand("SELECT user_name, age FROM test_tbl", conn))
                using (var reader = cmd.ExecuteReader())
                {
                    while (reader.Read())
                    {
                        Console.WriteLine("{0} {1}", reader.GetString(0), reader.GetInt32(1).ToString());
                    }
                }

                // トランザクション
                Console.WriteLine("=================================================");
                Console.WriteLine("トランザクション（ロールバック）");
                using (var tran = conn.BeginTransaction())
                {
                    using (var cmd = new OleDbCommand("INSERT INTO test_tbl (user_name, age) VALUES (?, ?)", conn, tran))
                    {
                        cmd.Parameters.AddWithValue("@user", "丹下さくら");
                        cmd.Parameters.AddWithValue("@age", 43);
                        cmd.ExecuteNonQuery();
                    }
                    tran.Rollback();
                }
                using (var cmd = new OleDbCommand("SELECT user_name, age FROM test_tbl", conn))
                using (var reader = cmd.ExecuteReader())
                {
                    while (reader.Read())
                    {
                        Console.WriteLine("{0} {1}", reader.GetString(0), reader.GetInt32(1).ToString());
                    }
                }
                Console.WriteLine("=================================================");
                Console.WriteLine("トランザクション（コミット）");
                using (var tran = conn.BeginTransaction())
                {
                    using (var cmd = new OleDbCommand("INSERT INTO test_tbl (user_name, age) VALUES (?, ?)", conn, tran))
                    {
                        cmd.Parameters.AddWithValue("@user", "丹下さくら");
                        cmd.Parameters.AddWithValue("@age", 43);
                        cmd.ExecuteNonQuery();
                    }
                    tran.Commit();
                }
                using (var cmd = new OleDbCommand("SELECT user_name, age FROM test_tbl", conn))
                using (var reader = cmd.ExecuteReader())
                {
                    while (reader.Read())
                    {
                        Console.WriteLine("{0} {1}", reader.GetString(0), reader.GetInt32(1).ToString());
                    }
                }
            }
            Console.ReadLine();
        }
    }
}

```  
  
## PowerShell  
  
```powershell
	using namespace System.Data.OleDb
	using namespace System.Runtime.InteropServices


	$path = "C:\dev\ps\database\test.mdb"
	if (Test-Path $path) {
		Remove-Item $path
	}
	$cnnStr = "Provider=Microsoft.Jet.OLEDB.4.0; Data Source=$path"
	$ct = New-Object -ComObject "ADOX.Catalog"
	$createdObj = $ct.Create($cnnStr)
	$tbl = New-Object -ComObject "ADOX.Table"
	$tbl.Name = "test_tbl"
	$tbl.Columns.Append("user_name", 202, 50)
	$tbl.Columns.Append("age", 3)
	$ct.Tables.Append($tbl)
	$createdObj.Close()
	[Marshal]::ReleaseComObject($createdObj) | Out-Null
	[Marshal]::ReleaseComObject($tbl) | Out-Null
	[Marshal]::ReleaseComObject($ct) | Out-Null

	Using-Object ($conn = New-Object OleDbConnection($cnnStr)) {
		$conn.Open()

		Using-Object ($cmd = New-Object OleDbCommand('INSERT INTO test_tbl (user_name, age) VALUES (?, ?)', $conn)) {
			$cmd.Parameters.AddWithValue("@user", "明日のジョー") | Out-Null
			$cmd.Parameters.AddWithValue("@age", 17) | Out-Null
			$cmd.ExecuteNonQuery() | Out-Null
		}

		Using-Object ($cmd = New-Object OleDbCommand("SELECT user_name, age FROM test_tbl", $conn)) {
			Using-Object ($reader = $cmd.ExecuteReader()){
			    while ($reader.Read())
			    {
			        Write-Host $reader.GetString(0)  $reader.GetInt32(1).ToString()
			    }
			}
		}
		Write-Host "================================================="
		Write-Host "トランザクション（ロールバック）"
		Using-Object ($tran = $conn.BeginTransaction()) {
		    Using-Object ($cmd = New-Object OleDbCommand("INSERT INTO test_tbl (user_name, age) VALUES (?, ?)", $conn, $tran)) {
		        $cmd.Parameters.AddWithValue("@user", "丹下さくら") | Out-Null
		        $cmd.Parameters.AddWithValue("@age", 43) | Out-Null
		        $cmd.ExecuteNonQuery() | Out-Null
		    }
		    $tran.Rollback()
		}
		Using-Object ($cmd = New-Object OleDbCommand("SELECT user_name, age FROM test_tbl", $conn)) {
			Using-Object ($reader = $cmd.ExecuteReader()){
			    while ($reader.Read())
			    {
			        Write-Host $reader.GetString(0)  $reader.GetInt32(1).ToString()
			    }
			}
		}

		Write-Host "================================================="
		Write-Host "トランザクション（コミット）"
		Using-Object ($tran = $conn.BeginTransaction()) {
		    Using-Object ($cmd = New-Object OleDbCommand("INSERT INTO test_tbl (user_name, age) VALUES (?, ?)", $conn, $tran)) {
		        $cmd.Parameters.AddWithValue("@user", "丹下さくら") | Out-Null
		        $cmd.Parameters.AddWithValue("@age", 43) | Out-Null
		        $cmd.ExecuteNonQuery() | Out-Null
		    }
		    $tran.Commit()
		}
		Using-Object ($cmd = New-Object OleDbCommand("SELECT user_name, age FROM test_tbl", $conn)) {
			Using-Object ($reader = $cmd.ExecuteReader()){
			    while ($reader.Read())
			    {
			        Write-Host $reader.GetString(0)  $reader.GetInt32(1).ToString()
			    }
			}
		}
	}
```  
  
# MariaDB/MySQL  
MySQLのインストーラについてくるMySql.Data.dllを利用して操作を行います。  
今回はMariaDBを対象としましたがMySQLも同様に動作すると思います。  
  
## 事前準備  
下記からMySQLのインストーラを手にいれてMySql.Data.dllを手に入れます。  
https://dev.mysql.com/doc/connector-net/en/connector-net-installation-binary-mysql-installer.html  
  
既定では以下にインストールされるので、参照してください。  
C:\Program Files (x86)\MySQL\MySQL Installer for Windows\MySql.Data.dll  
  
また下記のストアドプロシージャを作成しておきます。  
  
```sql
CREATE PROCEDURE test_sp(IN from_age integer, IN to_age integer)
BEGIN
  SELECT test_tbl.user_name,test_tbl.age FROM test_tbl
                            WHERE test_tbl.age BETWEEN from_age AND to_age;

END

```  
  
## C＃  
```csharp
// 以下を参照
//C:\Program Files (x86)\MySQL\MySQL Installer for Windows\MySql.Data.dll
using MySql.Data.MySqlClient;
using System;

namespace mysqlSample
{
    class Program
    {
        static void Main(string[] args)
        {
            // https://dev.mysql.com/doc/connector-net/en/connector-net-installation-binary-mysql-installer.html
            // https://dev.mysql.com/doc/connector-net/en/connector-net-tutorials-connection.html
            string connStr = "server=192.168.80.131;user=root;database=test;port=3306;password=root";
            using (var conn = new MySqlConnection(connStr))
            {
                try
                {
                    Console.WriteLine("Connecting to MySQL...");
                    conn.Open();

                    using (var cmd = new MySqlCommand("truncate table test_tbl", conn))
                    {
                        cmd.ExecuteNonQuery();
                    }

                    using (var cmd = new MySqlCommand("INSERT INTO test_tbl (user_name, age) VALUES (@user, @age)", conn))
                    {
                        cmd.Parameters.AddWithValue("@user", "明日のジョー");
                        cmd.Parameters.AddWithValue("@age", 17);
                        cmd.ExecuteNonQuery();

                    }
                    using (var cmd = new MySqlCommand("SELECT user_name, age FROM test_tbl", conn))
                    using (var reader = cmd.ExecuteReader())
                    {
                        while (reader.Read())
                        {
                            Console.WriteLine("{0} {1}", reader.GetString(0), reader.GetInt32(1).ToString());
                        }
                    }

                    // トランザクション
                    Console.WriteLine("=================================================");
                    Console.WriteLine("トランザクション（ロールバック）");
                    using (var tran = conn.BeginTransaction())
                    {
                        // Perform database operations
                        using (var cmd = new MySqlCommand("INSERT INTO test_tbl (user_name, age) VALUES (@user, @age)", conn))
                        {
                            cmd.Parameters.AddWithValue("@user", "丹下さくら");
                            cmd.Parameters.AddWithValue("@age", 43);
                            cmd.ExecuteNonQuery();
                        }
                        tran.Rollback();
                    }
                    using (var cmd = new MySqlCommand("SELECT user_name, age FROM test_tbl", conn))
                    using (var reader = cmd.ExecuteReader())
                    {
                        while (reader.Read())
                        {
                            Console.WriteLine("{0} {1}", reader.GetString(0), reader.GetInt32(1).ToString());
                        }
                    }
                    Console.WriteLine("=================================================");
                    Console.WriteLine("トランザクション（コミット）");
                    using (var tran = conn.BeginTransaction())
                    {
                        // Perform database operations
                        using (var cmd = new MySqlCommand("INSERT INTO test_tbl (user_name, age) VALUES (@user, @age)", conn))
                        {
                            cmd.Parameters.AddWithValue("@user", "丹下さくら");
                            cmd.Parameters.AddWithValue("@age", 43);
                            cmd.ExecuteNonQuery();
                        }
                        tran.Commit();
                    }
                    using (var cmd = new MySqlCommand("SELECT user_name, age FROM test_tbl", conn))
                    using (var reader = cmd.ExecuteReader())
                    {
                        while (reader.Read())
                        {
                            Console.WriteLine("{0} {1}", reader.GetString(0), reader.GetInt32(1).ToString());
                        }
                    }

                    Console.WriteLine("=================================================");
                    Console.WriteLine("ストアド");
                    using (var cmd = new MySqlCommand("call test_sp(@from, @to)", conn))
                    {
                        cmd.Parameters.AddWithValue("@from", 10);
                        cmd.Parameters.AddWithValue("@to", 19);
                        using (var reader = cmd.ExecuteReader())
                        {
                            while (reader.Read())
                            {
                                Console.WriteLine("{0} {1}", reader.GetString(0), reader.GetInt32(1).ToString());
                            }
                        }
                    }
                    conn.Close();
                }
                catch (Exception ex)
                {
                    Console.WriteLine(ex.ToString());
                }
            }
            Console.WriteLine("Done.");
            Console.ReadLine();
        }
    }
}

```  
  
## PowerShell  
  
```powershell
using namespace MySql.Data.MySqlClient
Add-Type -Path 'MySql.Data.dll'

Using-Object ($conn = New-Object MySqlConnection('server=192.168.80.131;user=root;database=test;port=3306;password=root')) {
	$conn.Open()
	Using-Object ($cmd = New-Object MySqlCommand('truncate table test_tbl', $conn)) {
		$cmd.ExecuteNonQuery() | Out-Null
	}

	Using-Object ($cmd = New-Object MySqlCommand('INSERT INTO test_tbl (user_name, age) VALUES (@user, @age)', $conn)) {
		$cmd.Parameters.AddWithValue("@user", "明日のジョー") | Out-Null
		$cmd.Parameters.AddWithValue("@age", 17) | Out-Null
		$cmd.ExecuteNonQuery() | Out-Null
	}

	Using-Object ($cmd = New-Object MySqlCommand("SELECT user_name, age FROM test_tbl", $conn)) {
		Using-Object ($reader = $cmd.ExecuteReader()){
		    while ($reader.Read())
		    {
		        Write-Host $reader.GetString(0)  $reader.GetInt32(1).ToString()
		    }
		}
	}
	
	Write-Host "================================================="
	Write-Host "トランザクション（ロールバック）"
	Using-Object ($tran = $conn.BeginTransaction()) {
	    Using-Object ($cmd = New-Object MySqlCommand('INSERT INTO test_tbl (user_name, age) VALUES (@user, @age)', $conn)) {
			$cmd.Parameters.AddWithValue("@user", "丹下さくら") | Out-Null
			$cmd.Parameters.AddWithValue("@age", 43) | Out-Null
			$cmd.ExecuteNonQuery() | Out-Null
	    }
	    $tran.Rollback()
	}
	Using-Object ($cmd = New-Object MySqlCommand("SELECT user_name, age FROM test_tbl", $conn)) {
		Using-Object ($reader = $cmd.ExecuteReader()){
		    while ($reader.Read())
		    {
		        Write-Host $reader.GetString(0)  $reader.GetInt32(1).ToString()
		    }
		}
	}
	Write-Host "================================================="
	Write-Host "トランザクション（コミット）"
	Using-Object ($tran = $conn.BeginTransaction()) {
	    Using-Object ($cmd = New-Object MySqlCommand('INSERT INTO test_tbl (user_name, age) VALUES (@user, @age)', $conn)) {
			$cmd.Parameters.AddWithValue("@user", "丹下さくら") | Out-Null
			$cmd.Parameters.AddWithValue("@age", 43) | Out-Null
			$cmd.ExecuteNonQuery() | Out-Null
	    }
	    $tran.Commit()
	}
	Using-Object ($cmd = New-Object MySqlCommand("SELECT user_name, age FROM test_tbl", $conn)) {
		Using-Object ($reader = $cmd.ExecuteReader()){
		    while ($reader.Read())
		    {
		        Write-Host $reader.GetString(0)  $reader.GetInt32(1).ToString()
		    }
		}
	}

	Write-Host "================================================="
	Write-Host "ストアド"
	Using-Object ($cmd = New-Object MySqlCommand('call test_sp(@from, @to)', $conn)) {
		$cmd.Parameters.AddWithValue("@from", 10) | Out-Null
		$cmd.Parameters.AddWithValue("@to", 19) | Out-Null
		$cmd.ExecuteNonQuery() | Out-Null
	}
	Using-Object ($cmd = New-Object MySqlCommand("SELECT user_name, age FROM test_tbl", $conn)) {
		Using-Object ($reader = $cmd.ExecuteReader()){
		    while ($reader.Read())
		    {
		        Write-Host $reader.GetString(0)  $reader.GetInt32(1).ToString()
		    }
		}
	}
	$conn.Close()
}
 
```  
  
# PostgreSQL   
外部ライブラリのNpgsqlを利用して操作を行います。  
  
## 事前準備  
NugetでNpgsqlをインストールします。  
下記のストアドプロシージャを作成します。  
  
```sql
CREATE OR REPLACE FUNCTION test_sp(IN from_age integer, IN to_age integer)
  RETURNS TABLE(user_name varchar(50), age integer) AS
$$
DECLARE
BEGIN
    RETURN QUERY SELECT test_tbl.user_name,test_tbl.age FROM test_tbl
            WHERE test_tbl.age BETWEEN from_age AND to_age;
END;
$$ LANGUAGE plpgsql;
```  
  
## C＃  
  
```csharp

using Npgsql;
using System;

namespace DbSample
{
    class Program
    {
        static void Main(string[] args)
        {
            var connString = "Host=192.168.80.131;Username=postgres;Password=postgres;Database=test";

            using (var conn = new NpgsqlConnection(connString))
            {
                conn.Open();

                //
                using (var cmd = new NpgsqlCommand())
                {
                    cmd.Connection = conn;
                    cmd.CommandText = "truncate table test_tbl";
                    cmd.ExecuteNonQuery();
                }

                // Insert some data
                using (var cmd = new NpgsqlCommand())
                {
                    cmd.Connection = conn;
                    cmd.CommandText = "INSERT INTO test_tbl (user_name, age) VALUES (@user, @age)";
                    cmd.Parameters.AddWithValue("user", "明日のジョー");
                    cmd.Parameters.AddWithValue("age", 17);
                    cmd.ExecuteNonQuery();
                }

                // Retrieve all rows
                using (var cmd = new NpgsqlCommand("SELECT user_name, age FROM test_tbl", conn))
                using (var reader = cmd.ExecuteReader())
                {
                    while (reader.Read())
                    {
                        Console.WriteLine("{0} {1}", reader.GetString(0), reader.GetInt32(1).ToString());
                    }
                }
                // トランザクション
                Console.WriteLine("=================================================");
                Console.WriteLine("トランザクション（ロールバック）");
                using (var tran = conn.BeginTransaction())
                {
                    using (var cmd = new NpgsqlCommand())
                    {
                        cmd.Connection = conn;
                        cmd.CommandText = "INSERT INTO test_tbl (user_name, age) VALUES (@user, @age)";
                        cmd.Parameters.AddWithValue("user", "丹下サクラ");
                        cmd.Parameters.AddWithValue("age", 43);
                        cmd.ExecuteNonQuery();
                    }
                    tran.Rollback();
                }
                using (var cmd = new NpgsqlCommand("SELECT user_name, age FROM test_tbl", conn))
                using (var reader = cmd.ExecuteReader())
                {
                    while (reader.Read())
                    {
                        Console.WriteLine("{0} {1}", reader.GetString(0), reader.GetInt32(1).ToString());
                    }
                }
                // 
                // トランザクション
                Console.WriteLine("=================================================");
                Console.WriteLine("トランザクション（コミット）");
                using (var tran = conn.BeginTransaction())
                {
                    using (var cmd = new NpgsqlCommand())
                    {
                        cmd.Connection = conn;
                        cmd.CommandText = "INSERT INTO test_tbl (user_name, age) VALUES (@user, @age)";
                        cmd.Parameters.AddWithValue("user", "丹下サクラ");
                        cmd.Parameters.AddWithValue("age", 43);
                        cmd.ExecuteNonQuery();
                    }
                    tran.Commit();
                }
                using (var cmd = new NpgsqlCommand("SELECT user_name, age FROM test_tbl", conn))
                using (var reader = cmd.ExecuteReader())
                {
                    while (reader.Read())
                    {
                        Console.WriteLine("{0} {1}", reader.GetString(0), reader.GetInt32(1).ToString());
                    }
                }
                // ストアドの試験
                Console.WriteLine("=================================================");
                Console.WriteLine("ストアドファンクション");
                using (var cmd = new NpgsqlCommand("SELECT user_name, age FROM test_sp(@fromage,@toage)", conn))
                {
                    cmd.Parameters.AddWithValue("fromage", 10);
                    cmd.Parameters.AddWithValue("toage", 19);

                    using (var reader = cmd.ExecuteReader())
                    {
                        while (reader.Read())
                        {
                            Console.WriteLine("{0} {1}", reader.GetString(0), reader.GetInt32(1).ToString());
                        }
                    }
                }
            }
        }
    }
}

```  
  
## PowerShell  
  
```powershell
using namespace Npgsql
try {
    Add-Type -Path 'System.Runtime.CompilerServices.Unsafe.dll'
    Add-Type -Path 'System.Threading.Tasks.Extensions.dll'
    Add-Type -Path 'System.Memory.dll'
    Add-Type -Path 'Npgsql.dll'
} catch [System.Reflection.ReflectionTypeLoadException] {
    $_.Exception.LoaderExceptions
}

Using-Object ($conn = New-Object NpgsqlConnection('Host=192.168.80.131;Username=postgres;Password=postgres;Database=test')) {
	$conn.Open()
	Using-Object ($cmd = New-Object NpgsqlCommand('truncate table test_tbl', $conn)) {
		$cmd.ExecuteNonQuery() | Out-Null
	}

	Using-Object ($cmd = New-Object NpgsqlCommand('INSERT INTO test_tbl (user_name, age) VALUES (@user, @age)', $conn)) {
		$cmd.Parameters.AddWithValue("user", "明日のジョー") | Out-Null
		$cmd.Parameters.AddWithValue("age", 17) | Out-Null
		$cmd.ExecuteNonQuery() | Out-Null
	}

	Using-Object ($cmd = New-Object NpgsqlCommand("SELECT user_name, age FROM test_tbl", $conn)) {
		Using-Object ($reader = $cmd.ExecuteReader()){
		    while ($reader.Read())
		    {
		        Write-Host $reader.GetString(0)  $reader.GetInt32(1).ToString()
		    }
		}
	}
	
	Write-Host "================================================="
	Write-Host "トランザクション（ロールバック）"
	Using-Object ($tran = $conn.BeginTransaction()) {
	    Using-Object ($cmd = New-Object NpgsqlCommand('INSERT INTO test_tbl (user_name, age) VALUES (@user, @age)', $conn)) {
			$cmd.Parameters.AddWithValue("user", "丹下さくら") | Out-Null
			$cmd.Parameters.AddWithValue("age", 43) | Out-Null
			$cmd.ExecuteNonQuery() | Out-Null
	    }
	    $tran.Rollback()
	}
	Using-Object ($cmd = New-Object NpgsqlCommand("SELECT user_name, age FROM test_tbl", $conn)) {
		Using-Object ($reader = $cmd.ExecuteReader()){
		    while ($reader.Read())
		    {
		        Write-Host $reader.GetString(0)  $reader.GetInt32(1).ToString()
		    }
		}
	}
	Write-Host "================================================="
	Write-Host "トランザクション（コミット）"
	Using-Object ($tran = $conn.BeginTransaction()) {
	    Using-Object ($cmd = New-Object NpgsqlCommand('INSERT INTO test_tbl (user_name, age) VALUES (@user, @age)', $conn)) {
			$cmd.Parameters.AddWithValue("user", "丹下さくら") | Out-Null
			$cmd.Parameters.AddWithValue("age", 43) | Out-Null
			$cmd.ExecuteNonQuery() | Out-Null
	    }
	    $tran.Commit()
	}
	Using-Object ($cmd = New-Object NpgsqlCommand("SELECT user_name, age FROM test_tbl", $conn)) {
		Using-Object ($reader = $cmd.ExecuteReader()){
		    while ($reader.Read())
		    {
		        Write-Host $reader.GetString(0)  $reader.GetInt32(1).ToString()
		    }
		}
	}

	Write-Host "================================================="
	Write-Host "ストアド"
	Using-Object ($cmd = New-Object NpgsqlCommand('SELECT user_name, age FROM test_sp(@fromage,@toage)', $conn)) {
		$cmd.Parameters.AddWithValue("@fromage", 10) | Out-Null
		$cmd.Parameters.AddWithValue("@toage", 19) | Out-Null
		Using-Object ($reader = $cmd.ExecuteReader()){
		    while ($reader.Read())
		    {
		        Write-Host $reader.GetString(0)
		    }
		}
	}
	$conn.Close()
}
 
```  
  
# Oracle12  
外部ライブラリのOracle.ManagedDataAccessを利用して操作をします。  
  
## 事前準備  
NugetでOracle.ManagedDataAccessをインストールします。  
  
## C＃  
  
```csharp
using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using Oracle.ManagedDataAccess.Client;

namespace OracleSample
{
    class Program
    {
        static void Main(string[] args)
        {
            string cnnStr = "user id=system;password=oracle;data source=" +
                             "(DESCRIPTION=(ADDRESS=(PROTOCOL=tcp)" +
                             "(HOST=192.168.99.102)(PORT=1521))(CONNECT_DATA=" +
                             "(SERVICE_NAME=orcl)))";
            using (var conn = new OracleConnection(cnnStr))
            {
                conn.Open();
                using (var cmd = new OracleCommand("truncate table test_tbl", conn))
                {
                    cmd.ExecuteNonQuery();
                }
                using (var cmd = new OracleCommand("INSERT INTO test_tbl (user_name, age) VALUES (:userName, :age)", conn))
                {
                    cmd.Parameters.Add( new OracleParameter("userName", "明日のジョー"));
                    cmd.Parameters.Add( new OracleParameter("age", 17));
                    cmd.ExecuteNonQuery();

                }
                using (var cmd = new OracleCommand("SELECT user_name, age FROM test_tbl", conn))
                using (var reader = cmd.ExecuteReader())
                {
                    while (reader.Read())
                    {
                        Console.WriteLine("{0} {1}", reader.GetString(0), reader.GetInt32(1).ToString());
                    }
                }

                // トランザクション
                Console.WriteLine("=================================================");
                Console.WriteLine("トランザクション（ロールバック）");
                using (var tran = conn.BeginTransaction())
                {
                    // Perform database operations
                    using (var cmd = new OracleCommand("INSERT INTO test_tbl (user_name, age) VALUES (:userName, :age)", conn))
                    {
                        cmd.Parameters.Add(new OracleParameter("userName", "丹下さくら"));
                        cmd.Parameters.Add(new OracleParameter("age", 43));
                        cmd.ExecuteNonQuery();
                    }
                    tran.Rollback();
                }
                using (var cmd = new OracleCommand("SELECT user_name, age FROM test_tbl", conn))
                using (var reader = cmd.ExecuteReader())
                {
                    while (reader.Read())
                    {
                        Console.WriteLine("{0} {1}", reader.GetString(0), reader.GetInt32(1).ToString());
                    }
                }

                Console.WriteLine("=================================================");
                Console.WriteLine("トランザクション（コミット）");
                using (var tran = conn.BeginTransaction())
                {
                    // Perform database operations
                    using (var cmd = new OracleCommand("INSERT INTO test_tbl (user_name, age) VALUES (:userName, :age)", conn))
                    {
                        cmd.Parameters.Add(new OracleParameter("userName", "丹下さくら"));
                        cmd.Parameters.Add(new OracleParameter("age", 43));
                        cmd.ExecuteNonQuery();
                    }
                    tran.Commit();
                }
                using (var cmd = new OracleCommand("SELECT user_name, age FROM test_tbl", conn))
                using (var reader = cmd.ExecuteReader())
                {
                    while (reader.Read())
                    {
                        Console.WriteLine("{0} {1}", reader.GetString(0), reader.GetInt32(1).ToString());
                    }
                }
                conn.Close();
            }
            Console.ReadLine();
        }
    }
}

```  
  
## PowerShell  
  
```powershell
using namespace Oracle.ManagedDataAccess.Client
Add-Type -Path 'Oracle.ManagedDataAccess.dll'


Using-Object ($conn = New-Object OracleConnection('user id=system;password=oracle;data source=(DESCRIPTION=(ADDRESS=(PROTOCOL=tcp)(HOST=192.168.99.102)(PORT=1521))(CONNECT_DATA=(SERVICE_NAME=orcl)))')) {
	$conn.Open()
	Using-Object ($cmd = New-Object OracleCommand('truncate table test_tbl', $conn)) {
		$cmd.ExecuteNonQuery() | Out-Null
	}

	Using-Object ($cmd = New-Object OracleCommand('INSERT INTO test_tbl (user_name, age) VALUES (:userName, :age)', $conn)) {
		$param = New-Object OracleParameter("userName", "明日のジョー")
		$cmd.Parameters.Add( $param ) | Out-Null
		$param = New-Object OracleParameter("age", 17)
		$cmd.Parameters.Add( $param ) | Out-Null
		$cmd.ExecuteNonQuery() | Out-Null
	}

	Using-Object ($cmd = New-Object OracleCommand("SELECT user_name, age FROM test_tbl", $conn)) {
		Using-Object ($reader = $cmd.ExecuteReader()){
		    while ($reader.Read())
		    {
		        Write-Host $reader.GetString(0)  $reader.GetInt32(1).ToString()
		    }
		}
	}
	
	Write-Host "================================================="
	Write-Host "トランザクション（ロールバック）"
	Using-Object ($tran = $conn.BeginTransaction()) {
	    Using-Object ($cmd = New-Object OracleCommand('INSERT INTO test_tbl (user_name, age) VALUES (:userName, :age)', $conn)) {
			$param = New-Object OracleParameter("userName", "丹下さくら")
			$cmd.Parameters.Add( $param ) | Out-Null
			$param = New-Object OracleParameter("age", 43)
			$cmd.Parameters.Add( $param ) | Out-Null
			$cmd.ExecuteNonQuery() | Out-Null
	    }
	    $tran.Rollback()
	}
	Using-Object ($cmd = New-Object OracleCommand("SELECT user_name, age FROM test_tbl", $conn)) {
		Using-Object ($reader = $cmd.ExecuteReader()){
		    while ($reader.Read())
		    {
		        Write-Host $reader.GetString(0)  $reader.GetInt32(1).ToString()
		    }
		}
	}
	Write-Host "================================================="
	Write-Host "トランザクション（コミット）"
	Using-Object ($tran = $conn.BeginTransaction()) {
	    Using-Object ($cmd = New-Object OracleCommand('INSERT INTO test_tbl (user_name, age) VALUES (:userName, :age)', $conn)) {
			$param = New-Object OracleParameter("userName", "丹下さくら")
			$cmd.Parameters.Add( $param ) | Out-Null
			$param = New-Object OracleParameter("age", 43)
			$cmd.Parameters.Add( $param ) | Out-Null
			$cmd.ExecuteNonQuery() | Out-Null
	    }
	    $tran.Commit()
	}
	Using-Object ($cmd = New-Object OracleCommand("SELECT user_name, age FROM test_tbl", $conn)) {
		Using-Object ($reader = $cmd.ExecuteReader()){
		    while ($reader.Read())
		    {
		        Write-Host $reader.GetString(0)  $reader.GetInt32(1).ToString()
		    }
		}
	}
	$conn.Close()
}
 
```  
  
# SQLServer  
標準についているSystem.Data.SqlClientを使用します。  
  
## 事前準備  
事前に下記のストアドプロシージャを作成します。  
  
```sql
CREATE PROCEDURE test_sp(@from int, @to int)
AS
BEGIN
    SET NOCOUNT ON;
    SELECT user_name, age FROM test_tbl
        WHERE age BETWEEN @from  AND  @to;
END
GO
```  
  
## C＃  
  
```csharp
using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using System.Data;
using System.Data.SqlClient;

namespace mssqlSample
{
    class Program
    {
        static void Main(string[] args)
        {
            string cnnString = @"Data Source=.\SQLEXPRESS;Initial Catalog=test;User ID=sa;Password=sa";
            using (var conn = new SqlConnection(cnnString))
            {
                conn.Open();
                using (var cmd = new SqlCommand("truncate table test_tbl", conn))
                {
                    cmd.ExecuteNonQuery();
                }
                using (var cmd = new SqlCommand("INSERT INTO test_tbl (user_name, age) VALUES (@user, @age)", conn))
                {
                    cmd.Parameters.AddWithValue("@user", "明日のジョー");
                    cmd.Parameters.AddWithValue("@age", 17);
                    cmd.ExecuteNonQuery();

                }
                using (var cmd = new SqlCommand("SELECT user_name, age FROM test_tbl", conn))
                using (var reader = cmd.ExecuteReader())
                {
                    while (reader.Read())
                    {
                        Console.WriteLine("{0} {1}", reader.GetString(0), reader.GetInt32(1).ToString());
                    }
                }

                // トランザクション
                Console.WriteLine("=================================================");
                Console.WriteLine("トランザクション（ロールバック）");
                using (var tran = conn.BeginTransaction())
                {
                    // Perform database operations
                    using (var cmd = new SqlCommand("INSERT INTO test_tbl (user_name, age) VALUES (@user, @age)", conn, tran))
                    {
                        cmd.Parameters.AddWithValue("@user", "丹下さくら");
                        cmd.Parameters.AddWithValue("@age", 43);
                        cmd.ExecuteNonQuery();
                    }
                    tran.Rollback();
                }
                using (var cmd = new SqlCommand("SELECT user_name, age FROM test_tbl", conn))
                using (var reader = cmd.ExecuteReader())
                {
                    while (reader.Read())
                    {
                        Console.WriteLine("{0} {1}", reader.GetString(0), reader.GetInt32(1).ToString());
                    }
                }
                Console.WriteLine("=================================================");
                Console.WriteLine("トランザクション（コミット）");
                using (var tran = conn.BeginTransaction())
                {
                    // Perform database operations
                    using (var cmd = new SqlCommand("INSERT INTO test_tbl (user_name, age) VALUES (@user, @age)", conn, tran))
                    {
                        cmd.Parameters.AddWithValue("@user", "丹下さくら");
                        cmd.Parameters.AddWithValue("@age", 43);
                        cmd.ExecuteNonQuery();
                    }
                    tran.Commit();
                }
                using (var cmd = new SqlCommand("SELECT user_name, age FROM test_tbl", conn))
                using (var reader = cmd.ExecuteReader())
                {
                    while (reader.Read())
                    {
                        Console.WriteLine("{0} {1}", reader.GetString(0), reader.GetInt32(1).ToString());
                    }
                }

                Console.WriteLine("=================================================");
                Console.WriteLine("ストアド");
                using (var cmd = new SqlCommand("EXEC test_sp @from, @to", conn))
                {
                    cmd.Parameters.AddWithValue("@from", 10);
                    cmd.Parameters.AddWithValue("@to", 19);
                    using (var reader = cmd.ExecuteReader())
                    {
                        while (reader.Read())
                        {
                            Console.WriteLine("{0} {1}", reader.GetString(0), reader.GetInt32(1).ToString());
                        }
                    }

                }
                conn.Close();
            }
            Console.ReadLine();
        }
    }
}

```  
  
## PowerShell  
  
```powershell
using namespace System.Data.SqlClient

Using-Object ($conn = New-Object SqlConnection('Data Source=.\SQLEXPRESS;Initial Catalog=test;User ID=sa;Password=sa')) {
	$conn.Open()
	Using-Object ($cmd = New-Object SqlCommand('truncate table test_tbl', $conn)) {
		$cmd.ExecuteNonQuery() | Out-Null
	}

	Using-Object ($cmd = New-Object SqlCommand('INSERT INTO test_tbl (user_name, age) VALUES (@user, @age)', $conn)) {
		$cmd.Parameters.AddWithValue("@user", "明日のジョー") | Out-Null
		$cmd.Parameters.AddWithValue("@age", 17) | Out-Null
		$cmd.ExecuteNonQuery() | Out-Null
	}

	Using-Object ($cmd = New-Object SqlCommand("SELECT user_name, age FROM test_tbl", $conn)) {
		Using-Object ($reader = $cmd.ExecuteReader()){
		    while ($reader.Read())
		    {
		        Write-Host $reader.GetString(0)  $reader.GetInt32(1).ToString()
		    }
		}
	}
	
	Write-Host "================================================="
	Write-Host "トランザクション（ロールバック）"
	Using-Object ($tran = $conn.BeginTransaction()) {
	    Using-Object ($cmd = New-Object SqlCommand("INSERT INTO test_tbl (user_name, age) VALUES (@user, @age)", $conn, $tran)) {
	        $cmd.Parameters.AddWithValue("@user", "丹下さくら") | Out-Null
	        $cmd.Parameters.AddWithValue("@age", 43) | Out-Null
	        $cmd.ExecuteNonQuery() | Out-Null
	    }
	    $tran.Rollback()
	}
	Using-Object ($cmd = New-Object SqlCommand("SELECT user_name, age FROM test_tbl", $conn)) {
		Using-Object ($reader = $cmd.ExecuteReader()){
		    while ($reader.Read())
		    {
		        Write-Host $reader.GetString(0)  $reader.GetInt32(1).ToString()
		    }
		}
	}

	Write-Host "================================================="
	Write-Host "トランザクション（コミット）"
	Using-Object ($tran = $conn.BeginTransaction()) {
	    Using-Object ($cmd = New-Object SqlCommand("INSERT INTO test_tbl (user_name, age) VALUES (@user, @age)", $conn, $tran)) {
	        $cmd.Parameters.AddWithValue("@user", "丹下さくら") | Out-Null
	        $cmd.Parameters.AddWithValue("@age", 43) | Out-Null
	        $cmd.ExecuteNonQuery() | Out-Null
	    }
	    $tran.Commit()
	}
	Using-Object ($cmd = New-Object SqlCommand("SELECT user_name, age FROM test_tbl", $conn)) {
		Using-Object ($reader = $cmd.ExecuteReader()){
		    while ($reader.Read())
		    {
		        Write-Host $reader.GetString(0)  $reader.GetInt32(1).ToString()
		    }
		}
	}

	Write-Host "================================================="
	Write-Host "ストアド"
	Using-Object ($cmd = New-Object SqlCommand('EXEC test_sp @from, @to', $conn)) {
		$cmd.Parameters.AddWithValue("@from", 10) | Out-Null
		$cmd.Parameters.AddWithValue("@to", 19) | Out-Null
		$cmd.ExecuteNonQuery() | Out-Null
	}

	Using-Object ($cmd = New-Object SqlCommand("SELECT user_name, age FROM test_tbl", $conn)) {
		Using-Object ($reader = $cmd.ExecuteReader()){
		    while ($reader.Read())
		    {
		        Write-Host $reader.GetString(0)  $reader.GetInt32(1).ToString()
		    }
		}
	}
	$conn.Close()
}
 
```  
  
# まとめ  
今回はC#やPowerShellでの各種データベースの取り扱いをまとめました。  
基本的な操作は全てのDBで同じようなインターフェイスで行われていることがわかります。  
