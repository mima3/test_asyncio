# Javaのバイトコードを解析した結果をクラス図やコールグラフで表現する  
## 目的  
Javaのバイトコードからクラスやメソッドの情報を抜き出してSqliteに記録します。  
上記の記録した情報を用いてクラス図やコールグラフを記載します。  
  
なお、doxygen + graphviz使える人は、それを使ったほうがいいです。  
  
## 使用環境  
・Windows10  
・Java8  
・bcel-6.3.1.  
・sqlite-jdbc-3.27.2.1  
・plantuml.jar  
  
## 使用ライブラリの解説  
### bcel  
BCEL API（バイトコードエンジニアリングライブラリ）は、静的分析および動的なJavaクラスファイルの作成のツールキットです。  
FindBugはBCELを使用してクラスファイルから静的解析を行っています。  
  
![bcel.png](/image/651ec926-321f-b299-d74c-c01e4fa4d1e1.png)  
  
  
https://commons.apache.org/proper/commons-bcel/manual/introduction.html  
  
#### サンプルコード  
JavaSE BCEL  
https://hondou.homedns.org/pukiwiki/index.php?JavaSE%20BCEL  
  
またバイトコードのバイナリをどう解釈するかは以下のcodeToStringが参考になります。  
https://github.com/llmhyy/commons-bcel/blob/master/src/main/java/org/apache/bcel/classfile/Utility.java  
  
### Sqlite-JDBC  
SQLiteを操作するJDBCで下記のページからダウンロードできます。  
  
ダウンロード  
https://bitbucket.org/xerial/sqlite-jdbc/downloads/  
  
  
#### サンプルコード  
  
```java
package sqlitesample;

import java.sql.Connection;
import java.sql.DriverManager;
import java.sql.PreparedStatement;
import java.sql.ResultSet;
import java.sql.SQLException;
import java.sql.Statement;

import org.sqlite.Function;

public class SqliteSample {
	public static void main(String[] args) throws ClassNotFoundException {
		System.out.println("start-----");
		// load the sqlite-JDBC driver using the current class loader
		Class.forName("org.sqlite.JDBC");

		Connection connection = null;
		Statement statement = null;
		ResultSet rs = null;
		PreparedStatement pstmt = null;

		try
		{
			// create a database connection
			// Connection connection = DriverManager.getConnection("jdbc:sqlite:C:/work/mydatabase.db");
			// Connection connection = DriverManager.getConnection("jdbc:sqlite::memory:");
			connection = DriverManager.getConnection("jdbc:sqlite:sample.db");
			connection.setAutoCommit(true);
			statement = connection.createStatement();
			statement.setQueryTimeout(30);	// set timeout to 30 sec.

			System.out.println("create table -----");
			statement.executeUpdate("drop table if exists person");
			statement.executeUpdate("create table person (id integer, name string)");
			statement.executeUpdate("insert into person values(1, 'leo')");
			statement.executeUpdate("insert into person values(2, 'yui')");
			rs = statement.executeQuery("select * from person");
			while(rs.next())
			{
				// read the result set
				System.out.println("name = " + rs.getString("name"));
				System.out.println("id = " + rs.getInt("id"));
			}
			rs.close();
			rs = null;

			System.out.println("update -----");
			pstmt = connection.prepareStatement("update person set name = ? where id = ?");
			pstmt.setString(1, "ole");
			pstmt.setInt(2, 1);
			pstmt.executeUpdate();
			rs = statement.executeQuery("select * from person");
			while(rs.next())
			{
				// read the result set
				System.out.println("name = " + rs.getString("name"));
				System.out.println("id = " + rs.getInt("id"));
			}
			rs.close();
			rs = null;


			System.out.println("Transactions -----");
			connection.setAutoCommit(false);
			statement.executeUpdate("insert into person values(3, 'zoo')");
			rs = statement.executeQuery("select * from person");
			while(rs.next())
			{
				// read the result set
				System.out.println("name = " + rs.getString("name"));
				System.out.println("id = " + rs.getInt("id"));
			}
			rs.close();
			rs = null;
			System.out.println("rollback -----");
			connection.rollback();
			rs = statement.executeQuery("select * from person");
			while(rs.next())
			{
				// read the result set
				System.out.println("name = " + rs.getString("name"));
				System.out.println("id = " + rs.getInt("id"));
			}
			rs.close();
			rs = null;

			System.out.println("function -----");
	        Function.create(connection, "total", new Function() {
	            @Override
	            protected void xFunc() throws SQLException
	            {
	                int sum = 0;
	                for (int i = 0; i < args(); i++)
	                    sum += value_int(i);
	                result(sum);
	            }
	        });
			rs = statement.executeQuery("select total(1, 2, 3, 4, 5)");
			while(rs.next())
			{
				// read the result set
				System.out.println("total(1,2,3,4,5) = " + rs.getInt(1));
			}
			rs.close();
			rs = null;

		}
		catch(SQLException e)
		{
			// if the error message is "out of memory",
			// it probably means no database file is found
			System.err.println(e.getMessage());
		}
		finally
		{
			try
			{
				if(rs != null)
				{
					rs.close();
				}
				if(pstmt != null)
				{
					pstmt.close();
				}
				if(statement != null)
				{
					statement.close();
				}
				if(connection != null)
				{
				connection.close();
				}
			}
			catch(SQLException e)
			{
				// connection close failed.
				System.err.println(e);
			}
		}
	}
}

```  
  
ユーザ定義関数とかも作成できます。  
その他、SQLite固有の操作については下記のテストコードが参考になります。  
https://github.com/xerial/sqlite-jdbc/tree/c7c5604bcc584460268abc9a64df2953fca788d3/src/test/java/org/sqlite  
  
  
### PlantUML  
DSLといわれる言語でUMLを含めた以下の図を記載できます。  
  
- シーケンス図  
- ユースケース図  
- クラス図  
- アクティビティ図（古い文法はこちら）  
- コンポーネント図  
- 状態遷移図（ステートマシン図）  
- オブジェクト図  
- 配置図   
- タイミング図   
- ワイヤーフレーム  
- アーキテクチャ図  
- 仕様及び記述言語 (SDL)  
- Ditaa  
- ガントチャート  
- マインドマップ   
- WBS図(作業分解図)   
- AsciiMath や JLaTeXMath による、数学的記法  
  
公式でWebページから実際の記載を試せます。  
[Redmineのプラグイン](https://github.com/mima3/note/blob/master/RedmineのWikiでUMLを記述する方法.md)もあるのでWikiにテキストデータとして各種図を埋め込むことができます。  
  
公式：  
http://plantuml.com/ja/  
  
ダウンロード  
http://plantuml.com/ja/download  
  
#### サンプル  
PlantUML Cheat Sheet  
https://qiita.com/ogomr/items/0b5c4de7f38fd1482a48  
  
plantuml.jarファイルを自分のJavaのプロジェクトに組み込むことで、自分のプログラムからPNGやSVGを出力することも可能です。  
http://plantuml.com/ja/api  
  
## 実験結果  
https://github.com/mima3/BcelToSqlite  
  
### bcelを使用してSqliteを記録する  
以下のコードではJarファイルを指定して、そこに格納されているclassファイルを解析してクラス、メソッド、フィールドの情報をSQLiteに記録しています。  
  
**BcelToSqlite.java**  
```java:BcelToSqlite.java

package bcelToSqlite;

import java.io.File;
import java.io.FileInputStream;
import java.io.IOException;
import java.sql.Connection;
import java.sql.DriverManager;
import java.sql.PreparedStatement;
import java.sql.SQLException;
import java.util.jar.JarEntry;
import java.util.jar.JarInputStream;

import org.apache.bcel.Const;
import org.apache.bcel.classfile.AnnotationEntry;
import org.apache.bcel.classfile.ClassFormatException;
import org.apache.bcel.classfile.ClassParser;
import org.apache.bcel.classfile.Constant;
import org.apache.bcel.classfile.ConstantPool;
import org.apache.bcel.classfile.Field;
import org.apache.bcel.classfile.JavaClass;
import org.apache.bcel.classfile.Utility;
import org.apache.bcel.generic.Type;
import org.apache.bcel.util.ByteSequence;

public class BcelToSqlite {
	Connection connection = null;
	PreparedStatement pstmt = null;
	int nextClassId = 1;
	int nextMethodId = 0x10000001;
	int nextAnnotationId = 0x20000001;

	/**
	 * 下記参考に実装
	 * https://hondou.homedns.org/pukiwiki/index.php?JavaSE%20BCEL
	 * @param args
	 * @throws Exception
	 */
	public static void main(String args[]) throws Exception
	{
		String srcPath;
		srcPath = ".\\lib\\bcel-6.3.1.jar";
        BcelToSqlite thisClass = new BcelToSqlite();
        thisClass.startWalk(new File(srcPath));
        System.out.println(srcPath + " -> output.sqlite");
	}

	private void executeSql(String sql) throws SQLException {
		pstmt = connection.prepareStatement(sql);
		pstmt.executeUpdate();
		pstmt.close();
		pstmt = null;
	}
	private void executeSql(String sql, Object args[]) throws SQLException {
		pstmt = connection.prepareStatement(sql);
		int ix = 1;
		for (Object obj : args) {
			try {
				pstmt.setInt(ix, (int)Integer.parseInt(obj.toString()));
			} catch (NumberFormatException ex) {
				pstmt.setString(ix, obj.toString());
			}

			++ix;
		}
		pstmt.executeUpdate();
		pstmt.close();
		pstmt = null;
	}

	private void startWalk(File path) throws Exception {
		try {
			connection = DriverManager.getConnection("jdbc:sqlite:output.sqlite");
			connection.setAutoCommit(true);
			executeSql("drop table if exists class");
			executeSql("create table class (id int primary key, name string , access_flags int, super_class_name string)");

			executeSql("drop table if exists interface");
			executeSql("create table interface (class_id int, interface_name string)");

			executeSql("drop index if exists index_interface");
			executeSql("create index index_interface on interface(class_id)");

			executeSql("drop table if exists method");
			executeSql("create table method (id int primary key, class_id int, name string, fullname string, access_flag int, return_type string, byte_code string)");

			executeSql("drop table if exists method_parameter");
			executeSql("create table method_parameter (method_id int, seq int, param_type string)");

			executeSql("drop index if exists index_method_parameter");
			executeSql("create index index_method_parameter on method_parameter(method_id)");

			executeSql("drop table if exists method_depend");
			executeSql("create table method_depend (method_id int, called_method string, opecode int)");

			executeSql("drop index if exists index_method_depend");
			executeSql("create index index_method_depend on method_depend(method_id)");

			executeSql("drop table if exists field");
			executeSql("create table field (id int primary key, class_id int, name string, fullname string, access_flag int, type string)");

			executeSql("drop table if exists anotation");
			executeSql("create table anotation (id int primary key, refid int, type string)");

			executeSql("drop index if exists index_anotation");
			executeSql("create index index_anotation on anotation(refid)");

			connection.setAutoCommit(false);
			dirWalk(path);
	        connection.commit();

		}
		finally
		{
			if(pstmt != null)
			{
				pstmt.close();
			}
			if(connection != null)
			{
				connection.close();
			}
		}
	}
    private void dirWalk(File path) throws Exception {
    	if (path.isDirectory()) {
    		for (File child : path.listFiles()) {
    			dirWalk(child);
	        }
    	} else if (path.getName().endsWith("jar") || path.getName().endsWith("zip")) {
    		jarWalk(path);
    	} else if (path.getName().endsWith("class")) {
    		JavaClass javaClass = new ClassParser(path.getAbsolutePath()).parse();
	        classWalk(javaClass);
    	}
    }

    private void jarWalk(File jarFile) throws Exception {
        try (JarInputStream jarIn = new JarInputStream(new FileInputStream(jarFile));) {
            JarEntry entry;
            while ((entry = jarIn.getNextJarEntry()) != null) {
                if (!entry.isDirectory()) {
                    String fileName = entry.getName();
                    if (fileName.endsWith("class")) {
                        JavaClass javaClass = new ClassParser(jarFile.getAbsolutePath(), fileName).parse();
                        classWalk(javaClass);
                    }
                }
            }
        }
    }

    private void classWalk(final JavaClass javaClass) throws SQLException, ClassNotFoundException, IOException {
    	System.out.println(javaClass.getClassName());

    	executeSql(
    		"insert into class values(?, ?, ?, ?)",
    		new Object[] {
    			nextClassId,
    			javaClass.getClassName(),
    			javaClass.getAccessFlags(),
    			javaClass.getSuperclassName()
    		}
    	);

    	// メソッドの取得
        final org.apache.bcel.classfile.Method[] methods = javaClass.getMethods();
        for (org.apache.bcel.classfile.Method method : methods) {
            methodWalk(nextClassId, javaClass, method);
        }

        Field[] fields = javaClass.getFields();
        for (Field field : fields) {
            fieldWalk(nextClassId, javaClass, field);
        }

        // インターフェイスの取得
        for (JavaClass i : javaClass.getAllInterfaces()) {
        	if (i.getClassName().equals(javaClass.getClassName())) {
        		continue;
        	}
			executeSql(
				"insert into interface values(?, ?)",
				new Object[] {
						nextClassId,
					i.getClassName()
				}
			);
        }

        // アノテーション
        anotationWalk(nextClassId, javaClass.getAnnotationEntries());

        if (nextClassId % 500 == 0) {
        	connection.commit();
        }

        // コミット
        ++nextClassId;
    }

    private void anotationWalk(final int refId, final AnnotationEntry[] annotations) throws SQLException {
        for (AnnotationEntry a : annotations) {
        	executeSql(
            		"insert into anotation values(?, ?, ?)",
            		new Object[] {
            				nextAnnotationId,
            				refId,
            				a.getAnnotationType()
            		}
            	);
        }
        ++nextAnnotationId;

    }

    private void methodWalk(final int classId, final JavaClass javaClass, final org.apache.bcel.classfile.Method method) throws SQLException, IOException {
		String code = getCode(method);
    	executeSql(
    		"insert into method values(?, ?,  ?, ?, ?, ?, ?)",
    		new Object[] {
    				nextMethodId,
    				classId,
    				method.getName(),
    				javaClass.getClassName() + "." + method.getName() + " " + method.getSignature(),
    				method.getAccessFlags(),
    				method.getReturnType().toString(),
    				code
    			}
    	);

		int seq = 1;
		for(Type p : method.getArgumentTypes()) {
			executeSql(
				"insert into method_parameter values(?, ?, ?)",
				new Object[] {
					nextMethodId,
					seq,
					p.toString()
				}
			);
			++seq;
		}
		if (method.getCode() != null) {
			ByteSequence stream = new ByteSequence(method.getCode().getCode());
			for (int i = 0; stream.available() > 0 ; i++) {
				analyzeCode(nextMethodId, stream, method.getConstantPool());
			}
		}


        // アノテーション
        anotationWalk(nextMethodId, method.getAnnotationEntries());

		++nextMethodId;
    }

    private void fieldWalk(final int classId, final JavaClass javaClass, final org.apache.bcel.classfile.Field field) throws SQLException, IOException {

    	executeSql(
    		"insert into field values(?, ?, ?, ?, ?, ?)",
    		new Object[] {
    				nextMethodId,
    				classId,
    				field.getName(),
    				javaClass.getClassName() + "." + field.getName() + " " + field.getSignature(),
    				field.getAccessFlags(),
    				field.getType().toString()
    			}
    	);

        // アノテーション
        anotationWalk(nextMethodId, field.getAnnotationEntries());

		++nextMethodId;
    }

    private  boolean wide = false; /* The `WIDE' instruction is used in the
     * byte code to allow 16-bit wide indices
     * for local variables. This opcode
     * precedes an `ILOAD', e.g.. The opcode
     * immediately following takes an extra
     * byte which is combined with the
     * following byte to form a
     * 16-bit value.
     */

    /**
     * 以下参考に実装
     * commons-bcel/src/main/java/org/apache/bcel/classfile/Utility.java
     * codeToString
     * @param bytes
     * @param constant_pool
     * @throws IOException
     * @throws SQLException
     * @throws ClassFormatException
     */
    public  void analyzeCode(final int methodId,  final ByteSequence bytes, final ConstantPool constant_pool) throws IOException, ClassFormatException, SQLException {
        final short opcode = (short) bytes.readUnsignedByte();
        int default_offset = 0;
        int low;
        int high;
        int npairs;
        int index;
        int vindex;
        int constant;
        int[] match;
        int[] jump_table;
        int no_pad_bytes = 0;
        int offset;
        final boolean verbose = true;
        final StringBuilder buf = new StringBuilder(Const.getOpcodeName(opcode));
        /* Special case: Skip (0-3) padding bytes, i.e., the
         * following bytes are 4-byte-aligned
         */
        if ((opcode == Const.TABLESWITCH) || (opcode == Const.LOOKUPSWITCH)) {
            final int remainder = bytes.getIndex() % 4;
            no_pad_bytes = (remainder == 0) ? 0 : 4 - remainder;
            for (int i = 0; i < no_pad_bytes; i++) {
                byte b;
                if ((b = bytes.readByte()) != 0) {
                    System.err.println("Warning: Padding byte != 0 in "
                            + Const.getOpcodeName(opcode) + ":" + b);
                }
            }
            // Both cases have a field default_offset in common
            default_offset = bytes.readInt();
        }
        switch (opcode) {
            /* Table switch has variable length arguments.
             */
            case Const.TABLESWITCH:
                low = bytes.readInt();
                high = bytes.readInt();
                offset = bytes.getIndex() - 12 - no_pad_bytes - 1;
                default_offset += offset;
                buf.append("\tdefault = ").append(default_offset).append(", low = ").append(low)
                        .append(", high = ").append(high).append("(");
                jump_table = new int[high - low + 1];
                for (int i = 0; i < jump_table.length; i++) {
                    jump_table[i] = offset + bytes.readInt();
                    buf.append(jump_table[i]);
                    if (i < jump_table.length - 1) {
                        buf.append(", ");
                    }
                }
                buf.append(")");
                break;
            /* Lookup switch has variable length arguments.
             */
            case Const.LOOKUPSWITCH: {
                npairs = bytes.readInt();
                offset = bytes.getIndex() - 8 - no_pad_bytes - 1;
                match = new int[npairs];
                jump_table = new int[npairs];
                default_offset += offset;
                buf.append("\tdefault = ").append(default_offset).append(", npairs = ").append(
                        npairs).append(" (");
                for (int i = 0; i < npairs; i++) {
                    match[i] = bytes.readInt();
                    jump_table[i] = offset + bytes.readInt();
                    buf.append("(").append(match[i]).append(", ").append(jump_table[i]).append(")");
                    if (i < npairs - 1) {
                        buf.append(", ");
                    }
                }
                buf.append(")");
            }
                break;
            /* Two address bytes + offset from start of byte stream form the
             * jump target
             */
            case Const.GOTO:
            case Const.IFEQ:
            case Const.IFGE:
            case Const.IFGT:
            case Const.IFLE:
            case Const.IFLT:
            case Const.JSR:
            case Const.IFNE:
            case Const.IFNONNULL:
            case Const.IFNULL:
            case Const.IF_ACMPEQ:
            case Const.IF_ACMPNE:
            case Const.IF_ICMPEQ:
            case Const.IF_ICMPGE:
            case Const.IF_ICMPGT:
            case Const.IF_ICMPLE:
            case Const.IF_ICMPLT:
            case Const.IF_ICMPNE:
                buf.append("\t\t#").append((bytes.getIndex() - 1) + bytes.readShort());
                break;
            /* 32-bit wide jumps
             */
            case Const.GOTO_W:
            case Const.JSR_W:
                buf.append("\t\t#").append((bytes.getIndex() - 1) + bytes.readInt());
                break;
            /* Index byte references local variable (register)
             */
            case Const.ALOAD:
            case Const.ASTORE:
            case Const.DLOAD:
            case Const.DSTORE:
            case Const.FLOAD:
            case Const.FSTORE:
            case Const.ILOAD:
            case Const.ISTORE:
            case Const.LLOAD:
            case Const.LSTORE:
            case Const.RET:
                if (wide) {
                    vindex = bytes.readUnsignedShort();
                    wide = false; // Clear flag
                } else {
                    vindex = bytes.readUnsignedByte();
                }
                buf.append("\t\t%").append(vindex);
                break;
            /*
             * Remember wide byte which is used to form a 16-bit address in the
             * following instruction. Relies on that the method is called again with
             * the following opcode.
             */
            case Const.WIDE:
                wide = true;
                buf.append("\t(wide)");
                break;
            /* Array of basic type.
             */
            case Const.NEWARRAY:
                buf.append("\t\t<").append(Const.getTypeName(bytes.readByte())).append(">");
                break;
            /* Access object/class fields.
             */
            case Const.GETFIELD:
            case Const.GETSTATIC:
            case Const.PUTFIELD:
            case Const.PUTSTATIC:
                index = bytes.readUnsignedShort();
                buf.append("\t\t").append(
                        constant_pool.constantToString(index, Const.CONSTANT_Fieldref)).append(
                        verbose ? " (" + index + ")" : "");

                executeSql(
                    	"insert into method_depend values(?,?,?)",
                    	new Object[] {
                    		methodId,
                    		constant_pool.constantToString(index, Const.CONSTANT_Fieldref),
                    		opcode
                    	}
                    );
                break;
            /* Operands are references to classes in constant pool
             */
            case Const.NEW:
            case Const.CHECKCAST:
                buf.append("\t");
                //$FALL-THROUGH$
            case Const.INSTANCEOF:
                index = bytes.readUnsignedShort();
                buf.append("\t<").append(
                        constant_pool.constantToString(index, Const.CONSTANT_Class))
                        .append(">").append(verbose ? " (" + index + ")" : "");

                executeSql(
                    	"insert into method_depend values(?,?,?)",
                    	new Object[] {
                    		methodId,
                    		constant_pool.constantToString(index, Const.CONSTANT_Class),
                    		opcode
                    	}
                    );
                break;
            /* Operands are references to methods in constant pool
             */
            case Const.INVOKESPECIAL:
            case Const.INVOKESTATIC:
                index = bytes.readUnsignedShort();
                final Constant c = constant_pool.getConstant(index);
                // With Java8 operand may be either a CONSTANT_Methodref
                // or a CONSTANT_InterfaceMethodref.   (markro)
                buf.append("\t").append(
                        constant_pool.constantToString(index, c.getTag()))
                        .append(verbose ? " (" + index + ")" : "");
                executeSql(
                	"insert into method_depend values(?,?,?)",
                	new Object[] {
                		methodId,
                		constant_pool.constantToString(index, c.getTag()),
                		opcode
                	}
                );
                break;
            case Const.INVOKEVIRTUAL:
                index = bytes.readUnsignedShort();
                buf.append("\t").append(
                        constant_pool.constantToString(index, Const.CONSTANT_Methodref))
                        .append(verbose ? " (" + index + ")" : "");

                executeSql(
                    	"insert into method_depend values(?,?,?)",
                    	new Object[] {
                    		methodId,
                    		constant_pool.constantToString(index, Const.CONSTANT_Methodref),
                    		opcode
                    	}
                    );
                break;
            case Const.INVOKEINTERFACE:
                index = bytes.readUnsignedShort();
                final int nargs = bytes.readUnsignedByte(); // historical, redundant
                buf.append("\t").append(
                        constant_pool
                                .constantToString(index, Const.CONSTANT_InterfaceMethodref))
                        .append(verbose ? " (" + index + ")\t" : "").append(nargs).append("\t")
                        .append(bytes.readUnsignedByte()); // Last byte is a reserved space
                executeSql(
                    	"insert into method_depend values(?,?,?)",
                    	new Object[] {
                    		methodId,
                    		constant_pool.constantToString(index, Const.CONSTANT_InterfaceMethodref),
                    		opcode
                    	}
                    );
                break;
            case Const.INVOKEDYNAMIC:
                index = bytes.readUnsignedShort();
                buf.append("\t").append(
                        constant_pool
                                .constantToString(index, Const.CONSTANT_InvokeDynamic))
                        .append(verbose ? " (" + index + ")\t" : "")
                        .append(bytes.readUnsignedByte())  // Thrid byte is a reserved space
                        .append(bytes.readUnsignedByte()); // Last byte is a reserved space

                executeSql(
                    	"insert into method_depend values(?,?,?)",
                    	new Object[] {
                    		methodId,
                    		constant_pool.constantToString(index, Const.CONSTANT_InvokeDynamic),
                    		opcode
                    	}
                    );
                break;
            /* Operands are references to items in constant pool
             */
            case Const.LDC_W:
            case Const.LDC2_W:
                index = bytes.readUnsignedShort();
                buf.append("\t\t").append(
                        constant_pool.constantToString(index, constant_pool.getConstant(index)
                                .getTag())).append(verbose ? " (" + index + ")" : "");
                break;
            case Const.LDC:
                index = bytes.readUnsignedByte();
                buf.append("\t\t").append(
                        constant_pool.constantToString(index, constant_pool.getConstant(index)
                                .getTag())).append(verbose ? " (" + index + ")" : "");
                break;
            /* Array of references.
             */
            case Const.ANEWARRAY:
                index = bytes.readUnsignedShort();
                buf.append("\t\t<").append(
                		Utility.compactClassName(constant_pool.getConstantString(index,
                                Const.CONSTANT_Class), false)).append(">").append(
                        verbose ? " (" + index + ")" : "");
                break;
            /* Multidimensional array of references.
             */
            case Const.MULTIANEWARRAY: {
                index = bytes.readUnsignedShort();
                final int dimensions = bytes.readUnsignedByte();
                buf.append("\t<").append(
                		Utility.compactClassName(constant_pool.getConstantString(index,
                                Const.CONSTANT_Class), false)).append(">\t").append(dimensions)
                        .append(verbose ? " (" + index + ")" : "");
            }
                break;
            /* Increment local variable.
             */
            case Const.IINC:
                if (wide) {
                    vindex = bytes.readUnsignedShort();
                    constant = bytes.readShort();
                    wide = false;
                } else {
                    vindex = bytes.readUnsignedByte();
                    constant = bytes.readByte();
                }
                buf.append("\t\t%").append(vindex).append("\t").append(constant);
                break;
            default:
                if (Const.getNoOfOperands(opcode) > 0) {
                    for (int i = 0; i < Const.getOperandTypeCount(opcode); i++) {
                        buf.append("\t\t");
                        switch (Const.getOperandType(opcode, i)) {
                            case Const.T_BYTE:
                                buf.append(bytes.readByte());
                                break;
                            case Const.T_SHORT:
                                buf.append(bytes.readShort());
                                break;
                            case Const.T_INT:
                                buf.append(bytes.readInt());
                                break;
                            default: // Never reached
                                throw new IllegalStateException("Unreachable default case reached!");
                        }
                    }
                }
        }
    }

    private String getCode(org.apache.bcel.classfile.Method method) {
    	if (method.getCode() == null) {
    		return "";
    	}
    	return method.getCode().toString();
    }

}
```  
  
### bcelの解析結果からクラス図を作成する  
bcelの解析結果を格納したSqliteからクラス図を作成しています。  
![plantUML.png](/image/687fa1c7-f24a-405b-e374-c86e2438836b.png)  
  
**SqliteToGraph.java**  
```java:SqliteToGraph.java

package sqliteToGraph;

import java.io.BufferedWriter;
import java.io.ByteArrayOutputStream;
import java.io.File;
import java.io.FileWriter;
import java.io.IOException;
import java.io.PrintWriter;
import java.nio.charset.Charset;
import java.sql.Connection;
import java.sql.DriverManager;
import java.sql.PreparedStatement;
import java.sql.ResultSet;
import java.sql.SQLException;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;

import org.apache.bcel.Const;

import net.sourceforge.plantuml.FileFormat;
import net.sourceforge.plantuml.FileFormatOption;
import net.sourceforge.plantuml.SourceStringReader;

public class SqliteToGraph {
	static final int MAX_MEMBER_SIZE = 10;

	public class ClassData {
		private int id;
		private String name;
		private String packageName;
		private String className;
		private int accessFlg;
		private String superClassName;

		public ClassData(ResultSet rs) throws SQLException {
			id = rs.getInt("id");
			name = rs.getString("name");
			accessFlg = rs.getInt("access_flags");
			superClassName = rs.getString("super_class_name");

			int ix = name.lastIndexOf(".");
			className = name.substring(ix + 1);
			packageName = name.substring(0, ix);
		}

		public int getId() {
			return id;
		}
		public String getName() {
			return name;
		}
		public String getPackageName() {
			return packageName;
		}
		public String getClassName() {
			return className;
		}
		public int getAccessFlg() {
			return accessFlg;
		}
		public String getSuperClassName() {
			return superClassName;
		}
	}

	public static void main(String[] args) throws SQLException, IOException{
		SqliteToGraph sg = new SqliteToGraph();
		String dbPath = "..\\bcelToSqlite\\output.sqlite";
		String path = "test_class.svg";
		sg.parse(dbPath, path);
		System.out.println("class:" + dbPath + "->" + path);
	}
	public void parse(String dbPath, String path) throws SQLException, IOException {
		Connection connection = null;
		ResultSet rs = null;
		PreparedStatement pstmt = null;
		PreparedStatement pstmtMethod = null;
		StringBuilder sb = new StringBuilder();
		try
		{
			// create a database connection
			// Connection connection = DriverManager.getConnection("jdbc:sqlite:C:/work/mydatabase.db");
			// Connection connection = DriverManager.getConnection("jdbc:sqlite::memory:");
			connection = DriverManager.getConnection("jdbc:sqlite:" + dbPath);
			pstmt = connection.prepareStatement("select id, name, access_flags, super_class_name from class order by id");
			rs = pstmt.executeQuery();
			HashMap<Integer, ClassData> mapClass = new HashMap<Integer, ClassData>();

			while(rs.next())
			{
				SqliteToGraph.ClassData data = new SqliteToGraph.ClassData(rs);
				mapClass.put(data.id, data);
			}
			rs.close();
			pstmt.close();
			pstmt = null;

			////
			sb.append("@startuml\n");
			sb.append("left to right direction\n");

			pstmt = connection.prepareStatement("select id, name , access_flag, type from field where class_id = ?");
			pstmtMethod = connection.prepareStatement("select distinct name , access_flag from method where class_id = ?");

			for(Integer key : mapClass.keySet()) {
				String prefix = "class";
				if ((mapClass.get(key).getAccessFlg() & Const.ACC_INTERFACE) == Const.ACC_INTERFACE) {
					prefix = "interface";
				}
				sb.append("  " + prefix +" \"" + mapClass.get(key).name + "\" {" + "\n");

				// field
				List<String> list = new ArrayList<String>();
				pstmt.setInt(1, mapClass.get(key).id);
				rs = pstmt.executeQuery();
				while(rs.next())
				{
					list.add(rs.getString("name"));
				}
				for(int i = 0; i < list.size()  ; ++i)  {
					sb.append("    " + list.get(i) + " \n");
					if (i > MAX_MEMBER_SIZE) {
						sb.append("    ... \n");
						break;
					}
				}
				rs.close();
				list = new ArrayList<String>();

				// method
				pstmtMethod.setInt(1, mapClass.get(key).id);
				rs = pstmtMethod.executeQuery();
				while(rs.next())
				{
					if ((rs.getInt("access_flag") & Const.ACC_PUBLIC) == Const.ACC_PUBLIC) {
						list.add(rs.getString("name"));
					}
				}
				rs.close();
				for(int i = 0; i < list.size()  ; ++i)  {
					sb.append("    " + list.get(i) + "() \n");
					if (i > MAX_MEMBER_SIZE) {
						sb.append("    ...() \n");
						break;
					}
				}
				sb.append("  }\n");
				if (checkSuperClassName(mapClass.get(key).getSuperClassName())) {
					sb.append("  " + mapClass.get(key).getSuperClassName() + " <|-- " + mapClass.get(key).name + "\n");
				}
			}
			pstmt.close();
			pstmt = null;

			pstmt = connection.prepareStatement("select class_id, interface_name from interface");
			rs = pstmt.executeQuery();
			while(rs.next())
			{
				if (checkSuperClassName(rs.getString("interface_name"))) {
					sb.append("  " + rs.getString("interface_name") + " <|.. " + mapClass.get(rs.getInt("class_id")).name + "\n");
				}
			}
			pstmt.close();
			pstmt = null;
			sb.append("@enduml\n");

			writeSvg(sb.toString(), path);
		}
		finally
		{
			try
			{
				if(rs != null)
				{
					rs.close();
				}
				if(pstmt != null)
				{
					pstmt.close();
				}
				if(pstmtMethod != null)
				{
					pstmtMethod.close();
				}
				if(connection != null)
				{
				connection.close();
				}
			}
			catch(SQLException e)
			{
				// connection close failed.
				System.err.println(e);
			}
		}

	}
    private boolean checkSuperClassName(String superClassName) {
		if (superClassName.startsWith("java.")) {
			return false;
		}
		if (superClassName.startsWith("javax.")) {
			return false;
		}
    	return true;
    }


	private static void writeSvg(String source, String path) throws IOException {
		SourceStringReader reader = new SourceStringReader(source);
		final ByteArrayOutputStream os = new ByteArrayOutputStream();
		// Write the first image to "os"
		@SuppressWarnings("deprecation")
		String desc = reader.generateImage(os, new FileFormatOption(FileFormat.SVG));
		os.close();

		final String svg = new String(os.toByteArray(), Charset.forName("UTF-8"));
		File out = new File(path);
		PrintWriter pw = new PrintWriter(new BufferedWriter(new FileWriter(out)));
		pw.write(svg);
		pw.close();

	}
}
```  
  
### bcelの解析結果からコールグラフを作成する  
bcelの解析結果を格納したSqliteから指定のメソッドのコールグラフを作成しています。  
  
![planguml2.png](/image/e0c84cd0-a356-d0a1-5fc3-248ec0130b53.png)  
  
  
**DependMethod.java**  
```java:DependMethod.java
package sqliteToGraph;

import java.io.BufferedWriter;
import java.io.ByteArrayOutputStream;
import java.io.File;
import java.io.FileWriter;
import java.io.IOException;
import java.io.PrintWriter;
import java.nio.charset.Charset;
import java.sql.Connection;
import java.sql.DriverManager;
import java.sql.PreparedStatement;
import java.sql.ResultSet;
import java.sql.SQLException;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;

import net.sourceforge.plantuml.FileFormat;
import net.sourceforge.plantuml.FileFormatOption;
import net.sourceforge.plantuml.SourceStringReader;

public class DependMethod {
	public static void main(String[] args) throws SQLException, IOException{
		DependMethod dm = new DependMethod();
		String dbPath = "..\\bcelToSqlite\\output.sqlite";
		String path = "test_depend.svg";
		String methodName = "org.apache.bcel.util.ClassPath.SYSTEM_CLASS_PATH";
		dm.parse(dbPath, path, methodName);
		System.out.println("depend:" + dbPath + "->" + path);
	}
	Connection connection = null;
	PreparedStatement pstmtLike = null;
	PreparedStatement pstmtEqual = null;

	class TreeItem {
		private String methodName;
		private List<TreeItem> children = new ArrayList<TreeItem>();
		public TreeItem(String m) {
			methodName = m;
		}
		public List<TreeItem> GetChildren() {
			return children;
		}
	}
	List<TreeItem> root = new ArrayList<TreeItem>();
	HashMap<String, TreeItem> map = new HashMap<String, TreeItem>();
	List<String> rectangles = new ArrayList<String>();

	public void parse(String dbPath, String path, String methodName) throws SQLException, IOException {
		ResultSet rs = null;
		try
		{
			connection = DriverManager.getConnection("jdbc:sqlite:" + dbPath);
			pstmtLike = connection.prepareStatement("select  distinct method_depend.called_method from method inner join method_depend on method.id = method_depend.method_id where method_depend.called_method like ?");
			pstmtLike.setString(1, "%" + methodName + "%");
			rs = pstmtLike.executeQuery();


			while(rs.next())
			{
				TreeItem item = new TreeItem(rs.getString("called_method"));
				root.add(item);
				map.put(item.methodName, item);
			}
			rs.close();

			pstmtEqual = connection.prepareStatement("select  distinct method.fullname as call_method from method inner join method_depend on method.id = method_depend.method_id where method_depend.called_method like ?");
			for (TreeItem item : root) {
				walkDependency(item.methodName);
			}
			StringBuilder sbDef = new StringBuilder();
			StringBuilder sbArrow = new StringBuilder();
			StringBuilder sb = new StringBuilder();
			rectangles = new ArrayList<String>();

			sb.append("@startuml\n");
			for (TreeItem item : root) {
				drawDependency(item, sbDef, sbArrow);
			}
			sb.append(sbDef.toString());
			sb.append(sbArrow.toString());

			sb.append("@enduml\n");
			System.out.println(sb.toString());
			writeSvg(sb.toString() + "\n" + sb.toString(), path);

		}
		finally
		{
			try
			{
				if(rs != null)
				{
					rs.close();
				}
				if(pstmtLike != null)
				{
					pstmtLike.close();
				}
				if(pstmtEqual != null)
				{
					pstmtEqual.close();
				}
				if(connection != null)
				{
				connection.close();
				}
			}
			catch(SQLException e)
			{
				// connection close failed.
				System.err.println(e);
			}
		}

	}

	void walkDependency(String calledMethod) throws SQLException {
		pstmtEqual.setString(1, calledMethod);
		ResultSet rs = pstmtEqual.executeQuery();

		List<String> list = new ArrayList<String>();

		while(rs.next())
		{
			String callMethod = rs.getString("call_method");
			if (callMethod.equals(calledMethod)) {
				// 再起呼び出し対策
				continue;
			}
			list.add(callMethod);
			if (!map.containsKey(callMethod)) {
				TreeItem item = new TreeItem(callMethod);
				map.put(item.methodName, item);
				map.get(calledMethod).GetChildren().add(item);
			}
		}
		rs.close();

		for (String callMethod : list) {
			walkDependency(callMethod);
		}

	}
	void drawDependency(TreeItem item, StringBuilder sbDef, StringBuilder sbArrow) {
		if (!rectangles.contains(item.methodName)) {
			rectangles.add(item.methodName);
			sbDef.append("rectangle \"" + item.methodName + "\" as " + makeAlias(item.methodName) + "\n");
		}
		for (TreeItem child : item.GetChildren()) {
			sbArrow.append(makeAlias(item.methodName) + "<--" + makeAlias(child.methodName) + "\n");
			drawDependency(child, sbDef, sbArrow);
		}

	}
	private String makeAlias(String name) {
		name = name.replaceAll("/", "_");
		name = name.replaceAll(" ", "_");
		name = name.replaceAll("<", "_");
		name = name.replaceAll(">", "_");
		name = name.replaceAll("\\$", "_");
		name = name.replaceAll(";", "_");
		name = name.replaceAll("\\(", "_");
		name = name.replaceAll("\\)", "_");
		name = name.replaceAll("\\[", "_");
		name = name.replaceAll("\\]", "_");
		return name;
	}

	private static void writeSvg(String source, String path) throws IOException {
		SourceStringReader reader = new SourceStringReader(source);
		final ByteArrayOutputStream os = new ByteArrayOutputStream();
		// Write the first image to "os"
		@SuppressWarnings("deprecation")
		String desc = reader.generateImage(os, new FileFormatOption(FileFormat.SVG));
		os.close();

		final String svg = new String(os.toByteArray(), Charset.forName("UTF-8"));
		File out = new File(path);
		PrintWriter pw = new PrintWriter(new BufferedWriter(new FileWriter(out)));
		pw.write(svg);
		pw.close();

	}
}
```  
  
## あとがき  
DoxygenとGraphVizを使えば、こんなことしなくてもいいです。  
Doxygenは結果をXMLを吐くこともできるので、解析も楽だと思います。  
  
ただ、bcelはfindbug等のよくつかわれるツールに入っているので、インターネット禁止縛りプレイを楽しんでいるところでも、利用できます。  
この時は、Sqliteでなくテキストに吐き出してからAccessにつっこんで使用するということをやっていました。  
  
また、解析結果をDatabaseに格納しておくと、依存関係の調査等で役に立ったりします。  
  
  
