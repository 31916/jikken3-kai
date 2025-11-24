
from flask import Flask, render_template, request
import pandas as pd
import plotly.express as px
import plotly.io as pio
import os

# ------------------------------
# Flask アプリ作成
# ------------------------------
app = Flask(__name__)

# ------------------------------
# データパス設定
# ------------------------------
DATA_DIR = "data"
CUST_PATH = os.path.join(DATA_DIR, "cust.csv")
ORDER_PATH = os.path.join(DATA_DIR, "order.csv")
ITEM_STOCK_PATH = os.path.join(DATA_DIR, "itemstock.csv")
 

# ------------------------------
# 金額フォーマット用フィルタ
# ------------------------------
@app.template_filter('format_currency')
def format_currency(value):
    if value is None or pd.isna(value):
        return "0"
    try:
        return f"{int(value):,}"
    except Exception:
        return str(value)

# ------------------------------
# ① 経営戦略ダッシュボード
# ------------------------------
@app.route('/dashboard', methods=['GET'])
def index():
    gender_filter = request.args.get('gender')
    min_age_filter = request.args.get('min_age', type=int)
    max_age_filter = request.args.get('max_age', type=int)
    area_filter = request.args.get('area')

    try:
        cust = pd.read_csv(CUST_PATH, encoding='utf-8-sig')
        order = pd.read_csv(ORDER_PATH, encoding='utf-8-sig')
        item_stock = pd.read_csv(ITEM_STOCK_PATH, encoding='utf-8-sig')
    except FileNotFoundError as e:
        return f"エラー: {e.filename} が見つかりません。", 500

    cust.columns = [c.lower() for c in cust.columns]
    order.columns = [c.lower() for c in order.columns]
    item_stock.columns = [c.lower() for c in item_stock.columns]

    order.rename(columns={'orderitem': 'itemcode'}, inplace=True)
    item_stock.rename(columns={'item': 'itemcode'}, inplace=True)

    # フィルタ処理
    filtered_cust = cust.copy()
    if gender_filter and 'sex' in cust.columns:
        filtered_cust = filtered_cust[filtered_cust['sex'].astype(str) == gender_filter]
    if 'age' in filtered_cust.columns:
        if min_age_filter is not None:
            filtered_cust = filtered_cust[filtered_cust['age'] >= min_age_filter]
        if max_age_filter is not None:
            filtered_cust = filtered_cust[filtered_cust['age'] <= max_age_filter]
    if area_filter and 'area' in filtered_cust.columns:
        filtered_cust = filtered_cust[filtered_cust['area'] == area_filter]


    filtered_customer_ids = filtered_cust['customerid'].unique()
    filtered_order = order[order['customerid'].isin(filtered_customer_ids)]
    # 都道府県を北海道→沖縄の順に固定
    pref_order = [
        "北海道",
        "青森県", "岩手県", "宮城県", "秋田県", "山形県", "福島県",
        "茨城県", "栃木県", "群馬県", "埼玉県", "千葉県", "東京都", "神奈川県",
        "新潟県", "富山県", "石川県", "福井県",
        "山梨県", "長野県",
        "岐阜県", "静岡県", "愛知県", "三重県",
        "滋賀県", "京都府", "大阪府", "兵庫県", "奈良県", "和歌山県",
        "鳥取県", "島根県", "岡山県", "広島県", "山口県",
        "徳島県", "香川県", "愛媛県", "高知県",
        "福岡県", "佐賀県", "長崎県", "熊本県", "大分県", "宮崎県", "鹿児島県",
        "沖縄県"
    ]

    # データにある都道府県だけ残す & 地図順で並ぶ
    area_list = [p for p in pref_order if p in cust['area'].unique()]


    # 集計
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

    total_customers = merged["customerid"].nunique()
    total_sales = merged["total_spent"].sum()
    avg_sales = total_sales / total_customers if total_customers else 0

    top_freq = merged.sort_values("purchase_count", ascending=False)
    top_spend = merged.sort_values("total_spent", ascending=False)
    
    # --------------------------
    # 地域別売上サマリ
    # --------------------------
    if not merged.empty and 'area' in merged.columns:
        area_summary = (
            merged.groupby('area')
            .agg(
                customers=('customerid', 'nunique'),
                total_sales=('total_spent', 'sum')
            )
            .reset_index()
        )
        area_summary['avg_sales_per_customer'] = (
            area_summary['total_sales'] / area_summary['customers']
        )
    else:
        area_summary = pd.DataFrame(
            columns=['area', 'customers', 'total_sales', 'avg_sales_per_customer']
        )

    # --------------------------
    # 年代 × 性別 セグメント
    # --------------------------
    if not merged.empty and 'age' in merged.columns and 'sex' in merged.columns:
        seg = merged.dropna(subset=['age', 'sex']).copy()
        seg['age_group'] = (seg['age'] // 10) * 10  
        age_gender = (
            seg.groupby(['age_group', 'sex'])
            .agg(
                total_sales=('total_spent', 'sum'),
                customer_count=('customerid', 'nunique')
            )
            .reset_index()
            .sort_values(['age_group', 'sex'])
        )
    else:
        age_gender = pd.DataFrame(
            columns=['age_group', 'sex', 'total_sales', 'customer_count']
        )

    return render_template(
        "dashboard.html",
        total_customers=int(total_customers),
        total_sales=int(total_sales),
        avg_sales=int(avg_sales),
        top_freq=top_freq.to_dict(orient="records"),
        top_spend=top_spend.to_dict(orient="records"),
        gender_filter=gender_filter,
        min_age_filter=min_age_filter,
        max_age_filter=max_age_filter,
        area_filter=area_filter,
        area_list=area_list,
        area_summary=area_summary.to_dict(orient="records"),
        age_gender=age_gender.to_dict(orient="records")
    )
    
# ==============================================================
# 🏠 ① 新しいホームページ (ルート / )
# ==============================================================
@app.route('/', methods=['GET']) # 👈 ルート / にアクセスされたらこの関数を実行
def home():
    # データを必要としないシンプルな home.html をレンダリング
    return render_template("index.html") 
# ------------------------------
# ② 個別顧客詳細ページ
# ------------------------------
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

    # グラフ作成
    fig = px.bar(
        cust_orders,
        x='orderdate',
        y='orderprice',
        title=f'顧客ID {customer_id} の購入履歴',
        labels={'orderdate': '注文日', 'orderprice': '注文金額'}
    )
    graph_html = pio.to_html(fig, full_html=False)

    customer_info = cust[cust['customerid'].astype(str) == str(customer_id)].to_dict(orient='records')[0]

    # テンプレートにデータを渡してレンダリング
    return render_template(
        'customer.html',  
        customer_info=customer_info,
        total_orders=total_orders,
        total_spent=total_spent,
        last_order=last_order,
        graph_html=graph_html,
        cust_orders=cust_orders.to_dict(orient='records')
    )

# ------------------------------
# ③ 在庫管理ページ（複合検索対応）
# ------------------------------
@app.route('/stock.html')
def stock_page():
    # データ読み込み
    order = pd.read_csv(ORDER_PATH, encoding='utf-8-sig')
    item_stock = pd.read_csv(ITEM_STOCK_PATH, encoding='utf-8-sig')
    item_master = pd.read_csv(os.path.join(DATA_DIR, 'item.csv'), encoding='utf-8-sig')

    # 前処理
    order.columns = [c.lower() for c in order.columns]
    item_stock.columns = [c.lower() for c in item_stock.columns]
    item_master.columns = [c.lower() for c in item_master.columns]

    order.rename(columns={'orderitem': 'itemcode', 'orderitemcate': 'itemcate'}, inplace=True)
    item_stock.rename(columns={'item': 'itemcode'}, inplace=True)
    item_master.rename(columns={'item': 'itemcode', 'itemcate': 'itemcate'}, inplace=True)

    # item_master と item_stock をマージして商品情報を作成
    item_info = pd.merge(item_master, item_stock, on='itemcode', how='left')

    # 在庫分析
    merge_cols = ['itemcode', 'itemcate']
    if 'itemname' in item_info.columns:
        merge_cols.append('itemname')

    order_stock_merged = pd.merge(
        order,
        item_info[merge_cols + ['stock']],
        on=['itemcode', 'itemcate'] if 'itemcate' in merge_cols else ['itemcode'],
        how='left'
    ).drop_duplicates(subset=['orderdate', 'orderno', 'itemcode'])

    item_analysis = (
        order_stock_merged.groupby(merge_cols)
        .agg(total_ordered=('ordernum', 'sum'), current_stock=('stock', 'max'))
        .reset_index()
    )
    item_analysis['stock_ratio'] = item_analysis.apply(
        lambda r: (r['current_stock'] / r['total_ordered']) if r['total_ordered'] else 0,
        axis=1
    )

    # 🔹 在庫率10%未満の商品（上位5件） →ここは表示数変更可能!
    low_stock_risk = (
        item_analysis[(item_analysis['total_ordered'] > 0) & (item_analysis['stock_ratio'] < 0.1)]
        .sort_values('stock_ratio')
        .head(5)
    )

    # --- 複合検索 ---
    itemcode_query = request.args.get('itemcode', '').strip()
    itemname_query = request.args.get('itemname', '').strip()
    itemcate_query = request.args.get('itemcate', '').strip()
    min_stock_ratio = request.args.get('min_stock_ratio', type=float)
    max_stock_ratio = request.args.get('max_stock_ratio', type=float)
    min_ordered = request.args.get('min_ordered', type=int)
    max_ordered = request.args.get('max_ordered', type=int)

    filtered_analysis = item_analysis.copy()

    if itemcode_query:
        filtered_analysis = filtered_analysis[filtered_analysis['itemcode'].str.contains(itemcode_query, case=False, na=False)]
    if 'itemname' in filtered_analysis.columns and itemname_query:
        filtered_analysis = filtered_analysis[filtered_analysis['itemname'].str.contains(itemname_query, case=False, na=False)]
    if 'itemcate' in filtered_analysis.columns and itemcate_query:
        filtered_analysis = filtered_analysis[filtered_analysis['itemcate'] == itemcate_query]
    if min_stock_ratio is not None:
        filtered_analysis = filtered_analysis[filtered_analysis['stock_ratio']*100 >= min_stock_ratio]
    if max_stock_ratio is not None:
        filtered_analysis = filtered_analysis[filtered_analysis['stock_ratio']*100 <= max_stock_ratio]
    if min_ordered is not None:
        filtered_analysis = filtered_analysis[filtered_analysis['total_ordered'] >= min_ordered]
    if max_ordered is not None:
        filtered_analysis = filtered_analysis[filtered_analysis['total_ordered'] <= max_ordered]

    # プルダウン用のカテゴリリスト（重複除去・ソート）
    categories = sorted(item_analysis['itemcate'].dropna().unique()) if 'itemcate' in item_analysis.columns else []

    return render_template(
        'stock.html',
        low_stock_risk=low_stock_risk.to_dict(orient='records'),
        item_analysis=filtered_analysis.to_dict(orient='records'),
        categories=categories,
        search_params={
            'itemcode': itemcode_query,
            'itemname': itemname_query,
            'itemcate': itemcate_query,
            'min_stock_ratio': min_stock_ratio,
            'max_stock_ratio': max_stock_ratio,
            'min_ordered': min_ordered,
            'max_ordered': max_ordered
        }
    )

# ------------------------------
# サーチページ
# ------------------------------
@app.route('/search.html')
def search_page():
    return render_template('search.html')

# ------------------------------
# Flask 実行
# ------------------------------
if __name__ == "__main__":
    app.run(debug=True)
