# 🔄 シーケンス図（Sequence Diagram）

本システムの主要な画面における  
「ブラウザ → Flask → CSVデータ → ブラウザ」  
の一連の処理フローを時系列で示す。

---

## 1. ダッシュボード表示（/dashboard）

sequenceDiagram
    autonumber
    actor User

    User ->> Browser: /dashboard にアクセス
    Browser ->> Flask: GET /dashboard

    Flask ->> CSV: cust.csv 読み込み
    CSV -->> Flask: データ返却

    Flask ->> CSV: order.csv 読み込み
    CSV -->> Flask: データ返却

    Flask ->> CSV: itemstock.csv 読み込み
    CSV -->> Flask: データ返却

    Flask ->> Flask: 性別・年齢・地域フィルタ処理
    Flask ->> Flask: 顧客別・地域別・年代別の集計処理
    Flask ->> Flask: 地図・グラフ用データ整形

    Flask -->> Browser: dashboard.html + JSONデータ
    Browser ->> Browser: Chart.js でグラフ描画
    Browser ->> Browser: SVG 日本地図に色を適用

sequenceDiagram
    autonumber
    actor User

    User ->> Browser: 顧客IDリンクをクリック
    Browser ->> Flask: GET /customer/1234

    Flask ->> CSV: cust.csv 読み込み
    CSV -->> Flask: 顧客データ返却

    Flask ->> CSV: order.csv 読み込み
    CSV -->> Flask: 顧客注文履歴返却

    Flask ->> Flask: 購入履歴の集計（合計・回数・最終購入日）
    Flask ->> Flask: Plotly を用いたグラフ生成

    Flask -->> Browser: customer.html + グラフHTML
    Browser ->> Browser: 注文履歴グラフ描画

sequenceDiagram
    autonumber
    actor User

    User ->> Browser: 在庫ページにアクセス
    Browser ->> Flask: GET /stock.html

    Flask ->> CSV: item.csv 読み込み
    CSV -->> Flask: 返却

    Flask ->> CSV: itemstock.csv 読み込み
    CSV -->> Flask: 返却

    Flask ->> CSV: order.csv 読み込み
    CSV -->> Flask: 返却

    Flask ->> Flask: 商品 × 注文データのマージ
    Flask ->> Flask: 在庫率（stock / ordered）を計算
    Flask -->> Browser: stock.html + データ表示
