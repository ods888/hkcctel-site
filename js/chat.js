/**
 * CCTel AI 智能客服 — 浮窗對話框
 */
(function () {
  'use strict';

  if (document.getElementById('cctel-chat-root')) return;

  // HTML
  var html =
    '<div id="cctel-chat-root" style="position:fixed;bottom:24px;right:24px;z-index:9999;font-family:system-ui,sans-serif;">' +
    '<div id="cctel-chat-bubble" style="width:56px;height:56px;border-radius:50%;background:var(--primary,#165DFF);display:flex;align-items:center;justify-content:center;cursor:pointer;box-shadow:0 4px 16px rgba(22,93,255,0.35);color:#fff;font-size:1.5rem;transition:transform 0.2s;user-select:none;" title="AI客服">' +
    '💬' +
    '</div>' +
    '<div id="cctel-chat-panel" style="display:none;position:absolute;bottom:70px;right:0;width:360px;max-height:520px;background:#fff;border-radius:16px;box-shadow:0 8px 40px rgba(0,0,0,0.15);flex-direction:column;overflow:hidden;">' +
    '<div style="display:flex;align-items:center;justify-content:space-between;padding:14px 18px;background:var(--primary,#165DFF);color:#fff;">' +
    '<div><div style="font-weight:700;font-size:0.95rem;">AI 智能客服</div><div style="font-size:0.72rem;opacity:0.8;">由 DeepSeek 驅動</div></div>' +
    '<div style="display:flex;gap:8px;">' +
    '<button id="cctel-chat-close" style="background:none;border:none;color:#fff;font-size:1.3rem;cursor:pointer;line-height:1;">✕</button>' +
    '</div>' +
    '</div>' +
    '<div id="cctel-chat-messages" style="flex:1;overflow-y:auto;padding:16px;min-height:200px;max-height:340px;background:#f7f8fa;display:flex;flex-direction:column;gap:10px;">' +
    '<div style="display:flex;align-items:flex-start;gap:8px;"><div style="width:32px;height:32px;border-radius:50%;background:var(--primary,#165DFF);display:flex;align-items:center;justify-content:center;color:#fff;font-size:0.7rem;flex-shrink:0;">AI</div><div style="background:#fff;padding:10px 14px;border-radius:12px;border-top-left-radius:2px;font-size:0.85rem;color:#333;line-height:1.5;max-width:260px;">你好！有什麼可以幫你？查產品、問價格、營業時間、地址等都可以問我 😊</div></div>' +
    '</div>' +
    '<div style="display:flex;gap:8px;padding:12px 14px;border-top:1px solid #e5e7eb;background:#fff;">' +
    '<input id="cctel-chat-input" type="text" placeholder="輸入問題..." style="flex:1;border:1px solid #e5e7eb;border-radius:20px;padding:8px 16px;font-size:0.85rem;outline:none;" maxlength="300">' +
    '<button id="cctel-chat-send" style="width:36px;height:36px;border-radius:50%;background:var(--primary,#165DFF);color:#fff;border:none;font-size:1rem;cursor:pointer;flex-shrink:0;display:flex;align-items:center;justify-content:center;">➤</button>' +
    '</div>' +
    '</div>' +
    '</div>';

  document.body.insertAdjacentHTML('beforeend', html);

  var panel = document.getElementById('cctel-chat-panel');
  var bubble = document.getElementById('cctel-chat-bubble');
  var messages = document.getElementById('cctel-chat-messages');
  var input = document.getElementById('cctel-chat-input');
  var sendBtn = document.getElementById('cctel-chat-send');
  var closeBtn = document.getElementById('cctel-chat-close');
  var isOpen = false;
  var loading = false;

  function toggle() {
    isOpen = !isOpen;
    panel.style.display = isOpen ? 'flex' : 'none';
    if (isOpen) input.focus();
  }

  bubble.addEventListener('click', toggle);
  closeBtn.addEventListener('click', function () { isOpen = false; panel.style.display = 'none'; });

  function addMessage(text, isUser) {
    var div = document.createElement('div');
    div.style.display = 'flex';
    div.style.alignItems = 'flex-start';
    div.style.gap = '8px';
    if (isUser) div.style.justifyContent = 'flex-end';
    var avatar = isUser ? '👤' : 'AI';
    var bg = isUser ? '#165DFF' : 'var(--primary,#165DFF)';
    var msgBg = isUser ? '#165DFF' : '#fff';
    var msgColor = isUser ? '#fff' : '#333';
    var borderRadius = isUser ? '12px 12px 2px 12px' : '12px 12px 12px 2px';
    div.innerHTML =
      (isUser ? '' : '<div style="width:32px;height:32px;border-radius:50%;background:' + bg + ';display:flex;align-items:center;justify-content:center;color:#fff;font-size:0.7rem;flex-shrink:0;">' + avatar + '</div>') +
      '<div style="padding:10px 14px;border-radius:' + borderRadius + ';font-size:0.85rem;color:' + msgColor + ';line-height:1.5;max-width:260px;background:' + msgBg + ';word-break:break-word;">' + escapeHtmlChat(text) + '</div>' +
      (isUser ? '<div style="width:32px;height:32px;border-radius:50%;background:#10b981;display:flex;align-items:center;justify-content:center;color:#fff;font-size:0.8rem;flex-shrink:0;">' + avatar + '</div>' : '');
    messages.appendChild(div);
    messages.scrollTop = messages.scrollHeight;
  }

  function addTyping() {
    var div = document.createElement('div');
    div.id = 'cctel-typing';
    div.style.display = 'flex';
    div.style.alignItems = 'flex-start';
    div.style.gap = '8px';
    div.innerHTML =
      '<div style="width:32px;height:32px;border-radius:50%;background:var(--primary,#165DFF);display:flex;align-items:center;justify-content:center;color:#fff;font-size:0.7rem;flex-shrink:0;">AI</div>' +
      '<div style="background:#fff;padding:12px 16px;border-radius:12px;border-top-left-radius:2px;"><span style="display:inline-block;width:6px;height:6px;border-radius:50%;background:#ccc;animation:cctel-typing 1.3s infinite;"></span> <span style="display:inline-block;width:6px;height:6px;border-radius:50%;background:#ccc;animation:cctel-typing 1.3s infinite 0.2s;"></span> <span style="display:inline-block;width:6px;height:6px;border-radius:50%;background:#ccc;animation:cctel-typing 1.3s infinite 0.4s;"></span></div>';
    messages.appendChild(div);
    messages.scrollTop = messages.scrollHeight;
  }

  function removeTyping() {
    var el = document.getElementById('cctel-typing');
    if (el) el.remove();
  }

  var styleEl = document.createElement('style');
  styleEl.textContent = '@keyframes cctel-typing{0%,60%,100%{opacity:0.2;transform:translateY(0)}30%{opacity:1;transform:translateY(-4px)}}';
  document.head.appendChild(styleEl);

  function escapeHtmlChat(text) {
    var div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML.replace(/\n/g, '<br>');
  }

  async function sendMessage() {
    var text = input.value.trim();
    if (!text || loading) return;
    loading = true;
    input.value = '';
    addMessage(text, true);
    addTyping();
    setTimeout(function() {
      removeTyping();
      addMessage('AI 客服暂未开通，如需查询产品或批发价格，请 WhatsApp +852 92445678 或亲临深水埗汝州街 256 号 A 地铺。', false);
      loading = false;
    }, 800);
  }

  sendBtn.addEventListener('click', sendMessage);
  input.addEventListener('keydown', function (e) {
    if (e.key === 'Enter') { e.preventDefault(); sendMessage(); }
  });
})();
