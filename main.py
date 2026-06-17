# pandasライブラリを使えるようにする
# CSVを読み込んだり、表形式のデータを扱うために使用する
import pandas as pd
import sqlite3
import unicodedata
import difflib

# ==============================
# テキストの揺らぎを修正、正規化する関数
# ==============================
def normalize_text(text):
    if text is None:
        return ""

    return unicodedata.normalize("NFKC", text).lower()
# ==============================
# 辞書CSVを読み込む関数
# ==============================
def load_dictionary(path, key_col, value_col):
    # CSVファイルを読み込んでDataFrameに変換する
    df = pd.read_csv(path)

    # 空の辞書を作成する
    dictionary = {}

    # CSVの1行ずつ処理する
    for index, row in df.iterrows():

        # キーワードを取得する
        # lower()で英字を小文字に統一する
        key = normalize_text(row[key_col])

        # 属性の値を取得する
        # 例：NIKE、adidas、黒、白など
        value = row[value_col]

        # 辞書に登録する
        # 例:
        # "nike" : "NIKE"
        dictionary[key] = value

    # 完成した辞書を返す
    return dictionary


# ==============================
# 商品名から属性を探す関数
# ==============================
def find_attribute(text, dictionary):

    # 商品名を正規化する
    # 例:
    # "ＮＩＫＥ キャップ BLACK"
    # ↓
    # "nike キャップ black"
    text = normalize_text(text)
    #空白、タブなどすべてを１ワードに分割、カンマ区切りの場合は.split(",")
    words = text.split()
    # 辞書のキーワードを1つずつ確認する
    for keyword, value in dictionary.items():

        # 正規化後の文字列で比較する
        if keyword in text:

            # 見つかったら属性を返す
            return value
    
     # あいまい検索の準備
    best_score = 0
    best_value = None
    
    # 辞書のキーワードを1つずつ取り出す
    # 例:
    # keyword = "nike"
    # value = "NIKE"
    for keyword, value in dictionary.items():
        # 商品名を分割した単語を1つずつ取り出す
        # 例:
        # words = ["nik", "キャップ", "black"]
        for word in words:
        # 辞書のキーワードと商品名の単語の類似度を計算する
        # 0.0 ～ 1.0 の数値が返る
        # 例:
        # "nike" と "nik" → 約0.85
        # "nike" と "black" → 低い値
            score = difflib.SequenceMatcher(
                None,
                keyword,
                word
            ).ratio()
        # 今まで記録した最高点より高い場合
        # 最高一致度と候補の属性を更新する
            if score > best_score:
                # 最高一致度を更新
                best_score = score
                # 一番似ていた属性を保存
                # 例:
                # "nike" → "NIKE"
                best_value = value

    # 類似度が0.8以上なら、その属性を採用する
    if best_score >= 0.8:
        return best_value

    # 0.8未満の場合は判定不能とする
    return None

# ==============================
# 商品データを読み込む
# ==============================

# products.csv をDataFrameとして読み込む
products = pd.read_csv(
    "data/input/products.csv"
)


# ==============================
# ブランド辞書を読み込む
# ==============================

# brand.csvを読み込み、Pythonの辞書型に変換する
# 例:
# {
#   "nike": "NIKE",
#   "ナイキ": "NIKE",
#   "adidas": "adidas"
# }
brand_dict = load_dictionary(
    "dictionary/brand.csv",
    "keyword",
    "brand"
)


# ==============================
# 色辞書を読み込む
# ==============================

# color.csvを辞書型に変換する
# 例:
# {
#   "black": "黒",
#   "ブラック": "黒",
#   "white": "白"
# }
color_dict = load_dictionary(
    "dictionary/color.csv",
    "keyword",
    "color"
)


# ==============================
# ブランド属性を補完する
# ==============================

# product_name列を1行ずつ取り出して処理する
# 例:
# "ナイキ メンズ ランニングシューズ ブラック"
#            ↓
# find_attributeで検索
#            ↓
# "NIKE"
#            ↓
# brand列として追加する
products["brand"] = products["product_name"].apply(
    lambda product_name: find_attribute(product_name, brand_dict)
)


# ==============================
# 色属性を補完する
# ==============================

# 商品名から色を検索してcolor列を作成する
products["color"] = products["product_name"].apply(
    lambda product_name: find_attribute(product_name, color_dict)
)

# ==============================
# 未検出ブランドを抽出する
# ==============================

unknown_brand = products[products["brand"].isna()]

unknown_brand.to_csv(
    "data/output/unknown_brand.csv",
    index=False,
    encoding="shift-jis"
)
# ==============================
# 補完後のCSVを保存する
# ==============================

# index=False:
# CSVの左端に自動の番号(0,1,2...)を書き込まない
#
# encoding="utf-8-sig":
# Excelで日本語が文字化けしにくい形式で保存する
products.to_csv(
    "data/output/completed_products.csv",
    index=False,
    encoding="shift-jis"
)
# SQLiteデータベースに接続する
conn = sqlite3.connect("products.db")

# DataFrameをproductsテーブルとして保存する
products.to_sql(
    "products",
    conn,
    if_exists="replace",
    index=False
)

# データベース接続を終了する
conn.close()

# ==============================
# 処理完了メッセージを表示する
# ==============================

print("商品属性補完が完了しました！")


# 補完後のデータを画面に表示する
print(products)