
const items = document.querySelectorAll('.carousel-item');
let currentIndex = 0;
let autoSlideInterval; // 自動スライド用のタイマーを格納する変数

/**
 * 指定されたインデックスのスライドに移動する
 * @param {number} n - 移動先のスライドのインデックス
 */
function goToSlide(n) {
    // 現在のスライドを非アクティブにする
    items[currentIndex].classList.remove('active');
    
    // 新しいインデックスを計算 (ループするように調整)
    currentIndex = (n + items.length) % items.length;
    
    // 新しいスライドをアクティブにする
    items[currentIndex].classList.add('active');
}

// 次のスライドに移動する
function nextSlide() {
    goToSlide(currentIndex + 1);
}

// 前のスライドに移動する
function prevSlide() {
    goToSlide(currentIndex - 1);
}

// ページロード時に自動スライドを開始する
window.onload = function() {
    // 自動スライドを開始し、タイマーIDを保持
    autoSlideInterval = setInterval(nextSlide, 3000); // 3秒ごと

    // 制御ボタンにイベントリスナーを追加
    document.getElementById('nextButton').addEventListener('click', () => {
        // 手動操作時、自動スライドタイマーをリセットし、再度開始
        clearInterval(autoSlideInterval);
        nextSlide();
        autoSlideInterval = setInterval(nextSlide, 3000);
    });

    document.getElementById('prevButton').addEventListener('click', () => {
        // 手動操作時、自動スライドタイマーをリセットし、再度開始
        clearInterval(autoSlideInterval);
        prevSlide();
        autoSlideInterval = setInterval(nextSlide, 3000);
    });
}

// 初期表示を確実に設定
items.forEach((item, index) => {
    if (index === 0) {
        item.classList.add('active');
    } else {
        item.classList.remove('active');
    }
});
