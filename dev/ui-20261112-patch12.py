import sys
fn=sys.argv[1]; s=open(fn,encoding='utf-8').read()
def rep(a,b,cnt=1):
    global s
    n=s.count(a); assert n==cnt,(fn,a[:70],n); s=s.replace(a,b)
# CSS: 2~3단 자동, 묶음은 안 끊김, 넓은 화면 도넛 크기
rep("""  .stock-sortable-legend.wide2{display:block;width:620px;max-width:100%;column-count:2;column-gap:56px;}""",
    """  .sec-grp{display:contents;}
  .stock-sortable-legend.wide2{display:block;width:100%;max-width:920px;columns:250px 3;column-gap:48px;}   /* 폭에 따라 2단·3단 자동 */
  .stock-sortable-legend.wide2 .sec-grp{display:block;break-inside:avoid;}   /* 한 섹터(지역) 묶음은 중간에 끊지 않고 통째로 다음 단으로 */
  @media(min-width:900px){ #stock-sortable-chart .donut-wrap-md{width:247px;height:247px;} #stock-sortable-chart .donut-wrap-lg{width:264px;height:264px;} #stock-sortable-chart .donut-wrap-xl{width:282px;height:282px;} #stock-sortable-chart .donut-wrap-xxl{width:299px;height:299px;} #stock-sortable-chart .stock-donut-center-label{font-size:16px;} }   /* 넓은 화면에서도 도넛은 휴대폰과 같은 크기 */
  .sec-all{flex-shrink:0;font-size:12px;font-weight:600;color:var(--text);border:1px solid var(--accent-dim);border-radius:12px;padding:2px 10px;cursor:pointer;user-select:none;-webkit-tap-highlight-color:transparent;white-space:nowrap;}
  .sec-all-row{display:flex;justify-content:center;width:100%;}""")
# 목록: 묶음 감싸기 + 모두 펴기 버튼
rep("""    if(rg){ const g = rg.gOf(d); if(g !== rg.last){ if(bodyOpen){ html += '</div>'; bodyOpen = false; } rg.last = g; html += rg.head(g); if(DONUT_ONE){ html += foldOpen('reg', g, !rg.folded[g]); bodyOpen = true; } } if(!DONUT_ONE && rg.folded[g]) return; }
    if(uniSec){ const k = stockSecKey(d); if(k !== uniLast){ if(bodyOpen){ html += '</div>'; bodyOpen = false; } uniLast = k;
      if(k !== '현금'){ html += `<div class="sec-head\"""",
    """    if(rg){ const g = rg.gOf(d); if(g !== rg.last){ if(bodyOpen){ html += '</div></div>'; bodyOpen = false; } rg.last = g; if(DONUT_ONE) html += '<div class="sec-grp">'; html += rg.head(g); if(DONUT_ONE){ html += foldOpen('reg', g, !rg.folded[g]); bodyOpen = true; } } if(!DONUT_ONE && rg.folded[g]) return; }
    if(uniSec){ const k = stockSecKey(d); if(k !== uniLast){ if(bodyOpen){ html += '</div></div>'; bodyOpen = false; } uniLast = k;
      if(k !== '현금' && secAllBtn && !secAllDone){ html += `<div class="sec-all-row">${secAllBtn}</div>`; secAllDone = true; }   // 현금 줄이 없으면 맨 위에 따로
      if(k !== '현금'){ html += `<div class="sec-grp"><div class="sec-head\"""")
rep("""  let bodyOpen = false, uniLast = null;""","""  let bodyOpen = false, uniLast = null, secAllDone = false;
  // 모두 펴기/접기(섹터순, 접힘이 있는 화면에서만): 현금 줄 가운데에 둠(2026-11-12 사용자)
  const secKeysAll = uniSec ? [...new Set(data.map(stockSecKey))].filter(k => k !== '현금') : [];
  const secAllBtn = (uniSec && !mpWideList() && secKeysAll.length > 1) ? `<span class="sec-all" data-sec-all>${secKeysAll.every(k => stockSectorOpen[k]) ? '▴ 모두 접기' : '▾ 모두 펴기'}</span>` : '';""")
rep("""    html += `<div class="legend-item"><span class="swatch" style="background:${color}"></span><span class="legend-name"${clickAttrs}>${escapeHTML(d.label)}</span><span class="legend-pct num ${valueModeClass}\"""",
    """    const allBtnHere = (uniSec && secAllBtn && !secAllDone && stockSecKey(d) === '현금') ? (secAllDone = true, secAllBtn) : '';
    html += `<div class="legend-item"><span class="swatch" style="background:${color}"></span><span class="legend-name"${clickAttrs}>${escapeHTML(d.label)}</span>${allBtnHere}<span class="legend-pct num ${valueModeClass}\"""")
rep("""  if(bodyOpen) html += '</div>';
  html += '</div>';
  return html;""","""  if(bodyOpen) html += (DONUT_ONE && (rg || uniSec)) ? '</div></div>' : '</div>';
  html += '</div>';
  return html;""")
rep("""const DONUT_ONE = true;            // 도넛 하나로 통일""","""document.addEventListener('click', e => {
  const b = e.target.closest && e.target.closest('[data-sec-all]'); if(!b) return;
  e.stopPropagation();
  const box = b.closest('#stock-sortable-chart'); if(!box) return;
  const keys = [...box.querySelectorAll('[data-sec-fold]')].map(h => h.dataset.secFold), open = !keys.every(k => stockSectorOpen[k]);
  keys.forEach(k => { if(!!stockSectorOpen[k] !== open){ stockSectorOpen[k] = open; mpFold(mpFoldBody(box, 'sec', k), open); } });
  b.textContent = open ? '▴ 모두 접기' : '▾ 모두 펴기'; mpDonutSync();
}, true);
const DONUT_ONE = true;            // 도넛 하나로 통일""")
# 섹터 줄 하나씩 눌렀을 때도 버튼 글자 맞춤
rep("""  mpFold(mpFoldBody(box, 'sec', k), !!stockSectorOpen[k]); mpDonutSync();
});""","""  mpFold(mpFoldBody(box, 'sec', k), !!stockSectorOpen[k]); mpDonutSync();
  const ab = box.querySelector('[data-sec-all]'); if(ab) ab.textContent = [...box.querySelectorAll('[data-sec-fold]')].every(h => stockSectorOpen[h.dataset.secFold]) ? '▴ 모두 접기' : '▾ 모두 펴기';
});""")
open(fn,'w',encoding='utf-8').write(s); print('ok',fn)
