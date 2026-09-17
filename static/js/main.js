/* ============================================================
   main.js — Brillo-Boom
   Navbar · Carrito (fetch API) · Auth tabs · Toasts · Animaciones
   ============================================================ */

document.addEventListener('DOMContentLoaded', () => {

  /* ── 1. NAVBAR: sombra al scroll + menú hamburger ────── */
  const navbar   = document.getElementById('navbar');
  const toggle   = document.getElementById('navToggle');
  const navLinks = document.getElementById('navLinks');

  window.addEventListener('scroll', () =>
    navbar?.classList.toggle('scrolled', window.scrollY > 10));

  toggle?.addEventListener('click', () =>
    navLinks?.classList.toggle('open'));

  document.addEventListener('click', e => {
    if (navbar && !navbar.contains(e.target))
      navLinks?.classList.remove('open');
  });

  /* ── 2. CARRITO: botón "Agregar" via fetch ────────────── */
  const cartBadge = document.getElementById('cartBadge');

  function updateBadge(n) {
    if (!cartBadge) return;
    cartBadge.textContent    = n;
    cartBadge.style.display  = n > 0 ? 'flex' : 'none';
  }

  /* ── 2b. SELECTOR DE CANTIDAD (+ / −) en detalle de producto ── */
  document.querySelectorAll('.btn-qty-menos, .btn-qty-mas').forEach(btn => {
    btn.addEventListener('click', function () {
      const input = this.parentElement.querySelector('input[type="number"]');
      if (!input) return;
      const max = parseInt(input.max) || 999;
      let val = parseInt(input.value) || 1;
      val = this.classList.contains('btn-qty-mas') ? Math.min(max, val + 1)
                                                    : Math.max(1, val - 1);
      input.value = val;
    });
  });

  document.querySelectorAll('.btn-add-cart').forEach(btn => {
    btn.addEventListener('click', async function () {
      const id     = this.dataset.id;
      const nombre = this.dataset.nombre;

      let cantidad = 1;
      const qtyInputId = this.dataset.qtyInput;
      if (qtyInputId) {
        const qtyInput = document.getElementById(qtyInputId);
        if (qtyInput) cantidad = Math.max(1, parseInt(qtyInput.value) || 1);
      }

      const orig   = this.innerHTML;

      this.disabled = true;
      this.innerHTML = '<i class="fas fa-spinner fa-spin"></i>';

      try {
        const res  = await fetch('/carrito/agregar', {
          method:  'POST',
          headers: { 'Content-Type': 'application/json' },
          body:    JSON.stringify({ id_producto: id, cantidad: cantidad })
        });
        const data = await res.json();

        if (data.ok) {
          updateBadge(data.total_items);
          showToast(`✅ "${nombre}" añadido al carrito`);
          this.innerHTML = '<i class="fas fa-check"></i> Añadido';
          setTimeout(() => { this.innerHTML = orig; this.disabled = false; }, 2200);
        } else {
          showToast(`⚠️ ${data.msg || 'No disponible'}`, 'warning');
          this.innerHTML = orig; this.disabled = false;
        }
      } catch {
        showToast('Error de conexión. Intenta de nuevo.', 'danger');
        this.innerHTML = orig; this.disabled = false;
      }
    });
  });

  /* ── 3. TOASTS ────────────────────────────────────────── */
  window.showToast = function (msg, type = 'success') {
    document.querySelectorAll('.bb-toast').forEach(t => t.remove());
    const toast = document.createElement('div');
    toast.className = `alert alert-${type} bb-toast`;
    toast.style.cssText = `
      position:fixed;bottom:1.5rem;right:1.5rem;z-index:9999;
      min-width:260px;max-width:380px;cursor:pointer;
      box-shadow:0 8px 32px rgba(228,60,126,.25);
    `;
    toast.innerHTML = msg;
    toast.onclick   = () => toast.remove();
    document.body.appendChild(toast);
    setTimeout(() => toast.remove(), 3500);
  };

  /* ── 4. FLASH: auto-cierre ────────────────────────────── */
  document.querySelectorAll('.alert[data-auto-close]').forEach(el => {
    el.style.cursor = 'pointer';
    el.onclick = () => el.remove();
    setTimeout(() => el.remove(), 4500);
  });

  /* ── 5. SCROLL ANIMATIONS ─────────────────────────────── */
  const observer = new IntersectionObserver(entries => {
    entries.forEach(e => {
      if (e.isIntersecting) {
        e.target.style.animation = 'fadeUp .55s ease both';
        observer.unobserve(e.target);
      }
    });
  }, { threshold: 0.08 });

  document.querySelectorAll('.product-card, .brand-card, .kpi-card, .profile-card')
    .forEach(el => observer.observe(el));

  /* ── 6. PREVIEW DE IMAGEN (admin form) ───────────────── */
  const imgInput   = document.getElementById('img-url-input');
  const imgPreview = document.getElementById('img-preview');
  if (imgInput && imgPreview) {
    imgInput.addEventListener('input', function () {
      imgPreview.src     = this.value;
      imgPreview.onload  = () => imgPreview.style.display = 'block';
      imgPreview.onerror = () => imgPreview.style.display = 'none';
    });
  }

  /* ── 7. SMOOTH SCROLL para anclas (#marcas, #comentarios) */
  document.querySelectorAll('a[href^="#"]').forEach(a => {
    a.addEventListener('click', e => {
      const target = document.querySelector(a.getAttribute('href'));
      if (target) {
        e.preventDefault();
        target.scrollIntoView({ behavior: 'smooth', block: 'start' });
      }
    });
  });

});
