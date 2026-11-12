import sys
fn=sys.argv[1]; s=open(fn,encoding='utf-8').read()
def rep(a,b,cnt=1):
    global s
    n=s.count(a); assert n==cnt,(fn,a[:70],n); s=s.replace(a,b)
rep("""  .trend-wrap{margin-top:8px;}
""","""  .trend-wrap{margin-top:8px;}
  /* 2026-11-12 사용자: PC에서도 가로 스크롤바 숨김(지표 줄·계좌 버튼 줄·유형 버튼 줄·월별 그래프). PC는 마우스로 끌어서 넘김 */
  #marketTicker, #accountBtnSelector, #historyAccSelector, #historyAccTypeSelector, .trend-scroll, .typeleg{scrollbar-width:none;-ms-overflow-style:none;}
  #marketTicker::-webkit-scrollbar, #accountBtnSelector::-webkit-scrollbar, #historyAccSelector::-webkit-scrollbar, #historyAccTypeSelector::-webkit-scrollbar, .trend-scroll::-webkit-scrollbar, .typeleg::-webkit-scrollbar{display:none;}
""")
rep("""const MP_SNAP_ON = true;""","""// 가로 스크롤바를 숨긴 줄: PC에서는 마우스로 잡아 끌어 넘김(끌었으면 그 클릭은 무시)
(function(){
  const SEL = '#marketTicker, #accountBtnSelector, #historyAccSelector, #historyAccTypeSelector, .trend-scroll, .typeleg';
  let el = null, x0 = 0, s0 = 0, moved = false;
  document.addEventListener('mousedown', e => { if(e.button !== 0) return; const t = e.target.closest && e.target.closest(SEL); if(!t || t.scrollWidth <= t.clientWidth + 1) return; el = t; x0 = e.clientX; s0 = t.scrollLeft; moved = false; });
  document.addEventListener('mousemove', e => { if(!el) return; const dx = e.clientX - x0; if(!moved && Math.abs(dx) < 5) return; moved = true; el.scrollLeft = s0 - dx; e.preventDefault(); });
  document.addEventListener('mouseup', () => { if(el && moved){ const stop = ev => { ev.stopPropagation(); ev.preventDefault(); }; document.addEventListener('click', stop, { capture: true, once: true }); setTimeout(() => document.removeEventListener('click', stop, true), 50); } el = null; });
})();
const MP_SNAP_ON = true;""")
open(fn,'w',encoding='utf-8').write(s); print('ok')
