
from flask import Flask, render_template, request
import pandas as pd
import plotly.express as px
import plotly.io as pio
import os

app = Flask(__name__)

# --- データパス設定 ---
DATA_DIR = "data"
CUST_PATH = os.path.join(DATA_DIR, "cust.csv")
ORDER_PATH = os.path.join(DATA_DIR, "order.csv")
ITEM_STOCK_PATH = os.path.join(DATA_DIR, "itemstock.csv")

# ==============================================================
# 📊 ① 経営戦略本部・在庫管理ダッシュボード
# ==============================================================
@app.route('/', methods=['GET'])
def index():
    gender_filter = request.args.get('gender')
    min_age_filter = request.args.get('min_age', type=int)
    max_age_filter = request.args.get('max_age', type=int)

    try:
        cust = pd.read_csv(CUST_PATH, encoding='utf-8-sig')
        order = pd.read_csv(ORDER_PATH, encoding='utf-8-sig')
        item_stock = pd.read_csv(ITEM_STOCK_PATH, encoding='utf-8-sig')
    except FileNotFoundError as e:
        return f"エラー: {e.filename} が見つかりません。", 500

    # --- 前処理 ---
    cust.columns = [c.lower() for c in cust.columns]
    order.columns = [c.lower() for c in order.columns]
    item_stock.columns = [c.lower() for c in item_stock.columns]

    order.rename(columns={'orderitem': 'itemcode'}, inplace=True)
    item_stock.rename(columns={'item': 'itemcode'}, inplace=True)

    # --- フィルタ処理 ---
    filtered_cust = cust.copy()
    if gender_filter and 'sex' in cust.columns:
        filtered_cust = filtered_cust[filtered_cust['sex'].astype(str) == gender_filter]
    if 'age' in filtered_cust.columns:
        if min_age_filter is not None:
            filtered_cust = filtered_cust[filtered_cust['age'] >= min_age_filter]
        if max_age_filter is not None:
            filtered_cust = filtered_cust[filtered_cust['age'] <= max_age_filter]

    filtered_customer_ids = filtered_cust['customerid'].unique()
    filtered_order = order[order['customerid'].isin(filtered_customer_ids)]

    # --- 集計処理 ---
    if not filtered_order.empty:
        summary = (
            filtered_order.groupby("customerid")
            .agg(
                purchase_count=("orderdate", "count"),
                total_spent=("orderprice", "sum"),
                last_order=("orderdate", "max")
            )
            .reset_index()
        )
        merged = pd.merge(filtered_cust, summary, on="customerid", how="left").fillna({
            'purchase_count': 0, 'total_spent': 0, 'last_order': 0
        })
    else:
        merged = filtered_cust.copy()
        merged['purchase_count'] = 0
        merged['total_spent'] = 0
        merged['last_order'] = 0

    # --- KPI ---
    total_customers = merged["customerid"].nunique()
    total_sales = merged["total_spent"].sum()
    avg_sales = total_sales / total_customers if total_customers else 0

    top_freq = merged.sort_values("purchase_count", ascending=False).head(10)
    top_spend = merged.sort_values("total_spent", ascending=False).head(10)

    #--- 在庫分析 ---
    order_stock_merged = pd.merge(
        filtered_order,
        item_stock[['itemcode', 'stock']],
        on='itemcode',
        how='left'
    ).drop_duplicates(subset=['orderdate', 'orderno', 'itemcode'])

    item_analysis = (
        order_stock_merged.groupby('itemcode')
        .agg(total_ordered=('ordernum', 'sum'), current_stock=('stock', 'max'))
        .reset_index()
    )
    item_analysis['stock_ratio'] = item_analysis['current_stock'] / item_analysis['total_ordered']

    low_stock_risk = item_analysis[
        (item_analysis['total_ordered'] > 0) & (item_analysis['stock_ratio'] < 0.1)
    ].sort_values('stock_ratio').head(5)

    return render_template(
        "dashboard.html",
        total_customers=int(total_customers),
        total_sales=int(total_sales),
        avg_sales=int(avg_sales),
        top_freq=top_freq.to_dict(orient="records"),
        top_spend=top_spend.to_dict(orient="records"),
        low_stock_risk=low_stock_risk.to_dict(orient="records"),
        item_analysis=item_analysis.to_dict(orient="records"),
        gender_filter=gender_filter,
        min_age_filter=min_age_filter,
        max_age_filter=max_age_filter,
    )

# ==============================================================
# 👤 ② 個別顧客詳細ページ
# ==============================================================
@app.route('/customer/<customer_id>', methods=['GET'])
def customer_detail(customer_id):
    try:
        cust = pd.read_csv(CUST_PATH, encoding='utf-8-sig')
        order = pd.read_csv(ORDER_PATH, encoding='utf-8-sig')
    except FileNotFoundError as e:
        return f"エラー: {e.filename} が見つかりません。", 500

    cust.columns = [c.lower() for c in cust.columns]
    order.columns = [c.lower() for c in order.columns]

    order['orderdate'] = pd.to_datetime(order['orderdate'])

    cust_orders = order[order['customerid'].astype(str) == str(customer_id)].sort_values('orderdate')
    if cust_orders.empty:
        return f"顧客ID {customer_id} の注文履歴はありません"

    total_orders = cust_orders.shape[0]
    total_spent = cust_orders['orderprice'].sum()
    last_order = cust_orders['orderdate'].max()

    # --- グラフ作成 ---
    fig = px.bar(
        cust_orders,
        x='orderdate',
        y='orderprice',
        title=f'顧客ID {customer_id} の購入履歴',
        labels={'orderdate': '注文日', 'orderprice': '注文金額'}
    )
    graph_html = pio.to_html(fig, full_html=False)

    # --- 顧客情報 ---
    customer_info = cust[cust['customerid'].astype(str) == str(customer_id)].to_dict(orient='records')[0]

    return render_template(
        'customer_detail.html',
        customer_info=customer_info,
        total_orders=total_orders,
        total_spent=total_spent,
        last_order=last_order,
        graph_html=graph_html,
        cust_orders=cust_orders.to_dict(orient='records')
    )

# ==============================================================
# 💰 金額フォーマット
# ==============================================================
@app.template_filter('format_currency')
def format_currency(value):
    if value is None or pd.isna(value):
        return "0"
    try:
        return f"{int(value):,}"
    except Exception:
        return str(value)

@app.route('/search.html')
def search_page():
    return render_template('search.html')


# ==============================================================
# 📦 ③ 在庫管理ページ
# ==============================================================
@app.route('/stock.html')
def stock_page():
    import pandas as pd
    import os

    DATA_DIR = "data"
    ORDER_PATH = os.path.join(DATA_DIR, "order.csv")
    ITEM_STOCK_PATH = os.path.join(DATA_DIR, "itemstock.csv")

    # データ読み込み
    order = pd.read_csv(ORDER_PATH, encoding='utf-8-sig')
    item_stock = pd.read_csv(ITEM_STOCK_PATH, encoding='utf-8-sig')

    # 前処理（index() と同じ規約にそろえる）
    order.columns = [c.lower() for c in order.columns]
    item_stock.columns = [c.lower() for c in item_stock.columns]
    order.rename(columns={'orderitem': 'itemcode'}, inplace=True)
    item_stock.rename(columns={'item': 'itemcode'}, inplace=True)

    # 在庫分析（index() と同じロジック）
    order_stock_merged = pd.merge(
        order,
        item_stock[['itemcode', 'stock']],
        on='itemcode',
        how='left'
    ).drop_duplicates(subset=['orderdate', 'orderno', 'itemcode'])

    item_analysis = (
        order_stock_merged.groupby('itemcode')
        .agg(total_ordered=('ordernum', 'sum'), current_stock=('stock', 'max'))
        .reset_index()
    )

    # 0除算ケア：total_ordered==0 は在庫率0に
    item_analysis['stock_ratio'] = item_analysis.apply(
        lambda r: (r['current_stock'] / r['total_ordered']) if r['total_ordered'] else 0,
        axis=1
    )

    low_stock_risk = (
        item_analysis[(item_analysis['total_ordered'] > 0) & (item_analysis['stock_ratio'] < 0.1)]
        .sort_values('stock_ratio')
        .head(5)
    )

    return render_template(
        'stock.html',
        low_stock_risk=low_stock_risk.to_dict(orient='records'),
        item_analysis=item_analysis.to_dict(orient='records')
    )


if __name__ == "__main__":
    app.run(debug=True)
