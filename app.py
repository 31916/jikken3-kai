@app.route('/stock.html')
def stock_page():
    import pandas as pd
    import os

    DATA_DIR = "data"
    ORDER_PATH = os.path.join(DATA_DIR, "order.csv")
    ITEM_STOCK_PATH = os.path.join(DATA_DIR, "itemstock.csv")

    # データ読み込み
    order = pd.read_csv(ORDER_PATH, encoding='utf-8-sig')
    item_stock = pd.read_csv(ITEM_STOCK_PATH, encoding='utf-8-sig')

    # 前処理
    order.columns = [c.lower() for c in order.columns]
    item_stock.columns = [c.lower() for c in item_stock.columns]
    order.rename(columns={'orderitem': 'itemcode'}, inplace=True)
    item_stock.rename(columns={'item': 'itemcode'}, inplace=True)

    # 在庫分析
    order_stock_merged = pd.merge(
        order,
        item_stock[['itemcode', 'itemname','stock']] if 'itemname' in item_stock.columns else item_stock[['itemcode', 'stock']],
        on='itemcode',
        how='left'
    ).drop_duplicates(subset=['orderdate', 'orderno', 'itemcode'])

    item_analysis = (
        order_stock_merged.groupby(['itemcode'] + (['itemname'] if 'itemname' in order_stock_merged.columns else []))
        .agg(total_ordered=('ordernum', 'sum'), current_stock=('stock', 'max'))
        .reset_index()
    )

    item_analysis['stock_ratio'] = item_analysis.apply(
        lambda r: (r['current_stock'] / r['total_ordered']) if r['total_ordered'] else 0,
        axis=1
    )

    low_stock_risk = (
        item_analysis[(item_analysis['total_ordered'] > 0) & (item_analysis['stock_ratio'] < 0.1)]
        .sort_values('stock_ratio')
        .head(5)
    )

    # --- 複合検索 ---
    itemcode_query = request.args.get('itemcode', '').strip()
    itemname_query = request.args.get('itemname', '').strip()
    min_stock_ratio = request.args.get('min_stock_ratio', type=float)
    max_stock_ratio = request.args.get('max_stock_ratio', type=float)
    min_ordered = request.args.get('min_ordered', type=int)
    max_ordered = request.args.get('max_ordered', type=int)

    if itemcode_query:
        item_analysis = item_analysis[item_analysis['itemcode'].str.contains(itemcode_query, case=False, na=False)]
        low_stock_risk = low_stock_risk[low_stock_risk['itemcode'].str.contains(itemcode_query, case=False, na=False)]

    if 'itemname' in item_analysis.columns and itemname_query:
        item_analysis = item_analysis[item_analysis['itemname'].str.contains(itemname_query, case=False, na=False)]
        low_stock_risk = low_stock_risk[low_stock_risk['itemname'].str.contains(itemname_query, case=False, na=False)]

    if min_stock_ratio is not None:
        item_analysis = item_analysis[item_analysis['stock_ratio']*100 >= min_stock_ratio]
        low_stock_risk = low_stock_risk[low_stock_risk['stock_ratio']*100 >= min_stock_ratio]
    if max_stock_ratio is not None:
        item_analysis = item_analysis[item_analysis['stock_ratio']*100 <= max_stock_ratio]
        low_stock_risk = low_stock_risk[low_stock_risk['stock_ratio']*100 <= max_stock_ratio]

    if min_ordered is not None:
        item_analysis = item_analysis[item_analysis['total_ordered'] >= min_ordered]
        low_stock_risk = low_stock_risk[low_stock_risk['total_ordered'] >= min_ordered]
    if max_ordered is not None:
        item_analysis = item_analysis[item_analysis['total_ordered'] <= max_ordered]
        low_stock_risk = low_stock_risk[low_stock_risk['total_ordered'] <= max_ordered]

    return render_template(
        'stock.html',
        low_stock_risk=low_stock_risk.to_dict(orient='records'),
        item_analysis=item_analysis.to_dict(orient='records'),
        search_params={
            'itemcode': itemcode_query,
            'itemname': itemname_query,
            'min_stock_ratio': min_stock_ratio,
            'max_stock_ratio': max_stock_ratio,
            'min_ordered': min_ordered,
            'max_ordered': max_ordered
        }
    )
