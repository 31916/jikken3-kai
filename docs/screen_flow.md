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


%% ホームからの遷移
A --> B
A --> C
A --> D

%%
B --> A
B --> C
B --> D

%%
C --> A
C --> B
C --> D
C --> E

%%
D --> A
D --> B
D --> C

%%
E --> A
E --> B
E --> C
E --> D

```