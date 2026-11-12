import sys
fn=sys.argv[1]; s=open(fn,encoding='utf-8').read()
def rep(a,b):
    global s
    assert s.count(a)==1,(fn,a[:60]); s=s.replace(a,b)
rep("""  el.innerHTML = cards;
  // 코스피·코스닥 카드: 50일 이격도·RSI 한 줄 (기간 탭과 무관하게 항상 일봉 기준)
  Object.keys(MKT_IND_SPECS).forEach(key => {
    const card = el.querySelector(`.mkt-card[data-mktkey="${key}"]`);
    const line = mktIndicatorLine(key);
    if(card && line) card.insertAdjacentHTML('beforeend', line);
  });
  el.querySelectorAll('.mkt-card[data-mktkey]').forEach(card => {
    card.addEventListener('click', () => cycleMarketRange(card.dataset.mktkey));
  });
}""","""  const sl0 = el.scrollLeft;
  el.innerHTML = cards;
  // 코스피·코스닥 카드: 50일 이격도·RSI 한 줄 (기간 탭과 무관하게 항상 일봉 기준)
  Object.keys(MKT_IND_SPECS).forEach(key => {
    const card = el.querySelector(`.mkt-card[data-mktkey="${key}"]`);
    const line = mktIndicatorLine(key);
    if(card && line) card.insertAdjacentHTML('beforeend', line);
  });
  if(mktLoopActive()){ const one = el.innerHTML; el.innerHTML = one + one + one; el.scrollLeft = sl0; mktLoopWrap(true); }   // 휴대폰: 같은 카드 묶음 3벌(끝없이 이어지게)
  el.querySelectorAll('.mkt-card[data-mktkey]').forEach(card => {
    card.addEventListener('click', () => { mktLoopPause(); cycleMarketRange(card.dataset.mktkey); });
  });
}
// ── 휴대폰: 지표 카드 줄이 끝없이 이어지며 천천히 흘러감(2026-11-13 사용자) ──────────────────
// 같은 카드 묶음 3벌을 붙여 두고 가운데 묶음 근처를 유지(벗어나면 한 묶음 폭만큼 몰래 되돌림). 손으로 끌거나 누르면 10초 멈춘 뒤 다시 흐름
const MKT_LOOP = true, MKT_LOOP_SPEED = 16, MKT_LOOP_PAUSE = 10000;   // px/초, 멈춤 ms
let mktLoopPauseUntil = 0, mktLoopTouch = false, mktLoopPos = -1, mktLoopSet = -1, mktLoopUserAt = 0;
function mktLoopActive(){ try{ return MKT_LOOP && donutCarOn(); }catch(e){ return false; } }
function mktLoopPause(){ mktLoopPauseUntil = Date.now() + MKT_LOOP_PAUSE; }
function mktLoopSetW(el){ const cs = el.querySelectorAll(':scope > .mkt-card'), n = MARKET_SYMBOLS.length; return cs.length >= 2 * n ? cs[n].offsetLeft - cs[0].offsetLeft : 0; }
function mktLoopWrap(force){
  const el = document.getElementById('marketTicker'); if(!el) return;
  const w = mktLoopSetW(el); if(!(w > 0)) return;
  let x = el.scrollLeft;
  if(x < w * 0.5) x += w; else if(x >= w * 1.5) x -= w; else if(!force) return;
  mktLoopSet = el.scrollLeft = x; mktLoopPos = x;
}
(function(){
  let last = 0;
  const tick = now => {
    requestAnimationFrame(tick);
    const dt = last ? Math.min(100, now - last) : 0; last = now;
    if(!mktLoopActive() || document.hidden) return;
    const el = document.getElementById('marketTicker'); if(!el || el.scrollWidth <= el.clientWidth + 2) return;
    if(mktLoopTouch || Date.now() < mktLoopPauseUntil){ return; }
    if(Date.now() - mktLoopUserAt < 250) return;              // 손을 뗀 뒤 관성 스크롤이 끝날 때까지
    if(mktLoopPos < 0 || Math.abs(el.scrollLeft - mktLoopSet) > 2) mktLoopPos = el.scrollLeft;   // 다른 이유로 움직였으면 거기서부터
    mktLoopPos += MKT_LOOP_SPEED * dt / 1000;
    el.scrollLeft = mktLoopPos; mktLoopSet = el.scrollLeft;
    const w = mktLoopSetW(el); if(w > 0 && mktLoopPos >= w * 1.5){ mktLoopPos -= w; el.scrollLeft = mktLoopPos; mktLoopSet = el.scrollLeft; }
  };
  requestAnimationFrame(tick);
  document.addEventListener('DOMContentLoaded', () => {
    const el = document.getElementById('marketTicker'); if(!el) return;
    el.addEventListener('touchstart', () => { mktLoopTouch = true; mktLoopPause(); }, { passive: true });
    const up = () => { mktLoopTouch = false; mktLoopPause(); mktLoopUserAt = Date.now(); };
    el.addEventListener('touchend', up, { passive: true }); el.addEventListener('touchcancel', up, { passive: true });
    let idle = 0;
    el.addEventListener('scroll', () => {
      if(Math.abs(el.scrollLeft - mktLoopSet) <= 2) return;   // 자동으로 흘린 것
      mktLoopUserAt = Date.now(); mktLoopPause();
      clearTimeout(idle); idle = setTimeout(() => { if(!mktLoopTouch) mktLoopWrap(false); }, 180);   // 손으로 넘긴 뒤 멈추면 가운데 묶음 쪽으로 되돌림(보이는 모습은 같음)
    }, { passive: true });
  });
})();""")
open(fn,'w',encoding='utf-8').write(s); print('ok',fn)
