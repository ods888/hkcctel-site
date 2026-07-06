/**
 * 燦成通信 CCTel - 多語言國際化系統
 * 支援：繁體中文（默認）、簡體中文、English
 */
const I18N = {
  currentLang: 'zh-HK',

  // 從 localStorage 讀取語言設置，無則按 IP 判斷
  init() {
    const saved = localStorage.getItem('cctel_lang');
    if (saved && ['zh-HK', 'zh-CN', 'en'].includes(saved)) {
      this.currentLang = saved;
      this.updateUI();
      return;
    }
    // 按訪問者 IP 地理位置自動選擇語言
    var self = this;
    fetch('https://ipapi.co/json/', { cache: 'no-store' })
      .then(function(r) { return r.json(); })
      .then(function(d) {
        var cc = (d.country_code || '').toUpperCase();
        if (cc === 'CN') { self.currentLang = 'zh-CN'; }
        else if (cc === 'HK' || cc === 'MO' || cc === 'TW') { self.currentLang = 'zh-HK'; }
        else { self.currentLang = 'en'; }
        self.updateUI();
      })
      .catch(function() {
        self.updateUI(); // API 失敗時保持默認 zh-HK
      });
  },

  // 切換語言
  switchLang(lang) {
    if (!['zh-HK', 'zh-CN', 'en'].includes(lang)) return;
    this.currentLang = lang;
    localStorage.setItem('cctel_lang', lang);
    this.updateUI();
  },

  // 獲取翻譯文本
  t(key) {
    const keys = key.split('.');
    let value = translations[this.currentLang];
    for (const k of keys) {
      if (value && value[k] !== undefined) {
        value = value[k];
      } else {
        // fallback to zh-HK
        value = translations['zh-HK'];
        for (const k2 of keys) {
          if (value && value[k2] !== undefined) {
            value = value[k2];
          } else {
            return key;
          }
        }
        return value;
      }
    }
    return value || key;
  },

  // 根據當前語言選擇欄位值
  field(product, field) {
    if (!product) return '';
    const lang = this.currentLang;
    var result;
    if (lang === 'en' && product[field + 'En']) result = product[field + 'En'];
    else if (lang === 'zh-CN' && product[field + 'Cn']) result = product[field + 'Cn'];
    else result = product[field] || '';
    return result;
  },

  // 更新所有帶 data-i18n 屬性的元素
  updateUI() {
    // 更新文字
    document.querySelectorAll('[data-i18n]').forEach(el => {
      const key = el.getAttribute('data-i18n');
      const text = this.t(key);
      if (text) el.textContent = text;
    });

    // 更新 placeholder
    document.querySelectorAll('[data-i18n-placeholder]').forEach(el => {
      const key = el.getAttribute('data-i18n-placeholder');
      const text = this.t(key);
      if (text) el.placeholder = text;
    });

    // 更新語言切換按鈕狀態
    document.querySelectorAll('.lang-switch button').forEach(btn => {
      btn.classList.remove('active');
      if (btn.getAttribute('data-lang') === this.currentLang) {
        btn.classList.add('active');
      }
    });

    // 更新 HTML lang 屬性
    document.documentElement.lang = this.currentLang;

    // 觸發自定義事件，讓其他腳本響應語言變更
    document.dispatchEvent(new CustomEvent('langChange', { detail: { lang: this.currentLang } }));
  }
};

// 翻譯字典
const translations = {
  'zh-HK': {
    // 通用
    site: { name: '燦成通信', slogan: '全球通信，高效互聯', subSlogan: '為您提供全球優質上網卡及通訊服務' },
    nav: { home: '首頁', about: '關於我們', products: '產品中心', contact: '聯繫我們', login: '後台管理' },
    lang: { label: '語言', zhHK: '繁', zhCN: '簡', en: 'EN' },

    // 首頁
    home: {
      heroKicker: 'Hong Kong Telecom Distribution Partner',
      heroTitle: '可靠連接，從香港走向全球',
      heroSub: '以中國移動香港相關產品為核心業務基礎，燦成通信長期堅持合規經營，連接香港本地分銷、零售、電商平台與跨境通信產品資源。',
      heroHighlight: '多年來，公司累計服務數十萬名旅客及跨境用戶，產品資源覆蓋 200+ 國家及地區，主要電商平台客戶好評率長期保持 99% 以上，並形成成熟的售前諮詢、產品交付及售後服務體系。',
      heroProofMarkets: '200+ 覆蓋國家及地區',
      heroProofRating: '99%+ 平台好評率',
      heroBtn: '查看產品資源',
      cooperationBtn: '商務合作查詢',
      visualRetail: '零售',
      visualEcom: '電商',
      panelEyebrow: 'Connectivity portfolio',
      panelTitle: '渠道、產品與服務運營',
      panelChannels: '本港及大陸多平台經營',
      proofTitle: '以本地渠道能力，承接跨境通信需求',
      foundationLabel: '營運基礎',
      foundationTitle: '以中國移動香港相關產品為核心業務基礎',
      foundationDesc: '多年來，燦成通信圍繞香港本地通信產品、跨境旅遊上網卡及多平台分銷，形成成熟的售前諮詢、產品交付及售後服務體系。',
      foundationPanelLabel: '營運基礎',
      foundationPanelTitle: '從產品資源到渠道交付',
      foundationPanelDesc: '圍繞 CMHK 相關產品、本地零售與多平台電商渠道，沉澱可持續的產品諮詢、交付與售後能力。',
      showcaseLabel: '核心產品資源',
      showcaseCoreTitle: '5G 18GB中國內地365日數據卡（新版本）',
      showcaseCoreDesc: 'CMHK 相關產品核心代表，面向中國內地跨境通信高頻需求。',
      featuredProductsLabel: '核心產品',
      featuredProducts: '核心產品資源',
      featuredProductsDesc: '覆蓋本地、內地、亞洲、歐洲及全球漫遊等多類通信產品，適配零售、分銷與商務出行需求。',
      viewAll: '查看全部',
      price: 'HK$',
      viewDetail: '查看詳情',
      capabilitiesLabel: '服務能力',
      capabilitiesTitle: '通信產品渠道與服務能力',
      capabilitiesDesc: '圍繞香港本地通信產品、跨境旅遊上網卡與多平台分銷，提供從產品諮詢到交付售後的穩定服務。',
      whyUs: '為什麼選擇我們',
      why1Title: 'CMHK 產品經營基礎',
      why1Desc: '以中國移動香港相關產品為核心業務基礎，持續服務香港本地及跨境通信需求。',
      why2Title: '多平台渠道運營',
      why2Desc: '具備香港本地分銷、零售及大陸、本港電商多平台經營經驗。',
      why3Title: '全球產品資源',
      why3Desc: '產品資源覆蓋 200+ 國家及地區，滿足旅遊、商務與跨境用戶通信場景。',
      why4Title: '服務體系沉澱',
      why4Desc: '形成成熟的售前諮詢、產品交付及售後服務體系，主要電商平台客戶好評率長期保持 99% 以上。',
      stats: { cmhk: '中國移動香港相關產品核心業務基礎', customersNumber: '數十萬+', customers: '累計服務旅客及跨境用戶', countries: '產品資源覆蓋國家及地區', products: '產品方案', satisfaction: '主要電商平台客戶好評率' },
      partnersLabel: '合作資源',
      partnersTitle: '合作與產品資源',
      partnersDesc: '圍繞多家運營商及國際通信產品資源，持續拓展穩定合作。'
    },

    // 關於我們
    about: {
      title: '關於我們',
      intro: '公司簡介',
      introText: '燦成通信貿易有限公司，註冊地為中國香港。公司立足香港國際樞紐優勢，深耕全球通信行業，與多個國家及地區主流基礎運營商達成代理及戰略合作。核心合作夥伴包括：香港移動 CMHK、中國聯通國際 CUniq（五星級代理商）、柬埔寨 Smart、馬爾代夫 Dhiraagu 等知名電信運營商。\n\n主營產品與服務包含：境外儲值卡、本地電話卡、全球 eSIM、通信增值券、AI 算力服務等多元化品類，代理業務覆蓋全球境外通信資源。\n\n銷售渠道全域佈局：線下入駐香港鴨寮街實體商圈，線上入駐 HKTVmall 電商平台；同時設立大陸子公司，專業運營國內電商渠道，覆蓋飛豬、京東、拼多多等平台，開展批發、分銷及零售業務。\n\n公司同步積極佈局人工智能領域，拓展 AI 產業鏈上下游資源與合作機會，實現通信主業與 AI 新業務協同發展。',
      mission: '發展理念',
      missionText: '助力全球通信高效互聯',
      values: '核心價值',
      val1Title: '全球合作',
      val1Desc: '與多國主流運營商達成戰略合作，覆蓋全球通信資源',
      val2Title: '多元服務',
      val2Desc: '境外儲值卡、eSIM、AI算力等多元化產品矩陣',
      val3Title: '全域渠道',
      val3Desc: '線下實體商圈+線上電商平台，批發分銷零售全覆蓋',
      val4Title: 'AI 創新',
      val4Desc: '佈局人工智能領域，通信主業與 AI 新業務協同發展'
    },

    // 產品中心
    products: {
      title: '產品中心',
      desc: '探索我們全系列上網卡及數據漫遊方案',
      allProducts: '全部產品',
      featured: '精選推薦',
      search: '搜尋產品...',
      noProducts: '暫無產品',
      price: 'HK$',
      viewDetail: '查看詳情',
      features: '產品特點',
      buyNow: '點擊獲取批發價',
      backToList: '返回產品列表',
      relatedProducts: '相關產品',
      retailPrice: '建議零售價',
      metaAgent: '官方授權代理商',
      metaDelivery: '即買即發·全港配送',
      metaWhatsApp: 'WhatsApp 實時客服'
    },

    // 聯繫我們
    contact: {
      title: '聯繫我們',
      desc: '如有任何查詢，歡迎與我們聯繫',
      address: '公司地址',
      addressText: '深水埗汝州街 256 號 A 地鋪',
      phone: '電話',
      email: '電郵',
      whatsapp: 'WhatsApp',
      businessHours: '營業時間',
      businessHoursText: '周一至周日 上午 10:00 - 下午 6:00\n公眾假期休息',
      form: { title: '發送查詢', name: '您的姓名', email: '電郵地址', phone: '聯絡電話', subject: '查詢主題',
        message: '查詢內容', submit: '提交查詢', success: '感謝您的查詢，我們會盡快回覆！' }
    },

    // 腳部
    footer: {
      rights: '版權所有',
      privacy: '私隱政策',
      terms: '服務條款',
      quickLinks: '快速連結',
      contactInfo: '聯繫資訊',
      followUs: '關注我們'
    },

    // 後台
    admin: {
      login: '後台管理登入',
      username: '用戶名',
      password: '密碼',
      loginBtn: '登入',
      dashboard: '管理儀表板',
      totalProducts: '產品總數',
      activeProducts: '上架產品',
      featuredProducts: '精選產品',
      logout: '退出登入',
      productMgmt: '產品管理',
      addProduct: '新增產品',
      editProduct: '編輯產品',
      edit: '編輯',
      productName: '產品名稱（繁體）',
      productNameEn: '產品名稱（English）',
      productNameCn: '產品名稱（簡體）',
      summary: '簡介（繁體）',
      summaryEn: '簡介（English）',
      summaryCn: '簡介（簡體）',
      description: '詳細描述（繁體）',
      descriptionEn: '詳細描述（English）',
      descriptionCn: '詳細描述（簡體）',
      price: '價格（HKD）',
      image: '產品圖片',
      featured: '設為首頁推薦',
      active: '上架',
      save: '儲存',
      cancel: '取消',
      delete: '刪除',
      confirmDelete: '確定要刪除此產品嗎？',
      noProducts: '暫無產品，請新增產品',
      backToDashboard: '返回儀表板',
      imageHint: '建議尺寸：800x600px，支援 JPG/PNG/GIF',
      existingImage: '目前圖片'
    }
  },

  'zh-CN': {
    site: { name: '灿成通信', slogan: '全球通信，高效互联', subSlogan: '为您提供全球优质上网卡及通讯服务' },
    nav: { home: '首页', about: '关于我们', products: '产品中心', contact: '联系我们', login: '后台管理' },
    lang: { label: '语言', zhHK: '繁', zhCN: '简', en: 'EN' },

    home: {
      heroKicker: 'Hong Kong Telecom Distribution Partner',
      heroTitle: '可靠连接，从香港走向全球',
      heroSub: '以中国移动香港相关产品为核心业务基础，灿成通信长期坚持合规经营，连接香港本地分销、零售、电商平台与跨境通信产品资源。',
      heroHighlight: '多年来，公司累计服务数十万名旅客及跨境用户，产品资源覆盖 200+ 国家及地区，主要电商平台客户好评率长期保持 99% 以上，并形成成熟的售前咨询、产品交付及售后服务体系。',
      heroProofMarkets: '200+ 覆盖国家及地区',
      heroProofRating: '99%+ 平台好评率',
      heroBtn: '查看产品资源',
      cooperationBtn: '商务合作查询',
      visualRetail: '零售',
      visualEcom: '电商',
      panelEyebrow: 'Connectivity portfolio',
      panelTitle: '渠道、产品与服务运营',
      panelChannels: '本港及大陆多平台经营',
      proofTitle: '以本地渠道能力，承接跨境通信需求',
      foundationLabel: '运营基础',
      foundationTitle: '以中国移动香港相关产品为核心业务基础',
      foundationDesc: '多年来，灿成通信围绕香港本地通信产品、跨境旅游上网卡及多平台分销，形成成熟的售前咨询、产品交付及售后服务体系。',
      foundationPanelLabel: '运营基础',
      foundationPanelTitle: '从产品资源到渠道交付',
      foundationPanelDesc: '围绕 CMHK 相关产品、本地零售与多平台电商渠道，沉淀可持续的产品咨询、交付与售后能力。',
      showcaseLabel: '核心产品资源',
      showcaseCoreTitle: '5G 18GB中国内地365日数据卡（新版本）',
      showcaseCoreDesc: 'CMHK 相关产品核心代表，面向中国内地跨境通信高频需求。',
      featuredProductsLabel: '核心产品',
      featuredProducts: '核心产品资源',
      featuredProductsDesc: '覆盖本地、内地、亚洲、欧洲及全球漫游等多类通信产品，适配零售、分销与商务出行需求。',
      viewAll: '查看全部',
      price: 'HK$',
      viewDetail: '查看详情',
      capabilitiesLabel: '服务能力',
      capabilitiesTitle: '通信产品渠道与服务能力',
      capabilitiesDesc: '围绕香港本地通信产品、跨境旅游上网卡与多平台分销，提供从产品咨询到交付售后的稳定服务。',
      whyUs: '为什么选择我们',
      why1Title: 'CMHK 产品经营基础',
      why1Desc: '以中国移动香港相关产品为核心业务基础，持续服务香港本地及跨境通信需求。',
      why2Title: '多平台渠道运营',
      why2Desc: '具备香港本地分销、零售及大陆、本港电商多平台经营经验。',
      why3Title: '全球产品资源',
      why3Desc: '产品资源覆盖 200+ 国家及地区，满足旅游、商务与跨境用户通信场景。',
      why4Title: '服务体系沉淀',
      why4Desc: '形成成熟的售前咨询、产品交付及售后服务体系，主要电商平台客户好评率长期保持 99% 以上。',
      stats: { cmhk: '中国移动香港相关产品核心业务基础', customersNumber: '数十万+', customers: '累计服务旅客及跨境用户', countries: '产品资源覆盖国家及地区', products: '产品方案', satisfaction: '主要电商平台客户好评率' },
      partnersLabel: '合作资源',
      partnersTitle: '合作与产品资源',
      partnersDesc: '围绕多家运营商及国际通信产品资源，持续拓展稳定合作。'
    },

    about: {
      title: '关于我们',
      intro: '公司简介',
      introText: '灿成通信贸易有限公司，注册地为中国香港。公司立足香港国际枢纽优势，深耕全球通信行业，与多个国家及地区主流基础运营商达成代理及战略合作。核心合作伙伴包括：香港移动 CMHK、中国联通国际 CUniq（五星级代理商）、柬埔寨 Smart、马尔代夫 Dhiraagu 等知名电信运营商。\n\n主营产品与服务包含：境外储值卡、本地电话卡、全球 eSIM、通信增值券、AI 算力服务等多元化品类，代理业务覆盖全球境外通信资源。\n\n销售渠道全域布局：线下入驻香港鸭寮街实体商圈，线上入驻 HKTVmall 电商平台；同时设立大陆子公司，专业运营国内电商渠道，覆盖飞猪、京东、拼多多等平台，开展批发、分销及零售业务。\n\n公司同步积极布局人工智能领域，拓展 AI 产业链上下游资源与合作机会，实现通信主业与 AI 新业务协同发展。',
      mission: '发展理念',
      missionText: '助力全球通信高效互联',
      values: '核心价值',
      val1Title: '全球合作',
      val1Desc: '与多国主流运营商达成战略合作，覆盖全球通信资源',
      val2Title: '多元服务',
      val2Desc: '境外储值卡、eSIM、AI算力等多元化产品矩阵',
      val3Title: '全渠道',
      val3Desc: '线下实体商圈+线上电商平台，批发分销零售全覆盖',
      val4Title: 'AI 创新',
      val4Desc: '布局人工智能领域，通信主业与 AI 新业务协同发展'
    },

    products: {
      title: '产品中心',
      desc: '探索我们全系列上网卡及数据漫游方案',
      allProducts: '全部产品',
      featured: '精选推荐',
      search: '搜索产品...',
      noProducts: '暂无产品',
      price: 'HK$',
      viewDetail: '查看详情',
      features: '产品特点',
      buyNow: '点击获取批发价',
      backToList: '返回产品列表',
      relatedProducts: '相关产品',
      retailPrice: '建议零售价',
      metaAgent: '官方授权代理商',
      metaDelivery: '即买即发·全港配送',
      metaWhatsApp: 'WhatsApp 实时客服'
    },

    contact: {
      title: '联系我们',
      desc: '如有任何查询，欢迎与我们联系',
      address: '公司地址',
      addressText: '深水埗汝州街 256 号 A 地铺',
      phone: '电话',
      email: '电邮',
      whatsapp: 'WhatsApp',
      businessHours: '营业时间',
      businessHoursText: '周一至周日 上午 10:00 - 下午 6:00\n公众假期休息',
      form: { title: '发送查询', name: '您的姓名', email: '电邮地址', phone: '联系电话', subject: '查询主题',
        message: '查询内容', submit: '提交查询', success: '感谢您的查询，我们会尽快回复！' }
    },

    footer: {
      rights: '版权所有',
      privacy: '隐私政策',
      terms: '服务条款',
      quickLinks: '快速链接',
      contactInfo: '联系信息',
      followUs: '关注我们'
    },

    admin: {
      login: '后台管理登录',
      username: '用户名',
      password: '密码',
      loginBtn: '登录',
      dashboard: '管理仪表板',
      totalProducts: '产品总数',
      activeProducts: '上架产品',
      featuredProducts: '精选产品',
      logout: '退出登录',
      productMgmt: '产品管理',
      addProduct: '新增产品',
      editProduct: '编辑产品',
      edit: '编辑',
      productName: '产品名称（简体）',
      productNameEn: '产品名称（English）',
      productNameCn: '产品名称（繁体）',
      summary: '简介（简体）',
      summaryEn: '简介（English）',
      summaryCn: '简介（繁体）',
      description: '详细描述（简体）',
      descriptionEn: '详细描述（English）',
      descriptionCn: '详细描述（繁体）',
      price: '价格（HKD）',
      image: '产品图片',
      featured: '设为首页推荐',
      active: '上架',
      save: '保存',
      cancel: '取消',
      delete: '删除',
      confirmDelete: '确定要删除此产品吗？',
      noProducts: '暂无产品，请新增产品',
      backToDashboard: '返回仪表板',
      imageHint: '建议尺寸：800x600px，支持 JPG/PNG/GIF',
      existingImage: '目前图片'
    }
  },

  'en': {
    site: { name: 'CCTel', slogan: 'Empowering Global Connectivity', subSlogan: 'Premium global SIM cards and communication services' },
    nav: { home: 'Home', about: 'About Us', products: 'Products', contact: 'Contact', login: 'Admin' },
    lang: { label: 'Language', zhHK: '繁', zhCN: '简', en: 'EN' },

    home: {
      heroKicker: 'Hong Kong Telecom Distribution Partner',
      heroTitle: 'Reliable connectivity, delivered from Hong Kong',
      heroSub: 'Built around China Mobile Hong Kong related products as a core business foundation, CCTel operates with a long-term focus on compliant operations, connecting local Hong Kong distribution, retail, ecommerce platforms, and cross-border telecom product resources.',
      heroHighlight: 'Over the years, we have served hundreds of thousands of travelers and cross-border users. Our product resources cover 200+ countries and regions, with major ecommerce platforms maintaining a long-term 99%+ positive customer rating and a mature pre-sales, fulfillment, and after-sales service process.',
      heroProofMarkets: '200+ countries and regions covered',
      heroProofRating: '99%+ positive platform rating',
      heroBtn: 'View Product Resources',
      cooperationBtn: 'Business Enquiry',
      visualRetail: 'Retail',
      visualEcom: 'Ecommerce',
      panelEyebrow: 'Connectivity portfolio',
      panelTitle: 'Channel, product and service operations',
      panelChannels: 'Hong Kong and Mainland multi-platform operations',
      proofTitle: 'Local channel capability for cross-border connectivity demand',
      foundationLabel: 'Operating Foundation',
      foundationTitle: 'Built on China Mobile Hong Kong related product resources',
      foundationDesc: 'Over the years, CCTel has built mature pre-sales consultation, product fulfillment, and after-sales service capabilities around Hong Kong telecom products, travel SIM cards, and multi-platform distribution.',
      foundationPanelLabel: 'Operating foundation',
      foundationPanelTitle: 'From product resources to channel delivery',
      foundationPanelDesc: 'Built around CMHK-related products, local retail, and multi-platform ecommerce channels, with sustainable consultation, fulfillment, and after-sales capabilities.',
      showcaseLabel: 'Core product resources',
      showcaseCoreTitle: '5G 18GB Mainland China 365-day Data Card (New Version)',
      showcaseCoreDesc: 'A core representative CMHK-related product for high-frequency Mainland China cross-border connectivity needs.',
      featuredProductsLabel: 'Core Products',
      featuredProducts: 'Core Product Resources',
      featuredProductsDesc: 'Local, Mainland China, Asia, Europe, and global roaming products for retail, distribution, and business travel scenarios.',
      viewAll: 'View All',
      price: 'HK$',
      viewDetail: 'View Details',
      capabilitiesLabel: 'Service Capabilities',
      capabilitiesTitle: 'Telecom Channel and Service Capabilities',
      capabilitiesDesc: 'Stable product consultation, fulfillment, and after-sales support around Hong Kong telecom products, travel SIM cards, and multi-platform distribution.',
      whyUs: 'Why Choose Us',
      why1Title: 'CMHK Product Foundation',
      why1Desc: 'Built around China Mobile Hong Kong related products as a core business foundation, serving local Hong Kong and cross-border telecom needs.',
      why2Title: 'Multi-platform Channels',
      why2Desc: 'Experience across Hong Kong local distribution, retail, and ecommerce channels in Hong Kong and Mainland China.',
      why3Title: 'Global Product Resources',
      why3Desc: 'Product resources covering 200+ countries and regions for travel, business, and cross-border connectivity scenarios.',
      why4Title: 'Service Process Maturity',
      why4Desc: 'A mature pre-sales, product fulfillment, and after-sales service process, with major ecommerce platforms maintaining a long-term 99%+ positive customer rating.',
      stats: { cmhk: 'Core foundation in China Mobile Hong Kong related products', customersNumber: '100K+', customers: 'Travelers and cross-border users served', countries: 'Countries and regions covered by product resources', products: 'Product Plans', satisfaction: 'Positive customer rating on major ecommerce platforms' },
      partnersLabel: 'Partner Resources',
      partnersTitle: 'Partners and Product Resources',
      partnersDesc: 'Continuously developing stable cooperation around telecom operators and international connectivity product resources.'
    },

    about: {
      title: 'About Us',
      intro: 'Company Profile',
      introText: 'Can Cheng Communication Trade Limited, registered in Hong Kong, China. Leveraging Hong Kong\'s advantages as an international hub, the company is deeply engaged in the global telecommunications industry, having established agency and strategic partnerships with major carriers across multiple countries and regions. Our core partners include: CMHK, China Unicom International CUniq (Five-Star Agent), Smart Cambodia, Dhiraagu Maldives, and other renowned telecom operators.\n\nOur main products and services include: overseas prepaid SIM cards, local SIM cards, global eSIM, telecom value-added vouchers, AI computing services, and other diversified categories, with our agency business covering global overseas communication resources.\n\nOur sales channels are comprehensively deployed: offline presence in Hong Kong\'s Apliu Street physical retail hub, online presence on the HKTVmall e-commerce platform; simultaneously, we have established a mainland subsidiary specializing in domestic e-commerce channels, covering platforms such as Fliggy, JD.com, and Pinduoduo, engaging in wholesale, distribution, and retail businesses.\n\nThe company is also actively expanding into the artificial intelligence sector, developing resources and partnership opportunities across the AI industry chain, achieving synergistic development between our core communications business and new AI ventures.',
      mission: 'Our Vision',
      missionText: 'Empowering Efficient Global Communication Connectivity',
      values: 'Core Values',
      val1Title: 'Global Partnership',
      val1Desc: 'Strategic partnerships with major global carriers, covering worldwide communication resources',
      val2Title: 'Diversified Services',
      val2Desc: 'Comprehensive product portfolio spanning prepaid SIM, eSIM, and AI computing',
      val3Title: 'Omni-Channel',
      val3Desc: 'Covering offline retail, online e-commerce, wholesale, distribution, and retail',
      val4Title: 'AI Innovation',
      val4Desc: 'Expanding into AI sector, driving synergy between telecom and new AI ventures'
    },

    products: {
      title: 'Products',
      desc: 'Explore our full range of SIM cards and data roaming plans',
      allProducts: 'All Products',
      featured: 'Featured',
      search: 'Search products...',
      noProducts: 'No products available',
      price: 'HK$',
      viewDetail: 'View Details',
      features: 'Features',
      buyNow: 'Get Wholesale Price',
      backToList: 'Back to Products',
      relatedProducts: 'Related Products',
      retailPrice: 'Suggested Retail Price',
      metaAgent: 'Official Authorized Agent',
      metaDelivery: 'Instant Dispatch · HK Wide Delivery',
      metaWhatsApp: 'WhatsApp Live Support'
    },

    contact: {
      title: 'Contact Us',
      desc: 'Feel free to reach out with any inquiries',
      address: 'Address',
      addressText: 'G/F, 256 A Yu Chau Street, Sham Shui Po, Kowloon, Hong Kong',
      phone: 'Phone',
      email: 'Email',
      whatsapp: 'WhatsApp',
      businessHours: 'Business Hours',
      businessHoursText: 'Mon - Sun: 10:00 AM - 6:00 PM\nClosed on Public Holidays',
      form: { title: 'Send Inquiry', name: 'Your Name', email: 'Email Address', phone: 'Phone Number', subject: 'Subject',
        message: 'Message', submit: 'Submit', success: 'Thank you for your inquiry! We will get back to you shortly.' }
    },

    footer: {
      rights: 'All Rights Reserved',
      privacy: 'Privacy Policy',
      terms: 'Terms of Service',
      quickLinks: 'Quick Links',
      contactInfo: 'Contact Info',
      followUs: 'Follow Us'
    },

    admin: {
      login: 'Admin Login',
      username: 'Username',
      password: 'Password',
      loginBtn: 'Login',
      dashboard: 'Dashboard',
      totalProducts: 'Total Products',
      activeProducts: 'Active Products',
      featuredProducts: 'Featured Products',
      logout: 'Logout',
      productMgmt: 'Product Management',
      addProduct: 'Add Product',
      editProduct: 'Edit Product',
      edit: 'Edit',
      productName: 'Product Name (Traditional Chinese)',
      productNameEn: 'Product Name (English)',
      productNameCn: 'Product Name (Simplified Chinese)',
      summary: 'Summary (Traditional Chinese)',
      summaryEn: 'Summary (English)',
      summaryCn: 'Summary (Simplified Chinese)',
      description: 'Description (Traditional Chinese)',
      descriptionEn: 'Description (English)',
      descriptionCn: 'Description (Simplified Chinese)',
      price: 'Price (HKD)',
      image: 'Product Image',
      featured: 'Featured on Homepage',
      active: 'Active',
      save: 'Save',
      cancel: 'Cancel',
      delete: 'Delete',
      confirmDelete: 'Are you sure you want to delete this product?',
      noProducts: 'No products yet. Add your first product.',
      backToDashboard: 'Back to Dashboard',
      imageHint: 'Recommended size: 800x600px, supports JPG/PNG/GIF',
      existingImage: 'Current Image'
    }
  }
};

// 頁面載入時初始化
document.addEventListener('DOMContentLoaded', () => { I18N.init(); });
