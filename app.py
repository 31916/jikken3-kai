from flask import Flask, render_template, request
import pandas as pd
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

cust.columns = [c.lower() for c in cust.columns]
order.columns = [c.lower() for c in order.columns]
order['orderdate'] = pd.to_datetime(order['orderdate'])

# --- トップページ（検索フォーム） ---
@app.route('/')
def index():
    return render_template('search.html')  # search.html のみ残す

if __name__ == "__main__":
    app.run(debug=True)
