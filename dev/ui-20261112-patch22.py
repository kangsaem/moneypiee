import sys
fn=sys.argv[1]; s=open(fn,encoding='utf-8').read()
def rep(a,b,cnt=1):
    global s
    n=s.count(a); assert n==cnt,(fn,a[:70],n); s=s.replace(a,b)
# 1) 지역순: 도넛 한 번 누르면 반대쪽 지역이 위로
rep("""  const mk = mpMarketSide(), other = mk.side === 'domestic' ? 'overseas' : 'domestic';
  if(WIDE_ALL_OPEN && mpWideList()) return { mk, other, folded: { domestic: false, overseas: false } };
  return { mk, other, folded: { [mk.side]: stockRegionFold[mk.side] === true, [other]: stockRegionFold[other] !== false } };""",
    """  const mk = mpMarketSide(), other = mk.side === 'domestic' ? 'overseas' : 'domestic';
  // first = 목록 위에 펼쳐지는 지역(보통 장중인 쪽, 도넛을 한 번 누르면 반대쪽 — stockRegionFlip). 링 색은 항상 장 기준(mk.side)
  const first = stockRegionFlip ? other : mk.side, second = first === mk.side ? other : mk.side;
  if(WIDE_ALL_OPEN && mpWideList()) return { mk, other, first, second, folded: { domestic: false, overseas: false } };
  return { mk, other, first, second, folded: { [first]: stockRegionFold[first] === true, [second]: stockRegionFold[second] !== false } };""")
rep("""let stockSectorOpen = {};          // 섹터순에서 펼친 섹터(처음엔 모두 접힘)""","""let stockSectorOpen = {};          // 섹터순에서 펼친 섹터(처음엔 모두 접힘)
let stockRegionFlip = false;       // 지역순에서 도넛을 한 번 눌러 반대쪽 지역을 위로 올린 상태(2026-11-12 사용자)""")
rep("""    if(rs) ordered = bySector(part(fs.mk.side)).concat(bySector(part(fs.other)));""","""    if(rs) ordered = bySector(part(fs.first)).concat(bySector(part(fs.second)));""")
rep("""  const regRing = rs ? [fs.mk.side, fs.other].flatMap(g => [""","""  const regRing = rs ? [fs.first, fs.second].flatMap(g => [""")
rep("""      const { mk, other, folded } = stockRegionFoldState();
      data = data.filter(d => gOf(d) === mk.side).concat(data.filter(d => gOf(d) === other));""","""      const fsr = stockRegionFoldState(), mk = { open: fsr.mk.open, side: fsr.first, real: fsr.mk.side }, other = fsr.second, folded = fsr.folded;   // side·other = 목록에서 위·아래 지역
      data = data.filter(d => gOf(d) === mk.side).concat(data.filter(d => gOf(d) === other));""")
rep("""live = mk.open && g === mk.side ? '<span class="rg-live">장중</span>' : '';""","""live = mk.open && g === mk.real ? '<span class="rg-live">장중</span>' : '';""")
rep("""  const cycle = stockSortCycleActive || STOCK_SORT_CYCLE_FULL;
  const idx = cycle.indexOf(stockLegendSortMode);
  stockLegendSortMode = cycle[(idx + 1) % cycle.length];""","""  // 지역순에서 도넛 한 번 = 반대쪽 지역을 위로 펼침(링 색은 그대로, 목록 순서만 바뀜). 한 번 더 누르면 다음 정렬로
  if(DONUT_ONE && stockLegendSortMode === 'region' && !stockRegionFlip){
    const bx = document.getElementById('stock-sortable-chart');
    if(bx && bx.dataset.urs === '1'){ stockRegionFlip = true; stockRegionFold = {}; stockSortPicked = true; render(); return; }
  }
  if(DONUT_ONE){ stockRegionFlip = false; stockRegionFold = {}; }
  const cycle = stockSortCycleActive || STOCK_SORT_CYCLE_FULL;
  const idx = cycle.indexOf(stockLegendSortMode);
  stockLegendSortMode = cycle[(idx + 1) % cycle.length];""")
# 2) 섹터 비중 숫자: 접힘 = 흰색 또렷, 펼침 = 톤다운
rep("""  .sec-head .sec-ln{flex:1;border-top:1px dashed var(--text-dim);} .sec-head .sec-pct{font-size:13px;color:var(--text);opacity:0.7;flex-shrink:0;font-weight:500;}""",
    """  .sec-head .sec-ln{flex:1;border-top:1px dashed var(--text-dim);} .sec-head .sec-pct{font-size:14px;color:#FFFFFF;opacity:1;flex-shrink:0;font-weight:700;transition:opacity .2s;}
  .sec-head.open .sec-pct{color:var(--text);opacity:0.7;font-weight:500;font-size:13px;}   /* 접힘 = 흰색 또렷, 펼침 = 톤다운(2026-11-12 사용자) */""")
rep("""html += `<div class="sec-grp"><div class="sec-head" data-sec-fold="${escapeHTML(k)}">""","""html += `<div class="sec-grp"><div class="sec-head${stockSecOpen(k) ? ' open' : ''}" data-sec-fold="${escapeHTML(k)}">""")
rep("""  mpFold(mpFoldBody(box, 'sec', k), !!stockSectorOpen[k]); mpDonutSync();
  const ab =""","""  mpFold(mpFoldBody(box, 'sec', k), !!stockSectorOpen[k]); mpDonutSync(); sh.classList.toggle('open', !!stockSectorOpen[k]);
  const ab =""")
rep("""  keys.forEach(k => { if(!!stockSectorOpen[k] !== open){ stockSectorOpen[k] = open; mpFold(mpFoldBody(box, 'sec', k), open); } });""",
    """  keys.forEach(k => { if(!!stockSectorOpen[k] !== open){ stockSectorOpen[k] = open; mpFold(mpFoldBody(box, 'sec', k), open); } });
  box.querySelectorAll('[data-sec-fold]').forEach(h => h.classList.toggle('open', open));""")
open(fn,'w',encoding='utf-8').write(s); print('ok')
