// Shared behavior for every page: the theme toggle, the Projects menu, and team bio dialogs.

document.getElementById('theme-toggle').addEventListener('click', function () {
    var current = document.documentElement.getAttribute('data-theme');
    var next = current === 'dark' ? 'light' : 'dark';
    document.documentElement.setAttribute('data-theme', next);
    try { localStorage.setItem('theme', next); } catch (e) {}
});

// Projects menu: opens on hover (CSS) and on click or tap; closes on Escape or a click elsewhere.
document.querySelectorAll('.nav-menu').forEach(function (menu) {
    var button = menu.querySelector('.nav-menu-button');
    function set(open) {
        menu.classList.toggle('open', open);
        button.setAttribute('aria-expanded', open ? 'true' : 'false');
    }
    button.addEventListener('click', function (e) {
        e.stopPropagation();
        set(!menu.classList.contains('open'));
    });
    document.addEventListener('click', function (e) { if (!menu.contains(e.target)) set(false); });
    document.addEventListener('keydown', function (e) { if (e.key === 'Escape') set(false); });
});

// Team bios open in a dialog; close with the button, Escape, or a click outside the panel.
document.querySelectorAll('[data-bio]').forEach(function (card) {
    var dialog = document.getElementById(card.getAttribute('data-bio'));
    card.addEventListener('click', function () { dialog.showModal(); });
    dialog.querySelector('.bio-close').addEventListener('click', function () { dialog.close(); });
    dialog.addEventListener('click', function (e) { if (e.target === dialog) dialog.close(); });
});
