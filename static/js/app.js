/* Al Perahan Collection - storefront script (vanilla JS, no dependencies) */
(() => {
  'use strict';

  const DATA = JSON.parse(document.getElementById('shop-data').textContent);
  const $ = (s, el = document) => el.querySelector(s);
  const $$ = (s, el = document) => [...el.querySelectorAll(s)];
  const reduceMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  const esc = (v) => String(v ?? '').replace(/[&<>"']/g, (c) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]));

  const store = {
    get(k, d) { try { const v = JSON.parse(localStorage.getItem(k)); return v ?? d; } catch { return d; } },
    set(k, v) { try { localStorage.setItem(k, JSON.stringify(v)); } catch { /* private mode */ } },
  };

  /* ---------------- state ---------------- */
  const RATES = { PKR: [1, 'PKR '], USD: [0.0036, '$'], GBP: [0.0028, '£'], AED: [0.0132, 'AED '] };
  const sizesOf = (p) => (p.sizes && p.sizes.length ? p.sizes : ['One size']);
  const products = DATA.products;
  const byId = new Map(products.map((p) => [p.id, p]));
  let currency = store.get('alp.currency', 'PKR');
  if (!RATES[currency]) currency = 'PKR';
  let cart = store.get('alp.cart', []).filter((l) => byId.has(l.id));
  let wish = new Set(store.get('alp.wish', []).filter((id) => byId.has(id)));
  let cat = 'all', query = '', sort = 'featured', qvId = null, qvSize = 'M';
  const SALE = DATA.sale || null;
  const catLabel = (p) => (p.sub ? `${p.category} \u00b7 ${p.sub}` : p.category);

  const fmt = (pkr) => {
    const [rate, sym] = RATES[currency];
    return sym + new Intl.NumberFormat('en-US', { maximumFractionDigits: 0 }).format(Math.round(pkr * rate));
  };
  const priceHtml = (p) => p.was
    ? `<div class="pr is-sale"><s data-pkr="${p.was}"></s><b data-pkr="${p.price}"></b></div>`
    : `<div class="pr"><b data-pkr="${p.price}"></b></div>`;
  const refreshPrices = () => $$('[data-pkr]').forEach((el) => { el.textContent = fmt(+el.dataset.pkr); });

  /* ---------------- images: fade in when fully loaded, fall back gracefully ---------------- */
  const FALLBACK = 'data:image/svg+xml;utf8,' + encodeURIComponent(
    '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 300 400"><rect width="300" height="400" fill="#026A6B"/>' +
    '<rect x="96" y="170" width="30" height="30" rx="3" fill="#D19B53"/><rect x="136" y="170" width="30" height="30" rx="3" fill="#D19B53"/>' +
    '<rect x="176" y="170" width="30" height="30" rx="3" fill="#D19B53"/><rect x="116" y="210" width="30" height="30" rx="3" fill="#D19B53"/></svg>');

  const imgDone = (img) => { img.classList.add('is-loaded'); const m = img.closest('.media, .room-media'); if (m) m.classList.add('is-loaded'); };
  document.addEventListener('load', (e) => { if (e.target.tagName === 'IMG') imgDone(e.target); }, true);
  document.addEventListener('error', (e) => {
    const img = e.target;
    if (img.tagName !== 'IMG' || img.dataset.fb) return;
    img.dataset.fb = '1'; img.removeAttribute('srcset'); img.src = FALLBACK;
  }, true);
  const scanImages = (root = document) => $$('img', root).forEach((i) => { if (i.complete && i.naturalWidth) imgDone(i); });

  const imgTag = (o, sizes, alt) =>
    `<img src="${esc(o.image || FALLBACK)}" ${o.srcset ? `srcset="${esc(o.srcset)}" sizes="${sizes}"` : ''} alt="${esc(alt ?? o.title ?? o.name ?? '')}" width="900" height="1200" loading="lazy" decoding="async">`;

  /* ---------------- toast ---------------- */
  let toastT;
  const toast = (msg) => {
    const t = $('#toast'); t.textContent = msg; t.classList.add('is-show');
    clearTimeout(toastT); toastT = setTimeout(() => t.classList.remove('is-show'), 2800);
  };

  /* ---------------- panels (drawers + modals) ---------------- */
  const scrim = $('#scrim');
  const PANEL = { bag: 'd-bag', wishlist: 'd-wishlist', menu: 'd-menu', track: 'm-track', checkout: 'm-checkout', qv: 'm-qv', bespoke: 'm-bespoke' };
  let active = null, lastFocus = null;

  function openPanel(name) {
    const el = document.getElementById(PANEL[name]);
    if (!el) return;
    if (active === el) return;
    if (typeof closeMega === 'function') closeMega();
    if (active) closePanel(true);
    lastFocus = document.activeElement;
    el.hidden = false;
    if (el.classList.contains('drawer')) { scrim.hidden = false; requestAnimationFrame(() => scrim.classList.add('is-open')); }
    void el.offsetWidth;
    requestAnimationFrame(() => el.classList.add('is-open'));
    document.body.classList.add('locked');
    active = el;
    setTimeout(() => { const f = $('input:not(.hp),select,textarea,button:not([data-close])', el); (f || el).focus?.({ preventScroll: true }); }, 120);
  }
  function closePanel(instant) {
    if (!active) return;
    const el = active; active = null;
    el.classList.remove('is-open'); scrim.classList.remove('is-open');
    document.body.classList.remove('locked');
    const finish = () => { if (el !== active) el.hidden = true; if (!active) scrim.hidden = true; };
    instant ? finish() : setTimeout(finish, 380);
    if (!instant && lastFocus && lastFocus.focus) lastFocus.focus({ preventScroll: true });
  }
  scrim.addEventListener('click', () => closePanel());
  document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape') { closeMega(); closePanel(); }
    if (e.key === 'Tab' && active) {
      const f = $$('a[href],button:not([disabled]),input:not(.hp):not([disabled]),select,textarea', active).filter((x) => x.offsetParent !== null);
      if (!f.length) return;
      const first = f[0], last = f[f.length - 1];
      if (e.shiftKey && document.activeElement === first) { e.preventDefault(); last.focus(); }
      else if (!e.shiftKey && document.activeElement === last) { e.preventDefault(); first.focus(); }
    }
  });
  $$('.modal').forEach((m) => m.addEventListener('mousedown', (e) => { if (e.target === m) closePanel(); }));

  /* ---------------- bag ---------------- */
  const saveCart = () => store.set('alp.cart', cart);
  const cartCount = () => cart.reduce((n, l) => n + l.qty, 0);
  const cartTotal = () => cart.reduce((s, l) => s + byId.get(l.id).price * l.qty, 0);

  function renderBag() {
    const body = $('#bag-body'), foot = $('#bag-foot'), n = cartCount();
    const badge = $('#bag-badge'); badge.textContent = n; badge.hidden = !n;
    if (!cart.length) {
      body.innerHTML = '<div class="empty-note"><svg class="ic" style="width:40px;height:40px"><use href="#i-bag"/></svg><b style="font-family:var(--serif);font-size:1.5rem;font-weight:500;color:var(--ink)">Your bag is empty</b><p>Pieces you add will wait for you here.</p><a class="btn btn-dark" href="#shop" data-close>Browse the shop</a></div>';
      foot.hidden = true; return;
    }
    foot.hidden = false;
    body.innerHTML = cart.map((l, i) => {
      const p = byId.get(l.id);
      return `<div class="line-item"><div class="media" data-qv="${p.id}">${imgTag(p, '140px')}</div><div>
        <h4>${esc(p.title)}</h4><small>Size ${esc(l.size)}</small>
        <div class="line-row"><div class="qty"><button type="button" data-qty="${i}" data-d="-1" aria-label="Decrease quantity"><svg class="ic"><use href="#i-minus"/></svg></button><span>${l.qty}</span><button type="button" data-qty="${i}" data-d="1" aria-label="Increase quantity"><svg class="ic"><use href="#i-plus"/></svg></button></div>
        <strong class="price" data-pkr="${p.price * l.qty}"></strong></div>
        <button class="rm" type="button" data-rm="${i}"><svg class="ic"><use href="#i-trash"/></svg>Remove</button></div></div>`;
    }).join('');
    $('#bag-total').dataset.pkr = cartTotal();
    refreshPrices(); scanImages(body);
  }
  function addToBag(id, size) {
    size = size || sizesOf(byId.get(id))[0];
    const hit = cart.find((l) => l.id === id && l.size === size);
    hit ? hit.qty = Math.min(hit.qty + 1, 10) : cart.push({ id, size, qty: 1 });
    saveCart(); renderBag();
    const b = $('#bag-badge'); b.classList.remove('bump'); void b.offsetWidth; b.classList.add('bump');
  }

  /* ---------------- wishlist ---------------- */
  function renderWish() {
    const b = $('#wish-badge'); b.textContent = wish.size; b.hidden = !wish.size;
    const body = $('#wish-body');
    if (!wish.size) {
      body.innerHTML = '<div class="empty-note"><svg class="ic" style="width:40px;height:40px"><use href="#i-heart"/></svg><b style="font-family:var(--serif);font-size:1.5rem;font-weight:500;color:var(--ink)">Nothing saved yet</b><p>Tap the heart on any piece to keep it here.</p><a class="btn btn-dark" href="#shop" data-close>Browse the shop</a></div>';
    } else {
      body.innerHTML = [...wish].map((id) => {
        const p = byId.get(id);
        return `<div class="line-item"><div class="media" data-qv="${p.id}">${imgTag(p, '140px')}</div><div><h4>${esc(p.title)}</h4><small>${esc(catLabel(p))}</small>
          <div class="line-row"><strong class="price" data-pkr="${p.price}"></strong><button class="link" type="button" data-qv="${p.id}">Choose size</button></div>
          <button class="rm" type="button" data-wish="${p.id}"><svg class="ic"><use href="#i-trash"/></svg>Remove</button></div></div>`;
      }).join('');
    }
    refreshPrices(); scanImages(body);
    $$('[data-wish][aria-pressed]').forEach((b2) => b2.setAttribute('aria-pressed', wish.has(+b2.dataset.wish)));
    $('#qv-wish').setAttribute('aria-pressed', qvId != null && wish.has(qvId));
  }
  function toggleWish(id) {
    wish.has(id) ? wish.delete(id) : wish.add(id);
    store.set('alp.wish', [...wish]); renderWish();
    toast(wish.has(id) ? 'Saved to your wishlist' : 'Removed from wishlist');
  }

  /* ---------------- catalog ---------------- */
  const card = (p, i) => `<article class="card" style="--i:${Math.min(i, 12)}">
    <div class="media" data-qv="${p.id}"><div class="badges">${p.tag ? `<span class="tag">${esc(p.tag)}</span>` : ''}${p.pct ? `<span class="off">-${p.pct}%</span>` : ''}</div>
      <button class="wish" type="button" data-wish="${p.id}" aria-pressed="${wish.has(p.id)}" aria-label="Save ${esc(p.title)} to wishlist"><svg class="ic"><use href="#i-heart"/></svg></button>
      ${imgTag(p, '(min-width:1100px) 25vw, (min-width:700px) 33vw, 50vw')}
      <button class="qv-btn" type="button" data-qv="${p.id}">Quick add</button></div>
    <h3>${esc(p.title)}</h3>${priceHtml(p)}</article>`;

  function renderRows() {
    const rowHtml = (slug, title, list) => `<section class="row wrap" id="row-${esc(slug)}">
      <header class="row-head"><h2>${esc(title)}</h2><div class="row-tools"><a class="see" href="#shop" data-cat="${esc(slug)}">SEE ALL</a>
      <button class="arrow" type="button" data-scroll="-1" aria-label="Previous"><svg class="ic" style="transform:scaleX(-1)"><use href="#i-arrow"/></svg></button>
      <button class="arrow" type="button" data-scroll="1" aria-label="Next"><svg class="ic"><use href="#i-arrow"/></svg></button></div></header>
      <div class="track">${list.map(card).join('')}</div></section>`;
    let html = '';
    const onSale = products.filter((p) => p.was);
    if (SALE && onSale.length) html += rowHtml('sale', SALE.title, onSale);
    DATA.categories.forEach((c) => {
      const list = products.filter((p) => p.catSlugs.includes(c.slug));
      if (list.length) html += rowHtml(c.slug, c.name, list);
    });
    const rows = $('#rows'); rows.innerHTML = html;
    refreshPrices(); scanImages(rows);
  }

  function renderChips() {
    const items = [{ slug: 'all', name: 'All pieces' }, ...(SALE ? [{ slug: 'sale', name: 'Sale' }] : []), ...DATA.categories];
    const top = DATA.categories.find((c) => c.slug === cat || c.children.some((k) => k.slug === cat));
    const isOn = (c) => c.slug === cat || (top && c.slug === top.slug && c.children && c.children.some((k) => k.slug === cat));
    const chip = (c, label) => `<button class="chip${isOn(c) || c.slug === cat ? ' is-active' : ''}" type="button" role="tab" aria-selected="${c.slug === cat}" data-chip="${esc(c.slug)}">${esc(label || c.name)}</button>`;
    $('#chips').innerHTML = items.map((c) => chip(c)).join('');
    const sub = $('#chips-sub');
    if (top && top.children.length) {
      sub.hidden = false;
      sub.innerHTML = [{ slug: top.slug, name: 'All ' + top.name }, ...top.children].map((c) => chip(c)).join('');
    } else { sub.hidden = true; sub.innerHTML = ''; }
  }
  function renderGrid() {
    const q = query.trim().toLowerCase();
    let list = products.filter((p) => (cat === 'all' || (cat === 'sale' ? p.was : p.catSlugs.includes(cat))) &&
      (!q || [p.title, p.category, p.sub, p.fabric, p.craft, p.desc, p.tag].join(' ').toLowerCase().includes(q)));
    if (sort === 'low') list = [...list].sort((a, b) => a.price - b.price);
    if (sort === 'high') list = [...list].sort((a, b) => b.price - a.price);
    $('#grid').innerHTML = list.map(card).join('');
    $('#empty').hidden = list.length > 0;
    $('#shop-count').textContent = `${list.length} ${list.length === 1 ? 'piece' : 'pieces'}${cat === 'sale' ? ' on sale' : cat !== 'all' ? ' in this collection' : ''}`;
    refreshPrices(); scanImages($('#grid'));
  }
  function setCategory(slug, scroll) {
    cat = slug; renderChips(); renderGrid();
    if (scroll) $('#shop').scrollIntoView({ behavior: reduceMotion ? 'auto' : 'smooth' });
  }
  let qT;
  $('#q').addEventListener('input', (e) => { clearTimeout(qT); qT = setTimeout(() => { query = e.target.value; renderGrid(); }, 160); });
  $('#sort').addEventListener('change', (e) => { sort = e.target.value; renderGrid(); });
  $('#reset').addEventListener('click', () => { query = ''; cat = 'all'; $('#q').value = ''; renderChips(); renderGrid(); });
  $('#btn-search').addEventListener('click', () => { $('#shop').scrollIntoView({ behavior: 'smooth' }); setTimeout(() => $('#q').focus({ preventScroll: true }), 500); });

  function renderFooterCats() {
    $('#foot-cats').innerHTML = DATA.categories.map((c) => `<li><a href="#shop" data-cat="${esc(c.slug)}">${esc(c.name)}</a></li>`).join('');
  }

  /* ---------------- quick view ---------------- */
  function openQuickView(id) {
    const p = byId.get(id); if (!p) return;
    qvId = id; qvSize = sizesOf(p)[0];
    $('#qv-media').classList.remove('is-loaded');
    $('#qv-media').innerHTML = imgTag(p, '(min-width:800px) 480px, 100vw').replace('loading="lazy"', 'loading="eager"');
    $('#qv-cat').textContent = catLabel(p);
    $('#qv-title').textContent = p.title;
    $('#qv-price').innerHTML = p.was ? `<s class="qv-was" data-pkr="${p.was}"></s> <span data-pkr="${p.price}"></span>` : `<span data-pkr="${p.price}"></span>`;
    $('#qv-desc').textContent = p.desc;
    $('#qv-fabric').textContent = p.fabric || '-';
    $('#qv-craft').textContent = p.craft || '-';
    $('#qv-delivery').textContent = p.delivery || '-';
    drawSizes();
    refreshPrices(); scanImages($('#qv-media'));
    $('#qv-wish').setAttribute('aria-pressed', wish.has(id));
    openPanel('qv');
  }
  function drawSizes() {
    $('#qv-sizes').innerHTML = sizesOf(byId.get(qvId)).map((s) => `<button type="button" class="size${s === qvSize ? ' is-active' : ''}" data-size="${esc(s)}" aria-pressed="${s === qvSize}">${esc(s)}</button>`).join('');
  }
  $('#qv-sizes').addEventListener('click', (e) => { const b = e.target.closest('[data-size]'); if (b) { qvSize = b.dataset.size; drawSizes(); } });
  $('#qv-add').addEventListener('click', () => { addToBag(qvId, qvSize); toast('Added to your bag'); openPanel('bag'); });
  $('#qv-wish').addEventListener('click', () => toggleWish(qvId));

  /* ---------------- category mega menu (opens on click) ---------------- */
  const mega = $('#mega'), megaIn = $('#mega-in'), megaDim = $('#mega-dim');
  let megaCat = null;
  const ARROW = '<svg class="ic"><use href="#i-arrow"/></svg>';
  function renderMega(slug) {
    const c = DATA.categories.find((x) => x.slug === slug); if (!c) return;
    megaCat = slug;
    const list = products.filter((p) => p.catSlugs.includes(slug)).slice(0, 4);
    megaIn.innerHTML = `
      <ul class="mega-tabs">${DATA.categories.map((k) => `<li><button type="button" data-mega-tab="${esc(k.slug)}" class="${k.slug === slug ? 'is-active' : ''}"><span>${esc(k.name)}</span><small>${k.count} ${k.count === 1 ? 'piece' : 'pieces'}</small></button></li>`).join('')}</ul>
      <div class="mega-mid">${c.children.length ? `<div class="mega-subs"><span>Shop by type</span><a href="#shop" data-cat="${esc(slug)}">All ${esc(c.name)}</a>${c.children.map((k) => `<a href="#shop" data-cat="${esc(k.slug)}">${esc(k.name)}<small>${k.count}</small></a>`).join('')}</div>` : ''}<div class="mega-prods">${list.map((p, n) => `<button type="button" class="mp" style="--i:${n}" data-qv="${p.id}"><div class="media">${imgTag(p, '200px')}</div><b>${esc(p.title)}</b>${priceHtml(p)}</button>`).join('')}</div></div>
      <a class="mega-feature" href="#shop" data-cat="${esc(slug)}"><div class="media">${imgTag(c, '340px', c.name)}</div><div class="mf-body"><h3>${esc(c.name)}</h3><p>${esc(c.blurb)}</p><span class="btn btn-gold">Shop all ${ARROW}</span></div></a>`;
    megaIn.classList.remove('swap'); void megaIn.offsetWidth; megaIn.classList.add('swap');
    refreshPrices(); scanImages(megaIn);
    $$('.nav [data-mega]').forEach((b) => { const on = b.dataset.mega === slug; b.classList.toggle('is-active', on); b.setAttribute('aria-expanded', on); });
  }
  function openMega(slug) {
    if (active) closePanel(true);
    const wasOpen = mega.classList.contains('is-open');
    mega.hidden = false; megaDim.hidden = false;
    renderMega(slug);
    if (!wasOpen) requestAnimationFrame(() => { mega.classList.add('is-open'); megaDim.classList.add('is-open'); });
  }
  function closeMega() {
    if (!mega || !mega.classList.contains('is-open')) return;
    mega.classList.remove('is-open'); megaDim.classList.remove('is-open'); megaCat = null;
    $$('.nav [data-mega]').forEach((b) => { b.classList.remove('is-active'); b.setAttribute('aria-expanded', 'false'); });
    setTimeout(() => { if (!mega.classList.contains('is-open')) { mega.hidden = true; megaDim.hidden = true; } }, 600);
  }
  megaIn.addEventListener('mouseover', (e) => {
    const b = e.target.closest('[data-mega-tab]');
    if (b && b.dataset.megaTab !== megaCat) renderMega(b.dataset.megaTab);
  });
  megaDim.addEventListener('click', closeMega);
  addEventListener('resize', () => { if (innerWidth < 1000) closeMega(); });

  /* ---------------- global clicks ---------------- */
  document.addEventListener('click', (e) => {
    const t = e.target;
    let el;
    if ((el = t.closest('[data-mega]'))) { megaCat === el.dataset.mega ? closeMega() : openMega(el.dataset.mega); return; }
    if ((el = t.closest('[data-mega-tab]'))) { renderMega(el.dataset.megaTab); return; }
    if (mega.classList.contains('is-open') && !t.closest('.mega')) closeMega();
    if ((el = t.closest('[data-scroll]'))) { const tr = el.closest('.row').querySelector('.track'); tr.scrollBy({ left: +el.dataset.scroll * tr.clientWidth * 0.85, behavior: reduceMotion ? 'auto' : 'smooth' }); return; }
    if ((el = t.closest('[data-wish]'))) { e.preventDefault(); e.stopPropagation(); toggleWish(+el.dataset.wish); return; }
    if ((el = t.closest('[data-qv]'))) { closeMega(); openQuickView(+el.dataset.qv); return; }
    if ((el = t.closest('[data-open]'))) { openPanel(el.dataset.open); return; }
    if ((el = t.closest('[data-bespoke]'))) { openBespoke(el.dataset.bespoke); return; }
    if ((el = t.closest('[data-cat]'))) { closeMega(); setCategory(el.dataset.cat, false); if (active) closePanel(); return; }
    if ((el = t.closest('[data-chip]'))) { setCategory(el.dataset.chip, false); return; }
    if ((el = t.closest('[data-qty]'))) {
      const l = cart[+el.dataset.qty]; l.qty += +el.dataset.d;
      if (l.qty < 1) cart.splice(+el.dataset.qty, 1); else l.qty = Math.min(l.qty, 10);
      saveCart(); renderBag(); return;
    }
    if ((el = t.closest('[data-rm]'))) { cart.splice(+el.dataset.rm, 1); saveCart(); renderBag(); return; }
    if (t.closest('[data-close]')) closePanel();
  });

  /* ---------------- currency ---------------- */
  const cur = $('#currency'); cur.value = currency;
  cur.addEventListener('change', () => { currency = cur.value; store.set('alp.currency', currency); refreshPrices(); renderCheckoutTotal(); });

  /* ---------------- hero banner slider ---------------- */
  (() => {
    const hero = $('#hero');
    const slides = $$('.hero3-slide'), n = slides.length;
    const dots = $('#hero-dots'), bar = $('#hero-bar'), cur = $('#hero-cur'), pauseBtn = $('#hero-pause');
    const pad = (k) => String(k).padStart(2, '0');
    $('#hero-total').textContent = pad(n);
    if (n < 2) { $$('.hero3-ctrl,.hero3-side,.hero3-progress').forEach((e) => { e.hidden = true; }); return; }
    const DELAY = 6500;
    let i = 0, timer, userPaused = false, hovering = false;
    dots.innerHTML = slides.map((_, k) => `<button type="button" aria-label="Show slide ${k + 1}" data-dot="${k}"></button>`).join('');
    const restartBar = () => { bar.classList.remove('run'); void bar.offsetWidth; if (!userPaused && !hovering) bar.classList.add('run'); };
    const stop = () => clearTimeout(timer);
    const schedule = () => {
      stop(); restartBar();
      if (userPaused || hovering || document.hidden) return;
      timer = setTimeout(() => { show(i + 1); }, DELAY);
    };
    const show = (k) => {
      i = (k + n) % n;
      slides.forEach((s, j) => { s.classList.toggle('is-active', j === i); s.setAttribute('aria-hidden', j !== i); });
      $$('button', dots).forEach((d, j) => { d.classList.toggle('is-active', j === i); d.setAttribute('aria-current', j === i); });
      cur.textContent = pad(i + 1);
      schedule();
    };
    $('#hero-next').addEventListener('click', () => show(i + 1));
    $('#hero-prev').addEventListener('click', () => show(i - 1));
    dots.addEventListener('click', (e) => { const b2 = e.target.closest('[data-dot]'); if (b2) show(+b2.dataset.dot); });
    pauseBtn.addEventListener('click', () => {
      userPaused = !userPaused;
      pauseBtn.classList.toggle('is-paused', userPaused);
      pauseBtn.setAttribute('aria-label', userPaused ? 'Play slideshow' : 'Pause slideshow');
      hero.classList.toggle('is-paused', userPaused);
      schedule();
    });
    const stage = $('.hero3-stage');
    // Autoplay never stops on hover; only the pause button stops it.
    document.addEventListener('visibilitychange', schedule);
    document.addEventListener('keydown', (e) => {
      if (active || mega.classList.contains('is-open')) return;
      if (e.target.closest('input,textarea,select')) return;
      const r = hero.getBoundingClientRect();
      if (r.bottom < 0 || r.top > innerHeight) return;
      if (e.key === 'ArrowRight') show(i + 1);
      if (e.key === 'ArrowLeft') show(i - 1);
    });
    let x0 = null;
    stage.addEventListener('touchstart', (e) => { x0 = e.touches[0].clientX; }, { passive: true });
    stage.addEventListener('touchend', (e) => {
      if (x0 === null) return; const dx = e.changedTouches[0].clientX - x0; x0 = null;
      if (Math.abs(dx) > 40) show(i + (dx < 0 ? 1 : -1));
    });
    show(0);
  })();

  /* ---------------- showroom ---------------- */
  (() => {
    const rooms = DATA.showrooms;
    if (!rooms.length) { $('#showroom').hidden = true; return; }
    const tabs = $('#room-tabs');
    const show = (k) => {
      const r = rooms[k];
      const img = $('#room-img'); img.classList.remove('is-loaded');
      if (r.srcset) { img.srcset = r.srcset; img.sizes = '(min-width:900px) 50vw, 100vw'; } else img.removeAttribute('srcset');
      img.src = r.image || FALLBACK; img.alt = r.title;
      $('#room-title').textContent = r.title; $('#room-desc').textContent = r.desc;
      $('#room-addr').textContent = r.address; $('#room-hours').textContent = r.hours || '-';
      $('#room-phone').textContent = r.phone; $('#room-phone-row').hidden = !r.phone;
      $$('button', tabs).forEach((b, j) => b.classList.toggle('is-active', j === k));
      if (img.complete && img.naturalWidth) imgDone(img);
    };
    if (rooms.length > 1) {
      tabs.innerHTML = rooms.map((r, k) => `<button type="button" data-room="${k}">${esc(r.city)}</button>`).join('');
      tabs.addEventListener('click', (e) => { const b = e.target.closest('[data-room]'); if (b) show(+b.dataset.room); });
    } else tabs.hidden = true;
    show(0);
  })();

  /* ---------------- forms ---------------- */
  const getCookie = (n) => (document.cookie.split('; ').find((c) => c.startsWith(n + '=')) || '').split('=')[1] || '';
  async function api(url, payload) {
    try {
      const r = await fetch(url, { method: 'POST', credentials: 'same-origin', headers: { 'Content-Type': 'application/json', 'X-CSRFToken': decodeURIComponent(getCookie('csrftoken')) }, body: JSON.stringify(payload) });
      let j = {}; try { j = await r.json(); } catch { /* not json */ }
      return { ok: r.ok && j.ok !== false, data: j };
    } catch { return { ok: false, data: { error: 'No connection. Please check your internet and try again.' } }; }
  }
  const formObj = (f) => Object.fromEntries(new FormData(f).entries());
  const clearErrors = (f) => { $$('[data-err]', f).forEach((s) => { s.textContent = ''; s.closest('.field')?.classList.remove('has-err'); }); };
  function showErrors(f, errors = {}) {
    let first;
    for (const [k, msg] of Object.entries(errors)) {
      const s = $(`[data-err="${k}"]`, f);
      if (s) { s.textContent = msg; s.closest('.field')?.classList.add('has-err'); first = first || $(`[name="${k}"]`, f); }
    }
    first?.focus();
  }
  const PHONE = /^[0-9+\-\s()]{7,20}$/;
  function validate(f, rules) {
    const v = formObj(f), errors = {};
    if (rules.name && v.name.trim().length < 2) errors.name = 'Please enter your full name.';
    if (rules.phone && !PHONE.test(v.phone.trim())) errors.phone = 'Enter a valid phone / WhatsApp number.';
    if (rules.city && v.city.trim().length < 2) errors.city = 'Please enter your city.';
    if (rules.address && v.address.trim().length < 8) errors.address = 'Please enter your full delivery address.';
    if (rules.email && v.email.trim() && !/^[^@\s]+@[^@\s]+\.[^@\s]+$/.test(v.email.trim())) errors.email = 'This email address does not look right.';
    return errors;
  }
  const setErr = (el, msg) => { el.textContent = msg || ''; el.hidden = !msg; };

  /* checkout */
  const renderCheckoutTotal = () => { $('#co-total').textContent = cart.length ? '- ' + fmt(cartTotal()) : ''; };
  $('#to-checkout').addEventListener('click', () => {
    if (!cart.length) return;
    $('#co-form-wrap').hidden = false; $('#co-done').hidden = true;
    clearErrors($('#co-form')); setErr($('#co-err'), '');
    renderCheckoutTotal(); openPanel('checkout');
  });
  $('#co-form').addEventListener('submit', async (e) => {
    e.preventDefault();
    const f = e.target; clearErrors(f); setErr($('#co-err'), '');
    const bad = validate(f, { name: 1, phone: 1, city: 1, address: 1, email: 1 });
    if (Object.keys(bad).length) { showErrors(f, bad); return; }
    const btn = $('#co-submit'); btn.disabled = true; const label = btn.innerHTML; btn.textContent = 'Placing order...';
    const res = await api('/api/checkout/', { ...formObj(f), items: cart.map((l) => ({ id: l.id, size: l.size, qty: l.qty })) });
    btn.disabled = false; btn.innerHTML = label;
    if (!res.ok) {
      if (res.data.errors) { showErrors(f, res.data.errors); if (res.data.errors.items) setErr($('#co-err'), res.data.errors.items); }
      else setErr($('#co-err'), res.data.error || 'Something went wrong. Please try again.');
      return;
    }
    $('#co-ref').textContent = res.data.reference; $('#co-wa').href = res.data.whatsapp;
    $('#co-form-wrap').hidden = true; $('#co-done').hidden = false;
    cart = []; saveCart(); renderBag(); f.reset();
  });

  /* tracking */
  $('#tr-form').addEventListener('submit', async (e) => {
    e.preventDefault();
    const ref = $('#tr-ref').value.trim(); const err = $('#tr-err'), out = $('#tr-result');
    setErr(err, ''); out.hidden = true;
    if (!ref) { setErr(err, 'Please enter your order reference.'); return; }
    try {
      const r = await fetch('/api/track/?ref=' + encodeURIComponent(ref), { credentials: 'same-origin' });
      const j = await r.json();
      if (!r.ok || !j.ok) { setErr(err, j.error || 'We could not find that order reference.'); return; }
      $('#tr-r').textContent = j.reference; $('#tr-d').textContent = j.placed;
      $('#tr-steps').innerHTML = j.cancelled ? '<li class="done-step">This order was cancelled. Message us on WhatsApp for help.</li>'
        : j.steps.map((s) => `<li class="${s.done ? 'done-step' : ''}">${esc(s.label)}</li>`).join('');
      out.hidden = false;
    } catch { setErr(err, 'No connection. Please try again.'); }
  });

  /* bespoke / appointment */
  function openBespoke(service) {
    $('#bs-form-wrap').hidden = false; $('#bs-done').hidden = true;
    clearErrors($('#bs-form')); setErr($('#bs-err'), '');
    const sel = $('#bs-service'); sel.value = [...sel.options].some((o) => o.value === service) ? service : sel.options[0].value;
    const d = $('#bs-date'); d.min = new Date().toISOString().slice(0, 10);
    openPanel('bespoke');
  }
  $('#bs-form').addEventListener('submit', async (e) => {
    e.preventDefault();
    const f = e.target; clearErrors(f); setErr($('#bs-err'), '');
    const bad = validate(f, { name: 1, phone: 1 });
    if (Object.keys(bad).length) { showErrors(f, bad); return; }
    const btn = $('#bs-submit'); btn.disabled = true;
    const res = await api('/api/bespoke/', formObj(f));
    btn.disabled = false;
    if (!res.ok) { res.data.errors ? showErrors(f, res.data.errors) : setErr($('#bs-err'), res.data.error || 'Something went wrong. Please try again.'); return; }
    $('#bs-form-wrap').hidden = true; $('#bs-done').hidden = false; f.reset();
  });

  /* newsletter */
  $('#news-form').addEventListener('submit', async (e) => {
    e.preventDefault();
    const f = e.target; const email = $('#news-email').value.trim();
    if (!email) { toast('Please enter your email address'); return; }
    const res = await api('/api/newsletter/', { email, website: f.website.value });
    if (res.ok) { toast(res.data.created ? 'Thank you, you are on the list' : 'You are already on the list'); f.reset(); }
    else toast(res.data.error || 'Please enter a valid email address');
  });

  /* ---------------- polish: header, announcement, counters ---------------- */
  const hdr = $('#hdr'); let tick = false;
  addEventListener('scroll', () => {
    if (tick) return; tick = true;
    requestAnimationFrame(() => { hdr.classList.toggle('is-stuck', scrollY > 40); tick = false; });
  }, { passive: true });

  $('#yr').textContent = new Date().getFullYear();

  /* ---------------- sale countdown (only exists while a sale is ON) ---------------- */
  (() => {
    if (!SALE || !SALE.endsAt) return;
    const end = new Date(SALE.endsAt).getTime();
    const timer = $('#sale-timer'), band = $('#sale-band-timer');
    const pad = (n) => String(n).padStart(2, '0');
    const tick = () => {
      let s = Math.floor((end - Date.now()) / 1000);
      if (s <= 0) { timer && (timer.textContent = ' - sale ended'); band && (band.hidden = true); return false; }
      const d = Math.floor(s / 86400); s -= d * 86400;
      const h = Math.floor(s / 3600); s -= h * 3600;
      const m = Math.floor(s / 60); s -= m * 60;
      if (timer) timer.textContent = ` - ends in ${d} day ${pad(h)} hours ${pad(m)} minutes ${pad(s)} seconds`;
      if (band) { band.hidden = false; band.innerHTML = [['Days', d], ['Hours', pad(h)], ['Min', pad(m)], ['Sec', pad(s)]].map(([l, v]) => `<div><b>${v}</b><small>${l}</small></div>`).join(''); }
      return true;
    };
    if (tick()) setInterval(tick, 1000);
  })();

  /* ---------------- boot ---------------- */
  renderFooterCats(); renderRows(); renderChips(); renderGrid(); renderBag(); renderWish(); refreshPrices(); scanImages();

  const seenSplash = () => { try { return sessionStorage.getItem('alp.splash'); } catch { return null; } };
  const splash = $('#splash');
  const ready = () => document.body.classList.add('is-ready');
  if (!splash) ready();
  else if (reduceMotion || seenSplash()) { splash.remove(); ready(); }
  else {
    try { sessionStorage.setItem('alp.splash', '1'); } catch { /* ignore */ }
    const end = () => { if (splash.classList.contains('is-done')) return; splash.classList.add('is-done'); ready(); setTimeout(() => splash.remove(), 700); };
    setTimeout(end, 2800); splash.addEventListener('click', end);
  }
})();
