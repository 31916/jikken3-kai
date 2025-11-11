from flask import Flask, render_template, request
import pandas as pd
import os

app = Flask(__name__)

# --- データパス設定 ---
DATA_DIR = "data"
CUST_PATH = os.path.join(DATA_DIR, "cust.csv")
ORDER_PATH = os.path.join(DATA_DIR, "order.csv")
ITEM_STOCK_PATH = os.path.join(DATA_DIR, "itemstock.csv")

@app.route('/', methods=['GET'])
def index():
    """
    経営戦略本部・在庫管理者共通のダッシュボード
    （元のindex()から変更なし）
    """
    gender_filter = request.args.get('gender')
    min_age_filter = request.args.get('min_age', type=int)
    max_age_filter = request.args.get('max_age', type=int)

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

    total_customers = merged["customerid"].nunique()
    total_sales = merged["total_spent"].sum()
    avg_sales = total_sales / total_customers if total_customers else 0

    top_freq = merged.sort_values("purchase_count", ascending=False).head(10)
    top_spend = merged.sort_values("total_spent", ascending=False).head(10)

    # --- 在庫分析 ---
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

    # --- HTML描画 ---
    return render_template(
        "dashboard.html",  # 経営戦略・在庫管理共通テンプレート
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

# --- ここからが新規追加部分 ---
@app.route('/customer/<customer_id>', methods=['GET'])
def customer_detail(customer_id):
    """
    🔹 オペレーターが顧客IDから注文履歴を確認するページ
    ※ 中身は“穴開き”。各自で実装してOK。
    """
    # ---- ここは自由に実装してください ----
    # 例:
    # cust = pd.read_csv(CUST_PATH)
    # order = pd.read_csv(ORDER_PATH)
    # item = pd.read_csv(os.path.join(DATA_DIR, "item.csv"))
    #
    # 顧客情報・注文履歴を抽出して
    # render_template("customer_detail.html", customer=..., orders=...)
    #
    # ---------------------------------------

    return render_template("customer_detail.html")  # 仮表示用

# --- Jinja用フォーマット関数 ---
@app.template_filter('format_currency')
def format_currency(value):
    if value is None or pd.isna(value):
        return "0"
    try:
        return f"{int(value):,}"
    except Exception:
        return str(value)

if __name__ == "__main__":
    app.run(debug=True)
from flask import Flask, render_template, request
import pandas as pd
import os

app = Flask(__name__)

# --- データパス設定 ---
DATA_DIR = "data"
CUST_PATH = os.path.join(DATA_DIR, "cust.csv")
ORDER_PATH = os.path.join(DATA_DIR, "order.csv")
ITEM_STOCK_PATH = os.path.join(DATA_DIR, "itemstock.csv")

@app.route('/', methods=['GET'])
def index():
    """
    経営戦略本部・在庫管理者共通のダッシュボード
    （元のindex()から変更なし）
    """
    gender_filter = request.args.get('gender')
    min_age_filter = request.args.get('min_age', type=int)
    max_age_filter = request.args.get('max_age', type=int)

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

    total_customers = merged["customerid"].nunique()
    total_sales = merged["total_spent"].sum()
    avg_sales = total_sales / total_customers if total_customers else 0

    top_freq = merged.sort_values("purchase_count", ascending=False).head(10)
    top_spend = merged.sort_values("total_spent", ascending=False).head(10)

    # --- 在庫分析 ---
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

    # --- HTML描画 ---
    return render_template(
        "dashboard.html",  # 経営戦略・在庫管理共通テンプレート
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

# --- ここからが新規追加部分 ---
@app.route('/customer/<customer_id>', methods=['GET'])
def customer_detail(customer_id):
    """
    🔹 オペレーターが顧客IDから注文履歴を確認するページ
    ※ 中身は“穴開き”。各自で実装してOK。
    """
    # ---- ここは自由に実装してください ----
    # 例:
    # cust = pd.read_csv(CUST_PATH)
    # order = pd.read_csv(ORDER_PATH)
    # item = pd.read_csv(os.path.join(DATA_DIR, "item.csv"))
    #
    # 顧客情報・注文履歴を抽出して
    # render_template("customer_detail.html", customer=..., orders=...)
    #
    # ---------------------------------------

    return render_template("customer_detail.html")  # 仮表示用

# --- Jinja用フォーマット関数 ---
@app.template_filter('format_currency')
def format_currency(value):
    if value is None or pd.isna(value):
        return "0"
    try:
        return f"{int(value):,}"
    except Exception:
        return str(value)

if __name__ == "__main__":
    app.run(debug=True)
