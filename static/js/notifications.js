// Minimal toast notification system used by the app
(function () {
  function createToast(message, type) {
    const container = document.getElementById('toast-container');
    if (!container) return;

    const toast = document.createElement('div');
    toast.className = `toast px-4 py-3 rounded-lg shadow-sm pointer-events-auto max-w-full w-80 ${
      type === 'error' ? 'bg-red-50 border border-red-200 text-red-700' : 'bg-green-50 border border-green-200 text-green-700'
    }`;
    toast.style.display = 'flex';
    toast.style.justifyContent = 'space-between';
    toast.style.alignItems = 'center';

    const text = document.createElement('div');
    text.innerText = message;
    text.style.flex = '1';

    const close = document.createElement('button');
    close.innerText = '✕';
    close.style.marginLeft = '12px';
    close.style.background = 'transparent';
    close.style.border = 'none';
    close.style.cursor = 'pointer';

    close.addEventListener('click', () => {
      toast.remove();
    });

    toast.appendChild(text);
    toast.appendChild(close);
    container.prepend(toast);

    setTimeout(() => {
      toast.remove();
    }, 5000);
  }

  window.showToast = function (message, type) {
    createToast(message || '', type || 'success');
  };
  window.showSuccessToast = function (message) {
    createToast(message || '', 'success');
  };
  window.showErrorToast = function (message) {
    createToast(message || '', 'error');
  };
})();
function showToast(message, type = 'success', duration = 4000) {
  const container = document.getElementById('toast-container');
  if (!container || !message) return;

  const styles = {
    success: 'bg-green-600',
    error: 'bg-red-600',
    warning: 'bg-amber-500',
    info: 'bg-skyfarm',
  };
  const icons = {
    success: '✓',
    error: '!',
    warning: '!',
    info: 'i',
  };

  const toast = document.createElement('div');
  toast.className = `pointer-events-auto flex items-start gap-3 rounded-xl px-4 py-3 text-sm font-semibold text-white shadow-lg transition duration-200 translate-y-2 opacity-0 ${styles[type] || styles.success}`;
  toast.innerHTML = `<span class="grid h-5 w-5 shrink-0 place-items-center rounded-full bg-white/20 text-xs">${icons[type] || icons.success}</span><span>${message}</span>`;
  container.appendChild(toast);

  requestAnimationFrame(() => {
    toast.classList.remove('translate-y-2', 'opacity-0');
  });

  setTimeout(() => {
    toast.classList.add('translate-y-2', 'opacity-0');
    setTimeout(() => toast.remove(), 220);
  }, duration);
}

window.showToast = showToast;
