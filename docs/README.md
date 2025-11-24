# 📘 システムドキュメント（概要）

このフォルダ `docs/` は、本システムの開発者・引き継ぎ担当向けに  
アプリケーションの内部構造と動作を理解できるようまとめたドキュメント群です。

---

# 📦 収録ドキュメント一覧

| ファイル名 | 内容 |
|------------|------|
| `table_structure.md` | データベース（CSV）のテーブル構造・ER図 |
| `screen_flow.md` | 画面遷移図・各画面の役割 |
| `sequence_diagram.md` | ブラウザ–Flask–CSV 間の処理フロー（Mermaid 形式） |
| `program_description.md` | Flask / HTML / JS / CSS 各ファイルの役割説明 |

---

# 🏗 システム全体の構成

このアプリケーションは以下で構成される：

- **Flask（Python）**  
  - ルーティング処理  
  - CSV 読み込み・集計ロジック  
  - HTML テンプレートへのデータ注入  

- **CSV データ（データベース代替）**  
  - `cust.csv`：顧客情報  
  - `order.csv`：購入履歴  
  - `itemstock.csv`：在庫情報  
  - `item.csv`: 商品情報

- **HTML + CSS + JavaScript**  
  - Chart.js によるグラフ描画  
  - SVG 日本地図の動的塗り分け  
  - Plotly で顧客履歴グラフ作成  
  - ハンバーガーメニュー（CSS + JS）

---

# 📬 連絡先

引き継ぎや修正依頼などは開発者まで。

---

## 📌 GitHub リポジトリ

本プロジェクトのソースコード一式はこちら：

🔗 https://github.com/31916/jikken3-kai

