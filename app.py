from flask import Flask, render_template, request
import pandas as pd
import plotly.express as px
import plotly.io as pio
import os

# Flaskアプリケーションのインスタンスを作成
app = Flask(__name__)

# --- CSVファイルのパス設定 ---
DATA_DIR = "data"  # データフォルダのパス
CUST_PATH = os.path.join(DATA_DIR, "cust.csv")   # 顧客情報CSVのパス
ORDER_PATH = os.path.join(DATA_DIR, "order.csv") # 注文情報CSVのパス

# --- CSVファイルの読み込み ---
# 顧客情報データをUTF-8で読み込み
cust = pd.read_csv(CUST_PATH, encoding='utf-8')

# 注文データは必要な列だけ選択して読み込み
order_cols = ['customerid','orderdate','orderno','itemprice','orderitem','orderitemcate','ordernum','orderprice']
order = pd.read_csv(ORDER_PATH, encoding='utf-8', usecols=order_cols)

# 列名をすべて小文字に統一（大文字・小文字の違いでバグを防ぐ）
cust.columns = [c.lower() for c in cust.columns]
order.columns = [c.lower() for c in order.columns]

# 日付データ（orderdate）をdatetime型に変換（グラフなどで扱いやすくするため）
order['orderdate'] = pd.to_datetime(order['orderdate'])

# --- トップページ（検索フォームを表示） ---
@app.route('/')
def index():
    # templates/search.html を表示
    return render_template('search.html')

# --- 顧客IDで検索したときの処理 ---
@app.route('/customer', methods=['POST'])
def customer():
    # フォームから顧客IDを取得
    customer_id = request.form.get('customer_id')
    
    # 顧客IDが空の場合のエラーチェック
    if not customer_id:
        return "顧客IDを入力してください"
    
    # 入力された顧客IDに一致する注文データを抽出
    cust_orders = order[order['customerid'] == customer_id].sort_values('orderdate')
    
    # 注文データが存在しない場合のメッセージ
    if cust_orders.empty:
        return f"顧客ID {customer_id} の注文履歴はありません"
    
    # --- KPI（重要指標）の計算 ---
    total_orders = cust_orders.shape[0]            # 累計注文回数
    total_spent = cust_orders['orderprice'].sum()  # 累計購入金額
    last_order = cust_orders['orderdate'].max()    # 最終購入日
    
    # --- 購入履歴グラフを作成（棒グラフ） ---
    fig = px.bar(
        cust_orders,
        x='orderdate',
        y='orderprice',
        title=f'顧客ID {customer_id} の購入履歴',
        labels={'orderdate':'注文日', 'orderprice':'注文金額'}
    )
    # グラフをHTMLとして埋め込み可能な形式に変換
    graph_html = pio.to_html(fig, full_html=False)
    
    # --- 顧客基本情報を取得 ---
    # 顧客IDに一致する顧客情報（1件分）を辞書形式に変換
    customer_info = cust[cust['customerid'] == customer_id].to_dict(orient='records')[0]
    
    # --- 結果をHTMLテンプレートに渡して表示 ---
    return render_template(
        'customer.html',
        customer_info=customer_info,           # 顧客情報
        total_orders=total_orders,             # 注文回数
        total_spent=total_spent,               # 総購入金額
        last_order=last_order,                 # 最終購入日
        graph_html=graph_html,                 # グラフ（HTML形式）
        cust_orders=cust_orders.to_dict(orient='records')  # 注文履歴（表表示用）
    )

# --- Flaskアプリを実行 ---
if __name__ == "__main__":
    app.run(debug=True)
