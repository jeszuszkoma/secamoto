/* Secamoto demo: menu, rev bar + gear indicator, TFT dash (modes, tach, clock, weather), list filters. No dependencies. */
(function () {
  var d = document;
  var reduce = window.matchMedia && matchMedia('(prefers-reduced-motion: reduce)').matches;

  /* ---- menu ---- */
  var burger = d.querySelector('.burger'), nav = d.getElementById('nav');
  if (burger && nav) burger.addEventListener('click', function () {
    var open = nav.classList.toggle('open');
    burger.setAttribute('aria-expanded', open ? 'true' : 'false');
  });
  var dds = [].slice.call(d.querySelectorAll('.dd'));
  dds.forEach(function (x) {
    x.addEventListener('toggle', function () { if (x.open) dds.forEach(function (y) { if (y !== x) y.open = false; }); });
  });
  d.addEventListener('click', function (ev) { dds.forEach(function (x) { if (x.open && !x.contains(ev.target)) x.open = false; }); });
  d.addEventListener('keydown', function (ev) { if (ev.key === 'Escape') dds.forEach(function (x) { x.open = false; }); });

  /* ---- rev bar + gear indicator follow the scroll ---- */
  var fill = d.getElementById('revFill'), gearNow = d.getElementById('gearNow');
  var current = '1';
  function setGear() {
    if (!gearNow) return;
    var top = (d.scrollingElement || d.documentElement).scrollTop < 40;
    var g = top ? 'N' : current;
    gearNow.textContent = g;
    gearNow.parentNode.classList.toggle('neutral', g === 'N');
  }
  function onScroll() {
    var h = d.scrollingElement || d.documentElement, max = h.scrollHeight - h.clientHeight;
    if (fill) fill.style.width = (max > 0 ? h.scrollTop / max * 100 : 0).toFixed(1) + '%';
    setGear();
  }
  addEventListener('scroll', onScroll, { passive: true });
  onScroll();
  if ('IntersectionObserver' in window) {
    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (en) { if (en.isIntersecting) { current = en.target.getAttribute('data-gear'); setGear(); } });
    }, { rootMargin: '-45% 0px -50% 0px' });
    d.querySelectorAll('main > section[data-gear], footer[data-gear]').forEach(function (s) { io.observe(s); });
  }

  /* ---- TFT dash (home) ---- */
  var tach = d.getElementById('tach');
  if (tach) {
    var N = 48, MAX = 14, AMBER = 9.5, RED = 11.5, svg = '';
    for (var i = 0; i < N; i++) {
      var x = 4 + i * (592 / N), w = 592 / N - 3, h = 8 + Math.pow(i / (N - 1), 1.7) * 36;
      var v = (i + 1) / N * MAX;
      svg += '<rect class="' + (v > RED ? 'rd' : v > AMBER ? 'am' : '') + '" x="' + x.toFixed(1) + '" y="' + (46 - h).toFixed(1) +
        '" width="' + w.toFixed(1) + '" height="' + h.toFixed(1) + '" rx="1" style="transition-delay:' + (reduce ? 0 : i * 7) + 'ms"/>';
    }
    for (var k = 0; k <= MAX; k += 2) svg += '<text x="' + (4 + k / MAX * 592).toFixed(1) + '" y="61" text-anchor="middle">' + k + '</text>';
    tach.innerHTML = svg;
    var rects = tach.querySelectorAll('rect');
    var setRpm = function (rpm) {
      rects.forEach(function (r, i) { r.classList.toggle('on', (i + 1) / N * MAX <= rpm); });
    };
    var tabs = [].slice.call(d.querySelectorAll('.modes [role="tab"]'));
    var dashGear = d.getElementById('dashGear'), shift = d.getElementById('shift');
    var touched = false;
    var select = function (id, focus) {
      tabs.forEach(function (t) {
        var on = t.getAttribute('data-mode') === id;
        t.setAttribute('aria-selected', on ? 'true' : 'false');
        t.tabIndex = on ? 0 : -1;
        var panel = d.getElementById('mp-' + t.getAttribute('data-mode'));
        if (panel) panel.hidden = !on;
        if (on) {
          var rpm = parseFloat(t.getAttribute('data-rpm'));
          dashGear.textContent = t.getAttribute('data-gear');
          shift.classList.toggle('on', rpm > RED);
          setRpm(rpm);
          if (focus) t.focus();
        }
      });
    };
    tabs.forEach(function (t, i) {
      t.addEventListener('click', function () { touched = true; select(t.getAttribute('data-mode')); });
      t.addEventListener('keydown', function (ev) {
        var dir = { ArrowDown: 1, ArrowRight: 1, ArrowUp: -1, ArrowLeft: -1 }[ev.key];
        if (!dir) return;
        ev.preventDefault(); touched = true;
        select(tabs[(i + dir + tabs.length) % tabs.length].getAttribute('data-mode'), true);
      });
    });
    var start = (tabs.filter(function (t) { return t.getAttribute('aria-selected') === 'true'; })[0] || tabs[0]).getAttribute('data-mode');
    // ignition self-test: needle sweeps to the limiter, then settles on the mode's revs
    if (reduce) select(start);
    else { setRpm(MAX); setTimeout(function () { if (!touched) select(start); }, 900); }

    var clock = d.getElementById('clock');
    var tick = function () {
      var n = new Date();
      clock.textContent = ('0' + n.getHours()).slice(-2) + ':' + ('0' + n.getMinutes()).slice(-2);
    };
    tick(); setInterval(tick, 15000);

    // live weather for Budapest XVII (Open-Meteo, no key). Ice warning at 3 °C like on real bikes.
    var wx = d.getElementById('wx');
    if (window.fetch && wx) {
      fetch('https://api.open-meteo.com/v1/forecast?latitude=47.48&longitude=19.26&current=temperature_2m,weather_code&timezone=Europe%2FBudapest')
        .then(function (r) { return r.ok ? r.json() : null; })
        .then(function (j) {
          if (!j || !j.current) return;
          var t = Math.round(j.current.temperature_2m), code = j.current.weather_code;
          wx.textContent = 'BP XVII  ' + t + ' °C';
          d.getElementById('ice').hidden = t > 3;
          var rain = (code >= 51 && code <= 67) || (code >= 80 && code <= 82) || code >= 95;
          if (rain && !touched) {
            select('rain');
            var note = d.getElementById('wxNote');
            note.textContent = 'Most esik Budapesten, ezért RAIN módban indultunk.';
            note.hidden = false;
          }
        })
        .catch(function () {});
    }
  }

  /* ---- list filters (category + mode pages) ---- */
  var grid = d.getElementById('grid'), bar = d.querySelector('.filters');
  if (grid && bar) {
    var items = [].slice.call(grid.children);
    var state = { f: 'all', g: 'all', stock: false, sort: 'i' };
    var empty = d.getElementById('empty');
    var apply = function () {
      var shown = 0;
      items.forEach(function (li) {
        var ok = (state.f === 'all' || (' ' + li.getAttribute('data-modes') + ' ').indexOf(' ' + state.f + ' ') > -1) &&
          (state.g === 'all' || li.getAttribute('data-group') === state.g) &&
          (!state.stock || li.getAttribute('data-stock') === '1');
        li.hidden = !ok;
        if (ok) shown++;
      });
      var key = state.sort === 'i' ? 'data-i' : 'data-price', sign = state.sort === 'pd' ? -1 : 1;
      items.slice().sort(function (a, b) { return sign * (parseFloat(a.getAttribute(key)) - parseFloat(b.getAttribute(key))); })
        .forEach(function (li) { grid.appendChild(li); });
      empty.hidden = shown > 0;
    };
    bar.querySelectorAll('.chip').forEach(function (c) {
      c.addEventListener('click', function () {
        var attr = c.hasAttribute('data-f') ? 'data-f' : 'data-g';
        bar.querySelectorAll('.chip[' + attr + ']').forEach(function (o) { o.setAttribute('aria-pressed', o === c ? 'true' : 'false'); });
        state[attr === 'data-f' ? 'f' : 'g'] = c.getAttribute(attr);
        apply();
      });
    });
    d.getElementById('onlyStock').addEventListener('change', function (ev) { state.stock = ev.target.checked; apply(); });
    d.getElementById('sortBy').addEventListener('change', function (ev) { state.sort = ev.target.value; apply(); });
  }
})();
