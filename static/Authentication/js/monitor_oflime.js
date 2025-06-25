
const fileInput = document.getElementById('file-upload');
const video = document.getElementById('video');
const canvas = document.getElementById('snapshot');
const context = canvas.getContext('2d');
const timerDisplay = document.getElementById('session-timer');

let timerInterval = null;
let elapsedTime = 0;

function formatTime(seconds) {
  const h = String(Math.floor(seconds / 3600)).padStart(2, '0');
  const m = String(Math.floor((seconds % 3600) / 60)).padStart(2, '0');
  const s = String(seconds % 60).padStart(2, '0');
  return `${h}:${m}:${s}`;
}

function startTimer() {
  timerInterval = setInterval(() => {
    elapsedTime++;
    timerDisplay.textContent = formatTime(elapsedTime);
  }, 1000);
}

function stopTimer() {
  clearInterval(timerInterval);
}

fileInput.addEventListener('change', function(event) {
  const file = event.target.files[0];
  if (file && file.type.startsWith('video/')) {
    video.src = URL.createObjectURL(file);
    video.style.display = 'block';
    canvas.style.display = 'none';
    elapsedTime = 0;
    timerDisplay.textContent = "00:00:00";
    video.onplay = function() {
      startTimer();
      analizarVideoFramePorFrame();
    };
    video.onpause = function() {
      stopTimer();
    };
    video.onended = function() {
      stopTimer();
    };
  }
});

function analizarVideoFramePorFrame() {
  function procesarFrame() {
    if (video.paused || video.ended) return;
    canvas.width = video.videoWidth;
    canvas.height = video.videoHeight;
    context.drawImage(video, 0, 0, canvas.width, canvas.height);
    const imagenBase64 = canvas.toDataURL('image/jpeg', 0.8);
    enviarFrameAlBackend(imagenBase64);
    setTimeout(procesarFrame, 1000); // cada 1 segundo
  }
  procesarFrame();
}

function enviarFrameAlBackend(imagenBase64) {
  fetch('/api/ia/analizar-imagen/', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ imagen: imagenBase64 })
  })
  .then(response => {
      if (!response.ok) {
          return response.json().then(err => { throw new Error(err.error || 'Error desconocido del servidor'); });
      }
      return response.json();
  })
  .then(data => {
      actualizarGraficas(data);
      console.log("Resultados de IA:", data);
  })
  .catch(error => {
      console.error('Error enviando frame al backend:', error);
  });
}

function actualizarGraficas(data) {
  const atentos = isFinite(Number(data.atentos)) ? Number(data.atentos) : 0;
  const distraidos = isFinite(Number(data.distraidos)) ? Number(data.distraidos) : 0;
  const somnolientos = isFinite(Number(data.somnolientos)) ? Number(data.somnolientos) : 0;

  document.getElementById('barra-atentos').style.width = atentos + '%';
  document.getElementById('barra-distraidos').style.width = distraidos + '%';
  document.getElementById('barra-somnolientos').style.width = somnolientos + '%';

  document.getElementById('porcentaje-atentos').innerText = atentos + '%';
  document.getElementById('porcentaje-distraidos').innerText = distraidos + '%';
  document.getElementById('porcentaje-somnolientos').innerText = somnolientos + '%';

  const alerta = document.getElementById('attention-alert');
  if (distraidos >= 50) {
      alerta.classList.remove('hidden');
      alerta.style.display = 'flex';
  } else {
      alerta.classList.add('hidden');
      alerta.style.display = 'none';
  }
}
