import sys
fn=sys.argv[1]; s=open(fn,encoding='utf-8').read()
def rep(a,b,cnt=1):
    global s
    n=s.count(a); assert n==cnt,(fn,a[:70],n); s=s.replace(a,b)
# '기타'는 그 안의 섹터가 모두 접혀 있을 때만 묶음으로 보임
rep("""    if(uniSec){ const k = stockSecKey(d), gk = stockSecEtc.has(k) ? ETC_KEY : k;""","""    if(uniSec){ const k = stockSecKey(d), gk = (etcMerged && stockSecEtc.has(k)) ? ETC_KEY : k;""")
rep("""  const secKeysAll = uniSec ? [...new Set(data.map(d => { const k = stockSecKey(d); return stockSecEtc.has(k) ? ETC_KEY : k; }))].filter(k => k !== '현금') : [];""",
    """  const secKeysAll = uniSec ? [...new Set(data.map(stockSecKey))].filter(k => k !== '현금') : [];
  // '기타'(1% 미만 섹터 묶음)는 그 섹터들이 모두 접혀 있을 때만 한 줄로 보임. 누르면 '기타' 줄은 사라지고 그 섹터들이 펼쳐진 채 나옴. 다 접으면 다시 '기타'로 묶임(2026-11-12 사용자)
  const etcMerged = uniSec && stockSecEtc.size > 0 && [...stockSecEtc].every(k => !stockSecOpen(k));""")
rep("""  if(mode === 'group'){ const open = sec === '현금' || stockSecOpen(stockSecEtc.has(sec) ? ETC_KEY : sec);""","""  if(mode === 'group'){ const open = sec === '현금' || stockSecOpen(sec);""")
rep("""  const k = sh.dataset.secFold, box = sh.closest('#stock-sortable-chart'); if(!box || (WIDE_ALL_OPEN && mpWideList())) return;
  stockSectorOpen[k] = !stockSectorOpen[k];""","""  const k = sh.dataset.secFold, box = sh.closest('#stock-sortable-chart'); if(!box || (WIDE_ALL_OPEN && mpWideList())) return;
  if(k === ETC_KEY){ stockSecEtc.forEach(x => { stockSectorOpen[x] = true; }); renderPreservingOpenChartAccordions(); return; }   // '기타' → 그 안의 섹터들을 펼친 채로 풀어 놓음
  stockSectorOpen[k] = !stockSectorOpen[k];
  if(stockSecEtc.has(k) && [...stockSecEtc].every(x => !stockSectorOpen[x])) setTimeout(() => { if([...stockSecEtc].every(x => !stockSectorOpen[x]) && document.getElementById('stock-sortable-chart')) renderPreservingOpenChartAccordions(); }, 440);   // 다 접으면 '기타'로 다시 묶음""")
rep("""  const ab = box.querySelector('[data-sec-all]'); if(ab) ab.textContent = [...box.querySelectorAll('[data-sec-fold]')].every(h => stockSectorOpen[h.dataset.secFold]) ? '▴ 모두 접기' : '▾ 모두 펴기';""",
    """  const ab = box.querySelector('[data-sec-all]'); if(ab) ab.textContent = [...box.querySelectorAll('[data-sec-fold]')].every(h => h.dataset.secFold === ETC_KEY ? false : stockSectorOpen[h.dataset.secFold]) ? '▴ 모두 접기' : '▾ 모두 펴기';""")
rep("""  const keys = [...box.querySelectorAll('[data-sec-fold]')].map(h => h.dataset.secFold), open = !keys.every(k => stockSectorOpen[k]);""",
    """  if(stockSecEtc.size){   // '기타' 묶음이 있으면 묶임/풀림이 바뀌므로 다시 그림
    const all = [...new Set([...box.querySelectorAll('[data-sec-fold]')].map(h => h.dataset.secFold).filter(k => k !== ETC_KEY).concat([...stockSecEtc]))], op = !all.every(k => stockSectorOpen[k]);
    all.forEach(k => { stockSectorOpen[k] = op; }); renderPreservingOpenChartAccordions(); return;
  }
  const keys = [...box.querySelectorAll('[data-sec-fold]')].map(h => h.dataset.secFold), open = !keys.every(k => stockSectorOpen[k]);""")
open(fn,'w',encoding='utf-8').write(s); print('ok')
