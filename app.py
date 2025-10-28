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

# --- CSV読み込み ---
cust = pd.read_csv(CUST_PATH, encoding='utf-8')
order_cols = ['customerid','orderdate','orderno','itemprice','orderitem','orderitemcate','ordernum','orderprice']
order = pd.read_csv(ORDER_PATH, encoding='utf-8', usecols=order_cols)

# 列名を小文字化
cust.columns = [c.lower() for c in cust.columns]
order.columns = [c.lower() for c in order.columns]

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
    
    # 該当顧客の注文履歴
    cust_orders = order[order['customerid'] == customer_id].sort_values('orderdate')
    
    if cust_orders.empty:
        return f"顧客ID {customer_id} の注文履歴はありません"
    
    # KPI計算
    total_orders = cust_orders.shape[0]            # 累計注文回数
    total_spent = cust_orders['orderprice'].sum()  # 累計購入金額
    last_order = cust_orders['orderdate'].max()    # 最終購入日
    
    # グラフ作成
    fig = px.bar(
        cust_orders,
        x='orderdate',
        y='orderprice',
        title=f'顧客ID {customer_id} の購入履歴',
        labels={'orderdate':'注文日', 'orderprice':'注文金額'}
    )
    graph_html = pio.to_html(fig, full_html=False)
    
    # 顧客情報
    customer_info = cust[cust['customerid'] == customer_id].to_dict(orient='records')[0]
    
    return render_template(
        'customer.html',
        customer_info=customer_info,
        total_orders=total_orders,
        total_spent=total_spent,
        last_order=last_order,
        graph_html=graph_html,
        cust_orders=cust_orders.to_dict(orient='records')
    )

if __name__ == "__main__":
    app.run(debug=True)
