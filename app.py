from flask import Flask, render_template
import pandas as pd
import plotly.express as px
import plotly.io as pio
import os

app = Flask(__name__)

DATA_DIR = "data"
ITEM_PATH = os.path.join(DATA_DIR, "item.csv")
STOCK_PATH = os.path.join(DATA_DIR, "itemstock.csv")
ORDER_PATH = os.path.join(DATA_DIR, "order.csv")

item = pd.read_csv(ITEM_PATH, encoding='utf-8')
stock = pd.read_csv(STOCK_PATH, encoding='utf-8')
order_cols = ['customerid','orderdate','orderno','itemprice','orderitem','orderitemcate','ordernum','orderprice']
order = pd.read_csv(ORDER_PATH, encoding='utf-8', usecols=order_cols)

item.columns = [c.lower() for c in item.columns]
stock.columns = [c.lower() for c in stock.columns]
order.columns = [c.lower() for c in order.columns]
order['orderdate'] = pd.to_datetime(order['orderdate'])

# 商品集計
item_summary = (
    order.groupby(['orderitem','orderitemcate'])
    .agg(total_sales=('orderprice','sum'), order_count=('orderno','count'))
    .reset_index()
)
item_summary = pd.merge(item_summary, stock, left_on='orderitem', right_on='item', how='left')

low_stock_items = item_summary[item_summary['stock'] <= 5].to_dict(orient='records')

# グラフ作成
fig = px.bar(
    item_summary.sort_values('total_sales', ascending=False),
    x='orderitem', y='total_sales', color='orderitemcate',
    title='商品別累計売上ランキング',
    labels={'orderitem':'商品コード', 'total_sales':'累計売上'}
)
graph_html = pio.to_html(fig, full_html=False, include_plotlyjs='cdn')

@app.route('/item_analysis')
def item_analysis():
    return render_template(
        'item_analysis.html',
        graph_html=graph_html,
        low_stock_items=low_stock_items
    )

if __name__ == "__main__":
    app.run(debug=True)
