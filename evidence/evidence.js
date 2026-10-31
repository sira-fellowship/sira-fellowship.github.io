// Evidence page: the growth chart and the two searchable lists (research, demand).
// Data comes from data.js, which tools/evidence_data.py generates from the research sweep.

(function () {
    var data = window.SIRA_EVIDENCE;
    if (!data) return;
    var FIRST = 10, PAGE = 20;  // a short first view so the next section is close by

    function el(tag, cls, text) {
        var node = document.createElement(tag);
        if (cls) node.className = cls;
        if (text != null) node.textContent = text;
        return node;
    }

    function count(list, key) {
        var out = {};
        list.forEach(function (x) { out[x[key]] = (out[x[key]] || 0) + 1; });
        return out;
    }

    // Growth chart: research items per year, 2020 on. The current year is partial and drawn lighter.
    (function chart() {
        var host = document.getElementById('growth-chart');
        if (!host) return;
        var byYear = count(data.research, 'yn');
        var years = [2020, 2021, 2022, 2023, 2024, 2025, 2026];
        var max = Math.max.apply(null, years.map(function (y) { return byYear[y] || 0; }));
        host.setAttribute('role', 'img');
        host.setAttribute('aria-label', 'Items per year: ' + years.map(function (y) {
            return y + ', ' + (byYear[y] || 0);
        }).join('; ') + ' (2026 through October).');
        years.forEach(function (y) {
            var n = byYear[y] || 0;
            var col = el('div', 'bar-col' + (y === 2026 ? ' partial' : ''));
            col.setAttribute('aria-hidden', 'true');
            col.appendChild(el('span', 'bar-n', n));
            var bar = el('div', 'bar');
            bar.style.height = (n / max * 100) + '%';
            col.appendChild(bar);
            col.appendChild(el('span', 'bar-y', y === 2026 ? '2026*' : y));
            host.appendChild(col);
        });
    })();

    function setup(root, list, opts) {
        var controls = {};
        root.querySelectorAll('[data-filter]').forEach(function (c) { controls[c.getAttribute('data-filter')] = c; });
        var listEl = root.querySelector('.db-list');
        var countEl = root.querySelector('.db-count');
        var more = root.querySelector('.db-more');
        var shown = FIRST;

        // Fill each dropdown with its values and counts.
        Object.keys(opts.selects).forEach(function (key) {
            var sel = controls[key];
            var counts = count(list, key);
            Object.keys(counts).sort(opts.selects[key].sort).forEach(function (v) {
                var o = el('option', null, opts.selects[key].label(v) + ' (' + counts[v] + ')');
                o.value = v;
                sel.appendChild(o);
            });
        });

        function matches(x) {
            var q = controls.q.value.trim().toLowerCase();
            if (q && opts.text(x).toLowerCase().indexOf(q) === -1) return false;
            for (var key in opts.selects) {
                if (controls[key].value && String(x[key]) !== controls[key].value) return false;
            }
            if (controls.g && controls.g.checked && !x.g) return false;
            return true;
        }

        function render() {
            var hits = list.filter(matches);
            listEl.textContent = '';
            hits.slice(0, shown).forEach(function (x) { listEl.appendChild(opts.item(x)); });
            countEl.textContent = hits.length === list.length
                ? list.length + ' items'
                : hits.length + ' of ' + list.length + ' items';
            more.hidden = hits.length <= shown;
        }

        Object.keys(controls).forEach(function (key) {
            controls[key].addEventListener(key === 'q' ? 'input' : 'change', function () {
                shown = FIRST;
                render();
            });
        });
        more.addEventListener('click', function () { shown += PAGE; render(); });
        render();
        return { controls: controls, render: render };
    }

    function head(x) {
        var li = el('li', 'db-item');
        var title = el('a', 'db-title', x.t);
        title.href = x.u;
        title.target = '_blank';
        title.rel = 'noopener';
        li.appendChild(title);
        var who = x.a && !/^multiple authors/i.test(x.a) && x.a !== x.o.split(' · ')[0] ? x.a + ' · ' : '';
        li.appendChild(el('p', 'db-meta', who + x.o + ' · ' + x.y));
        return li;
    }

    function tags(li, list) {
        var row = el('p', 'db-tags');
        list.forEach(function (t) { if (t) row.appendChild(el('span', t[1], t[0])); });
        li.appendChild(row);
        return li;
    }

    var research = document.querySelector('.db[data-set="research"]');
    if (research) {
        var r = setup(research, data.research, {
            text: function (x) { return [x.t, x.a, x.o, x.s, x.d, x.d2].join(' '); },
            selects: {
                m: { label: function (v) { return data.tm[v]; }, sort: function (a, b) { return a - b; } },
                d: { label: function (v) { return v; }, sort: undefined }
            },
            item: function (x) {
                return tags(head(x), [
                    [data.tm[x.m], 'db-tm db-tm-' + x.m],
                    [x.d, 'db-tag'],
                    [x.s.replace(/\s*\(.*\)$/, ''), 'db-tag'],
                    x.g ? ['Large-N or RCT', 'db-gold'] : null
                ]);
            }
        });

        // "See all" links under each threat model set the filter and jump to the list.
        document.querySelectorAll('.see-all').forEach(function (b) {
            b.addEventListener('click', function () {
                r.controls.m.value = b.getAttribute('data-tm');
                r.controls.q.value = '';
                r.controls.d.value = '';
                r.controls.g.checked = false;
                r.render();
                document.getElementById('database').scrollIntoView();
            });
        });
    }

    var demand = document.querySelector('.db[data-set="demand"]');
    if (demand) {
        var order = ['Teams and institutes', 'Funding', 'Community calls', 'Convenings', 'Agendas and calls', 'Methods and data'];
        // Lead with the strongest signals (teams, funding); order within a type is kept.
        data.demand.sort(function (a, b) { return order.indexOf(a.c) - order.indexOf(b.c); });
        setup(demand, data.demand, {
            text: function (x) { return [x.t, x.a, x.o, x.s, x.c].join(' '); },
            selects: {
                c: { label: function (v) { return v; }, sort: function (a, b) { return order.indexOf(a) - order.indexOf(b); } },
                x: { label: function (v) { return v; }, sort: undefined }
            },
            item: function (x) {
                return tags(head(x), [[x.c, 'db-tm db-kind'], [x.x, 'db-tag']]);
            }
        });
    }
})();
