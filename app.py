from flask import Flask, render_template, request
import pandas as pd
import os

app = Flask(__name__)

# --- データパス設定 ---
# 以下のディレクトリとファイルが、このapp.pyと同じ階層にある必要があります
DATA_DIR = "data" 
CUST_PATH = os.path.join(DATA_DIR, "cust.csv")
ORDER_PATH = os.path.join(DATA_DIR, "order.csv")
ITEM_STOCK_PATH = os.path.join(DATA_DIR, "itemstock.csv") 

@app.route('/', methods=['GET'])
def index():
    # フィルタリングクエリパラメータの取得
    gender_filter = request.args.get('gender')
    min_age_filter = request.args.get('min_age', type=int)
    max_age_filter = request.args.get('max_age', type=int)
    
    # ===== データ読み込みと準備 =====
    try:
        cust = pd.read_csv(CUST_PATH)
        order = pd.read_csv(ORDER_PATH)
        item_stock = pd.read_csv(ITEM_STOCK_PATH)
    except FileNotFoundError as e:
        # ファイルが見つからない場合のエラー処理
        return f"エラー: 必要なデータファイル ({e.filename}) が見つかりません。'data'フォルダとファイル名を確認してください。", 500

    # 列名を小文字化（安全のため）
    cust.columns = [c.lower() for c in cust.columns]
    order.columns = [c.lower() for c in order.columns]
    item_stock.columns = [c.lower() for c in item_stock.columns]
    
    # 列名のリネーム（データ結合のため）
    order.rename(columns={'orderitem': 'itemcode'}, inplace=True) 
    item_stock.rename(columns={'item': 'itemcode'}, inplace=True)
    
    # ===== フィルタリング処理 (custデータに対してage, sexを使用) =====
    filtered_cust = cust.copy()
    
    # 1. 性別フィルタリング (custに'sex'列があると仮定)
    if gender_filter and 'sex' in cust.columns:
        # データ型を文字列に変換してから小文字で比較
        filtered_cust = filtered_cust[filtered_cust['sex'].astype(str).str.lower() == gender_filter.lower()]

    # 2. 年齢フィルタリング (custに'age'列があると仮定)
    if 'age' in filtered_cust.columns:
        if min_age_filter is not None:
            filtered_cust = filtered_cust[filtered_cust['age'] >= min_age_filter]
        if max_age_filter is not None:
            filtered_cust = filtered_cust[filtered_cust['age'] <= max_age_filter]

    # フィルタリングされた顧客IDのリストを取得
    filtered_customer_ids = filtered_cust['customerid'].unique()
    
    # フィルタリングされた顧客の注文データのみを使用
    filtered_order = order[order['customerid'].isin(filtered_customer_ids)]
    
    # ===== フィルタリング後の集計処理 =====
    
    if not filtered_order.empty:
        # 各顧客の購入回数・合計金額・最終注文日 (フィルタリング後)
        summary = (
            filtered_order.groupby("customerid")
            .agg(
                purchase_count=("orderdate", "count"),
                total_spent=("orderprice", "sum"),
                last_order=("orderdate", "max")
            )
            .reset_index()
        )
        # フィルタリングされた顧客情報と集計結果を結合
        merged = pd.merge(filtered_cust, summary, on="customerid", how="left").fillna({
            'purchase_count': 0, 'total_spent': 0, 'last_order': 0
        })
    else:
        # 注文データがない場合
        merged = filtered_cust.copy()
        merged['purchase_count'] = 0
        merged['total_spent'] = 0
        merged['last_order'] = 0

    # 全体のKPI (フィルタリング後)
    total_customers = merged["customerid"].nunique()
    total_sales = merged["total_spent"].sum()
    avg_sales = total_sales / total_customers if total_customers else 0

    # ランキング (フィルタリング後)
    top_freq = merged.sort_values("purchase_count", ascending=False).head(10)
    top_spend = merged.sort_values("total_spent", ascending=False).head(10)

    # ===== 在庫分析の追加 =====
    
    # 注文データと在庫データを結合
    order_stock_merged = pd.merge(
        filtered_order, 
        item_stock[['itemcode', 'stock']], 
        on='itemcode', 
        how='left'
    ).drop_duplicates(subset=['orderdate', 'orderno', 'itemcode']) # 重複防止

    # 商品ごとの注文総数と現在の在庫数を集計
    item_analysis = (
        order_stock_merged.groupby('itemcode')
        .agg(
            total_ordered=('ordernum', 'sum'),
            current_stock=('stock', 'max') 
        )
        .reset_index()
    )
    
    # 在庫残量が注文総数に対して危険な割合の商品を抽出
    item_analysis['stock_ratio'] = item_analysis['current_stock'] / item_analysis['total_ordered']
    
    # 在庫切れリスクの高い商品トップ5（注文数が1以上かつ、在庫比率が0.1未満）
    low_stock_risk = item_analysis[
        (item_analysis['total_ordered'] > 0) & 
        (item_analysis['stock_ratio'] < 0.1)
    ].sort_values('stock_ratio').head(5)


    # HTMLへ渡す
    return render_template(
        "index.html",
        # 全体KPI
        total_customers=int(total_customers),
        total_sales=int(total_sales),
        avg_sales=int(avg_sales),
        # ランキング
        top_freq=top_freq[['customerid', 'lastname', 'firstname', 'purchase_count']].to_dict(orient="records"),
        top_spend=top_spend[['customerid', 'lastname', 'firstname', 'total_spent']].to_dict(orient="records"),
        # 在庫分析
        low_stock_risk=low_stock_risk.to_dict(orient="records"),
        # フィルタリング条件
        gender_filter=gender_filter,
        min_age_filter=min_age_filter,
        max_age_filter=max_age_filter,
    )

if __name__ == "__main__":
    app.run(debug=True)