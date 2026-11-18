// Shared behavior for every page: the phone menu, the Projects menu, team bio dialogs,
// and the scrolling strip of institution names on the home page.

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

// FAQs: questions open and close with a short height animation, and opening one closes any
// other open question in the same list. Instant when the visitor prefers reduced motion.
(function () {
    var reduce = window.matchMedia('(prefers-reduced-motion: reduce)');
    var DURATION = 320, EASING = 'cubic-bezier(0.2, 0.7, 0.2, 1)';

    function finish(d) {
        d.style.overflow = '';
        d.classList.remove('is-closing');
        d._anim = null;
    }
    function animate(d, from, to, done) {
        if (d._anim) d._anim.cancel();
        d.style.overflow = 'hidden';
        d._anim = d.animate({ height: [from + 'px', to + 'px'] }, { duration: DURATION, easing: EASING });
        d._anim.onfinish = function () { if (done) done(); finish(d); };
        d._anim.oncancel = function () { finish(d); };
    }
    function close(d) {
        if (!d.open) return;
        if (reduce.matches || !d.animate) { d.open = false; return; }
        var from = d.offsetHeight, to = d.querySelector('summary').offsetHeight;
        d.classList.add('is-closing');
        animate(d, from, to, function () { d.open = false; });
    }
    function open(d) {
        if (d._anim) d._anim.cancel();
        var from = d.offsetHeight;
        d.open = true;
        if (reduce.matches || !d.animate) return;
        animate(d, from, d.offsetHeight);
    }

    document.querySelectorAll('.faq details').forEach(function (d) {
        var summary = d.querySelector('summary');
        if (!summary) return;
        summary.addEventListener('click', function (e) {
            e.preventDefault();
            if (d.open && !d.classList.contains('is-closing')) {
                close(d);
            } else {
                d.parentElement.querySelectorAll(':scope > details[open]').forEach(function (other) {
                    if (other !== d) close(other);
                });
                open(d);
            }
        });
    });
})();
