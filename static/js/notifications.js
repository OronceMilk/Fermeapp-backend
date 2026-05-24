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
