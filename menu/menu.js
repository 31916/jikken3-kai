const menuIcon = document.getElementById("menu-icon");
const sidebar = document.getElementById("sidebar");
const mainContent = document.getElementById("main-content");

menuIcon.addEventListener("click", () => {
  sidebar.classList.toggle("active");
  mainContent.classList.toggle("active");
});
