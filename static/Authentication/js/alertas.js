// Lógica de mostrar/ocultar alerta
  const alerta = document.getElementById('attention-alert');
  if (distraidos >= 50) {
      alerta.classList.remove('hidden');
      alerta.style.display = 'flex';
  } else {
      alerta.classList.add('hidden');
      alerta.style.display = 'none';
  }
  // Lógica de notificaciones
let notificaciones = [];

function toggleNotificationMenu() {
  const dropdown = document.getElementById('notificationDropdown');
  dropdown.style.display = (dropdown.style.display === 'block') ? 'none' : 'block';
  mostrarNotificaciones();
}

function mostrarNotificaciones() {
  const dropdown = document.getElementById('notificationDropdown');
  const badge = document.getElementById('notification-badge');
  const campana = document.getElementById('campana-icon');
  if (notificaciones.length > 0) {
    badge.style.display = 'inline-block';
    badge.textContent = notificaciones.length;
    campana.src = "/static/Authentication/image/campana0.png";
    dropdown.innerHTML = notificaciones.map((n, i) =>
      `<a href="#" onclick="borrarNotificacion(${i});return false;" style="display:block; margin-bottom:8px;">${n}</a>`
    ).join('');
  } else {
    badge.style.display = 'none';
    campana.src = "/static/Authentication/image/campana.png";
    dropdown.innerHTML = `
      <div style="
        width:100%;height:100%;
        display:flex;align-items:center;justify-content:center;
        min-height:80px;
      ">
        <span class="block text-gray-500 text-center" style="font-size:1.1em;">Sin notificaciones</span>
      </div>
    `;
  }
  dropdown.style.minWidth = "220px";
  dropdown.style.minHeight = "80px";
  dropdown.style.background = "#fafbfc";
  dropdown.style.padding = "0";
  dropdown.style.boxSizing = "border-box";
}

function agregarNotificacion(mensaje) {
  notificaciones.push(mensaje);
  mostrarNotificaciones();
}

function borrarNotificacion(idx) {
  notificaciones.splice(idx, 1);
  mostrarNotificaciones();
  document.getElementById('notificationDropdown').style.display = 'none';
}

// Ejemplo de integración con atención en clase
function verificarAtencion(distraidos) {
  if (distraidos >= 50) {
    agregarNotificacion('¡Alerta! Más del 50% de estudiantes están distraídos.');
  }
}

document.addEventListener('DOMContentLoaded', function() {
  mostrarNotificaciones();
});
