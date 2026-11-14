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

// Institution strip: repeat each row's names enough times to fill the screen, then add one hidden
// copy so the animation (translate by -50%) loops without a jump. Speed is constant across rows.
// Skipped for reduced motion, where the strip is a static wrapped list. The copy count is computed
// up front and capped, so a row that cannot be measured never loops forever.
if (!window.matchMedia('(prefers-reduced-motion: reduce)').matches) {
    document.querySelectorAll('.orgs-track').forEach(function (track) {
        var names = Array.prototype.slice.call(track.children);
        var setWidth = track.scrollWidth;
        if (!names.length || !setWidth) return;
        var copies = Math.min(20, Math.ceil(window.innerWidth * 1.2 / setWidth));
        for (var i = 1; i < copies; i++) {
            names.forEach(function (li) {
                var copy = li.cloneNode(true);
                copy.setAttribute('aria-hidden', 'true');
                track.appendChild(copy);
            });
        }
        Array.prototype.slice.call(track.children).forEach(function (li) {
            var copy = li.cloneNode(true);
            copy.setAttribute('aria-hidden', 'true');
            track.appendChild(copy);
        });
        var pxPerSecond = track.closest('.orgs-row-slow') ? 22 : 32;
        track.style.setProperty('--orgs-duration', (track.scrollWidth / 2 / pxPerSecond) + 's');
    });
}

// FAQs: opening one question closes any other open question in the same list.
document.addEventListener('toggle', (event) => {
    const opened = event.target;
    if (!(opened instanceof HTMLDetailsElement) || !opened.open) return;
    opened.parentElement.querySelectorAll(':scope > details[open]').forEach((other) => {
        if (other !== opened) other.open = false;
    });
}, true);
