from flask import Flask, render_template
import pandas as pd
import os

app = Flask(__name__)

# --- データパス設定 ---
DATA_DIR = "data"
CUST_PATH = os.path.join(DATA_DIR, "cust.csv")
ORDER_PATH = os.path.join(DATA_DIR, "order.csv")

@app.route("/")
def index():
    # ===== データ読み込み =====
    cust = pd.read_csv(CUST_PATH)
    order = pd.read_csv(ORDER_PATH)

    # 列名を小文字化（安全のため）
    cust.columns = [c.lower() for c in cust.columns]
    order.columns = [c.lower() for c in order.columns]

    # ===== 集計処理 =====
    # 各顧客の購入回数・合計金額・最終注文日
    summary = (
        order.groupby("customerid")
        .agg(
            purchase_count=("orderdate", "count"),
            total_spent=("orderprice", "sum"),
            last_order=("orderdate", "max")
        )
        .reset_index()
    )

    # 顧客情報と結合
    merged = pd.merge(cust, summary, on="customerid", how="left").fillna(0)

    # 全体のKPI
    total_customers = merged["customerid"].nunique()
    total_sales = merged["total_spent"].sum()
    avg_sales = total_sales / total_customers if total_customers else 0

    # ランキング
    top_freq = merged.sort_values("purchase_count", ascending=False).head(10)
    top_spend = merged.sort_values("total_spent", ascending=False).head(10)

    # HTMLへ渡す
    return render_template(
        "index.html",
        total_customers=int(total_customers),
        total_sales=int(total_sales),
        avg_sales=int(avg_sales),
        top_freq=top_freq.to_dict(orient="records"),
        top_spend=top_spend.to_dict(orient="records"),
    )

if __name__ == "__main__":
    app.run(debug=True)
