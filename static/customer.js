const menuIcon = document.getElementById('menu-icon');
const sidebar = document.getElementById('sidebar');

menuIcon.addEventListener('click', () => {
    sidebar.classList.toggle('open');
    menuIcon.classList.toggle('open');
});
