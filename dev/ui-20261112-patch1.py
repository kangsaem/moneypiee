import sys,re
fn=sys.argv[1]; s=open(fn,encoding='utf-8').read()
def rep(a,b,cnt=1):
    global s
    n=s.count(a)
    assert n==cnt, (fn,a[:70],n)
    s=s.replace(a,b)

# ---------- A. 광고 스위치 ----------
rep("  .wrap{max-width:960px;margin:0 auto;padding:76px 10px 32px;}",
    "  .wrap{max-width:960px;margin:0 auto;padding:76px 10px 32px;}\n  /* 2026-11-12 광고 스위치: MP_AD_ON=false면 위쪽 광고 띠와 그 자리(76px)를 없앰 */\n  .no-ad .wrap{padding-top:12px;} .no-ad #adfit-bottom{display:none !important;}")
m=re.search(r'<div id="adfit-bottom">\s*<ins class="kakao_ad_area" style="display:none;"\s*data-ad-unit="DAN-mgWowulkqYj3kO2r"\s*data-ad-width="320"\s*data-ad-height="50"></ins>\s*<script type="text/javascript" src="//t1.kakaocdn.net/kas/static/ba.min.js" async></script>\s*</div>', s)
assert m
s=s[:m.start()]+'''<script>
/* 위쪽 광고(카카오 애드핏). MP_AD_ON=true일 때만 넣음 — 코드는 보관(2026-11-12 사용자: 스위치로 끔) */
if(window.MP_AD_ON){ (function(){
  var d = document.createElement('div'); d.id = 'adfit-bottom';
  d.innerHTML = '<ins class="kakao_ad_area" style="display:none;" data-ad-unit="DAN-mgWowulkqYj3kO2r" data-ad-width="320" data-ad-height="50"></ins>';
  document.body.appendChild(d);
  var sc = document.createElement('script'); sc.async = true; sc.src = '//t1.kakaocdn.net/kas/static/ba.min.js'; d.appendChild(sc);
})(); }
</script>'''+s[m.end():]
m=re.search(r'<head>\s*', s); assert m
s=s[:m.end()]+"<script>/* 광고 스위치(2026-11-12): true로 바꾸면 위쪽 광고 띠가 다시 나옴 */window.MP_AD_ON=false;if(!window.MP_AD_ON)document.documentElement.classList.add('no-ad');</script>\n"+s[m.end():]

# ---------- B. 정렬 순서 ----------
rep("const STOCK_SORT_CYCLE_FULL = ['amount', 'group', 'region', 'name'];","const STOCK_SORT_CYCLE_FULL = ['region', 'group', 'amount', 'name'];   // 2026-11-12 사용자: 지역순→섹터순→금액순→이름순")
rep("const STOCK_SORT_CYCLE_NO_REGION = ['amount', 'group', 'name'];","const STOCK_SORT_CYCLE_NO_REGION = ['group', 'amount', 'name'];")

# ---------- C. 도넛 하나로 ----------
rep("  .rg-head{position:relative;} .charts.dn-car .rg-reload{display:flex;}",
    """  /* 2026-11-12 도넛 통일: 밑에 섹터 색, 위에 종목 조각. 접힌 묶음은 종목 조각을 숨겨 섹터 색이 보임 */
  #stock-sortable-chart [data-u]{transition:opacity .22s;}
  #stock-sortable-chart [data-u="base"]{transition:opacity 0s;}
  #stock-sortable-chart [data-u="base"][data-hide]{transition:opacity 0s .22s;}
  #stock-sortable-chart [data-u][data-dim]{opacity:.3 !important;}
  #stock-sortable-chart [data-u][data-hide]{opacity:0 !important;}
  .fold-body{display:flex;flex-direction:column;gap:6px;width:100%;transition:max-height .38s cubic-bezier(.16,.9,.3,1), margin-top .38s cubic-bezier(.16,.9,.3,1);}
  .fold-body.closed{max-height:0;margin-top:-6px;} .fold-body.closed, .fold-body.anim{overflow:hidden;}
  .sec-head{display:flex;align-items:center;gap:8px;margin:8px 0 4px;width:100%;cursor:pointer;-webkit-tap-highlight-color:transparent;}
  .sec-head .sec-nm{font-size:13px;color:var(--text);font-weight:400;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;min-width:0;opacity:0.7;}
  .sec-head .sec-ln{flex:1;border-top:1px dashed var(--text-dim);} .sec-head .sec-pct{font-size:13px;color:var(--text);opacity:0.7;flex-shrink:0;font-weight:500;}
  .rg-head{position:relative;} .charts.dn-car .rg-reload, .charts.mp-phone .rg-reload{display:flex;}""")

rep("""    return `<circle cx="${cx}" cy="${cy}" r="${radius}" fill="none" stroke="${color}" stroke-width="${strokeWidth}"${opacityAttr} stroke-dasharray""",
    """    return `<circle cx="${cx}" cy="${cy}" r="${radius}" fill="none" stroke="${d.color || color}" stroke-width="${strokeWidth}"${opacityAttr}${d.attrs || ''} stroke-dasharray""")

# 지역 접기: 다시 그리지 않고 그 자리에서 펼침(애니메이션)
rep("""  stockRegionFold[el.dataset.regionFold] = el.dataset.regionFolded !== '1';
  renderPreservingOpenChartAccordions();
});""","""  const g = el.dataset.regionFold, nowFolded = el.dataset.regionFolded !== '1';
  stockRegionFold[g] = nowFolded;
  const box = el.closest('#stock-sortable-chart'), body = box && mpFoldBody(box, 'reg', g);
  if(!DONUT_ONE || !body){ renderPreservingOpenChartAccordions(); return; }
  box.querySelectorAll('[data-region-fold="' + g + '"]').forEach(h => { h.style.display = ((h.dataset.regionFolded === '1') === nowFolded) ? '' : 'none'; });
  mpFold(body, !nowFolded); mpDonutSync();
  try{ assetPanelEnhance(); }catch(e){}
});
// 섹터순: 섹터 줄을 누르면 그 섹터 종목이 펼쳐지고 도넛의 그 섹터 구간에 종목 색이 나타남(2026-11-12 사용자)
document.addEventListener('click', e => {
  const sh = e.target.closest && e.target.closest('[data-sec-fold]'); if(!sh) return;
  const k = sh.dataset.secFold, box = sh.closest('#stock-sortable-chart'); if(!box) return;
  stockSectorOpen[k] = !stockSectorOpen[k];
  mpFold(mpFoldBody(box, 'sec', k), !!stockSectorOpen[k]); mpDonutSync();
});
const DONUT_ONE = true;            // 도넛 하나로 통일(2026-11-12). false면 예전처럼 섹터·종목·지역 3개
let stockSectorOpen = {};          // 섹터순에서 펼친 섹터(처음엔 모두 접힘)
function mpFoldBody(box, kind, key){ return [...box.querySelectorAll('[data-fold-body]')].find(b => b.dataset.foldBody === kind + ':' + key) || null; }
function mpFold(body, open){
  if(!body) return;
  const h = body.scrollHeight;
  body.classList.add('anim');
  if(open){ body.classList.remove('closed'); body.style.maxHeight = '0px'; void body.offsetHeight; body.style.maxHeight = h + 'px'; }
  else { body.style.maxHeight = h + 'px'; void body.offsetHeight; body.classList.add('closed'); body.style.maxHeight = ''; }
  clearTimeout(body._ft);
  body._ft = setTimeout(() => { body.classList.remove('anim'); if(!body.classList.contains('closed')) body.style.maxHeight = ''; try{ window.dispatchEvent(new Event('mp-fold-done')); }catch(e){} }, 420);
}
function stockSecKey(d){ return (isCashLikeLabel(d.label) || d.group === '현금') ? '현금' : (d.group || '?'); }
function stockRegKey(d){ return (d.region || 'domestic') === 'overseas' ? 'overseas' : 'domestic'; }
function stockRegionFoldState(){
  const mk = mpMarketSide(), other = mk.side === 'domestic' ? 'overseas' : 'domestic';
  return { mk, other, folded: { [mk.side]: stockRegionFold[mk.side] === true, [other]: stockRegionFold[other] !== false } };
}
// 도넛 조각 한 개가 지금 보여야 하는지: u = st(종목 조각) · base(밑의 섹터 색) · ring(섹터 링)
function stockUState(u, sec, reg, mode, rs, fs){
  if(mode === 'group'){ const open = sec === '현금' || !!stockSectorOpen[sec]; return { hide: u === 'st' ? !open : (u === 'base' ? open : false), dim: false }; }
  if(mode === 'region' && rs){ const f = !!fs.folded[reg]; return { hide: u === 'st' ? f : (u === 'base' ? !f : false), dim: f && u !== 'st' }; }
  return { hide: u === 'base', dim: false };
}
function stockUAttrs(u, sec, reg, st){ return ` data-u="${u}" data-sec="${escapeHTML(sec)}" data-reg="${reg}"${st.hide ? ' data-hide="1"' : ''}${st.dim ? ' data-dim="1"' : ''}`; }
function mpDonutSync(){
  const box = document.getElementById('stock-sortable-chart'); if(!box) return;
  const mode = box.dataset.umode, rs = box.dataset.urs === '1', fs = stockRegionFoldState();
  box.querySelectorAll('[data-u]').forEach(el => {
    const st = stockUState(el.dataset.u, el.dataset.sec, el.dataset.reg, mode, rs, fs);
    if(st.hide) el.setAttribute('data-hide', '1'); else el.removeAttribute('data-hide');
    if(st.dim) el.setAttribute('data-dim', '1'); else el.removeAttribute('data-dim');
  });
}
function pieSlicePaths(items, total, r, cx, cy){
  let angle = -90, out = '';
  items.forEach(d => {
    const sweep = (d.amount / total) * 360; if(!(sweep > 0)) return;
    if(sweep >= 359.9){ out += `<circle cx="${cx}" cy="${cy}" r="${r}" fill="${d.color}"${d.attrs || ''}/>`; angle += sweep; return; }
    const large = sweep > 180 ? 1 : 0, end = angle + sweep;
    const x1 = cx + r*Math.cos(angle*Math.PI/180), y1 = cy + r*Math.sin(angle*Math.PI/180);
    const x2 = cx + r*Math.cos(end*Math.PI/180), y2 = cy + r*Math.sin(end*Math.PI/180);
    out += `<path d="M${cx},${cy} L${x1.toFixed(2)},${y1.toFixed(2)} A${r},${r} 0 ${large} 1 ${x2.toFixed(2)},${y2.toFixed(2)} Z" fill="${d.color}"${d.attrs || ''}/>`;
    angle = end;
  });
  return out;
}
// 통일 도넛 설계: 종목 순서(도넛·목록 공통), 밑의 섹터 색 층, 섹터 링·지역 링 자료
function stockUnifiedPlan(raw, holdings, mode){
  const secW = reorderCashFirst(computeWeights(holdings, 'group')), secColor = {};
  secW.forEach((d, i) => { secColor[(isCashLikeLabel(d.label)) ? '현금' : d.label] = rankColor(d.label, d.rank !== undefined ? d.rank : i, d.rankCount !== undefined ? d.rankCount : secW.length, 'group'); });
  const bySector = xs => { const tot = {}; xs.forEach(d => { const k = stockSecKey(d); tot[k] = (tot[k] || 0) + d.amount; });
    return xs.slice().sort((a, b) => { const ka = stockSecKey(a), kb = stockSecKey(b);
      return ((kb === '현금') - (ka === '현금')) || (tot[kb] - tot[ka]) || (ka < kb ? -1 : (ka > kb ? 1 : 0)) || (b.amount - a.amount); }); };
  let ordered = sortStockData(raw, mode), rs = false;
  const fs = stockRegionFoldState();
  if(mode === 'group') ordered = bySector(raw);
  else if(mode === 'region'){
    const part = g => raw.filter(d => stockRegKey(d) === g);
    rs = part('domestic').length > 0 && part('overseas').length > 0;
    if(rs) ordered = bySector(part(fs.mk.side)).concat(bySector(part(fs.other)));   // 지역 안에서 섹터끼리 모음(지역별 섹터 링과 순서를 맞춤)
  }
  const total = _.sumBy(ordered, 'amount') || 1, n = ordered.length, useBase = mode === 'group' || rs;
  const st = (u, sec, reg) => stockUState(u, sec, reg, mode, rs, fs);
  const runs = [];
  if(useBase) ordered.forEach(d => { const sec = stockSecKey(d), reg = stockRegKey(d), k = mode === 'group' ? sec : reg + '|' + sec, l = runs[runs.length - 1];
    if(l && l.k === k) l.amount += d.amount; else runs.push({ k, amount: d.amount, sec, reg: mode === 'group' ? '' : reg }); });
  const regTot = { domestic: 0, overseas: 0 }, regCash = { domestic: 0, overseas: 0 };
  ordered.forEach(d => { const g = stockRegKey(d); regTot[g] += d.amount; if(stockSecKey(d) === '현금') regCash[g] += d.amount; });
  const baseItems = runs.map(r => ({ amount: r.amount, color: secColor[r.sec] || CASH_COLOR, attrs: stockUAttrs('base', r.sec, r.reg, st('base', r.sec, r.reg)) }));
  const stItems = ordered.map((d, i) => { const sec = stockSecKey(d), reg = stockRegKey(d);
    return { amount: d.amount, color: rankColor(d.label, d.rank !== undefined ? d.rank : i, d.rankCount !== undefined ? d.rankCount : n, 'stock'), attrs: ` data-slice-idx="${i}"` + stockUAttrs('st', sec, reg, st('st', sec, reg)) }; });
  const secRing = useBase ? runs.map(r => ({ label: (rs ? (r.reg === 'domestic' ? '국내 ' : '해외 ') : '') + r.sec, amount: r.amount,
    pct: rs ? (regTot[r.reg] ? r.amount / regTot[r.reg] * 100 : 0) : r.amount / total * 100,   // 지역순: 그 지역 안에서의 섹터 비중
    color: secColor[r.sec] || CASH_COLOR, attrs: stockUAttrs('ring', r.sec, r.reg, st('ring', r.sec, r.reg)) })) : null;
  const regRing = rs ? [fs.mk.side, fs.other].flatMap(g => [
    { label: g === 'domestic' ? '원화' : '외화', amount: regCash[g], pct: regCash[g] / total * 100, rank: 0, rankCount: 2 },
    { label: g === 'domestic' ? '국내' : '해외', amount: regTot[g] - regCash[g], pct: (regTot[g] - regCash[g]) / total * 100, rank: g === 'domestic' ? 0 : 1, rankCount: 2 }
  ]).filter(d => d.amount > 0) : null;
  const r = 74, cx = 80, cy = 80;
  const pieInner = n === 0
    ? `<circle cx="${cx}" cy="${cy}" r="${r}" fill="none" stroke="var(--text-dim)" stroke-width="1.5" stroke-dasharray="4 4"/>`
    : `<g transform="translate(160,0) scale(-1,1)">${pieSlicePaths(baseItems, total, r, cx, cy)}${pieSlicePaths(stItems, total, r, cx, cy)}<circle cx="${cx}" cy="${cy}" r="${r*0.55}" fill="var(--surface2)"/></g>`;
  return { ordered, pieInner, secRing, regRing, rs };
}""")

# 목록: 접힘 구조
rep("""      const mk = mpMarketSide(), other = mk.side === 'domestic' ? 'overseas' : 'domestic';
      const folded = { [mk.side]: stockRegionFold[mk.side] === true, [other]: stockRegionFold[other] !== false };""",
    """      const { mk, other, folded } = stockRegionFoldState();""")
rep("""        return folded[g]
          ? `<div class="rg-head rg-fold${g === other ? ' rg-sep' : ''}" data-region-fold="${g}" data-region-folded="1"><span>▸</span><b>${nm} ${cnt[g]}종목</b>${live}<span class="rg-cap">눌러서 펼치기</span><button type="button" class="rg-reload" title="시세 새로고침">↻</button></div>`
          : `<div class="rg-head${g === other ? ' rg-sep' : ''}" data-region-fold="${g}" data-region-folded="0"><span>▾</span><b>${nm}</b>${live}<span class="rg-cap">${cap}</span></div>`;""",
    """        const off = ' style="display:none"';
        const hf = (on) => `<div class="rg-head rg-fold${g === other ? ' rg-sep' : ''}" data-region-fold="${g}" data-region-folded="1"${on ? '' : off}><span>▸</span><b>${nm} ${cnt[g]}종목</b>${live}<span class="rg-cap">눌러서 펼치기</span><button type="button" class="rg-reload" title="시세 새로고침">↻</button></div>`;
        const ho = (on) => `<div class="rg-head${g === other ? ' rg-sep' : ''}" data-region-fold="${g}" data-region-folded="0"${on ? '' : off}><span>▾</span><b>${nm}</b>${live}<span class="rg-cap">${cap}</span></div>`;
        if(DONUT_ONE) return hf(folded[g]) + ho(!folded[g]);   // 두 머리줄을 다 넣어 두고 그 자리에서 바꿈(다시 그리지 않아 펼침 애니메이션이 살아 있음)
        return folded[g] ? hf(true) : ho(true);""")
rep("""  if(sortMode === 'group' && data.length > 0){
    html += sectionHeader(data[0].group);
  }
  data.forEach((d,i) => {
    if(rg){ const g = rg.gOf(d); if(g !== rg.last){ rg.last = g; html += rg.head(g); } if(rg.folded[g]) return; }""",
    """  const uniSec = DONUT_ONE && compactTotalMode && sortMode === 'group';   // 섹터순: 섹터마다 접힘 묶음
  const foldOpen = (kind, key, open) => `<div class="fold-body${open ? '' : ' closed'}" data-fold-body="${kind}:${escapeHTML(key)}">`;
  let bodyOpen = false, uniLast = null;
  const secPct = {}; if(uniSec) data.forEach(d => { const k = stockSecKey(d); secPct[k] = (secPct[k] || 0) + d.pct; });
  if(sortMode === 'group' && !uniSec && data.length > 0){
    html += sectionHeader(data[0].group);
  }
  data.forEach((d,i) => {
    if(rg){ const g = rg.gOf(d); if(g !== rg.last){ if(bodyOpen){ html += '</div>'; bodyOpen = false; } rg.last = g; html += rg.head(g); if(DONUT_ONE){ html += foldOpen('reg', g, !rg.folded[g]); bodyOpen = true; } } if(!DONUT_ONE && rg.folded[g]) return; }
    if(uniSec){ const k = stockSecKey(d); if(k !== uniLast){ if(bodyOpen){ html += '</div>'; bodyOpen = false; } uniLast = k;
      if(k !== '현금'){ html += `<div class="sec-head" data-sec-fold="${escapeHTML(k)}"><span class="sec-nm">${escapeHTML(k)}</span><div class="sec-ln"></div><span class="sec-pct num">${(secPct[k] || 0).toFixed(1)}<span class="pct-sign">%</span></span></div>` + foldOpen('sec', k, !!stockSectorOpen[k]); bodyOpen = true; } } }""")
rep("""      if(sortMode === 'group' && d.group !== next.group) showDivider = true;""",
    """      if(sortMode === 'group' && !uniSec && d.group !== next.group) showDivider = true;""")
rep("""        }
      }
    }
  });
  html += '</div>';
  return html;
}

function stockChartBlockSortable(""","""        }
      }
    }
  });
  if(bodyOpen) html += '</div>';
  html += '</div>';
  return html;
}

function stockChartBlockSortable(""")

# 도넛 블록
rep("""  const ordered = sortStockData(rawData, stockLegendSortMode);
  const centerLabel = STOCK_SORT_LABEL[stockLegendSortMode];
  // 외부링은""","""  const U = (DONUT_ONE && compactTotalMode) ? stockUnifiedPlan(rawData, holdings, stockLegendSortMode) : null;
  const ordered = U ? U.ordered : sortStockData(rawData, stockLegendSortMode);
  const centerLabel = STOCK_SORT_LABEL[stockLegendSortMode];
  // 외부링은""")
rep("""    if(stockLegendSortMode === 'region' && spec.name === 'decorative-region') opacity = 1;
    return { ...spec, opacity };""","""    if(stockLegendSortMode === 'region' && spec.name === 'decorative-region') opacity = 1;
    if(U && spec.name === 'decorative-sector' && U.secRing) return { ...spec, data: U.secRing, preOrdered: true, opacity: null };   // 종목 순서와 맞춘 섹터 링(지역순이면 지역별 섹터 비중)
    if(U && spec.name === 'decorative-region'){
      if(stockLegendSortMode === 'group') opacity = 0;                                  // 섹터순에서는 지역 링 숨김(자리는 유지해 도넛 크기가 안 변함)
      else if(U.regRing) return { ...spec, data: U.regRing, preOrdered: true, opacity: 1 };
    }
    return { ...spec, opacity };""")
rep("""  const pieInner = donutSVG(ordered, 160, 'stock').replace(/^<div class="donut-wrap">/, '').replace(/<\\/div>$/, '');""",
    """  const pieInner = U ? U.pieInner : donutSVG(ordered, 160, 'stock').replace(/^<div class="donut-wrap">/, '').replace(/<\\/div>$/, '');""")
rep("""  return `<div class="chart-box" id="stock-sortable-chart">
    <div class="donut-wrap ${sizeClass}\"""","""  return `<div class="chart-box" id="stock-sortable-chart" data-umode="${stockLegendSortMode}" data-urs="${U && U.rs ? 1 : 0}">
    <div class="donut-wrap ${sizeClass}\"""")

# 호출부: 섹터·지역 도넛 빼기
rep("        ${sectorChartBlock(holdings)}\n","        ${DONUT_ONE ? '' : sectorChartBlock(holdings)}\n")
rep("        ${noFilterActive ? '' : lockedRegionDonutBlock(","        ${(DONUT_ONE || noFilterActive) ? '' : lockedRegionDonutBlock(")
rep("        ${sectorChartBlock(scopedHoldings)}\n","        ${DONUT_ONE ? '' : sectorChartBlock(scopedHoldings)}\n")
rep("        ${regionChartBlock(scopedHoldings)}\n","        ${DONUT_ONE ? '' : regionChartBlock(scopedHoldings)}\n")
rep("      ${sectorChartBlock(acc.holdings)}\n","      ${DONUT_ONE ? '' : sectorChartBlock(acc.holdings)}\n")
rep("      ${regionChartBlock(acc.holdings)}\n","      ${DONUT_ONE ? '' : regionChartBlock(acc.holdings)}\n")
rep("""  const ch = panel.querySelector('.charts'); if(!ch || ch.classList.contains('dn-car')) return;""",
    """  const ch0 = panel.querySelector('.charts'); if(ch0) ch0.classList.toggle('mp-phone', donutCarOn());
  const ch = panel.querySelector('.charts'); if(!ch || ch.classList.contains('dn-car')) return;""")
open(fn,'w',encoding='utf-8').write(s)
print('ok',fn)
