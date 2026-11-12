import sys,re
fn=sys.argv[1]; s=open(fn,encoding='utf-8').read()
def rep(a,b,cnt=1):
    global s
    n=s.count(a); assert n==cnt,(fn,a[:70],n); s=s.replace(a,b)
# 목록: 1% 미만 섹터는 '기타' 묶음
i=s.index("    if(uniSec){ const k = stockSecKey(d); if(k !== uniLast){")
j=s.index("bodyOpen = true; } } }", i)+len("bodyOpen = true; } } }")
s=s[:i]+"""    if(uniSec){ const k = stockSecKey(d), gk = stockSecEtc.has(k) ? ETC_KEY : k;   // 1% 미만 섹터는 '기타' 한 묶음(펼치면 섹터별로 다 풀어서 보임)
      if(gk !== uniLast){ if(subOpen){ html += '</div>'; subOpen = false; } if(bodyOpen){ html += '</div></div>'; bodyOpen = false; } uniLast = gk; subLast = null;
        if(gk !== '현금' && secAllBtn && !secAllDone){ html += `<div class="sec-all-row">${secAllBtn}</div>`; secAllDone = true; }   // 현금 줄이 없으면 맨 위에 따로
        if(gk !== '현금'){ const isEtc = gk === ETC_KEY, pctV = isEtc ? _.sum([...stockSecEtc].map(x => secPct[x] || 0)) : (secPct[k] || 0);
          html += `<div class="sec-grp"><div class="sec-head${stockSecOpen(gk) ? ' open' : ''}" data-sec-fold="${escapeHTML(gk)}"><span class="swatch" style="background:${isEtc ? '#9A9BA1' : (stockSecColorNow[k] || CASH_COLOR)}"></span><span class="sec-nm">${isEtc ? '기타' : escapeHTML(k)}</span><div class="sec-ln"></div><span class="sec-pct num">${pctV.toFixed(1)}<span class="pct-sign">%</span></span></div>` + foldOpen('sec', gk, stockSecOpen(gk)); bodyOpen = true; } }
      if(gk === ETC_KEY && k !== subLast){ if(subOpen) html += '</div>'; subLast = k; subOpen = true;
        html += `<div class="sec-head sub open"><span class="swatch" style="background:${stockSecColorNow[k] || CASH_COLOR}"></span><span class="sec-nm">${escapeHTML(k)}</span><div class="sec-ln"></div><span class="sec-pct num">${(secPct[k] || 0).toFixed(1)}<span class="pct-sign">%</span></span></div><div class="sec-sub">`; } }"""+s[j:]
rep("""  let bodyOpen = false, uniLast = null, secAllDone = false;""","""  let bodyOpen = false, uniLast = null, secAllDone = false, subOpen = false, subLast = null;""")
rep("""  const secKeysAll = uniSec ? [...new Set(data.map(stockSecKey))].filter(k => k !== '현금') : [];""","""  const secKeysAll = uniSec ? [...new Set(data.map(d => { const k = stockSecKey(d); return stockSecEtc.has(k) ? ETC_KEY : k; }))].filter(k => k !== '현금') : [];""")
rep("""  if(bodyOpen) html += (DONUT_ONE && (rg || uniSec)) ? '</div></div>' : '</div>';""","""  if(subOpen) html += '</div>';
  if(bodyOpen) html += (DONUT_ONE && (rg || uniSec)) ? '</div></div>' : '</div>';""")
# 상태·도넛
rep("""let stockRegionFlip = false; """,""" const ETC_KEY = '__etc__';        // 섹터순의 '기타'(1% 미만 섹터 묶음) 접힘 키
let stockSecEtc = new Set();       // 지금 '기타'로 묶인 섹터들(2개 이상일 때만 묶음)
let stockRegionFlip = false; """)
rep("""  if(mode === 'group'){ const open = sec === '현금' || stockSecOpen(sec);""","""  if(mode === 'group'){ const open = sec === '현금' || stockSecOpen(stockSecEtc.has(sec) ? ETC_KEY : sec);""")
rep("""  if(mode === 'group') ordered = bySector(raw);""","""  stockSecEtc = new Set();
  if(mode === 'group'){ ordered = bySector(raw);
    const tot = _.sumBy(raw, 'amount') || 1, st = {}; raw.forEach(d => { const k = stockSecKey(d); st[k] = (st[k] || 0) + d.amount; });
    const small = Object.keys(st).filter(k => k !== '현금' && st[k] / tot * 100 < 1); if(small.length >= 2) stockSecEtc = new Set(small); }""")
rep("""  .sec-all{flex-shrink:0;""","""  .sec-head.sub{cursor:default;margin:0;padding:2px 0;} .sec-sub{display:flex;flex-direction:column;gap:6px;padding-left:16px;box-sizing:border-box;width:100%;margin-bottom:6px;}
  .stock-sortable-legend.wide2 .sec-sub{display:block;}
  .sec-all{flex-shrink:0;""")
open(fn,'w',encoding='utf-8').write(s); print('ok')
