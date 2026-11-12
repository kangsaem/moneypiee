import sys
fn=sys.argv[1]; s=open(fn,encoding='utf-8').read()
def rep(a,b,cnt=1):
    global s
    n=s.count(a); assert n==cnt,(fn,a[:70],n); s=s.replace(a,b)
# ---- CSS
rep("""  .trend-wrap{margin-top:8px;}""","""  .trend-wrap{margin-top:8px;}
  /* 월별 탭 개편(2026-11-12): 선 켜고 끄는 범례, 확대·축소 버튼, 제목 없는 촘촘한 막대 */
  .hl-chip{display:inline-flex;align-items:center;gap:4px;margin-right:11px;padding:4px 0;cursor:pointer;user-select:none;-webkit-tap-highlight-color:transparent;font-size:12px;}
  .hl-chip i{width:8px;height:8px;border-radius:2px;display:inline-block;} .hl-chip.off{opacity:.38;}
  .hz-btn{width:26px;height:26px;border:1px solid var(--border);border-radius:6px;background:transparent;color:var(--text);font-size:17px;line-height:1;cursor:pointer;padding:0;font-family:inherit;-webkit-tap-highlight-color:transparent;}
  .tb2-grp{max-width:860px;margin:10px auto 0;} .tb2-row{position:relative;margin-bottom:1px;} .tb2-row.hid{display:none;}
  .tb2-bar{position:relative;height:var(--tbh, 9px);cursor:pointer;} .tb2-bar svg{height:100% !important;border-radius:3px !important;}
  .tb2-lb{position:absolute;left:5px;top:50%;transform:translateY(-50%);z-index:1;font-size:10px;line-height:1;font-weight:600;color:#fff;text-shadow:0 0 3px #000, 0 0 2px #000, 0 0 1px #000;pointer-events:none;}
  #tb2More{margin:10px auto 0;width:56px;height:28px;border-radius:14px;background:rgba(40,41,45,.82);display:none;align-items:center;justify-content:center;color:var(--text-dim);font-size:14px;cursor:pointer;user-select:none;}""")
# ---- lineChartSVG
rep("""function lineChartSVG(points, extraSeries, width, height, labelMode, responsive){
  if(points.length === 0) return '<div class="empty">저장된 월별 자산이 없습니다.</div>';
  labelMode = labelMode || 'normal';
  const padX = 30, topPad = 66, bottomPad = 34;
  const maxVal = Math.max(...points.map(p=>p.value), 1);""","""function lineChartSVG(points, extraSeries, width, height, labelMode, responsive, opts){
  if(points.length === 0) return '<div class="empty">저장된 월별 자산이 없습니다.</div>';
  labelMode = labelMode || 'normal';
  opts = opts || {};
  const padX = 30, topPad = 66, bottomPad = 34;
  let denseMax = 1; (opts.dense || []).forEach(sr => sr.pts.forEach(p => { if(p[1] > denseMax) denseMax = p[1]; }));   // 지수선(일별)도 세로 범위에 넣음
  const maxVal = Math.max(...points.map(p=>p.value), 1, denseMax);""")
rep("""  const legendHtml = `<div style="display:flex;justify-content:space-between;align-items:center;font-size:11px;color:var(--text-dim);margin-bottom:4px;"><span>${legend}</span><span>단위: 만원</span></div>`;""",
    """  // 지수선(2026-11-12): 월말 종가 점 + 그 사이 일별 궤적. x는 '몇 번째 달'(소수) 단위
  (opts.dense || []).forEach(sr => {
    const dp = sr.pts.map((p,i) => (i ? 'L' : 'M') + (padX + p[0]*xStep).toFixed(1) + ',' + scaleY(p[1]).toFixed(1)).join(' ');
    extraPaths += `<path d="${dp}" fill="none" stroke="${sr.color}" stroke-width="1.4" stroke-linejoin="round" opacity="0.95"/>` + sr.ends.map(p => `<circle cx="${(padX + p[0]*xStep).toFixed(1)}" cy="${scaleY(p[1]).toFixed(1)}" r="2.3" fill="${sr.color}"/>`).join('');
  });
  const legendHtml = `<div style="display:flex;justify-content:space-between;align-items:center;font-size:11px;color:var(--text-dim);margin-bottom:4px;"><span>${opts.legendHtml != null ? opts.legendHtml : legend}</span><span style="flex-shrink:0;">단위: 만원</span></div>`;""")
# ---- trendBarsHTML
rep("""  const ordered = snapshots.slice().reverse();
  const seriesArr = [];
  const rows = ordered.map((s,i) => {
    const holdings = _.flatMap(s.accounts, a => a.holdings);
    const byKeyRaw = computeWeights(holdings, groupKey);
    const byKey = reorderCashFirst(byKeyRaw);
    seriesArr.push({ byKey, monthLabel: fullMonthLabel(s.label) });""","""  const ordered = snapshots.slice().reverse();
  const seriesArr = [];
  if(HIST_NEW){
    // 2026-11-12 사용자: 제목 없음, 막대는 왼쪽 끝까지, 날짜 글자는 매년 1월 줄에만(막대 위에 겹쳐 표시). 굵기·보이는 줄 수는 historyBarsFit이 화면에 맞춤
    const rows2 = ordered.map((s,i) => {
      const byKey = reorderCashFirst(computeWeights(_.flatMap(s.accounts, a => a.holdings), groupKey));
      seriesArr.push({ byKey, monthLabel: fullMonthLabel(s.label) });
      const rowId = `${idPrefix}-${i}`, jan = normalizeLabel(s.label).slice(4,6) === '01';
      return `<div class="tb2-row" data-age="${i}"><div class="tb2-bar" data-trendrow="${rowId}">${stackedBarSVG(byKey, 600, 13, type)}${jan ? `<span class="tb2-lb num">${escapeHTML(shortMonthLabel(s.label))}</span>` : ''}</div><div id="trend-slot-${rowId}"></div></div>`;
    }).join('');
    trendSeriesData[idPrefix] = seriesArr;
    return `<div class="tb2-grp">${rows2}</div>`;
  }
  const rows = ordered.map((s,i) => {
    const holdings = _.flatMap(s.accounts, a => a.holdings);
    const byKeyRaw = computeWeights(holdings, groupKey);
    const byKey = reorderCashFirst(byKeyRaw);
    seriesArr.push({ byKey, monthLabel: fullMonthLabel(s.label) });""")
# ---- 모듈
rep("""function renderHistoryPanel(){
  const panel = document.getElementById('panel');""","""// ── 월별 탭 개편(2026-11-12 사용자) ─────────────────────────────────────────────
// 지수선: 코스피·나스닥·S&P 일별 종가를 하루 한 번 받아 기기에 저장. 선택 기간 첫 달의 자산 금액에 시작점을 맞춰 같은 축에 그림(입출금이 있으면 자산선과 직접 비교는 어긋남 — 사용자 인지)
const HIST_NEW = true;
const HIDX = [ { key:'kospi', sym:'^KS11', name:'코스피', color:'#F2A65A' }, { key:'ndx', sym:'^IXIC', name:'나스닥', color:'#E87BA4' }, { key:'spx', sym:'^GSPC', name:'S&P', color:'#5FB8E0' } ];   // 색 = 200일선 붕괴 사례 페이지의 지수 색(crash200.js XC)
const HIDX_KEY = 'moneypie:idxhist', HLINE_KEY = 'moneypie:histlines';
let hidxData = null, hidxBusy = false, hidxFailAt = 0;
let historyLineOff = (() => { try{ const v = JSON.parse(localStorage.getItem(HLINE_KEY) || 'null'); if(v && typeof v === 'object') return v; }catch(e){} return { '국내': true, '해외': true, 'S&P': true }; })();   // 처음엔 자산·코스피·나스닥만(마통은 자료 있으면 표시)
let historyZoom = 1, historyBarsAll = false;
async function hidxEnsure(fromYm){
  if(!fromYm || fromYm.length < 6) return;
  if(!hidxData){ try{ hidxData = JSON.parse(localStorage.getItem(HIDX_KEY) || 'null'); }catch(e){} }
  const p1 = Math.floor(Date.UTC(+fromYm.slice(0,4), +fromYm.slice(4,6) - 1, 1) / 1000) - 12*86400, today = new Date().toLocaleDateString('sv');
  if(hidxData && hidxData.day === today && hidxData.from <= p1) return;
  if(hidxBusy || Date.now() - hidxFailAt < 5*60000) return;
  hidxBusy = true;
  try{
    const p2 = Math.floor(Date.now()/1000) + 86400, out = { day: today, from: p1, idx: {} };
    await Promise.all(HIDX.map(async cfg => {
      const res = await fetchViaProxy(`https://query1.finance.yahoo.com/v8/finance/chart/${encodeURIComponent(cfg.sym)}?period1=${p1}&period2=${p2}&interval=1d&_=${Date.now()}`, 15000);
      if(!res || !res.ok) throw new Error('지수 ' + cfg.key);
      const j = await res.json(), r = j && j.chart && j.chart.result && j.chart.result[0];
      if(!r || !r.timestamp) throw new Error('지수 자료 없음');
      const off = (r.meta && r.meta.gmtoffset) || 0, cl = ((r.indicators.quote || [])[0] || {}).close || [], d = [], c = [];
      r.timestamp.forEach((t, i) => { if(cl[i] == null) return; const ds = new Date((t + off) * 1000).toISOString().slice(0, 10);
        if(d.length && d[d.length-1] === ds){ c[c.length-1] = +cl[i].toFixed(2); return; } d.push(ds); c.push(+cl[i].toFixed(2)); });
      out.idx[cfg.key] = { d, c };
    }));
    hidxData = out; try{ localStorage.setItem(HIDX_KEY, JSON.stringify(out)); }catch(e){}
    if(state.activeId === '__history__' && !historyListMode) render();
  }catch(e){ hidxFailAt = Date.now(); }
  finally{ hidxBusy = false; }
}
// labels = 화면에 그리는 달(YYYYMM)들. 각 달의 마지막 개장일 종가를 점으로, 그 사이 일별 종가를 궤적으로. base = 첫 달 자산
function hidxDense(cfg, labels, base){
  const sr = hidxData && hidxData.idx && hidxData.idx[cfg.key]; if(!sr || !sr.d || !sr.d.length || !(base > 0) || labels.length < 2) return null;
  const endIdx = ym => { const lim = ym.slice(0,4) + '-' + ym.slice(4,6) + '-31'; let lo = 0, hi = sr.d.length - 1, r = -1; while(lo <= hi){ const m = (lo + hi) >> 1; if(sr.d[m] <= lim){ r = m; lo = m + 1; } else hi = m - 1; } return r; };
  const e = labels.map(endIdx); if(e[0] < 0) return null;
  const b = sr.c[e[0]]; if(!(b > 0)) return null;
  const pts = [[0, base]], ends = [[0, base]];
  for(let i = 1; i < e.length; i++){
    const a = e[i-1], z = e[i];
    if(z <= a){ const v = pts[pts.length-1][1]; pts.push([i, v]); ends.push([i, v]); continue; }
    for(let k = a + 1; k <= z; k++) pts.push([(i - 1) + (k - a) / (z - a), sr.c[k] / b * base]);
    ends.push([i, sr.c[z] / b * base]);
  }
  return { name: cfg.name, color: cfg.color, pts, ends };
}
// 막대: 화면 아래 끝까지 스크롤 없이 다 보이게 굵기를 정함(4~13px). 4px로도 다 안 들어가면 최근 달부터 들어가는 만큼만 보이고 ▼로 전체
function historyBarsFit(){
  const panel = document.getElementById('panel'); if(!panel) return;
  const grps = [...panel.querySelectorAll('.tb2-grp')]; if(!grps.length) return;
  const n = grps[0].querySelectorAll('.tb2-row').length; if(!n) return;
  const top = grps[0].getBoundingClientRect().top + window.scrollY;
  let avail = window.innerHeight - top - 46; if(avail < 150) avail = 3 * Math.min(n, 12) * 8 + 20;   // 화면이 낮으면(가로보기 등) 12줄 기준
  const per = (avail - 20) / 3;
  let bar = Math.floor(per / n) - 1, show = n; const trunc = bar < 4;
  if(trunc && !historyBarsAll) show = Math.max(3, Math.floor(per / 5));
  bar = Math.max(4, Math.min(13, bar));
  panel.style.setProperty('--tbh', bar + 'px');
  grps.forEach(g => g.querySelectorAll('.tb2-row').forEach(r => r.classList.toggle('hid', +r.dataset.age >= show)));
  const mb = document.getElementById('tb2More'); if(mb){ mb.style.display = trunc ? 'flex' : 'none'; mb.textContent = historyBarsAll ? '▲' : '▼'; }
}
window.addEventListener('resize', () => { try{ if(state.activeId === '__history__' && !historyListMode){ if(historyLandNow() !== historyLandNow.was) render(); else historyBarsFit(); } }catch(e){} });
function historyLandNow(){ try{ donutCarOn(); return !!mpTouchDev && window.innerWidth > window.innerHeight && window.innerHeight <= 540; }catch(e){ return false; } }   // 휴대폰 가로보기
function renderHistoryPanel(){
  const panel = document.getElementById('panel');""")
# ---- renderHistoryPanel 본문
rep("""      <div>${snapBtnHtml()}</div>${historyListBtnHtml()}<div style="display:flex;justify-content:flex-end;">""",
    """      <div>${snapBtnHtml()}</div><div style="display:flex;align-items:center;gap:6px;">${HIST_NEW ? '<button type="button" class="hz-btn" data-hzoom="-1" title="그래프 축소">−</button>' : ''}${historyListBtnHtml()}${HIST_NEW ? '<button type="button" class="hz-btn" data-hzoom="1" title="그래프 확대">+</button>' : ''}</div><div style="display:flex;justify-content:flex-end;">""")
rep("""  if(hasCreditData) lineSeries.push({ points: creditUsedPoints, color: CREDIT_USED_COLOR, name: '마통', showLabel: false, area: true });
  if(showRegionLines){
    lineSeries.push({ points: domesticPoints, color: '#C7C8CD', name: '국내' });
    lineSeries.push({ points: overseasPoints, color: '#9A9BA1', name: '해외' });
  }
""","""  const lineOn = nm => !HIST_NEW || !historyLineOff[nm];
  if(hasCreditData && lineOn('마통')) lineSeries.push({ points: creditUsedPoints, color: CREDIT_USED_COLOR, name: '마통', showLabel: false, area: true });
  if(showRegionLines){
    if(lineOn('국내')) lineSeries.push({ points: domesticPoints, color: '#C7C8CD', name: '국내' });
    if(lineOn('해외')) lineSeries.push({ points: overseasPoints, color: '#9A9BA1', name: '해외' });
  }
  // 범례 = 선 켜고 끄는 버튼(끈 선은 흐리게). 지수선은 자료가 오면 그려짐
  const hlChip = (nm, color) => `<span class="hl-chip${historyLineOff[nm] ? ' off' : ''}" data-hline="${nm}"><i style="background:${color}"></i>${nm}</span>`;
  const chartOpts = {};
  let chartW = 860, chartH = 205, chartResp = rk === 'all' || rk === '3' || rk === '6';
  let chartLm = rk === '24' ? 'shrink' : (rk === 'all' ? 'sparse' : ((rk === '6' || rk === '12') ? 'small' : 'normal'));
  if(HIST_NEW){
    chartOpts.legendHtml = (hasCreditData ? hlChip('마통', CREDIT_USED_COLOR) : '') + (showRegionLines ? hlChip('국내', '#C7C8CD') + hlChip('해외', '#9A9BA1') : '') + HIDX.map(c => hlChip(c.name, c.color)).join('');
    const labels = filtered.map(s => normalizeLabel(s.label));
    chartOpts.dense = points.length > 1 ? HIDX.filter(c => !historyLineOff[c.name]).map(c => hidxDense(c, labels, points[0].value)).filter(Boolean) : [];
    if(sorted.length) hidxEnsure(normalizeLabel(sorted[0].label));
    const contW = Math.max(280, (panel.clientWidth || 360) - 26), land = historyLandNow(); historyLandNow.was = land;
    const byStep = w => { const st = (w - 60) / Math.max(1, points.length - 1); return st >= 62 ? 'normal' : (st >= 50 ? 'small' : (st >= 34 ? 'shrink' : 'sparse')); };
    if(land){ chartH = Math.max(205, window.innerHeight - 84); if(historyZoom === 1){ chartW = contW; chartResp = false; chartLm = byStep(contW); } }   // 가로보기: 그래프가 화면 높이·폭에 꽉 차게
    if(historyZoom !== 1){   // 확대·축소: 그래프 폭을 배율만큼(화면 폭보다 좁아지지는 않음). 글자 밀도는 점 간격에 맞춤
      const baseW = (chartResp || land) ? contW : 860;
      const minZ = contW / baseW; if(historyZoom < minZ) historyZoom = minZ;
      chartW = Math.round(Math.max(contW, baseW * historyZoom)); chartResp = false; chartLm = byStep(chartW);
    }
  }
""")
rep("""      <div class="trend-wrap">${lineChartSVG(points, lineSeries, 860, 205, rk === '24' ? 'shrink' : (rk === 'all' ? 'sparse' : ((rk === '6' || rk === '12') ? 'small' : 'normal')), rk === 'all' || rk === '3' || rk === '6')}</div>
    </div>""","""      <div class="trend-wrap">${lineChartSVG(points, lineSeries, chartW, chartH, chartLm, chartResp, chartOpts)}</div>
    </div>""")
rep("""    ${trendBarsHTML(filtered, 'name', 'stock', '종목', rk === 'all' || rk === '24', 'stock')}
  `;
  const trendScrollEl = panel.querySelector('.trend-scroll');
  if(trendScrollEl) trendScrollEl.scrollLeft = trendScrollEl.scrollWidth;""","""    ${trendBarsHTML(filtered, 'name', 'stock', '종목', rk === 'all' || rk === '24', 'stock')}
    ${HIST_NEW ? '<div id="tb2More">▼</div>' : ''}
  `;
  const trendScrollEl = panel.querySelector('.trend-scroll');
  if(trendScrollEl) trendScrollEl.scrollLeft = trendScrollEl.scrollWidth;
  if(HIST_NEW){
    panel.querySelectorAll('[data-hline]').forEach(el => el.addEventListener('click', () => {
      const nm = el.dataset.hline; historyLineOff[nm] = !historyLineOff[nm];
      try{ localStorage.setItem(HLINE_KEY, JSON.stringify(historyLineOff)); }catch(e){}
      render();
    }));
    const zoomBy = f => { historyZoom = Math.max(0.3, Math.min(5, historyZoom * f)); if(Math.abs(historyZoom - 1) < 0.06) historyZoom = 1; render(); };
    panel.querySelectorAll('[data-hzoom]').forEach(b => b.addEventListener('click', () => zoomBy(b.dataset.hzoom === '1' ? 1.3 : 1 / 1.3)));
    // 두 손가락으로 벌리기·오므리기 = 확대·축소(손을 떼면 반영)
    const tw = panel.querySelector('.trend-wrap');
    if(tw){ let d0 = 0, d1 = 0; const dist = t => Math.hypot(t[0].clientX - t[1].clientX, t[0].clientY - t[1].clientY);
      tw.addEventListener('touchstart', ev => { if(ev.touches.length === 2){ d0 = d1 = dist(ev.touches); } }, { passive: true });
      tw.addEventListener('touchmove', ev => { if(ev.touches.length === 2 && d0){ d1 = dist(ev.touches); if(ev.cancelable) ev.preventDefault(); } }, { passive: false });
      tw.addEventListener('touchend', ev => { if(d0 && ev.touches.length < 2){ const f = d1 / d0; d0 = 0; if(Math.abs(f - 1) > 0.08) zoomBy(f); } }, { passive: true });
      tw.addEventListener('gesturestart', ev => ev.preventDefault()); }
    const mb = document.getElementById('tb2More'); if(mb) mb.addEventListener('click', () => { historyBarsAll = !historyBarsAll; historyBarsFit(); });
    historyBarsFit(); requestAnimationFrame(historyBarsFit);
    if(historyLandNow() && tw){ try{ window.scrollTo(0, tw.getBoundingClientRect().top + window.scrollY - 74); }catch(e){} }
  }""")
open(fn,'w',encoding='utf-8').write(s); print('ok',fn)
