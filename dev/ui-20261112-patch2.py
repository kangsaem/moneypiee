import sys
fn=sys.argv[1]; s=open(fn,encoding='utf-8').read()
def rep(a,b,cnt=1):
    global s
    n=s.count(a); assert n==cnt,(fn,a[:70],n); s=s.replace(a,b)
# 섹터 줄에 섹터 색 표시
rep("""html += `<div class="sec-head" data-sec-fold="${escapeHTML(k)}"><span class="sec-nm">""",
    """html += `<div class="sec-head" data-sec-fold="${escapeHTML(k)}"><span class="swatch" style="background:${stockSecColorNow[k] || CASH_COLOR}"></span><span class="sec-nm">""")
rep("""  const secW = reorderCashFirst(computeWeights(holdings, 'group')), secColor = {};""",
    """  const secW = reorderCashFirst(computeWeights(holdings, 'group')), secColor = {};
  stockSecColorNow = secColor;""")
rep("""let stockSectorOpen = {};          // 섹터순에서 펼친 섹터(처음엔 모두 접힘)""",
    """let stockSectorOpen = {};          // 섹터순에서 펼친 섹터(처음엔 모두 접힘)
let stockSecColorNow = {};         // 지금 그린 도넛의 섹터 색(목록 섹터 줄의 색 네모와 같게)""")
# 화면맞춤
rep("""  #stock-sortable-chart [data-u]{transition:opacity .22s;}""",
    """  #mpSnapDn{position:fixed;left:50%;bottom:calc(6px + env(safe-area-inset-bottom, 0px));transform:translateX(-50%);width:56px;height:30px;display:none;align-items:center;justify-content:center;font-size:15px;color:var(--text-dim);background:rgba(40,41,45,.82);border-radius:15px;z-index:40;cursor:pointer;user-select:none;-webkit-tap-highlight-color:transparent;}
  #mpSnapDn.on{display:flex;}
  #stock-sortable-chart [data-u]{transition:opacity .22s;}""")
rep("""  const ch = panel.querySelector('.charts'); if(!ch || ch.classList.contains('dn-car')) return;""",
    """  try{ mpSnapLayout(); }catch(e){}
  const ch = panel.querySelector('.charts'); if(!ch || ch.classList.contains('dn-car')) return;""")
rep("""const DONUT_ONE = true;            // 도넛 하나로 통일""","""// ── 휴대폰 화면맞춤(2026-11-12 사용자) ─────────────────────────────────────────
// 자산 탭 첫 화면은 지표~도넛이 한 화면에 딱 맞고 아래 ▼. ▼를 누르거나 위로 끌면 단계별로 내려감(탭 아래가 맨 위로 → 목록 끝).
// 손가락을 따라 흘러가는 스크롤 대신 단계 사이를 애니메이션으로 이동. PC와 다른 탭은 예전 그대로.
const MP_SNAP_ON = true;
let mpSnapAnim = false;
function mpSnapActive(){
  try{ return MP_SNAP_ON && donutCarOn() && ['__total__', '__domestic__', '__overseas__'].includes(state.activeId) && !!document.getElementById('stock-sortable-chart'); }catch(e){ return false; }
}
function mpSnapStages(){
  const H = window.innerHeight, panel = document.getElementById('panel');
  const end = Math.max(0, Math.round(document.documentElement.scrollHeight - H));
  const a = [0]; if(end < 8) return a;
  const y1 = panel ? Math.max(0, Math.round(panel.getBoundingClientRect().top + window.scrollY) - 4) : 0;
  if(y1 > 8 && y1 < end - 8){ a.push(y1); const step = Math.max(200, H - 90); for(let y = y1 + step; y < end - 60; y += step) a.push(y); }
  a.push(end); return a;
}
function mpSnapBtn(){
  let b = document.getElementById('mpSnapDn');
  if(!b){ b = document.createElement('div'); b.id = 'mpSnapDn'; b.textContent = '▼'; b.setAttribute('aria-label', '아래로'); document.body.appendChild(b); b.addEventListener('click', e => { e.stopPropagation(); mpSnapGo(1); }); }
  return b;
}
function mpSnapArrow(){
  const b = mpSnapBtn(); if(!mpSnapActive()){ b.classList.remove('on'); return; }
  const st = mpSnapStages(); b.classList.toggle('on', window.scrollY < st[st.length - 1] - 8);
}
function mpSnapGo(dir){
  if(mpSnapAnim) return;
  const st = mpSnapStages(), cur = window.scrollY;
  const to = dir > 0 ? st.find(y => y > cur + 8) : st.slice().reverse().find(y => y < cur - 8);
  if(to == null) return;
  const t0 = performance.now(), D = 460; mpSnapAnim = true;
  const tick = now => { const t = Math.min(1, (now - t0) / D), e = 1 - Math.pow(1 - t, 4);   // 처음에 세게, 끝에서 천천히
    window.scrollTo(0, cur + (to - cur) * e);
    if(t < 1) requestAnimationFrame(tick); else { mpSnapAnim = false; mpSnapArrow(); } };
  requestAnimationFrame(tick);
}
// 첫 화면 맞춤: 도넛이 화면 아래 끝(▼ 자리 위)에 딱 맞게 크기·여백을 정하고, 탭 아래가 맨 위에 붙을 만큼 길이를 확보
function mpSnapLayout(){
  const on = mpSnapActive(), panel = document.getElementById('panel');
  const box = document.getElementById('stock-sortable-chart'), dw = box && box.querySelector('.donut-wrap');
  if(dw){ dw.style.width = dw.style.height = dw.style.marginTop = dw.style.marginBottom = ''; }
  if(panel && panel.dataset.snapMin){ panel.style.minHeight = ''; delete panel.dataset.snapMin; }
  if(!on || !dw || !panel){ mpSnapArrow(); return; }
  const H = window.innerHeight, ARW = 40, r = dw.getBoundingClientRect(), top = r.top + window.scrollY;
  const size = Math.round(Math.max(150, Math.min(H - top - ARW, r.height * 1.25, (box.clientWidth || 300) - 24)));
  const spare = Math.max(0, H - ARW - top - size);
  dw.style.width = dw.style.height = size + 'px';
  dw.style.marginTop = Math.floor(spare / 2) + 'px'; dw.style.marginBottom = (Math.ceil(spare / 2) + ARW) + 'px';
  const wrap = document.querySelector('.wrap'), pr = panel.getBoundingClientRect();
  const below = wrap ? Math.max(0, wrap.getBoundingClientRect().bottom - pr.bottom) : 0, need = Math.ceil(H - below + 4);
  if(pr.height < need){ panel.dataset.snapMin = '1'; panel.style.minHeight = need + 'px'; const h2 = panel.getBoundingClientRect().height; if(h2 > need + 1) panel.style.minHeight = Math.max(0, need - (h2 - need)) + 'px'; }
  mpSnapArrow();
}
(function(){
  let sx = 0, sy = 0, mode = -1;   // -1 = 관여 안 함, 0 = 방향 판정 전, 1 = 세로 단계 이동
  // 안에서 따로 스크롤되는 곳(팝업·창)은 건드리지 않음
  const own = el => { for(let n = el; n && n.nodeType === 1 && n !== document.body; n = n.parentElement){
    const cs = getComputedStyle(n); if(cs.position === 'fixed') return true;
    if(/(auto|scroll)/.test(cs.overflowY) && n.scrollHeight > n.clientHeight + 2) return true; } return false; };
  document.addEventListener('touchstart', e => {
    mode = (e.touches.length === 1 && mpSnapActive() && !own(e.target)) ? 0 : -1;
    if(mode === 0){ sx = e.touches[0].clientX; sy = e.touches[0].clientY; }
  }, { passive: true });
  document.addEventListener('touchmove', e => {
    if(mode === -1) return;
    const dx = e.touches[0].clientX - sx, dy = e.touches[0].clientY - sy;
    if(mode === 0){
      if(Math.abs(dx) < 3 && Math.abs(dy) < 3) return;
      if(Math.abs(dy) <= Math.abs(dx)){ mode = -1; return; }          // 가로 끌기(지표 카드 넘기기 등)는 그대로
      if(dy > 0 && window.scrollY <= 0){ mode = -1; return; }         // 맨 위에서 아래로 당기기(새로고침)는 그대로
      mode = 1;
    }
    if(e.cancelable) e.preventDefault(); else mode = -1;
  }, { passive: false });
  const end = e => { if(mode === 1){ const dy = e.changedTouches[0].clientY - sy; if(Math.abs(dy) >= 24) mpSnapGo(dy < 0 ? 1 : -1); } mode = -1; };
  document.addEventListener('touchend', end, { passive: true });
  document.addEventListener('touchcancel', () => { mode = -1; }, { passive: true });
  window.addEventListener('scroll', () => { if(!mpSnapAnim) mpSnapArrow(); }, { passive: true });
  window.addEventListener('resize', () => { try{ mpSnapLayout(); }catch(e){} });
  window.addEventListener('mp-fold-done', () => { try{ mpSnapArrow(); }catch(e){} });
})();
const DONUT_ONE = true;            // 도넛 하나로 통일""")
open(fn,'w',encoding='utf-8').write(s); print('ok',fn)
