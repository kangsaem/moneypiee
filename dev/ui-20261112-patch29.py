import sys
fn=sys.argv[1]; s=open(fn,encoding='utf-8').read()
a="const MP_SNAP_ON = true;"
assert s.count(a)==1
s=s.replace(a,"""// 휴대폰: 화면을 좌우로 쓸면 옆 탭으로(자산 ↔ 월별 ↔ 관심 ↔ V1 ↔ 관리) — 2026-11-12 사용자
// 가로로 넘기는 영역(지표 줄·계좌 버튼 줄·월별 그래프·표)과 팝업 위에서 시작한 쓸기는 제외. 계좌 탭·마통 탭에서는 동작 안 함
(function(){
  let x0 = 0, y0 = 0, t0 = 0, ok = false;
  const blocked = el => { for(let n = el; n && n.nodeType === 1 && n !== document.body; n = n.parentElement){
    if(n.id === 'marketTicker' || n.id === 'tabs' || (n.classList && n.classList.contains('trend-wrap'))) return true;
    const cs = getComputedStyle(n); if(cs.position === 'fixed') return true;
    if(/(auto|scroll)/.test(cs.overflowX) && n.scrollWidth > n.clientWidth + 2) return true; } return false; };
  document.addEventListener('touchstart', e => {
    ok = false; try{ if(e.touches.length !== 1 || !donutCarOn() || blocked(e.target)) return; }catch(err){ return; }
    ok = true; x0 = e.touches[0].clientX; y0 = e.touches[0].clientY; t0 = Date.now();
  }, { passive: true });
  document.addEventListener('touchmove', e => { if(e.touches.length > 1) ok = false; }, { passive: true });
  document.addEventListener('touchend', e => {
    if(!ok) return; ok = false;
    const t = e.changedTouches[0], dx = t.clientX - x0, dy = t.clientY - y0;
    if(Math.abs(dx) < 70 || Math.abs(dx) < Math.abs(dy) * 2 || Date.now() - t0 > 700) return;
    try{
      const order = ['__total__', '__history__', WATCHLIST_ID, '__analysis__', '__deleteAccounts__'];
      const cur = ['__total__', '__domestic__', '__overseas__'].includes(state.activeId) ? 0 : order.indexOf(state.activeId);
      const nx = cur + (dx < 0 ? 1 : -1); if(cur < 0 || nx < 0 || nx >= order.length) return;
      switchTab(order[nx]);
    }catch(err){}
  }, { passive: true });
})();
const MP_SNAP_ON = true;""")
open(fn,'w',encoding='utf-8').write(s); print('ok')
