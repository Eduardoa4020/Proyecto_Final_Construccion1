function toggleMenu() {
  document.querySelector('.navbar-collapse').classList.toggle('open');
}

function toggleDropdown() {
  const dropdown = document.getElementById('dropdownMenu');
  const notification = document.getElementById('notificationDropdown');
  if (notification.classList.contains('open')) {
    notification.classList.remove('open');
  }
  dropdown.classList.toggle('open');
}

function toggleNotificationMenu() {
  const dropdown = document.getElementById('dropdownMenu');
  const notification = document.getElementById('notificationDropdown');
  if (dropdown.classList.contains('open')) {
    dropdown.classList.remove('open');
  }
  notification.classList.toggle('open');
}

function handleLogoClick(event) {
  event.preventDefault();
  alert('¡Bienvenido de nuevo!');
}
