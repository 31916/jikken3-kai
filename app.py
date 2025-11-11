# ===============================================
# 📦 在庫管理ページ
# ===============================================
@app.route('/stock.html')
def stock_page():
    # データ読み込み
    item_master = pd.read_csv(ITEM_PATH, encoding='utf-8-sig')
    item_stock = pd.read_csv(ITEM_STOCK_PATH, encoding='utf-8-sig')
    order = pd.read_csv(ORDER_PATH, encoding='utf-8-sig')

    item_master.columns = [c.lower() for c in item_master.columns]
    item_stock.columns = [c.lower() for c in item_stock.columns]
    order.columns = [c.lower() for c in order.columns]

    # マスタ + 在庫結合
    merged_items = pd.merge(item_master, item_stock, on='item', how='left')

    # 注文 + 在庫結合
    order_stock_merged = pd.merge(order, merged_items, left_on='orderitem', right_on='item', how='left')
    order_stock_merged = order_stock_merged.drop_duplicates(subset=['orderdate','orderno','orderitem'])

    # 在庫分析
    item_analysis = (
        order_stock_merged.groupby(['item','itemcate'])
        .agg(total_ordered=('ordernum','sum'), current_stock=('stock','max'))
        .reset_index()
    )
    item_analysis['stock_ratio'] = item_analysis.apply(
        lambda r: (r['current_stock']/r['total_ordered']) if r['total_ordered'] else 0, axis=1
    )

    # 低在庫5件（常に表示）
    low_stock_risk = (
        item_analysis[(item_analysis['total_ordered']>0) & (item_analysis['stock_ratio']<0.1)]
        .sort_values('stock_ratio')
        .head(5)
    )

    # --- 検索処理 ---
    item_query = request.args.get('item','').strip()
    cate_query = request.args.get('itemcate','').strip()
    min_stock_ratio = request.args.get('min_stock_ratio', type=float)
    max_stock_ratio = request.args.get('max_stock_ratio', type=float)
    min_ordered = request.args.get('min_ordered', type=float)
    max_ordered = request.args.get('max_ordered', type=float)

    search_item_analysis = item_analysis.copy()
    if item_query:
        search_item_analysis = search_item_analysis[search_item_analysis['item'].str.contains(item_query, case=False, na=False)]
    if cate_query:
        search_item_analysis = search_item_analysis[search_item_analysis['itemcate'].str.contains(cate_query, case=False, na=False)]
    if min_stock_ratio is not None:
        search_item_analysis = search_item_analysis[search_item_analysis['stock_ratio']*100 >= min_stock_ratio]
    if max_stock_ratio is not None:
        search_item_analysis = search_item_analysis[search_item_analysis['stock_ratio']*100 <= max_stock_ratio]
    if min_ordered is not None:
        search_item_analysis = search_item_analysis[search_item_analysis['total_ordered'] >= min_ordered]
    if max_ordered is not None:
        search_item_analysis = search_item_analysis[search_item_analysis['total_ordered'] <= max_ordered]

    # プルダウン用のカテゴリリスト
    categories = item_analysis['itemcate'].dropna().unique().tolist()
    categories.sort()

    search_params = {
        "item": item_query,
        "itemcate": cate_query,
        "min_stock_ratio": min_stock_ratio if min_stock_ratio is not None else '',
        "max_stock_ratio": max_stock_ratio if max_stock_ratio is not None else '',
        "min_ordered": min_ordered if min_ordered is not None else '',
        "max_ordered": max_ordered if max_ordered is not None else ''
    }

    return render_template(
        'stock.html',
        low_stock_risk=low_stock_risk.to_dict(orient='records'),
        item_analysis=search_item_analysis.to_dict(orient='records'),
        search_params=search_params,
        categories=categories
    )
