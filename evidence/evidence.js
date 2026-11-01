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

    // Growth chart: papers per year from the literature census (census.js), each bar split into
    // empirical work (accent) and everything else (grey). Falls back to the database's own items per
    // year without a split. The current year is partial and drawn hatched.
    (function chart() {
        var host = document.getElementById('growth-chart');
        if (!host) return;
        var census = window.SIRA_CENSUS, years, totals, empirical, partial;
        if (census) {
            years = census.years;
            totals = census.papers;
            empirical = census.empiricalByYear;
            partial = census.partialYear;
        } else {
            var byYear = count(data.research, 'yn');
            years = [2020, 2021, 2022, 2023, 2024, 2025, 2026];
            totals = years.map(function (y) { return byYear[y] || 0; });
            empirical = null;
            partial = 2026;
        }
        function short(n) { return n >= 1000 ? (n / 1000).toFixed(n >= 10000 ? 0 : 1) + 'k' : String(n); }
        function full(n) { return n.toLocaleString('en-US'); }
        var max = Math.max.apply(null, totals);
        host.style.gridTemplateColumns = 'repeat(' + years.length + ', 1fr)';
        host.setAttribute('role', 'group');
        host.setAttribute('aria-label', 'Papers per year: ' + years.map(function (y, i) {
            return y + ', ' + full(totals[i]) + (empirical ? ' (' + Math.round(empirical[i] / totals[i] * 100) + '% empirical)' : '');
        }).join('; ') + ' (' + partial + ' January to October).');

        years.forEach(function (y, i) {
            var col = el('div', 'bar-col' + (y === partial ? ' partial' : '') + (i >= years.length - 3 ? ' tip-left' : ''));
            col.tabIndex = 0;
            var share = empirical ? Math.round(empirical[i] / totals[i] * 100) : null;
            col.setAttribute('aria-label', y + (y === partial ? ' (January to October)' : '') + ': ' + full(totals[i]) +
                ' papers' + (empirical ? ', ' + full(empirical[i]) + ' empirical (' + share + '%)' : ''));
            col.appendChild(el('span', 'bar-n', short(totals[i])));
            var bar = el('div', 'bar');
            bar.style.height = (totals[i] / max * 100) + '%';
            if (empirical) {
                var other = el('div', 'seg seg-other');
                other.style.flexGrow = totals[i] - empirical[i];
                var emp = el('div', 'seg seg-emp');
                emp.style.flexGrow = empirical[i];
                bar.appendChild(other);
                bar.appendChild(emp);
            }
            col.appendChild(bar);
            var label = el('span', 'bar-y', String(y));
            if (y === partial) label.appendChild(el('small', null, 'Jan–Oct'));
            col.appendChild(label);
            var tip = el('span', 'bar-tip');
            tip.appendChild(el('strong', null, y + (y === partial ? ', Jan–Oct' : '')));
            tip.appendChild(el('span', null, full(totals[i]) + ' papers'));
            if (empirical) tip.appendChild(el('span', null, full(empirical[i]) + ' empirical (' + share + '%)'));
            if (census && census.oneInN && census.oneInN[i]) {
                tip.appendChild(el('span', null, '1 in ' + full(census.oneInN[i]) + ' social science papers'));
            }
            col.appendChild(tip);
            host.appendChild(col);
        });

        // Annotation at the turn of 2022-23, where the curve bends.
        var at = years.indexOf(2023);
        if (at > 0) {
            var note = el('div', 'chart-note');
            note.setAttribute('aria-hidden', 'true');
            note.style.left = (at / years.length * 100) + '%';
            note.appendChild(el('span', null, 'ChatGPT released'));
            note.appendChild(el('span', null, 'Nov 2022'));
            host.appendChild(note);
        }
    })();

    // Census figures for each threat model: a line under its examples, and the summary table.
    var CENSUS_TM = window.SIRA_CENSUS && window.SIRA_CENSUS.threatModelStats;
    function pct(n, d) { return Math.round(n / d * 100) + '%'; }
    if (CENSUS_TM) {
        document.querySelectorAll('[data-census-tm]').forEach(function (p) {
            var t = CENSUS_TM[p.getAttribute('data-census-tm')];
            if (!t) return;
            p.textContent = '';
            p.appendChild(el('strong', null, t.papers.toLocaleString('en-US')));
            p.appendChild(document.createTextNode(' papers in our census of the literature, ' +
                pct(t.experiments, t.papers) + ' of them experiments'));
            p.hidden = false;
        });

        var table = document.getElementById('tm-table');
        if (table) {
            var rows = [
                ['human_ai_interaction', 'Human-AI interaction'],
                ['persuasion_manipulation', 'Persuasion and manipulation'],
                ['economic_labor', 'Economic and labor'],
                ['institutional_organizational', 'Institutional and organizational'],
                ['governance_policy', 'Governance and policy'],
                ['other_societal', 'Other societal effects']
            ];
            var total = window.SIRA_CENSUS.meets;
            var body = table.querySelector('tbody');
            rows.forEach(function (r, i) {
                var t = CENSUS_TM[r[0]];
                if (!t) return;
                var tr = el('tr', (i >= 4 ? 'outside' : '') + (r[0] === 'persuasion_manipulation' ? ' hl' : ''));
                var name = el('td');
                name.appendChild(document.createTextNode(r[1]));
                if (i >= 4) name.appendChild(el('span', 'tm-table-tag', 'outside our four'));
                tr.appendChild(name);
                [t.papers.toLocaleString('en-US'), pct(t.papers, total), Math.round(t.y2025 / t.y2019) + '×',
                 pct(t.empirical, t.papers), pct(t.experiments, t.papers)].forEach(function (v) {
                    tr.appendChild(el('td', null, v));
                });
                body.appendChild(tr);
            });
            table.closest('.tm-summary').hidden = false;
        }
    }

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
        // Newest first; within a year, data.js order (strongest studies first) is kept.
        data.research.sort(function (a, b) { return (b.yn || 0) - (a.yn || 0); });
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
