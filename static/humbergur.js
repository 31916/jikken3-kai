const menuIcon = document.getElementById("menu-icon");
const sidebar = document.getElementById("sidebar");
const mainContent = document.getElementById("main-content");

menuIcon.addEventListener("click", () => {
    sidebar.classList.toggle("active");
    menuIcon.classList.toggle("active");
});

const backToTopButton = document.getElementById("back-to-top");

// 初期状態ではボタンを非表示にする
backToTopButton.style.display = "none"; 

// ページをスクロールしたときの動作
window.addEventListener("scroll", () => {
    // スクロール量が200pxを超えたらボタンを表示
    if (document.body.scrollTop > 200 || document.documentElement.scrollTop > 200) {
        backToTopButton.style.display = "block";
    } else {
        backToTopButton.style.display = "none";
    }
});

// ボタンをクリックしたときの動作
backToTopButton.addEventListener("click", () => {
    window.scrollTo({
        top: 0,
        behavior: "smooth" // スムーズスクロールを有効にする
    });
});