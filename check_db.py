# SQLiteを操作するライブラリ
import sqlite3

# データベースに接続
conn = sqlite3.connect("products.db")

# SQLを実行して結果を取得
cursor = conn.execute(
"SELECT * FROM products WHERE brand = 'NIKE';"
)

# 1行ずつ表示
for row in cursor:
    print(row)

# 接続終了
conn.close()