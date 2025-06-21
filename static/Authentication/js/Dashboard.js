
// Atención promedio por minutos
const ctx1 = document.getElementById('attentionByClass').getContext('2d');
new Chart(ctx1, {
    type: 'bar',
    data: {
        labels: ['10', '20', '30', '40', '50', '60', '70', '80', '90', '100'],
        datasets: [{
            label: 'Nivel de atención (%)',
            data: [82, 68, 45, 73, 80, 70, 60, 90, 75, 82],
            backgroundColor: ['#10b981', '#f59e0b', '#ef4444', '#3b82f6']
        }]
    },
    options: {
        responsive: true,
        scales: {
            y: {
                beginAtZero: true,
                max: 100
            }
        }
    }
});

// Tendencia diaria
const ctx2 = document.getElementById('attentionTrend').getContext('2d');
new Chart(ctx2, {
    type: 'line',
    data: {
        labels: ['10', '20', '30', '40', '50', '60', '70', '80', '90', '100'],
        datasets: [{
            label: 'Nivel de atención (%)',
            data: [82, 68, 45, 73, 80, 70, 60, 90, 75, 82],
            fill: false,
            borderColor: 'rgba(59, 130, 246, 1)',
            backgroundColor: 'rgba(59, 130, 246, 0.2)',
            tension: 0.2,
            pointBorderColor: 'rgba(59, 130, 246, 1)',
            pointBackgroundColor: 'rgba(59, 130, 246, 1)',
            pointRadius: 4
        }]
    },
    options: {
        responsive: true,
        scales: {
            y: {
                beginAtZero: true,
                max: 100
            }
        }
    }
});
