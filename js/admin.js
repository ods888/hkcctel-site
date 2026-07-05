/**
 * 燦成通信 CCTel - 後台管理 JavaScript
 * 處理：登入認證、產品管理 CRUD、儀表板
 */
(function () {
  'use strict';

  // CSRF Token
  var csrfToken = '';
  async function fetchCsrfToken() {
    try {
      var r = await fetch('/api/csrf-token');
      var d = await r.json();
      csrfToken = d.token || '';
    } catch(e) { csrfToken = ''; }
  }

  // 封裝帶 CSRF 的 fetch
  function apiFetch(url, options) {
    options = options || {};
    options.headers = options.headers || {};
    if (csrfToken) {
      options.headers['X-CSRF-Token'] = csrfToken;
    }
    return fetch(url, options);
  }

  // ============ 認證檢查 ============

  async function checkAuth() {
    try {
      const res = await fetch('/api/check-auth');
      const data = await res.json();
      return data.authenticated;
    } catch (e) {
      return false;
    }
  }

  async function requireAuth() {
    const authed = await checkAuth();
    if (!authed) {
      window.location.href = '/admin/login.html';
      return false;
    }
    return true;
  }

  // ============ 登入頁面 ============

  const loginForm = document.getElementById('loginForm');
  if (loginForm) {
    loginForm.addEventListener('submit', async (e) => {
      e.preventDefault();
      const username = document.getElementById('username').value;
      const password = document.getElementById('password').value;

      try {
        const res = await fetch('/api/login', {
          method: 'POST',
          headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
          body: 'username=' + encodeURIComponent(username) + '&password=' + encodeURIComponent(password)
        });
        const data = await res.json();
        if (data.success) {
          await fetchCsrfToken();
          window.location.href = '/admin/dashboard.html';
        } else {
          showToast(data.message || 'Login failed', 'error');
        }
      } catch (err) {
        showToast('Network error: ' + err.message, 'error');
      }
    });

    // Check if already logged in
    (async () => {
      const authed = await checkAuth();
      if (authed) window.location.href = '/admin/dashboard.html';
    })();
  }

  // ============ 登出 ============

  window.logout = async function () {
    await fetch('/api/logout', { method: 'POST' });
    window.location.href = '/admin/login.html';
  };

  // ============ I18N helper ============

  function t(key) {
    if (typeof I18N !== 'undefined' && I18N.t) return I18N.t(key);
    return key;
  }

  function field(product, fieldName) {
    if (typeof I18N !== 'undefined' && I18N.field) return I18N.field(product, fieldName);
    return product[fieldName] || '';
  }

  // ============ Toast ============

  function showToast(message, type) {
    if (type === undefined) type = 'success';
    var existing = document.querySelector('.toast');
    if (existing) existing.remove();
    var toast = document.createElement('div');
    toast.className = 'toast toast-' + type;
    toast.textContent = message;
    document.body.appendChild(toast);
    setTimeout(function() {
      toast.style.opacity = '0';
      toast.style.transition = 'opacity 0.3s';
      setTimeout(function() { toast.remove(); }, 300);
    }, 3000);
  }
  window.showToast = showToast;

  // ============ 儀表板 & 產品列表 ============

  async function loadDashboardProducts() {
    try {
      var res = await fetch('/api/products?admin=true');
      var products = await res.json();

      // Update stats
      var totalEl = document.getElementById('totalProducts');
      var activeEl = document.getElementById('activeProducts');
      var featuredEl = document.getElementById('featuredProducts');
      if (totalEl) totalEl.textContent = products.length;
      if (activeEl) activeEl.textContent = products.filter(function(p) { return p.active; }).length;
      if (featuredEl) featuredEl.textContent = products.filter(function(p) { return p.featured; }).length;

      // Render table
      var tbody = document.getElementById('productTableBody');
      if (!tbody) return;

      if (products.length === 0) {
        tbody.innerHTML = '<tr><td colspan="7" class="empty-state">' + t('admin.noProducts') + '</td></tr>';
        return;
      }

      var path = window.location.pathname;
      var isDashboard = path.includes('dashboard.html');

      tbody.innerHTML = products.map(function(p) {
        var imgHtml = p.image
          ? '<img src="' + p.image + '" class="product-thumb" onerror="this.style.display=\'none\';this.nextElementSibling.style.display=\'flex\';"><span style="display:none;width:80px;height:60px;align-items:center;justify-content:center;background:var(--gray-100);border-radius:4px;font-size:1.5rem;">📦</span>'
          : '<span style="display:flex;width:80px;height:60px;align-items:center;justify-content:center;background:var(--gray-100);border-radius:4px;font-size:1.5rem;">📦</span>';

        var name = field(p, 'name');
        var statusBadge = p.active
          ? '<span class="badge badge-success">' + t('admin.active') + '</span>'
          : '<span class="badge badge-danger">' + t('admin.inactive') + '</span>';
        var featuredCheck = '<input type="checkbox" class="featured-check" data-id="' + p.id + '"' + (p.featured ? ' checked' : '') + '>';
        var dateStr = new Date(p.createdAt).toLocaleDateString('zh-HK');

        var editBtn = '<a href="product-form.html?id=' + p.id + '" class="btn btn-sm" style="background:#fff;color:#374151;border:1px solid #d1d5db;">' + t('admin.edit') + '</a>';
        var deleteBtn = '<button onclick="deleteProduct(' + p.id + ')" class="btn btn-sm btn-danger">' + t('admin.delete') + '</button>';

        if (isDashboard) {
          return '<tr><td>' + imgHtml + '</td><td><strong>' + name + '</strong></td><td>HKD ' + p.price.toFixed(2) + '</td><td>' + featuredCheck + '</td><td>' + statusBadge + '</td><td>' + editBtn + ' ' + deleteBtn + '</td></tr>';
        }
        return '<tr><td>' + imgHtml + '</td><td><strong>' + name + '</strong></td><td>HKD ' + p.price.toFixed(2) + '</td><td>' + featuredCheck + '</td><td>' + statusBadge + '</td><td>' + dateStr + '</td><td>' + editBtn + ' ' + deleteBtn + '</td></tr>';
      }).join('');
    } catch (e) {
      console.error('Failed to load products:', e);
    }
  }

  // ============ 批量精選 ============

  window.saveFeatured = async function () {
    var checks = document.querySelectorAll('.featured-check');
    var updates = [];
    checks.forEach(function(cb) {
      updates.push({ id: parseInt(cb.getAttribute('data-id')), featured: cb.checked });
    });
    var count = 0;
    for (var i = 0; i < updates.length; i++) {
      var u = updates[i];
      try {
        var res = await apiFetch('/api/products/save', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ id: u.id, featured: u.featured, _partial: true })
        });
        if (res.ok) count++;
      } catch (e) {}
    }
    showToast('已保存 ' + count + ' 個精選狀態');
  };

  // ============ 刪除產品 ============

  window.deleteProduct = async function (id) {
    if (!confirm(t('admin.confirmDelete') || '確定要刪除嗎？')) return;
    try {
      var res = await apiFetch('/api/products/delete', {
        method: 'POST',
        headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
        body: 'id=' + id
      });
      var result = await res.json();
      if (result.success) {
        showToast(t('admin.productDeleted') || '產品已刪除');
        loadDashboardProducts();
      } else {
        showToast(result.message || '刪除失敗', 'error');
      }
    } catch (e) {
      showToast('Network error', 'error');
    }
  };

  // ============ 產品表單 ============

  var productForm = document.getElementById('productForm');
  if (productForm) {
    // Load existing product data
    var params = new URLSearchParams(window.location.search);
    var editId = params.get('id');
    if (editId) {
      (async function() {
        try {
          var res = await fetch('/api/products?id=' + editId + '&admin=true');
          var product = await res.json();
          if (product) {
            document.getElementById('formTitle').textContent = t('admin.editProduct') || '編輯產品';
            document.getElementById('productId').value = product.id;
            document.getElementById('name').value = product.name || '';
            document.getElementById('nameEn').value = product.nameEn || '';
            document.getElementById('nameCn').value = product.nameCn || '';
            document.getElementById('summary').value = product.summary || '';
            document.getElementById('summaryEn').value = product.summaryEn || '';
            document.getElementById('summaryCn').value = product.summaryCn || '';
            document.getElementById('description').value = product.description || '';
            document.getElementById('descriptionEn').value = product.descriptionEn || '';
            document.getElementById('descriptionCn').value = product.descriptionCn || '';
            document.getElementById('price').value = product.price || 0;
            document.getElementById('featured').checked = product.featured;
            document.getElementById('active').checked = product.active;
            if (product.image) {
              document.getElementById('existingImageContainer').style.display = 'block';
              document.getElementById('existingImagePreview').src = product.image;
              document.getElementById('existingImageInput').value = product.image;
            }
            var deleteBtn = document.getElementById('deleteBtn');
            if (deleteBtn) deleteBtn.style.display = 'inline-block';
          }
        } catch (e) {}
      })();
    }

    // Delete button
    var deleteBtn = document.getElementById('deleteBtn');
    if (deleteBtn) {
      deleteBtn.addEventListener('click', function() {
        if (editId) deleteProduct(parseInt(editId));
      });
    }

    // Form submit
    productForm.addEventListener('submit', async function(e) {
      e.preventDefault();
      var formData = new FormData(productForm);
      try {
        var res = await apiFetch('/api/products/save', {
          method: 'POST',
          body: formData
        });
        var result = await res.json();
        if (result.success) {
          showToast(t('admin.productSaved') || '產品已儲存');
          setTimeout(function() { window.location.href = 'products.html'; }, 800);
        } else {
          showToast(result.message || '儲存失敗', 'error');
        }
      } catch (err) {
        showToast('Network error', 'error');
      }
    });
  }

  // ============ 頁面初始化 ============

  document.addEventListener('DOMContentLoaded', async function() {
    var path = window.location.pathname;

    // 需要認證的頁面
    if (path.indexOf('/admin/') !== -1 && path.indexOf('login.html') === -1) {
      var authed = await requireAuth();
      if (!authed) return;
    }

    // 載入儀表板或產品列表
    if (path.indexOf('dashboard.html') !== -1 || path.indexOf('/admin/products.html') !== -1) {
      loadDashboardProducts();
    }
  });

})();
