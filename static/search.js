const menuIcon = document.getElementById('menu-icon');
const sidebar = document.getElementById('sidebar');

menuIcon.addEventListener('click', () => {
    sidebar.classList.toggle('open');
    menuIcon.classList.toggle('open');
});

// 顧客ID検索フォーム送信
function goCustomer() {
    // 必要な要素を取得
    const customerIdInput = document.getElementById('customer_id');
    const errorMessageDiv = document.getElementById('error-message');
    
    // 入力値を取得し、前後の空白を削除
    const customerId = customerIdInput.value.trim();

    // エラーメッセージを一旦クリア
    errorMessageDiv.textContent = ""; 

    // 1. 入力値が空欄かどうかをチェック
    if (customerId === "") {
        // エラーメッセージを設定して表示 (赤文字表示のCSSが適用されます)
        errorMessageDiv.textContent = "⚠️ 顧客IDを入力してください。";
        
        // 入力フィールドにフォーカスを戻す
        customerIdInput.focus();
        
        // フォームの送信（ページ遷移）を中止
        return false; 
    }

    // 2. 入力値が有効な場合、顧客情報ページへ遷移
    // /customer/ID の形式でページ遷移を実行
    window.location.href = `/customer/${customerId}`;
    
    // フォームの送信を中止 (ページ遷移はJS側で行うため)
    return false;
}
