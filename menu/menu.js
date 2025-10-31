document.addEventListener('DOMContentLoaded', () => {
    // 要素の取得
    const menuIcon = document.getElementById('menu-icon');
    const sidebar = document.getElementById('sidebar');
    const mainContent = document.getElementById('main-content');

    // アイコンクリック時の処理
    menuIcon.addEventListener('click', () => {
        // sidebar、menu-icon、main-contentの全てに 'active' / 'shifted' クラスを切り替える
        
        // サイドバーとアイコンの開閉状態を切り替え
        sidebar.classList.toggle('active');
        menuIcon.classList.toggle('active');
        
        // メインコンテンツの位置を切り替え
        // CSSで定義したshiftedクラスを付与/削除
        mainContent.classList.toggle('shifted');
    });
});