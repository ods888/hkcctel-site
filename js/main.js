/**
 * 燦成通信 CCTel - 前台 JavaScript
 * 處理：導航、產品加載、產品詳情、聯繫表單、語言切換
 */
(function () {
  'use strict';

  // ============ 導航 ============

  window.addEventListener('scroll', () => {
    const navbar = document.getElementById('navbar');
    if (navbar) {
      navbar.classList.toggle('scrolled', window.scrollY > 10);
    }
  });

  const menuToggle = document.getElementById('menuToggle');
  const navLinks = document.getElementById('navLinks');
  if (menuToggle && navLinks) {
    menuToggle.addEventListener('click', () => {
      navLinks.classList.toggle('open');
    });
    navLinks.querySelectorAll('a').forEach(link => {
      link.addEventListener('click', () => navLinks.classList.remove('open'));
    });
  }

  // ============ API ============

  // 静态模式：从本地嵌入数据读取，无需 API
  var _productsReady = false;
  function ensureProducts() {
    if (!_productsReady) {
      window.CCTEL_PRODUCTS = window.CCTEL_PRODUCTS || [];
      _productsReady = true;
    }
  }
  async function fetchProducts(params) {
    params = params || {};
    ensureProducts();
    var products = window.CCTEL_PRODUCTS;
    if (params.id) {
      for (var i = 0; i < products.length; i++) {
        if (products[i].id === parseInt(params.id, 10)) return products[i];
      }
      return null;
    }
    if (params.featured) {
      return products.filter(function(p) { return p.featured; });
    }
    return products;
  }

  // ============ 產品卡片 ============

  function createProductCard(product, langOverride, options) {
    options = options || {};
    var lang = langOverride || I18N.currentLang;
    var cardProduct = product;
    var variantIndex = typeof options.variantIndex === 'number' ? options.variantIndex : null;
    var variant = null;
    if (variantIndex !== null && product.variants && product.variants[variantIndex]) {
      variant = product.variants[variantIndex];
      cardProduct = variant;
    }

    var card = document.createElement('a');
    card.className = 'product-card';
    card.href = '/product-detail.html?id=' + product.id + (variant ? '&variant=' + variantIndex : '');
    card.style.textDecoration = 'none';
    card.style.color = 'inherit';
    card.style.display = 'block';

    // 選擇正確語言的名字
    var displayName = cardProduct.name || product.name;
    if (lang === 'en' && cardProduct.nameEn) displayName = cardProduct.nameEn;
    else if (lang === 'zh-CN' && cardProduct.nameCn) displayName = cardProduct.nameCn;

    var displaySummary = cardProduct.summary || product.summary;
    if (lang === 'en' && cardProduct.summaryEn) displaySummary = cardProduct.summaryEn;
    else if (lang === 'zh-CN' && cardProduct.summaryCn) displaySummary = cardProduct.summaryCn;

    var imgHtml = '';
    var displayImage = cardProduct.image || product.image;
    if (displayImage && displayImage.trim()) {
      imgHtml = '<img src="' + displayImage + '" alt="' + escapeHtml(displayName) + '" loading="lazy" onerror="this.classList.add(\'error\');">';
    }
    var fbHtml = '';
    if (!displayImage || !displayImage.trim()) {
      fbHtml = '<div class="placeholder-icon">📦</div>';
    } else {
      fbHtml = '<div class="img-fallback" style="display:none;position:absolute;inset:0;align-items:center;justify-content:center;font-size:4rem;color:var(--gray-300);opacity:0.5;">📦</div>';
    }
    var badgeHtml = product.featured ? '<span class="product-badge">★</span>' : '';

    var priceText = 'HK$' + (cardProduct.price || product.price);
    if (!variant && product.hasVariants && product.variants && product.variants.length > 1) {
      priceText = 'HK$' + product.price + '起';
    }

    card.innerHTML =
      '<div class="product-card-image">' +
      imgHtml + fbHtml + badgeHtml +
      '</div>' +
      '<div class="product-card-body">' +
      '<h3>' + escapeHtml(displayName) + '</h3>' +
      '<p class="summary">' + escapeHtml(displaySummary) + '</p>' +
      '<div class="product-card-footer">' +
      '<div class="product-price">' + priceText + '</div>' +
      '<span class="btn-detail">' + I18N.t('home.viewDetail') + '</span>' +
      '</div></div>';
    return card;
  }

  function escapeHtml(text) {
    if (!text) return '';
    var div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
  }

  // ============ 語言切換 ============

  var rendering = false;
  document.addEventListener('langChange', function() {
    if (rendering) return;
    rendering = true;
    renderCurrentPage();
    rendering = false;
  });

  function renderCurrentPage() {
    var path = window.location.pathname;
    if (path === '/' || path === '/index.html' || path === '') {
      loadFeaturedProducts();
    } else if (path === '/products' || path === '/products.html') {
      loadAllProducts();
    } else if (path === '/product-detail' || path === '/product-detail.html' || path === '/product-detail.html') {
      loadProductDetail();
    }
  }

  // ============ 首頁 ============

  async function loadFeaturedProducts() {
    var grid = document.getElementById('featuredProductsGrid');
    if (!grid) return;
    // 鎖定當前語言，避免 async 過程中被切換
    var lang = I18N.currentLang;

    var products = await fetchProducts({ featured: true });
    if (grid.getAttribute('data-skip-core-product') === '1') {
      products = products.filter(function(p) { return p.id !== 1; });
    }
    var displayProducts = products;
    if (displayProducts.length < 4) {
      var all = await fetchProducts();
      displayProducts = displayProducts.concat(all.filter(function(p) { return !p.featured; }));
    }
    displayProducts = displayProducts.slice(0, 4);

    grid.innerHTML = '';
    if (displayProducts.length === 0) {
      grid.innerHTML = '<div class="empty-state"><div class="empty-icon">📦</div><p>' + I18N.t('products.noProducts') + '</p></div>';
      return;
    }

    displayProducts.forEach(function(p) { grid.appendChild(createProductCard(p, lang)); });
  }

  // ============ 產品中心 ============

  var allProductsCache = [];
  var currentFilter = 'all';

  async function loadAllProducts() {
    var grid = document.getElementById('productsGrid');
    if (!grid) return;
    var lang = I18N.currentLang;

    allProductsCache = await fetchProducts();
    applyProductFilter(lang);

    document.querySelectorAll('.filter-tab').forEach(function(tab) {
      tab.addEventListener('click', function() {
        document.querySelectorAll('.filter-tab').forEach(function(t) { t.classList.remove('active'); });
        this.classList.add('active');
        currentFilter = this.getAttribute('data-filter');
        applyProductFilter();
      });
    });

    var searchInput = document.getElementById('productSearch');
    if (searchInput) {
      searchInput.addEventListener('input', applyProductFilter);
    }
  }

  function applyProductFilter(langOverride) {
    var lang = langOverride || I18N.currentLang;
    var grid = document.getElementById('productsGrid');
    var noMsg = document.getElementById('noProductsMsg');
    var searchTerm = (document.getElementById('productSearch')?.value || '').toLowerCase();

    var filtered = allProductsCache;
    if (currentFilter === 'featured') {
      filtered = filtered.filter(function(p) { return p.featured; });
    }
    if (searchTerm) {
      filtered = filtered.filter(function(p) {
        return (p.name && p.name.toLowerCase().indexOf(searchTerm) !== -1) ||
               (p.nameEn && p.nameEn.toLowerCase().indexOf(searchTerm) !== -1) ||
               (p.nameCn && p.nameCn.toLowerCase().indexOf(searchTerm) !== -1) ||
               (p.summary && p.summary.toLowerCase().indexOf(searchTerm) !== -1);
      });
    }

    grid.innerHTML = '';
    if (filtered.length === 0) {
      if (noMsg) noMsg.style.display = 'block';
    } else {
      if (noMsg) noMsg.style.display = 'none';
      filtered.forEach(function(p) { grid.appendChild(createProductCard(p, lang)); });
    }
  }

  // ============ 產品詳情 ============

  var currentProduct = null;
  var currentVariantIndex = 0;

  function processDescription(desc, descEl, descFullEl) {
    if (!desc || !desc.trim().startsWith('<')) {
      if (descEl) descEl.innerHTML = (desc || '').replace(/\r\n/g, '<br>').replace(/\n/g, '<br>');
      return;
    }

    // CUniq 格式（無 fee-section）：剝離外層 wrapper 後直接放全寬區域
    var inner = desc;
    // 移除描述中的主圖（左側 productImage 已顯示），只移除 <p><img...></p>
    inner = inner.replace(/<p[^>]*>\s*<img[^>]*>\s*<\/p>/gi, '');
    inner = inner.replace(/<img[^>]*>/gi, '');

    // 剝離 product-desc-html 包裹
    var wrapStart = /<div[^>]*class\s*=\s*"[^"]*product-desc-html[^"]*"[^>]*>/i;
    var wm = inner.match(wrapStart);
    if (wm) {
      inner = inner.substring(wm.index + wm[0].length);
      // 剝離 desc-section 包裹
      var dsMatch = inner.match(/<div[^>]*class\s*=\s*"[^"]*desc-section[^"]*"[^>]*>/i);
      if (dsMatch) inner = inner.substring(dsMatch.index + dsMatch[0].length);
      // 去除最外層兩個 </div>
      inner = inner.replace(/<\/div>\s*<\/div>\s*$/, '');
    }

    if (descFullEl) descFullEl.innerHTML = '';
    if (descEl) descEl.innerHTML = '';

    // 在 fee-section/table 處拆分（CMHK 格式）
    var si = inner.search(/<div[^>]*class\s*=\s*"[^"]*fee-section[^"]*"[^>]*>/i);
    if (si === -1) si = inner.search(/<div[^>]*class\s*=\s*"[^"]*section-divider[^"]*"[^>]*>/i);
    if (si === -1) si = inner.search(/<table[^>]*class\s*=\s*"[^"]*fee-table[^"]*"[^>]*>/i);
    if (si === -1) si = inner.search(/<table/i);
    if (si === -1) si = inner.search(/<h3[^>]*class\s*=\s*"[^"]*fee-title[^"]*"[^>]*>/i);

    if (si > 0) {
      // CMHK 格式：上半 → 右欄，下半 → 全寬
      if (descEl) descEl.innerHTML = '<div class="product-desc-html">' + inner.substring(0, si).trim() + '</div>';
      var lp = inner.substring(si).trim();
      if (!/fee-section/.test(lp)) lp = '<div class="fee-section"><div class="section-divider"></div>' + lp + '</div>';
      if (descFullEl) descFullEl.innerHTML = '<div class="product-desc-html">' + lp + '</div>';
    } else {
      // CUniq 格式 → 全寬區域
      if (descFullEl) {
        descFullEl.innerHTML = '<div class="product-desc-html">\n<div class="desc-section">\n' + inner + '\n</div>\n</div>';
      }
    }
  }

  function selectVariant(index) {
    if (!currentProduct || !currentProduct.variants) return;
    currentVariantIndex = index;
    var variant = currentProduct.variants[index];
    var lang = I18N.currentLang;

    // 1. 更新產品名稱（三語對應）
    var nameEl = document.getElementById('productName');
    if (nameEl) {
      var vn = variant.name;
      if (lang === 'en' && variant.nameEn) vn = variant.nameEn;
      else if (lang === 'zh-CN' && variant.nameCn) vn = variant.nameCn;
      nameEl.textContent = vn || variant.name;
    }

    // 2. 更新價格
    var priceEl = document.getElementById('productPrice');
    if (priceEl) priceEl.innerHTML = '<small>HK$</small>' + variant.price;

    // 3. 更新主圖
    var imageContainer = document.getElementById('productImage');
    if (imageContainer && variant.image) {
      var altName = variant.nameEn || variant.name;
      imageContainer.innerHTML = '<img src="' + variant.image + '" alt="' + escapeHtml(altName) + '" onerror="this.style.display=\'none\';">';
    } else if (imageContainer && currentProduct.image) {
      imageContainer.innerHTML = '<img src="' + currentProduct.image + '" alt="' + escapeHtml(I18N.field(currentProduct, 'name')) + '" onerror="this.style.display=\'none\';">';
    }

    // 4. 更新描述（根據語言選對應的變體描述）
    var descEl = document.getElementById('productDesc');
    var descFullEl = document.getElementById('productDescFull');
    var vdesc = variant.description;
    if (lang === 'en' && variant.descriptionEn) vdesc = variant.descriptionEn;
    else if (lang === 'zh-CN' && variant.descriptionCn) vdesc = variant.descriptionCn;
    if (vdesc) {
      processDescription(vdesc, descEl, descFullEl);
    }

    // 5. 更新頁面標題
    var displayName = variant.name;
    if (lang === 'en' && variant.nameEn) displayName = variant.nameEn;
    else if (lang === 'zh-CN' && variant.nameCn) displayName = variant.nameCn;
    document.title = displayName + ' - ' + I18N.t('site.name');

    // 6. 更新活動選項樣式
    var options = document.querySelectorAll('.variant-option');
    options.forEach(function(opt, i) {
      opt.classList.toggle('active', i === index);
    });
  }

  async function loadProductDetail() {
    var container = document.getElementById('productDetail');
    if (!container) return;
    var lang = I18N.currentLang;

    var params = new URLSearchParams(window.location.search);
    var id = params.get('id');
    if (!id) { window.location.href = '/products'; return; }

    var product = await fetchProducts({ id: parseInt(id) });
    if (!product || !product.id) { window.location.href = '/products'; return; }

    currentProduct = product;
    var requestedVariantIndex = parseInt(params.get('variant'), 10);
    if (isNaN(requestedVariantIndex) || !product.variants || !product.variants[requestedVariantIndex]) {
      requestedVariantIndex = 0;
    }
    currentVariantIndex = requestedVariantIndex;

    // 捕捉第一個變體（如果有的話），用於初始顯示
    var firstVariant = (product.variants && product.variants.length > 0) ? product.variants[currentVariantIndex] : null;

    // Helper: 根據捕獲的語言選字段
    function pf(obj, field) {
      if (lang === 'en' && obj[field + 'En']) return obj[field + 'En'];
      if (lang === 'zh-CN' && obj[field + 'Cn']) return obj[field + 'Cn'];
      return obj[field] || '';
    }

    // 初始化顯示用的對象：變體優先
    var displayObj = firstVariant && product.hasVariants ? firstVariant : product;
    var displayName = pf(displayObj, 'name');
    var displayImage = firstVariant && firstVariant.image ? firstVariant.image : product.image;
    var displayPrice = firstVariant ? firstVariant.price : product.price;

    var imageContainer = document.getElementById('productImage');
    if (imageContainer) {
      if (displayImage && displayImage.trim()) {
        imageContainer.innerHTML = '<img src="' + displayImage + '" alt="' + escapeHtml(displayName) + '" onerror="this.style.display=\'none\';">';
      } else {
        imageContainer.innerHTML = '<div class="placeholder-icon">📦</div>';
      }
    }

    var nameEl = document.getElementById('productName');
    var priceEl = document.getElementById('productPrice');
    var descEl = document.getElementById('productDesc');
    var variantEl = document.getElementById('variantSelector');
    var descFullEl = document.getElementById('productDescFull');

    if (nameEl) nameEl.textContent = displayName;
    if (descFullEl) descFullEl.innerHTML = '';

    // Variant selector
    if (variantEl) {
      if (product.hasVariants && product.variants && product.variants.length > 1) {
        var selLabel = lang === 'en' ? 'Select plan' : (lang === 'zh-CN' ? '选择套餐' : '選擇方案');
        var html = '<div class="variant-selector-label">' + selLabel + '</div><div class="variant-options">';
        product.variants.forEach(function(v, i) {
          var day = v.day || '';
          var data = v.data || '';
          var label = day ? (day + (lang === 'en' ? '-Day ' : '日 ')) : '';
          if (data) label += data + ' ';
          label += 'HK$' + v.price;
          html += '<div class="variant-option' + (i === currentVariantIndex ? ' active' : '') + '" onclick="selectVariant(' + i + ')">' + label.trim() + '</div>';
        });
        html += '</div>';
        variantEl.innerHTML = html;
        variantEl.style.display = 'block';
      } else {
        variantEl.style.display = 'none';
      }
    }

    // Price
    if (priceEl) priceEl.innerHTML = '<small>HK$</small>' + displayPrice;

    // Description
    if (descEl) processDescription(pf(product, 'description'), descEl, descFullEl);

    // Document title — 用變體名稱
    document.title = displayName + ' - ' + I18N.t('site.name');

    var allProducts = await fetchProducts();
    var relatedPool = [
      { id: 1 },
      { id: 2 },
      { id: 3 },
      { id: 14, variantIndex: 1 },
      { id: 27, variantIndex: 0 }
    ];
    var related = [];

    relatedPool.forEach(function(item) {
      var match = allProducts.find(function(p) { return p.id === item.id && p.id !== product.id; });
      if (match) related.push({ product: match, variantIndex: item.variantIndex });
    });

    allProducts.forEach(function(p) {
      var exists = related.some(function(item) { return item.product.id === p.id; });
      if (p.id !== product.id && !exists) related.push({ product: p });
    });

    related = related.slice(0, 4);
    var relatedGrid = document.getElementById('relatedProductsGrid');
    if (relatedGrid) {
      relatedGrid.innerHTML = '';
      related.forEach(function(item) {
        relatedGrid.appendChild(createProductCard(item.product, lang, { variantIndex: item.variantIndex }));
      });
    }
  }

  window.selectVariant = selectVariant;
  // ============ 聯繫表單 ============

  var contactForm = document.getElementById('contactForm');
  if (contactForm) {
    contactForm.addEventListener('submit', async function(e) {
      e.preventDefault();
      var name = (this.querySelector('[name="name"]') || {}).value || '';
      var email = (this.querySelector('[name="email"]') || {}).value || '';
      var phone = (this.querySelector('[name="phone"]') || {}).value || '';
      var subject = (this.querySelector('[name="subject"]') || {}).value || '';
      var message = (this.querySelector('[name="message"]') || {}).value || '';
      // 先提交到後端存檔
      try {
        var fd = new FormData(this);
        await fetch('https://formspree.io/f/xqevbnzg', { method: 'POST', body: fd });
      } catch(e) {}
      // 同時彈出 WhatsApp
      var body = encodeURIComponent('姓名：' + name + '\n电话：' + phone + '\n电邮：' + email + '\n主题：' + subject + '\n内容：' + message);
      var isMobile = /Android|iPhone|iPad|iPod/i.test(navigator.userAgent);
      if (isMobile) {
        window.open('https://api.whatsapp.com/send?phone=85292445678&text=' + body, '_blank');
      } else {
        window.open('https://web.whatsapp.com/send?phone=85292445678&text=' + body, '_blank');
      }
      showToast(I18N.t('contact.form.success') || '感谢您的查询，我们会尽快回复！', 'success');
      this.reset();
    });
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

  // ============ 合作夥伴輪播 ============

  var partners = [
    { id: 'cmhk', name: '中國移動香港', nameEn: 'CMHK', nameCn: '中国移动香港', img: '/static/picture/h1.jpg', featured: true },
    { id: 'mobileduck', name: '鴨聊佳', nameEn: 'Mobile Duck', nameCn: '鸭聊佳', img: '/static/picture/h2.png', featured: true },
    { id: 'hkunicom', name: '香港聯通', nameEn: 'HK Unicom', nameCn: '香港联通', img: '/static/picture/h3.jpg', featured: true },
    { id: 'smart', name: '柬埔寨 Smart', nameEn: 'Smart Cambodia', nameCn: '柬埔寨 Smart', img: '/static/picture/h4.jpg', featured: true },
    { id: 'dhiraagu', name: '馬爾代夫 Dhiraagu', nameEn: 'Dhiraagu Maldives', nameCn: '马尔代夫 Dhiraagu', img: '/static/picture/h5.jpg', featured: false },
    { id: 'softbank', name: '日本 SoftBank', nameEn: 'SoftBank Japan', nameCn: '日本 SoftBank', img: '/static/picture/h6.jpg', featured: false },
    { id: 'vodafone', name: 'Vodafone', nameEn: 'Vodafone', nameCn: 'Vodafone', img: '/static/picture/h7.jpg', featured: false },
    { id: 'etl', name: '老撾 ETL', nameEn: 'ETL Laos', nameCn: '老挝 ETL', img: '/static/picture/h8.jpg', featured: false },
    { id: 'true', name: '泰國 True', nameEn: 'True Thailand', nameCn: '泰国 True', img: '/static/picture/h9.jpg', featured: false }
  ];

  var partnersVisible = 4;
  var partnersIndex = 0;
  var partnersAutoTimer = null;

  function getPartnerName(p, langOverride) {
    var lang = langOverride || I18N.currentLang;
    if (lang === 'en') return p.nameEn;
    if (lang === 'zh-CN') return p.nameCn;
    return p.name;
  }

  function renderPartners() {
    var track = document.getElementById('partnersTrack');
    var dots = document.getElementById('partnersDots');
    if (!track || !dots) return;

    var totalPages = partners.length;
    var html = '';
    for (var i = 0; i < partners.length; i++) {
      var p = partners[i];
      var cls = 'partner-card';
      html += '<div class="' + cls + '">' +
        '<div class="partner-img-wrap"><img src="' + (p.img || '/uploads/logos/' + p.id + '.svg') + '" alt="' + getPartnerName(p) + '" class="partner-logo-img"></div>' +
        '</div>';
    }
    track.innerHTML = html;

    // Update card widths based on visible count
    updatePartnerCardWidth();

    // Render dots
    var dotCount = partners.length;
    var dotsHtml = '';
    for (var d = 0; d < dotCount; d++) {
      dotsHtml += '<button class="partners-dot' + (d === partnersIndex ? ' active' : '') + '" data-index="' + d + '"></button>';
    }
    dots.innerHTML = dotsHtml;

    // Dot click events
    dots.querySelectorAll('.partners-dot').forEach(function(dot) {
      dot.addEventListener('click', function() {
        goToPartner(parseInt(this.getAttribute('data-index')));
      });
    });

    updatePartnerPosition();
  }

  function updatePartnerCardWidth() {
    var track = document.getElementById('partnersTrack');
    if (!track) return;
    var cards = track.querySelectorAll('.partner-card');
    if (cards.length === 0) return;
    var v = partnersVisible;
    if (window.innerWidth <= 480) v = 2;
    else if (window.innerWidth <= 768) v = 3;
    var gapPx = 20;
    if (v <= 2) gapPx = 10;
    var cardWidth = 'calc((100% - ' + (gapPx * (v - 1)) + 'px) / ' + v + ')';
    cards.forEach(function(c) { c.style.minWidth = cardWidth; });
  }

  function updatePartnerPosition() {
    var track = document.getElementById('partnersTrack');
    if (!track) return;
    var v = partnersVisible;
    if (window.innerWidth <= 480) v = 2;
    else if (window.innerWidth <= 768) v = 3;
    var gapPx = 20;
    if (v <= 2) gapPx = 10;
    var totalCards = partners.length;
    // Wrap index
    if (partnersIndex >= totalCards) partnersIndex = 0;
    if (partnersIndex < 0) partnersIndex = totalCards - 1;
    var cardPercent = 100 / v;
    var gapPercent = gapPx / ((document.querySelector('.partners-carousel-clip')?.clientWidth || 1100) / 100);
    var offset = partnersIndex * (cardPercent + gapPercent);
    track.style.transform = 'translateX(-' + offset + '%)';

    // Update dots
    document.querySelectorAll('.partners-dot').forEach(function(d, i) {
      d.classList.toggle('active', i === partnersIndex);
    });
  }

  function goToPartner(index) {
    partnersIndex = index;
    updatePartnerPosition();
    resetPartnersAuto();
  }

  function nextPartner() {
    partnersIndex++;
    if (partnersIndex >= partners.length) partnersIndex = 0;
    updatePartnerPosition();
    resetPartnersAuto();
  }

  function prevPartner() {
    partnersIndex--;
    if (partnersIndex < 0) partnersIndex = partners.length - 1;
    updatePartnerPosition();
    resetPartnersAuto();
  }

  function resetPartnersAuto() {
    if (partnersAutoTimer) clearInterval(partnersAutoTimer);
    partnersAutoTimer = setInterval(nextPartner, 4000);
  }

  var partnersStarted = false;
  function initPartners() {
    var track = document.getElementById('partnersTrack');
    if (!track) return;
    renderPartners();
    document.getElementById('partnersArrowRight').addEventListener('click', nextPartner);
    document.getElementById('partnersArrowLeft').addEventListener('click', prevPartner);
    window.addEventListener('resize', function() {
      updatePartnerCardWidth();
      updatePartnerPosition();
    });
    var wrapper = document.querySelector('.partners-carousel-wrapper');
    if (wrapper) {
      wrapper.addEventListener('mouseenter', function() { clearInterval(partnersAutoTimer); });
      wrapper.addEventListener('mouseleave', function() { resetPartnersAuto(); });
    }
    // 页面滚动到合作伙伴区域后 4 秒才开始滑动
    var section = document.querySelector('.partners-section');
    if (section && !partnersStarted) {
      var observer = new IntersectionObserver(function(entries) {
        if (entries[0].isIntersecting && !partnersStarted) {
          partnersStarted = true;
          setTimeout(function() { resetPartnersAuto(); }, 4000);
          observer.disconnect();
        }
      }, { threshold: 0.3 });
      observer.observe(section);
    } else {
      resetPartnersAuto();
    }
  }
  if (window.location.pathname === '/' || window.location.pathname === '/index.html' || window.location.pathname === '') {
    document.addEventListener('DOMContentLoaded', function() { setTimeout(initPartners, 100); });
  }
})();
