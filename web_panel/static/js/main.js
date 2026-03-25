/**
 * QR Access Control PRO - Main JavaScript
 * Theme toggle, sidebar, Chart.js, AJAX interactions
 */

// ── Theme Management ────────────────────
function initTheme() {
    const saved = localStorage.getItem('qr-theme') || 'dark';
    document.documentElement.setAttribute('data-theme', saved);
    updateThemeIcon(saved);
}

function toggleTheme() {
    const current = document.documentElement.getAttribute('data-theme');
    const next = current === 'dark' ? 'light' : 'dark';
    document.documentElement.setAttribute('data-theme', next);
    localStorage.setItem('qr-theme', next);
    updateThemeIcon(next);
    // Re-render charts with new colors
    if (typeof renderCharts === 'function') renderCharts();
}

function updateThemeIcon(theme) {
    const btn = document.getElementById('themeToggle');
    if (btn) btn.innerHTML = theme === 'dark' ? '☀️' : '🌙';
}

// ── Sidebar ─────────────────────────────
function toggleSidebar() {
    const sidebar = document.querySelector('.sidebar');
    sidebar.classList.toggle('open');
}

// ── Flash Messages ──────────────────────
function closeFlash(btn) {
    const msg = btn.closest('.flash-msg');
    msg.style.opacity = '0';
    msg.style.transform = 'translateY(-10px)';
    setTimeout(() => msg.remove(), 300);
}

function autoCloseFlash() {
    document.querySelectorAll('.flash-msg').forEach(msg => {
        setTimeout(() => {
            msg.style.opacity = '0';
            msg.style.transform = 'translateY(-10px)';
            setTimeout(() => msg.remove(), 300);
        }, 5000);
    });
}

// ── Modal Management ────────────────────
function openModal(modalId) {
    const modal = document.getElementById(modalId);
    if (modal) modal.classList.add('active');
}

function closeModal(modalId) {
    const modal = document.getElementById(modalId);
    if (modal) modal.classList.remove('active');
}

// Close modal on overlay click
document.addEventListener('click', function(e) {
    if (e.target.classList.contains('modal-overlay')) {
        e.target.classList.remove('active');
    }
});

// ── Charts (Dashboard) ─────────────────
let weeklyChart = null;
let doughnutChart = null;

function getChartColors() {
    const isDark = document.documentElement.getAttribute('data-theme') !== 'light';
    return {
        text: isDark ? '#a0a0c0' : '#4a4a6a',
        grid: isDark ? 'rgba(255,255,255,0.05)' : 'rgba(0,0,0,0.05)',
        permitidos: '#4ade80',
        denegados: '#f87171',
        gradient1: '#667eea',
        gradient2: '#764ba2',
    };
}

function renderCharts() {
    const weeklyEl = document.getElementById('weeklyChart');
    const doughnutEl = document.getElementById('doughnutChart');
    if (!weeklyEl || !doughnutEl) return;

    const colors = getChartColors();
    const weekData = JSON.parse(weeklyEl.getAttribute('data-stats') || '[]');

    const labels = weekData.map(d => {
        const date = new Date(d.fecha + 'T00:00:00');
        return date.toLocaleDateString('es', { weekday: 'short', day: 'numeric' });
    });
    const permitidos = weekData.map(d => d.permitidos);
    const denegados = weekData.map(d => d.denegados);

    // Destroy existing charts
    if (weeklyChart) weeklyChart.destroy();
    if (doughnutChart) doughnutChart.destroy();

    // Weekly bar chart
    weeklyChart = new Chart(weeklyEl, {
        type: 'bar',
        data: {
            labels: labels,
            datasets: [
                {
                    label: 'Permitidos',
                    data: permitidos,
                    backgroundColor: 'rgba(74, 222, 128, 0.7)',
                    borderColor: colors.permitidos,
                    borderWidth: 1,
                    borderRadius: 6,
                    borderSkipped: false,
                },
                {
                    label: 'Denegados',
                    data: denegados,
                    backgroundColor: 'rgba(248, 113, 113, 0.7)',
                    borderColor: colors.denegados,
                    borderWidth: 1,
                    borderRadius: 6,
                    borderSkipped: false,
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: { labels: { color: colors.text, font: { family: 'Inter', size: 12 } } }
            },
            scales: {
                x: { ticks: { color: colors.text }, grid: { color: colors.grid } },
                y: { ticks: { color: colors.text, stepSize: 1 }, grid: { color: colors.grid }, beginAtZero: true }
            }
        }
    });

    // Doughnut chart
    const totalP = permitidos.reduce((a, b) => a + b, 0);
    const totalD = denegados.reduce((a, b) => a + b, 0);

    doughnutChart = new Chart(doughnutEl, {
        type: 'doughnut',
        data: {
            labels: ['Permitidos', 'Denegados'],
            datasets: [{
                data: [totalP || 0, totalD || 0],
                backgroundColor: ['rgba(74, 222, 128, 0.8)', 'rgba(248, 113, 113, 0.8)'],
                borderColor: ['#4ade80', '#f87171'],
                borderWidth: 2,
                hoverOffset: 8,
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            cutout: '65%',
            plugins: {
                legend: {
                    position: 'bottom',
                    labels: { color: colors.text, font: { family: 'Inter', size: 12 }, padding: 16 }
                }
            }
        }
    });
}

// ── Edit User Modal ─────────────────────
function editUser(id, nombre, correo, rol, departamento, telefono) {
    document.getElementById('editUserId').value = id;
    document.getElementById('editNombre').value = nombre || '';
    document.getElementById('editCorreo').value = correo || '';
    document.getElementById('editRol').value = rol || 'usuario';
    document.getElementById('editDepartamento').value = departamento || '';
    document.getElementById('editTelefono').value = telefono || '';
    document.getElementById('editForm').action = '/admin/usuarios/' + id + '/editar';
    openModal('editUserModal');
}

// ── Confirm Delete ──────────────────────
function confirmDelete(id, nombre) {
    if (confirm('¿Estás seguro de que deseas eliminar a "' + nombre + '"?\nEsta acción no se puede deshacer.')) {
        // Submit the hidden POST form (prevents accidental GET deletion)
        const form = document.getElementById('deleteForm_' + id);
        if (form) {
            form.submit();
        }
    }
}

// ── Utilities ──────────────────────────
const Utils = {
    formatDate: function(dateString) {
        if (!dateString) return '-';
        const date = new Date(dateString);
        return date.toLocaleString('es-CL', {
            day: '2-digit',
            month: '2-digit',
            year: 'numeric',
            hour: '2-digit',
            minute: '2-digit'
        });
    },
    escapeHtml: function(text) {
        if (!text) return '';
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    },
    debounce: function(func, wait) {
        let timeout;
        return function executedFunction(...args) {
            const later = () => {
                clearTimeout(timeout);
                func(...args);
            };
            clearTimeout(timeout);
            timeout = setTimeout(later, wait);
        };
    }
};

const Filters = {
    getValues: function() {
        const filters = {};
        document.querySelectorAll('[data-filter]').forEach(el => {
            filters[el.dataset.filter] = el.value;
        });
        return filters;
    }
};

const LiveUpdates = {
    intervals: {},
    start: function(endpoint, callback, intervalMs = 5000) {
        this.stop(endpoint);
        const fetchAndUpdate = async () => {
            try {
                const sep = endpoint.includes('?') ? '&' : '?';
                const url = `${endpoint}${sep}_t=${Date.now()}`;
                const response = await fetch(url, {
                    headers: { 'X-Requested-With': 'XMLHttpRequest' }
                });
                if (response.ok) {
                    const data = await response.json();
                    callback(data);
                }
            } catch (error) {
                console.error('Live update error:', error);
            }
        };
        fetchAndUpdate();
        this.intervals[endpoint] = setInterval(fetchAndUpdate, intervalMs);
    },
    stop: function(endpoint) {
        if (this.intervals[endpoint]) {
            clearInterval(this.intervals[endpoint]);
            delete this.intervals[endpoint];
        }
    }
};

// Export to window
window.Utils = Utils;
window.Filters = Filters;
window.LiveUpdates = LiveUpdates;

// ── Init ────────────────────────────────
document.addEventListener('DOMContentLoaded', function() {
    initTheme();
    autoCloseFlash();
    if (document.getElementById('weeklyChart')) {
        renderCharts();
    }
});
