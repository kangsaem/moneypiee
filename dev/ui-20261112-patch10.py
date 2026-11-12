import sys
fn=sys.argv[1]; s=open(fn,encoding='utf-8').read()
def rep(a,b,cnt=1):
    global s
    n=s.count(a); assert n==cnt,(fn,a[:70],n); s=s.replace(a,b)
rep("""  .fold-body.closed{max-height:0;margin-top:-6px;}""","""  /* 섹터순: 종목은 들여쓰고, 펼친 섹터 아래는 간격을 벌림(2026-11-12 사용자: 섹터와 종목 구분) */
  .fold-body[data-fold-body^="sec:"]{padding-left:16px;box-sizing:border-box;transition:max-height .38s cubic-bezier(.16,.9,.3,1), margin .38s cubic-bezier(.16,.9,.3,1);}
  .fold-body[data-fold-body^="sec:"]:not(.closed){margin-bottom:12px;}
  /* 넓은 PC 화면: 접지 않고 다 펼쳐 두 줄(2단)로 */
  .stock-sortable-legend.wide2{display:block;width:620px;max-width:100%;column-count:2;column-gap:56px;}
  .stock-sortable-legend.wide2 .legend-item, .stock-sortable-legend.wide2 .rg-head{break-inside:avoid;margin-bottom:6px;}
  .stock-sortable-legend.wide2 .fold-body{display:block;margin-top:0;}
  .stock-sortable-legend.wide2 .sec-head{margin:10px 0 4px;padding:2px 0;cursor:default;break-inside:avoid;break-after:avoid;}
  .stock-sortable-legend.wide2 .rg-head{cursor:default;break-after:avoid;} .stock-sortable-legend.wide2 .rg-head.rg-sep{border-top:0;margin-top:0;padding-top:4px;}
  .fold-body.closed{max-height:0;margin-top:-6px;}""")
rep("""function stockRegionFoldState(){
  const mk = mpMarketSide(), other = mk.side === 'domestic' ? 'overseas' : 'domestic';
  return { mk, other, folded: {""","""// 넓은 PC 화면(터치 아님 + 폭 900px 이상): 접힘 없이 다 펼치고 목록을 두 줄로(2026-11-12 사용자)
function mpWideList(){ try{ return !donutCarOn() && window.innerWidth >= 900; }catch(e){ return false; } }
function stockSecOpen(k){ return mpWideList() || !!stockSectorOpen[k]; }
(function(){ let was = null; window.addEventListener('resize', () => { const w = mpWideList(); if(was !== null && w !== was && document.getElementById('stock-sortable-chart')){ try{ renderPreservingOpenChartAccordions(); }catch(e){} } was = w; }); was = mpWideList(); })();
function stockRegionFoldState(){
  const mk = mpMarketSide(), other = mk.side === 'domestic' ? 'overseas' : 'domestic';
  if(mpWideList()) return { mk, other, folded: { domestic: false, overseas: false } };
  return { mk, other, folded: {""")
rep("""  if(mode === 'group'){ const open = sec === '현금' || !!stockSectorOpen[sec];""","""  if(mode === 'group'){ const open = sec === '현금' || stockSecOpen(sec);""")
rep("""foldOpen('sec', k, !!stockSectorOpen[k]); bodyOpen = true;""","""foldOpen('sec', k, stockSecOpen(k)); bodyOpen = true;""")
rep("""  const legendClass = compactTotalMode ? 'legend stock-sortable-legend' : 'legend';""","""  const legendClass = compactTotalMode ? ('legend stock-sortable-legend' + (DONUT_ONE && mpWideList() ? ' wide2' : '')) : 'legend';""")
rep("""  const g = el.dataset.regionFold, nowFolded = el.dataset.regionFolded !== '1';""","""  if(DONUT_ONE && mpWideList()) return;   // 넓은 화면은 항상 펼침
  const g = el.dataset.regionFold, nowFolded = el.dataset.regionFolded !== '1';""")
rep("""  const k = sh.dataset.secFold, box = sh.closest('#stock-sortable-chart'); if(!box) return;""","""  const k = sh.dataset.secFold, box = sh.closest('#stock-sortable-chart'); if(!box || mpWideList()) return;""")
open(fn,'w',encoding='utf-8').write(s); print('ok',fn)
