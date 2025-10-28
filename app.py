from flask import Flask, render_template, request
import pandas as pd
import plotly.express as px
import plotly.io as pio
import os

app = Flask(__name__)

DATA_DIR = "data"
CUST_PATH = os.path.join(DATA_DIR, "cust.csv")
ORDER_PATH = os.path.join(DATA_DIR, "order.csv")

# --- CSV読み込み（アプリ起動時に1回だけ読み込む） ---
cust = pd.read_csv(CUST_PATH)
order = pd.read_csv(ORDER_PATH)

# 列名小文字化
cust.columns = [c.lower() for c in cust.columns]
order.columns = [c.lower() for c in order.columns]

# orderdateをdatetime型に変換
order['orderdate'] = pd.to_datetime(order['orderdate'])

@app.route('/')
def index():
    return render_template('search.html')

@app.route('/customer', methods=['POST'])
def customer():
    customer_id = request.form.get('customer_id')
    
    # 入力チェック
    if not customer_id.isdigit():
        return "顧客IDは数字で入力してください"
    
    customer_id = int(customer_id)
    
    # 該当顧客の注文履歴
    cust_orders = order[order['customerid'] == customer_id].sort_values('orderdate')
    
    if cust_orders.empty:
        return f"顧客ID {customer_id} の注文履歴はありません"
    
    # 時系列棒グラフ作成
    fig = px.bar(cust_orders, x='orderdate', y='orderprice',
                 title=f'顧客ID {customer_id} の購入履歴',
                 labels={'orderdate':'注文日', 'orderprice':'注文金額'})
    
    # HTML化
    graph_html = pio.to_html(fig, full_html=False)
    
    # 顧客情報取得
    customer_info = cust[cust['customerid']==customer_id].to_dict(orient='records')[0]
    
    return render_template('customer.html', graph_html=graph_html, customer_info=customer_info)
