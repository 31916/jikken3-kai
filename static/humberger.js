
const menuIcon = document.getElementById("menu-icon");
const sidebar = document.getElementById("sidebar");
const mainContent = document.getElementById("main-content");

menuIcon.addEventListener("click", () => {
    // ✅ 修正なし。メニューアイコンクリックで .active クラスをトグルし、
    //    CSSでサイドバーとメインコンテンツを移動させます。
    sidebar.classList.toggle("active");
    mainContent.classList.toggle("active");
});
