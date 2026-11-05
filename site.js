// Shared behavior for every page: the theme toggle, the phone menu, the Projects menu, team bio dialogs,
// and the scrolling strip of institution names on the home page.

document.getElementById('theme-toggle').addEventListener('click', function () {
    var current = document.documentElement.getAttribute('data-theme');
    var next = current === 'dark' ? 'light' : 'dark';
    document.documentElement.setAttribute('data-theme', next);
    try { localStorage.setItem('theme', next); } catch (e) {}
});

// Phone menu: the three-line button opens the nav as a panel; a link, Escape, or a click outside closes it.
(function () {
    var header = document.querySelector('.site-header');
    var toggle = document.querySelector('.menu-toggle');
    if (!header || !toggle) return;
    function set(open) {
        header.classList.toggle('menu-open', open);
        toggle.setAttribute('aria-expanded', open ? 'true' : 'false');
        toggle.setAttribute('aria-label', open ? 'Close menu' : 'Menu');
    }
    toggle.addEventListener('click', function (e) {
        e.stopPropagation();
        set(!header.classList.contains('menu-open'));
    });
    header.querySelectorAll('.nav a').forEach(function (a) {
        a.addEventListener('click', function () { set(false); });
    });
    document.addEventListener('click', function (e) { if (!header.contains(e.target)) set(false); });
    document.addEventListener('keydown', function (e) { if (e.key === 'Escape') set(false); });
})();

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

// Institution strip: repeat each row's names until it is wider than the screen, then add one hidden
// copy so the animation (translate by -50%) loops without a jump. Speed is constant across rows.
document.querySelectorAll('.orgs-track').forEach(function (track) {
    var names = Array.prototype.slice.call(track.children);
    function append(hidden) {
        names.forEach(function (li) {
            var copy = li.cloneNode(true);
            if (hidden) copy.setAttribute('aria-hidden', 'true');
            track.appendChild(copy);
        });
    }
    while (track.scrollWidth < window.innerWidth * 1.2) append(true);
    var set = Array.prototype.slice.call(track.children);
    set.forEach(function (li) {
        var copy = li.cloneNode(true);
        copy.setAttribute('aria-hidden', 'true');
        track.appendChild(copy);
    });
    var pxPerSecond = track.closest('.orgs-row-slow') ? 22 : 32;
    track.style.setProperty('--orgs-duration', (track.scrollWidth / 2 / pxPerSecond) + 's');
});
