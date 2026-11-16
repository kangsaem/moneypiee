import sys
p = sys.argv[1]; s = open(p, encoding='utf-8').read()
def rep(a, b, cnt=1):
    global s
    assert s.count(a) == cnt, (a[:70], s.count(a)); s = s.replace(a, b)
rep("""        <div id="stock-history-chart-${key}" style="min-height:94px;display:flex;align-items:center;justify-content:center;">
          <div style="font-size:11px;color:#777777;">그래프 불러오는 중...</div>
        </div>""", """        <div style="position:relative;">
        <div id="stock-history-chart-${key}" style="min-height:94px;display:flex;align-items:center;justify-content:center;">
          <div style="font-size:11px;color:#777777;">그래프 불러오는 중...</div>
        </div>
        ${!isCashHolding(h) ? `<button type="button" data-stock-history-v1 style="position:absolute;left:50%;top:50%;transform:translate(-50%,-50%);width:42px;border:1px solid #333333;background:#333333;color:#FFFFFF;border-radius:4px;padding:3px 2px;font-size:10px;font-family:inherit;font-weight:700;cursor:pointer;line-height:1.15;">V1</button>` : ''}
        </div>""")
rep("""    if(e.target.closest('[data-stock-history-close]')){
      closeStockHistoryAccordion(key);
      return;
    }""", """    if(e.target.closest('[data-stock-history-close]')){
      closeStockHistoryAccordion(key);
      return;
    }
    if(e.target.closest('[data-stock-history-v1]')){            // V1 탭의 이 종목으로(돋보기도 같이 돌림, 2026-11-16)
      const hv = findHoldingById(stockHistoryAccordions[key].accId, stockHistoryAccordions[key].holdId);
      closeStockHistoryAccordion(key);
      if(hv) anGoV1(hv);
      return;
    }""")
rep("""function anFillRoot(){""", """// 자산 탭 종목 팝업의 V1 버튼(2026-11-16): V1 탭으로 가서 돋보기를 돌리고, 그 종목 카드를 펼쳐 그 자리로 스크롤 + 잠깐 테두리 강조
async function anGoV1(h){
  const find = () => { const rs = (anState.result && anState.result.results) || [];
    return rs.find(r => r.hname === h.name) || (h.symbol ? rs.find(r => r.code === h.symbol || r.code === String(h.symbol).replace(/\\.(KS|KQ)$/i, '')) : null) || rs.find(r => r.name === h.name) || null; };
  let moved = false;
  window.addEventListener('wheel', () => { moved = true; }, { once: true, passive: true });
  window.addEventListener('touchmove', () => { moved = true; }, { once: true, passive: true });
  const open = (flash) => {
    const r = find(); if(!r) return false;
    const k = 'd:' + r.code, root = document.getElementById('analysisRoot'); if(!root) return false;
    anState.openKeys.add(k);
    let det = [...root.querySelectorAll('details[data-an-key]')].find(d => d.dataset.anKey === k);
    if(!det){ anState.html = null; anFillRoot(); det = [...root.querySelectorAll('details[data-an-key]')].find(d => d.dataset.anKey === k); }
    if(!det) return false;
    for(let p = det.parentElement && det.parentElement.closest('details'); p; p = p.parentElement && p.parentElement.closest('details')){ if(!p.open){ p.open = true; if(p.dataset.anKey) anState.openKeys.add(p.dataset.anKey); } }
    if(!det.open) det.open = true;
    if(flash){
      requestAnimationFrame(() => {
        const hold = document.getElementById('mktHold'), off = hold ? Math.max(0, hold.getBoundingClientRect().bottom) : 0;
        window.scrollTo({ top: window.scrollY + det.getBoundingClientRect().top - off - 8, behavior: 'smooth' });
        det.style.transition = 'box-shadow .3s'; det.style.boxShadow = '0 0 0 2px #D4FF3D';
        setTimeout(() => { det.style.boxShadow = ''; setTimeout(() => { det.style.transition = ''; }, 400); }, 1600);
      });
    }
    return true;
  };
  anState.view = 'report';
  if(anState.filter) anState.filter = '';
  anState.html = null;
  switchTab('__analysis__');
  const run = runAnalysis();
  try{ loadMarketData(true).catch(() => {}); }catch(e){}
  await new Promise(r => requestAnimationFrame(() => requestAnimationFrame(r)));
  const first = open(true);
  try{ await run; }catch(e){}
  if(state.activeId !== '__analysis__') return;
  open(!first && !moved);                                     // 처음엔 결과에 없던 종목이면 분석 뒤 그 자리로
}

function anFillRoot(){""")
open(p, 'w', encoding='utf-8').write(s)
