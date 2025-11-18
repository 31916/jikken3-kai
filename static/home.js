// ------------------------------
// カルーセル基本設定
// ------------------------------
const items = document.querySelectorAll('.carousel-item');
let currentIndex = 0;
let autoSlideInterval; // 自動スライド用のタイマーを格納

/**
 * 指定されたインデックスのスライドに移動する
 * @param {number} n - 移動先のスライドインデックス
 */
function goToSlide(n) {
    // 現在のスライドを非アクティブにする
    items[currentIndex].classList.remove('active');
    
    // 新しいインデックスを計算（ループ対応）
    currentIndex = (n + items.length) % items.length;
    
    // 新しいスライドをアクティブにする
    items[currentIndex].classList.add('active');
}

// 次のスライドに移動
function nextSlide() {
    goToSlide(currentIndex + 1);
}

// 前のスライドに移動
function prevSlide() {
    goToSlide(currentIndex - 1);
}

// ------------------------------
// ページロード時処理
// ------------------------------
window.onload = function() {
    // 初期スライドを設定
    items.forEach((item, index) => {
        if (index === 0) {
            item.classList.add('active');
        } else {
            item.classList.remove('active');
        }
    });

    // 自動スライド開始（3秒ごと）
    autoSlideInterval = setInterval(nextSlide, 3000);

    // 制御ボタンイベント
    document.getElementById('nextButton').addEventListener('click', () => {
        clearInterval(autoSlideInterval); // タイマー停止
        nextSlide();
        autoSlideInterval = setInterval(nextSlide, 3000); // 再開
    });

    document.getElementById('prevButton').addEventListener('click', () => {
        clearInterval(autoSlideInterval); // タイマー停止
        prevSlide();
        autoSlideInterval = setInterval(nextSlide, 3000); // 再開
    });

    // ------------------------------
    // マウスオーバーで自動スライド停止
    // ------------------------------
    const carouselContainer = document.getElementById('carousel-container');

    carouselContainer.addEventListener('mouseenter', () => {
        clearInterval(autoSlideInterval); // 停止
    });

    carouselContainer.addEventListener('mouseleave', () => {
        autoSlideInterval = setInterval(nextSlide, 3000); // 再開
    });
};
