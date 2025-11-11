const menuIcon = document.getElementById('menu-icon');
const sidebar = document.getElementById('sidebar');

menuIcon.addEventListener('click', () => {
    sidebar.classList.toggle('open');
    menuIcon.classList.toggle('open');
});

// 顧客ID検索フォーム送信
function goCustomer() {
    const customerId = document.getElementById('customer_id').value.trim();
    if (!customerId) {
        alert('顧客IDを入力してください');
        return false;
    }
    window.location.href = `/customer/${customerId}`;
    return false;
}
