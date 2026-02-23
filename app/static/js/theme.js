function setTheme(theme) {
    document.documentElement.setAttribute('data-bs-theme', theme);
    localStorage.setItem('theme', theme);
    updateButton(theme);
}

function updateButton(theme) {
    const btn = document.getElementById('themeToggle');
    if (!btn) return;
    btn.textContent = theme === 'dark' ? '☀️' : '🌙';
}

document.addEventListener('DOMContentLoaded', function() {
    const savedTheme = localStorage.getItem('theme') || 'light';
    setTheme(savedTheme);

    const btn = document.getElementById('themeToggle');
    if (btn) {
        btn.addEventListener('click', function() {
            const current = document.documentElement.getAttribute('data-bs-theme');
            const newTheme = current === 'light' ? 'dark' : 'light';
            setTheme(newTheme);
        });
    }
});