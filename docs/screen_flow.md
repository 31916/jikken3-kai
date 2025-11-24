# 📱 画面遷移図（Screen Flow）

本アプリケーションの画面構成と遷移関係をまとめる。

## 画面一覧

- **① ホームページ（/）**
- **② ダッシュボード（/dashboard）**
- **③ 顧客 ID 検索（/search.html）**
- **④ 在庫リスト（/stock.html）**
- **⑤ 顧客詳細ページ（/customer/<id>）**

---

## 画面遷移図

```mermaid
flowchart TD

%% 画面ノード
A[ホーム /]
B[ダッシュボード /dashboard]
C[顧客ID検索 /search.html]
D[在庫一覧 /stock.html]
E[顧客詳細 /customer/<id>]

%% 共通ナビ（全画面に常駐するUI）
H[共通ハンバーガーメニュー<br/>（header + sidebar）]

%% ホームからの遷移
A --> B
A --> C
A --> D

%% 共通ナビからの遷移（全ページで可能）
H --> A
H --> B
H --> C
H --> D

%% 各ページに共通ナビがあることを明示（点線＝UI常駐）
A -.常駐.-> H
B -.常駐.-> H
C -.常駐.-> H
D -.常駐.-> H
E -.常駐.-> H

%% 個別遷移
C --> E


```