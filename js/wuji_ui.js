// 工坊提示词 · 前端扩展：为所有提示词输入框添加「提示词优化 / 翻译」按钮
import { app } from '../../scripts/app.js';

const SVG_OPTIMIZE = "<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' fill='none' stroke='currentColor' stroke-width='2' stroke-linecap='round' stroke-linejoin='round'><path d='m21.64 3.64-1.28-1.28a1.21 1.21 0 0 0-1.72 0L2.36 18.64a1.21 1.21 0 0 0 0 1.72l1.28 1.28a1.2 1.2 0 0 0 1.72 0L21.64 5.36a1.2 1.2 0 0 0 0-1.72Z'/><path d='m14 7 3 3'/><path d='M5 6v4'/><path d='M19 14v4'/><path d='M10 2v2'/><path d='M7 8H3'/><path d='M21 16h-4'/><path d='M11 3H9'/></svg>";

const SVG_TRANSLATE = "<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' fill='none' stroke='currentColor' stroke-width='2' stroke-linecap='round' stroke-linejoin='round'><path d='m5 8 6 6'/><path d='m4 14 6-6 2-3'/><path d='M2 5h12'/><path d='M7 2h1'/><path d='m22 22-5-10-5 10'/><path d='M14 18h6'/></svg>";

const processed = new WeakSet();
let toastEl = null;
let toastTimer = null;
let scanTimer = null;

function log() {
  try { console.log('[WujiNodes]', Array.prototype.slice.call(arguments).join(' ')); } catch (e) {}
}

function showToast(message, isError) {
  if (!toastEl) {
    toastEl = document.createElement('div');
    toastEl.className = 'wuji-toast';
    document.body.appendChild(toastEl);
  }
  toastEl.textContent = message;
  toastEl.className = 'wuji-toast wuji-visible' + (isError ? ' wuji-error' : '');
  clearTimeout(toastTimer);
  toastTimer = setTimeout(function () { toastEl.classList.remove('wuji-visible'); }, 2600);
}

function setLoading(btn, loading) {
  if (!btn) return;
  if (loading) { btn.classList.add('wuji-loading'); btn.disabled = true; }
  else { btn.classList.remove('wuji-loading'); btn.disabled = false; }
}

function getValue(ta) {
  if (!ta) return '';
  if (ta.tagName === 'TEXTAREA') return ta.value || '';
  return ta.textContent || '';
}

function setValue(ta, val) {
  if (!ta) return;
  if (ta.tagName === 'TEXTAREA') { ta.value = val; }
  else { ta.textContent = val; }
  ta.dispatchEvent(new Event('input', { bubbles: true }));
}

async function runAction(textarea, btn, type) {
  const text = getValue(textarea).trim();
  if (!text) { showToast('输入框为空', true); return; }
  const endpoint = type === 'optimize' ? '/wuji/optimize_prompt' : '/wuji/translate';
  const failMsg = type === 'optimize' ? '优化失败，请重试' : '翻译失败，请重试';
  setLoading(btn, true);
  try {
    const resp = await fetch(endpoint, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ text: text })
    });
    const data = await resp.json();
    if (data && data.success && data.text) { setValue(textarea, data.text); }
    else { showToast(failMsg, true); }
  } catch (e) {
    showToast(failMsg, true);
  } finally {
    setLoading(btn, false);
  }
}

function bindTooltip(btn) {
  let tip = null;
  let showTimer = null;
  btn.addEventListener('mouseenter', function () {
    clearTimeout(showTimer);
    showTimer = setTimeout(function () {
      if (!tip) {
        tip = document.createElement('div');
        tip.className = 'wuji-tooltip';
        tip.textContent = btn.getAttribute('data-tip');
        btn.appendChild(tip);
      }
      requestAnimationFrame(function () { tip.classList.add('wuji-visible'); });
    }, 300);
  });
  btn.addEventListener('mouseleave', function () {
    clearTimeout(showTimer);
    if (tip) {
      tip.classList.remove('wuji-visible');
      setTimeout(function () {
        if (tip && tip.parentNode) tip.parentNode.removeChild(tip);
        tip = null;
      }, 200);
    }
  });
}

function buildToolbar(textarea) {
  const bar = document.createElement('div');
  bar.className = 'wuji-toolbar';
  const btnO = document.createElement('button');
  btnO.type = 'button';
  btnO.className = 'wuji-btn';
  btnO.setAttribute('data-tip', '提示词优化');
  btnO.innerHTML = SVG_OPTIMIZE;
  const btnT = document.createElement('button');
  btnT.type = 'button';
  btnT.className = 'wuji-btn';
  btnT.setAttribute('data-tip', '翻译');
  btnT.innerHTML = SVG_TRANSLATE;
  bar.appendChild(btnO);
  bar.appendChild(btnT);
  bindTooltip(btnO);
  bindTooltip(btnT);
  btnO.addEventListener('click', function () { runAction(textarea, btnO, 'optimize'); });
  btnT.addEventListener('click', function () { runAction(textarea, btnT, 'translate'); });
  return bar;
}

function injectToTextarea(textarea) {
  if (processed.has(textarea)) return;
  if (!textarea.parentNode) return;
  processed.add(textarea);
  const parent = textarea.parentNode;
  // 让按钮能绝对定位到输入框内部右侧：将父容器设为定位上下文（不改变布局）
  if (getComputedStyle(parent).position === 'static') {
    parent.style.position = 'relative';
  }
  // 输入框右侧预留空白，避免文字与按钮组重叠
  textarea.classList.add('wuji-textarea');
  const bar = buildToolbar(textarea);
  parent.insertBefore(bar, textarea.nextSibling);
}

function scanAndInject() {
  let count = 0;
  document.querySelectorAll('textarea').forEach(function (ta) {
    if (processed.has(ta)) return;
    injectToTextarea(ta);
    count += 1;
  });
  return count;
}

function scheduleScan() {
  clearTimeout(scanTimer);
  scanTimer = setTimeout(function () {
    const n = scanAndInject();
    if (n > 0) log('已注入按钮到', n, '个输入框');
  }, 300);
}

function isEditable(el) {
  return !!el && (el.tagName === 'TEXTAREA' || el.isContentEditable);
}

function setupShortcuts() {
  document.addEventListener('keydown', function (e) {
    if (!(e.ctrlKey && e.shiftKey)) return;
    const active = document.activeElement;
    if (!isEditable(active)) return;
    const key = (e.key || '').toLowerCase();
    if (key === 'o') { e.preventDefault(); runAction(active, null, 'optimize'); }
    else if (key === 't') { e.preventDefault(); runAction(active, null, 'translate'); }
  });
}

function injectCss() {
  try {
    const url = new URL('./wuji_styles.css', import.meta.url);
    const link = document.createElement('link');
    link.rel = 'stylesheet';
    link.type = 'text/css';
    link.href = url.toString();
    document.head.appendChild(link);
  } catch (e) { log('CSS 注入失败', e); }
}

app.registerExtension({
  name: 'Wuji.Nodes.UI',
  async setup() {
    log('扩展已加载');
    injectCss();
    setupShortcuts();
    scheduleScan();
    const observer = new MutationObserver(scheduleScan);
    observer.observe(document.body, { childList: true, subtree: true });
    log('监听已启动，等待输入框渲染');
  }
});
