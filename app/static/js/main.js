/**
 * CraveCart Master JavaScript
 * Handles responsive navigation, alert dismissals, quantity controls, and UI interactions.
 */

document.addEventListener('DOMContentLoaded', () => {
  // 1. Customer Mobile Navigation Toggle
  const navToggleBtn = document.getElementById('mobileNavToggle');
  const navLinks = document.querySelector('.nav-links');
  if (navToggleBtn && navLinks) {
    navToggleBtn.addEventListener('click', (e) => {
      e.stopPropagation();
      const isOpen = navLinks.classList.toggle('is-open');
      navToggleBtn.setAttribute('aria-expanded', isOpen ? 'true' : 'false');
    });

    // Close mobile nav when clicking outside
    document.addEventListener('click', (e) => {
      if (!navLinks.contains(e.target) && !navToggleBtn.contains(e.target)) {
        navLinks.classList.remove('is-open');
        navToggleBtn.setAttribute('aria-expanded', 'false');
      }
    });
  }

  // 2. Admin Mobile Sidebar Toggle
  const adminToggleBtn = document.getElementById('adminMobileToggle');
  const adminNav = document.querySelector('.admin-nav');
  const adminFooter = document.querySelector('.admin-sidebar-footer');
  if (adminToggleBtn && adminNav) {
    adminToggleBtn.addEventListener('click', (e) => {
      e.stopPropagation();
      const isOpen = adminNav.classList.toggle('is-open');
      if (adminFooter) adminFooter.classList.toggle('is-open');
      adminToggleBtn.setAttribute('aria-expanded', isOpen ? 'true' : 'false');
    });
  }

  // 3. Flash Alerts Auto-Dismiss (with smooth fade-out)
  const alerts = document.querySelectorAll('.alert');
  alerts.forEach(alert => {
    // Dismiss button handler
    const closeBtn = alert.querySelector('.alert-close');
    if (closeBtn) {
      closeBtn.addEventListener('click', () => {
        dismissAlert(alert);
      });
    }

    // Auto-dismiss after 6 seconds
    const timeoutId = setTimeout(() => {
      dismissAlert(alert);
    }, 6000);

    // Pause dismissal timer if hovered
    alert.addEventListener('mouseenter', () => clearTimeout(timeoutId));
  });

  function dismissAlert(alertEl) {
    if (!alertEl) return;
    alertEl.style.transition = 'opacity 0.35s ease, transform 0.35s ease, margin 0.35s ease, max-height 0.35s ease';
    alertEl.style.opacity = '0';
    alertEl.style.transform = 'translateY(-6px)';
    setTimeout(() => {
      alertEl.remove();
    }, 350);
  }

  // 4. Quantity Stepper Controls (Food Detail page)
  const quantityInput = document.getElementById('detailQuantity');
  if (quantityInput) {
    window.stepQuantity = function(delta) {
      let val = parseInt(quantityInput.value, 10) || 1;
      val = Math.max(1, Math.min(20, val + delta));
      quantityInput.value = val;
    };
  }

  // 5. Duplicate Submission Protection for Forms
  const protectForms = document.querySelectorAll('form[data-prevent-duplicate]');
  protectForms.forEach(form => {
    form.addEventListener('submit', () => {
      const submitBtn = form.querySelector('button[type="submit"], input[type="submit"]');
      if (submitBtn) {
        submitBtn.disabled = true;
        const originalText = submitBtn.innerText || submitBtn.value;
        submitBtn.setAttribute('data-original-text', originalText);
        if (submitBtn.tagName === 'INPUT') {
          submitBtn.value = 'Processing...';
        } else {
          submitBtn.innerHTML = '<span style="display:inline-block; animation:spin 1s linear infinite; margin-right:6px;">⌛</span> Processing...';
        }
      }
    });
  });

  // 6. Smooth Scroll to first validation error on page load if any
  const firstError = document.querySelector('.form-control.is-invalid, .form-error');
  if (firstError) {
    firstError.scrollIntoView({ behavior: 'smooth', block: 'center' });
    if (firstError.tagName === 'INPUT' || firstError.tagName === 'SELECT' || firstError.tagName === 'TEXTAREA') {
      firstError.focus();
    }
  }
});
