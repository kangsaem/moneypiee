import sys
p = sys.argv[1]; s = open(p, encoding='utf-8').read()
def rep(a, b, cnt=1):
    global s
    assert s.count(a) == cnt, (a[:70], s.count(a)); s = s.replace(a, b)
rep("""function stockHistoryInitialPosition(triggerEl){
  const width = 240;
  const height = 210;
  if(triggerEl){
    const rect = triggerEl.getBoundingClientRect();
    const left = Math.max(8, Math.min(window.innerWidth - width - 8, rect.left));
    const top = Math.max(8, Math.min(window.innerHeight - height - 8, rect.bottom + 4));
    return { left, top, zIndex:null };
  }""", """function stockHistoryInitialPosition(triggerEl, ev){
  const width = 240;
  const height = 210;
  if(triggerEl){
    // 종목명 바로 아래, 페이지에 붙여(스크롤하면 같이 움직임) — 2026-11-17 사용자: 아이폰에서 아래로 스크롤한 뒤 누르면 도넛 근처(화면 밖)에 떠 안 보였음
    let rect = triggerEl.getBoundingClientRect();
    if(!rect.height && ev && ev.clientY != null) rect = { left: ev.clientX - 20, bottom: ev.clientY + 10 };   // 누른 요소가 다시 그려져 빠졌으면 누른 자리 기준
    const left = Math.max(8, Math.min(window.innerWidth - width - 8, rect.left));
    return { left, top: rect.bottom + 4 + window.scrollY, zIndex:null, abs:true };
  }""")
rep("""  el.style.position = 'fixed';
  el.style.left = (typeof pos.left === 'number' ? pos.left + 'px' : pos.left);""",
    """  el.style.position = pos.abs ? 'absolute' : 'fixed';          // abs = 페이지 좌표(종목 그래프 팝업, 2026-11-17)
  el.style.left = (typeof pos.left === 'number' ? pos.left + 'px' : pos.left);""")
rep("""function openStockHistoryAccordion(accId, holdId, triggerEl){""", """function openStockHistoryAccordion(accId, holdId, triggerEl, ev){""")
rep("""    position: stockHistoryInitialPosition(triggerEl)
  };
  renderStockHistoryAccordion(key);""", """    position: stockHistoryInitialPosition(triggerEl, ev)
  };
  renderStockHistoryAccordion(key);
  if(triggerEl) requestAnimationFrame(() => {                    // 아래가 화면 밖으로 잘리면 보이는 만큼만 부드럽게 내림
    const f = document.querySelector(`#stock-history-slot-${CSS.escape(key)} .floating-acc`); if(!f) return;
    const over = f.getBoundingClientRect().bottom + 8 - window.innerHeight; if(over > 0) window.scrollBy({ top: over, behavior: 'smooth' });
  });""")
rep("""        openStockHistoryAccordion(cell.dataset.stockHistoryAcc, cell.dataset.stockHistoryName, cell);""",
    """        openStockHistoryAccordion(cell.dataset.stockHistoryAcc, cell.dataset.stockHistoryName, cell, e);""", 2)
rep("""      openStockHistoryAccordion(cell.dataset.stockHistoryAcc, cell.dataset.stockHistoryName, cell);""",
    """      openStockHistoryAccordion(cell.dataset.stockHistoryAcc, cell.dataset.stockHistoryName, cell, e);""")
open(p, 'w', encoding='utf-8').write(s)
