/* ── IRONFORGE MAIN JS ────────────────────────────────────────── */

// ── Navbar scroll effect
const navbar = document.getElementById('navbar');
if (navbar) {
  window.addEventListener('scroll', () => {
    navbar.classList.toggle('scrolled', window.scrollY > 40);
  }, { passive: true });
}

// ── Mobile hamburger
const hamburger = document.getElementById('hamburger');
const navLinks  = document.getElementById('navLinks');
if (hamburger && navLinks) {
  hamburger.addEventListener('click', () => {
    navLinks.classList.toggle('open');
    const open = navLinks.classList.contains('open');
    hamburger.setAttribute('aria-expanded', open);
    hamburger.querySelectorAll('span').forEach((s, i) => {
      if (open) {
        if (i === 0) s.style.transform = 'translateY(7px) rotate(45deg)';
        if (i === 1) s.style.opacity   = '0';
        if (i === 2) s.style.transform = 'translateY(-7px) rotate(-45deg)';
      } else {
        s.style.transform = '';
        s.style.opacity   = '';
      }
    });
  });
}

// ── Auto-dismiss alerts after 5s
document.querySelectorAll('.js-alert').forEach(el => {
  setTimeout(() => {
    el.style.opacity = '0';
    el.style.transform = 'translateX(20px)';
    el.style.transition = '0.4s ease';
    setTimeout(() => el.remove(), 400);
  }, 5000);
});

// ── Intersection Observer for AOS-style animations
const observer = new IntersectionObserver((entries) => {
  entries.forEach(entry => {
    if (entry.isIntersecting) {
      entry.target.classList.add('aos-visible');
      observer.unobserve(entry.target);
    }
  });
}, { threshold: 0.1, rootMargin: '0px 0px -60px 0px' });

document.querySelectorAll('[data-aos]').forEach(el => observer.observe(el));

// ── Animate numbers (counter effect)
function animateCounter(el) {
  const target = parseFloat(el.dataset.target || el.textContent.replace(/[^0-9.]/g, ''));
  const suffix = el.dataset.suffix || '';
  const prefix = el.dataset.prefix || '';
  const duration = 1600;
  const start = performance.now();

  const update = (now) => {
    const elapsed = now - start;
    const progress = Math.min(elapsed / duration, 1);
    const eased = 1 - Math.pow(1 - progress, 3);
    const value = Math.round(eased * target);
    el.textContent = prefix + value.toLocaleString() + suffix;
    if (progress < 1) requestAnimationFrame(update);
  };
  requestAnimationFrame(update);
}

const counterObserver = new IntersectionObserver((entries) => {
  entries.forEach(entry => {
    if (entry.isIntersecting) {
      animateCounter(entry.target);
      counterObserver.unobserve(entry.target);
    }
  });
}, { threshold: 0.5 });

document.querySelectorAll('[data-counter]').forEach(el => counterObserver.observe(el));

// ── Confirm dialogs for destructive actions
document.querySelectorAll('[data-confirm]').forEach(el => {
  el.addEventListener('click', e => {
    if (!confirm(el.dataset.confirm || 'Are you sure?')) {
      e.preventDefault();
    }
  });
});

// ── Tab switching
document.querySelectorAll('[data-tab-target]').forEach(btn => {
  btn.addEventListener('click', () => {
    const target = document.getElementById(btn.dataset.tabTarget);
    if (!target) return;
    const container = target.closest('[data-tabs]') || document;
    container.querySelectorAll('.tab-panel').forEach(p => p.hidden = true);
    container.querySelectorAll('[data-tab-target]').forEach(b => b.classList.remove('active'));
    target.hidden = false;
    btn.classList.add('active');
  });
});

// ── Rating stars UI
document.querySelectorAll('.star-rating').forEach(container => {
  const stars = container.querySelectorAll('.star');
  const input  = container.querySelector('input[type=hidden]');
  stars.forEach((star, i) => {
    star.addEventListener('mouseover', () => {
      stars.forEach((s, j) => s.classList.toggle('hover', j <= i));
    });
    star.addEventListener('mouseout', () => {
      stars.forEach(s => s.classList.remove('hover'));
    });
    star.addEventListener('click', () => {
      if (input) input.value = i + 1;
      stars.forEach((s, j) => s.classList.toggle('selected', j <= i));
    });
  });
});

// ── Toast helper (usable from inline scripts)
window.toast = function(msg, type = 'info') {
  const el = document.createElement('div');
  el.className = `alert alert--${type} js-alert`;
  el.innerHTML = `<span>${msg}</span><button class="alert-close" onclick="this.parentElement.remove()">✕</button>`;
  let container = document.querySelector('.messages-container');
  if (!container) {
    container = document.createElement('div');
    container.className = 'messages-container';
    document.body.appendChild(container);
  }
  container.appendChild(el);
  setTimeout(() => {
    el.style.opacity = '0';
    el.style.transform = 'translateX(20px)';
    el.style.transition = '0.4s ease';
    setTimeout(() => el.remove(), 400);
  }, 4000);
};

// ── Active nav link highlight
(function() {
  const path = window.location.pathname;
  document.querySelectorAll('.nav-links a').forEach(link => {
    const href = link.getAttribute('href');
    if (href && href !== '/' && path.startsWith(href)) {
      link.classList.add('active');
    } else if (href === '/' && path === '/') {
      link.classList.add('active');
    }
  });
})();

// ── Smooth scroll for anchor links
document.querySelectorAll('a[href^="#"]').forEach(link => {
  link.addEventListener('click', e => {
    const target = document.querySelector(link.getAttribute('href'));
    if (target) {
      e.preventDefault();
      target.scrollIntoView({ behavior: 'smooth', block: 'start' });
    }
  });
});

// ── Auto-close mobile nav on link click
document.querySelectorAll('#navLinks a').forEach(link => {
  link.addEventListener('click', () => {
    if (navLinks) navLinks.classList.remove('open');
  });
});

// ── Form validation feedback
document.querySelectorAll('form').forEach(form => {
  form.addEventListener('submit', () => {
    const btn = form.querySelector('button[type=submit]');
    if (btn && !btn.disabled) {
      btn.disabled = true;
      const original = btn.innerHTML;
      btn.innerHTML = '<div class="spinner" style="width:18px;height:18px;border-width:2px"></div> Processing...';
      btn.style.display = 'inline-flex';
      btn.style.alignItems = 'center';
      btn.style.gap = '8px';
      // Re-enable after 8s as failsafe
      setTimeout(() => { btn.disabled = false; btn.innerHTML = original; }, 8000);
    }
  });
});

// ── Scroll-to-top button
(function() {
  const btn = document.createElement('button');
  btn.innerHTML = '<i class="bi bi-arrow-up"></i>';
  btn.setAttribute('aria-label', 'Scroll to top');
  btn.style.cssText = `
    position:fixed;bottom:28px;right:28px;z-index:500;
    width:44px;height:44px;border-radius:50%;
    background:var(--card);border:1px solid var(--border-hi);
    color:var(--text);font-size:1rem;display:none;
    align-items:center;justify-content:center;
    cursor:pointer;transition:all .2s ease;
    box-shadow:0 4px 20px rgba(0,0,0,.4);
  `;
  btn.addEventListener('click', () => window.scrollTo({ top: 0, behavior: 'smooth' }));
  btn.addEventListener('mouseenter', () => { btn.style.borderColor='var(--primary)'; btn.style.color='var(--primary)'; });
  btn.addEventListener('mouseleave', () => { btn.style.borderColor='var(--border-hi)'; btn.style.color='var(--text)'; });
  document.body.appendChild(btn);

  window.addEventListener('scroll', () => {
    btn.style.display = window.scrollY > 400 ? 'flex' : 'none';
  }, { passive: true });
})();

// ── Keyboard shortcut: press '/' to focus search (if exists)
document.addEventListener('keydown', e => {
  if (e.key === '/' && e.target.tagName !== 'INPUT' && e.target.tagName !== 'TEXTAREA') {
    const searchInput = document.querySelector('input[name=q], .search-box input');
    if (searchInput) { e.preventDefault(); searchInput.focus(); }
  }
});
