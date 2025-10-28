from flask import Flask, render_template, request
import pandas as pd
import plotly.express as px
import plotly.io as pio
import os

app = Flask(__name__)

# --- CSVパス ---
DATA_DIR = "data"
CUST_PATH = os.path.join(DATA_DIR, "cust.csv")
ORDER_PATH = os.path.join(DATA_DIR, "order.csv")
ITEM_PATH = os.path.join(DATA_DIR, "item.csv")
ITEMSTOCK_PATH = os.path.join(DATA_DIR, "itemstock.csv")

# --- CSV読み込み ---
cust = pd.read_csv(CUST_PATH, encoding='utf-8')
order_cols = ['customerid','orderdate','orderno','itemprice','orderitem','orderitemcate','ordernum','orderprice']
order = pd.read_csv(ORDER_PATH, encoding='utf-8', usecols=order_cols)
item = pd.read_csv(ITEM_PATH, encoding='utf-8')
itemstock = pd.read_csv(ITEMSTOCK_PATH, encoding='utf-8')

# 列名を小文字化
cust.columns = [c.lower() for c in cust.columns]
order.columns = [c.lower() for c in order.columns]
item.columns = [c.lower() for c in item.columns]
itemstock.columns = [c.lower() for c in itemstock.columns]

# orderdateをdatetime型に変換
order['orderdate'] = pd.to_datetime(order['orderdate'])

# --- トップページ ---
@app.route('/')
def index():
    return render_template('search.html')

# --- 顧客ID検索 ---
@app.route('/customer', methods=['POST'])
def customer():
    customer_id = request.form.get('customer_id')
    if not customer_id:
        return "顧客IDを入力してください"
    
    cust_orders = order[order['customerid'] == customer_id].sort_values('orderdate')
    if cust_orders.empty:
        return f"顧客ID {customer_id} の注文履歴はありません"

    total_orders = cust_orders.shape[0]
    total_spent = cust_orders['orderprice'].sum()
    last_order = cust_orders['orderdate'].max()

    fig = px.bar(cust_orders, x='orderdate', y='orderprice',
                 title=f'顧客ID {customer_id} の購入履歴',
                 labels={'orderdate':'注文日', 'orderprice':'注文金額'})
    graph_html = pio.to_html(fig, full_html=False)

    customer_info = cust[cust['customerid'] == customer_id].to_dict(orient='records')[0]

    return render_template(
        'customer.html',
        graph_html=graph_html,
        customer_info=customer_info,
        cust_orders=cust_orders.to_dict(orient='records'),
        total_orders=total_orders,
        total_spent=total_spent,
        last_order=last_order
    )

# --- 商品分析・在庫警告 ---
@app.route('/item_analysis')
def item_analysis():
    # 人気商品ランキング（累計売上）
    top_items = order.groupby('orderitem').agg(
        total_sales=('orderprice','sum'),
        order_count=('orderno','count')
    ).reset_index().sort_values('total_sales', ascending=False).head(10)
    
    # 在庫数と結合
    top_items = pd.merge(top_items, itemstock, left_on='orderitem', right_on='item', how='left')
    
    # 在庫少ない警告
    low_stock_items = top_items[top_items['stock'] <= 5]  # 在庫5以下を警告
    
    fig = px.bar(top_items, x='orderitem', y='total_sales', 
                 title='人気商品ランキング（売上順）', labels={'orderitem':'商品コード','total_sales':'累計売上'})
    graph_html = pio.to_html(fig, full_html=False)
    
    return render_template('item_analysis.html', graph_html=graph_html, low_stock_items=low_stock_items.to_dict(orient='records'))

# --- 地域別売上分析 ---
@app.route('/region_analysis')
def region_analysis():
    merged = pd.merge(order, cust[['customerid','area','age','sex']], on='customerid', how='left')
    
    # 都道府県別売上
    region_sales = merged.groupby('area').agg(total_sales=('orderprice','sum'), order_count=('orderno','count')).reset_index()
    fig_map = px.choropleth(region_sales, locations='area', locationmode='country names',
                            color='total_sales', title='都道府県別売上', color_continuous_scale='Blues')
    map_html = pio.to_html(fig_map, full_html=False)
    
    # 年齢・性別別購入傾向
    age_sex_sales = merged.groupby(['age','sex']).agg(total_sales=('orderprice','sum')).reset_index()
    fig_age_sex = px.bar(age_sex_sales, x='age', y='total_sales', color='sex', barmode='group',
                         title='年齢・性別別購入金額')
    age_sex_html = pio.to_html(fig_age_sex, full_html=False)
    
    return render_template('region_analysis.html', map_html=map_html, age_sex_html=age_sex_html)

if __name__ == "__main__":
    app.run(debug=True)
