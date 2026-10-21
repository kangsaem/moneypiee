// 200일선 붕괴 사례 페이지 공용 코드(2026-10-14) — kospi200.html · spx200.html · ndx200.html
// 페이지마다 window.C200 = { key, name, live: 'naver' | 'yahoo', naver, yahoo, issues: { 'YYYY-MM-DD': '이슈' }, missText, archive, autoNotes }
// 사례 값·그래프 일봉 = crash200_<key>.json (moneypier crash200.py, GitHub Actions에서 계산해 이 저장소로 복사)
// 맨 위 = 현재 지수 + 진행 중 국면(실시간 현재가로 다시 계산), 아래 = 하락률 구간별 사례 카드(날짜·칩 / 세부내용 버튼·이슈 / 그래프 / 세부내용)
'use strict';
const CFG = window.C200;
const HOLD_DAYS = 40;
const $ = id => document.getElementById(id);

// ---------- 공용 ----------
const PROXY_PRIMARY = 'https://moneypie-proxy.y0n2.workers.dev/?url=';
const PROXY_SECONDARY = 'https://moneypie-proxy2-1091905448059.asia-northeast3.run.app/?url=';
function fetchWithTimeout(url, opts, ms){
  const c = new AbortController(); const t = setTimeout(() => c.abort(), ms || 4000);
  return fetch(url, { ...opts, signal: c.signal }).finally(() => clearTimeout(t));
}
async function fetchViaProxy(targetUrl, timeoutMs, retries){
  timeoutMs = timeoutMs || 7000; retries = retries != null ? retries : 1;
  let res = null;
  try{
    for(let a = 0; a <= retries; a++){
      res = await fetchWithTimeout(PROXY_PRIMARY + encodeURIComponent(targetUrl), { cache: 'no-store' }, timeoutMs);
      if(res.status !== 429) break;
      if(a < retries) await new Promise(r => setTimeout(r, 1500));
    }
  }catch(e){ res = null; }
  if(res && res.ok) return res;
  try{ return await fetchWithTimeout(PROXY_SECONDARY + encodeURIComponent(targetUrl), { cache: 'no-store' }, timeoutMs); }
  catch(e){ if(res) return res; throw e; }
}
const num = v => { const x = parseFloat(String(v == null ? '' : v).replace(/,/g, '')); return isFinite(x) ? x : null; };
const pad = n => String(n).padStart(2, '0');
const kstNow = () => new Date(Date.now() + 9 * 3600e3);
const kstKey = k => `${k.getUTCFullYear()}-${pad(k.getUTCMonth() + 1)}-${pad(k.getUTCDate())}`;
const nyKey = ms => { const p = new Intl.DateTimeFormat('en-CA', { timeZone: 'America/New_York', year: 'numeric', month: '2-digit', day: '2-digit' }).format(new Date(ms)); return p; };
const fmt = x => x == null ? '–' : x.toLocaleString('ko-KR', { minimumFractionDigits: 2, maximumFractionDigits: 2 });
const tri = (x, nd) => `${x > 0 ? '▲' : x < 0 ? '▼' : ''}${Math.abs(x).toFixed(nd == null ? 1 : nd)}<span class="pc">%</span>`;   // ▲▼ + 작은 %
const cls = x => x > 0 ? 'up' : x < 0 ? 'dn' : '';
const esc = s => String(s).replace(/[&<>"]/g, c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]));
const median = a => { const s = a.slice().sort((x, y) => x - y), n = s.length; return n ? (n % 2 ? s[(n - 1) / 2] : (s[n / 2 - 1] + s[n / 2]) / 2) : null; };
const ymd = s => s.length === 8 ? `${s.slice(0, 4)}-${s.slice(4, 6)}-${s.slice(6, 8)}` : s;
const BANDS = [[-5, '-5% 이상'], [-3, '-3~-5%'], [-2, '-2~-3%'], [-1, '-1~-2%'], [0, '0~-1%']];
const bandOf = chg => { for(const [lim, nm] of BANDS) if(chg <= lim) return nm; return '0~-1%'; };

// ---------- 시세 ----------
// 국장: 네이버 실시간 지수 + 네이버 일봉(2년), 실패 시 야후 / 미장: 야후 일봉(2년) + 메타 현재가
async function liveNaver(){
  const url = `https://polling.finance.naver.com/api/realtime/domestic/index/${CFG.naver}?_=${Date.now()}`;
  let res;
  try{ res = await fetchWithTimeout(url, { cache: 'no-store' }, 3000); if(!res.ok) throw 0; }
  catch(e){ res = await fetchViaProxy(url); }
  if(!res || !res.ok) throw new Error('실시간 지수 응답 없음');
  const row = (await res.json()).datas?.[0];
  if(!row) throw new Error('실시간 지수 데이터 없음');
  return { price: num(row.closePrice), chgPct: num(row.fluctuationsRatio), at: row.localTradedAt || '', tz: '' };
}
function parseNaver(txt){
  const re = /\[\s*["'](\d{8})["']\s*,\s*([-\d.]+)\s*,\s*([-\d.]+)\s*,\s*([-\d.]+)\s*,\s*([-\d.]+)/g, map = new Map(); let m;
  while((m = re.exec(txt))){ const c = parseFloat(m[5]); if(c > 0) map.set(ymd(m[1]), { l: parseFloat(m[4]), c }); }
  return map;
}
async function dailyNaver(years){
  const k = kstNow(), y = k.getUTCFullYear(), d = yy => `${yy}${pad(k.getUTCMonth() + 1)}${pad(k.getUTCDate())}`;
  const res = await fetchViaProxy(`https://api.finance.naver.com/siseJson.naver?symbol=${CFG.naver}&requestType=1&startTime=${d(y - years)}&endTime=${d(y)}&timeframe=day`, 20000);
  if(!res || !res.ok) throw new Error('네이버 일봉 ' + (res ? res.status : '응답 없음'));
  const map = parseNaver(await res.text());
  if(map.size < 320) throw new Error('네이버 일봉 부족');
  return map;
}
async function chartYahoo(range){
  const res = await fetchViaProxy(`https://query1.finance.yahoo.com/v8/finance/chart/${encodeURIComponent(CFG.yahoo)}?range=${range}&interval=1d`, 15000);
  if(!res || !res.ok) throw new Error('야후 일봉 응답 없음');
  const r = (await res.json()).chart?.result?.[0];
  const ts = r?.timestamp || [], q = r?.indicators?.quote?.[0] || {}, map = new Map(), us = CFG.live === 'yahoo';
  ts.forEach((t, i) => { const c = q.close?.[i]; if(c > 0) map.set(us ? nyKey(t * 1000) : kstKey(new Date(t * 1000 + 9 * 3600e3)), { l: q.low?.[i] > 0 ? q.low[i] : c, c }); });
  if(map.size < 320) throw new Error('야후 일봉 부족');
  return { map, meta: r.meta || {} };
}
async function loadLive(){
  if(CFG.live === 'naver'){
    const [live, daily] = await Promise.all([liveNaver(), dailyNaver(2).catch(async () => (await chartYahoo('2y')).map)]);
    return { live, daily };
  }
  const { map, meta } = await chartYahoo('2y');
  const t = meta.regularMarketTime ? meta.regularMarketTime * 1000 : Date.now(), day = nyKey(t), keys = [...map.keys()].filter(k => k < day).sort();
  const price = meta.regularMarketPrice || map.get(day)?.c, prev = map.get(keys[keys.length - 1])?.c;
  const at = new Intl.DateTimeFormat('en-CA', { timeZone: 'America/New_York', hour: '2-digit', minute: '2-digit', hour12: false }).format(new Date(t));
  return { live: { price, chgPct: prev ? (price / prev - 1) * 100 : null, at: `${day}T${at}`, tz: ' (뉴욕)' }, daily: map };
}

// ---------- 진행 중 국면 추적(현재가 포함) ----------
function weekKey(key){
  const d = new Date(key + 'T00:00:00Z'), dow = (d.getUTCDay() + 6) % 7;
  return kstKey(new Date(d.getTime() - dow * 864e5 + 9 * 3600e3 - 9 * 3600e3));
}
let TRACK_FROM = '9999';
function compute(live, daily){
  const todayKey = live.at && /^\d{4}-\d{2}-\d{2}/.test(live.at) ? live.at.slice(0, 10) : kstKey(kstNow());
  const todayBar = daily.get(todayKey);
  const keys = [...daily.keys()].filter(k => k < todayKey).sort();
  const closes = keys.map(k => daily.get(k).c);
  const p = live.price != null ? live.price : (todayBar ? todayBar.c : null);
  if(p == null || closes.length < 300) throw new Error('계산할 데이터 부족');
  const n = closes.length, sum = a => a.reduce((s, x) => s + x, 0);
  const prevClose = closes[n - 1], maPrev = sum(closes.slice(n - 200)) / 200, maToday = (sum(closes.slice(n - 199)) + p) / 200;
  const wk = new Map(); keys.forEach((k, i) => wk.set(weekKey(k), closes[i])); wk.set(weekKey(todayKey), p);
  const wv = [...wk.entries()].sort((a, b) => a[0] < b[0] ? -1 : 1).map(e => e[1]);
  const w60 = wv.length >= 60 ? sum(wv.slice(-60)) / 60 : null;
  const chgPct = live.chgPct != null ? live.chgPct : (p / prevClose - 1) * 100;
  const lows = keys.map(k => daily.get(k).l > 0 ? daily.get(k).l : daily.get(k).c);
  const todayLow = todayBar && todayBar.l > 0 ? Math.min(todayBar.l, p) : p;
  const ep = trackEpisode([...keys, todayKey], [...closes, p], chgPct, [...lows, todayLow]);
  return { todayKey, p, chgPct, prevClose, maPrev, maToday, w60, ep, D: [...keys, todayKey], C: [...closes, p] };
}
// TRACK_FROM(진행 중 사례 이탈일, 없으면 마지막 계산일) 이후 첫 이탈부터: 바닥까지·60주선·200일선 위 연속·실패. 40일 채우면 안정 → 그 뒤 새 이탈은 새로 추적
function trackEpisode(D, C, liveChg, L){
  const N = C.length, ma = new Array(N).fill(null);
  let s = 0;
  for(let i = 0; i < N; i++){ s += C[i]; if(i >= 200) s -= C[i - 200]; if(i >= 199) ma[i] = s / 200; }
  const wk = D.map(weekKey), lastOfWeek = new Map();
  D.forEach((d, i) => lastOfWeek.set(wk[i], C[i]));
  const weeks = [...lastOfWeek.keys()].sort();
  const w60At = i => { const k = weeks.indexOf(wk[i]); if(k < 59) return null; let t = C[i]; for(let j = k - 59; j < k; j++) t += lastOfWeek.get(weeks[j]); return t / 60; };
  let ep = null;
  const done = [];
  const fin = e => {
    const end = e.recovered ? e.runFromIdx : N; let mi = e.b; for(let k = e.b; k < end; k++) if(C[k] < C[mi]) mi = k;
    e.min = C[mi]; e.minAt = mi; e.drop = (e.min / C[e.b] - 1) * 100; e.dropDays = e.minAt - e.b; if(e.recovered) e.recDays = e.runFromIdx - e.b;
    e.prevClose = C[e.b - 1]; e.stabPct = e.recovered ? (C[e.runFromIdx] / e.prevClose - 1) * 100 : null;
    e.idxRec = null; e.idxRecDays = null;
    if(e.recovered) for(let k = e.runFromIdx; k < N; k++) if(C[k] >= e.prevClose){ e.idxRec = D[k]; e.idxRecDays = k - e.runFromIdx; e.idxRecN = k - e.b + 1; break; }
    return e;
  };
  for(let i = 1; i < N; i++){
    if(D[i] < TRACK_FROM || ma[i] == null || ma[i - 1] == null) continue;
    const above = C[i] >= ma[i];
    if(!ep || ep.recovered){
      if(C[i - 1] > ma[i - 1] && C[i] < ma[i]){
        if(ep) done.push(fin(ep));
        ep = { b: i, date: D[i], chg: i === N - 1 && liveChg != null ? liveChg : (C[i] / C[i - 1] - 1) * 100,
               prevGap: (C[i - 1] / ma[i - 1] - 1) * 100, run: 0, fail: 0, recovered: null };
        const w = w60At(i);
        ep.w60b = w ? (C[i] / w - 1) * 100 : null;
        ep.w60 = w == null ? null : C[i] <= w ? { already: true } : (L && L[i] <= w ? { days: 0, date: D[i], pc: (w / C[i - 1] - 1) * 100 } : null);
      }
      continue;
    }
    if(!ep.w60 && L && !ep.recovered){ const w = w60At(i); if(w != null && L[i] <= w) ep.w60 = { days: i - ep.b, date: D[i], pc: (w / C[ep.b - 1] - 1) * 100 }; }
    if(above){ ep.run++; if(ep.run === 1){ ep.runFrom = D[i]; ep.runFromIdx = i; } if(ep.run >= HOLD_DAYS) ep.recovered = ep.runFrom; }
    else { if(ep.run > 0) ep.fail++; ep.run = 0; }
  }
  if(ep){ fin(ep); ep.nowAbove = C[N - 1] >= ma[N - 1]; ep.done = done; ep.D = D; ep.C = C; }
  return ep;
}

// ---------- 화면 뼈대 ----------
const CELL = ['전날 200일선 대비위치', '이후 바닥까지', '60주선까지', '200일선 안정', '돌파후 재이탈', '지수회복까지'];
const LV_IDS = ['lvPrevGap', 'lvDrop', 'lvW60', 'lvUp', 'lvFail', 'lvRec'];
const LV_LAB = Object.fromEntries(LV_IDS.map((id, i) => [id, i === 3 ? '최근 200일선 돌파후' : CELL[i]]));
// 그래프 색 설명(V1 지수 차트 범례와 같은 크기) — 세부내용 버튼·이슈 줄 오른쪽
const GLG = `<span class="glg"><span class="lgi"><i class="sw sw-close"></i>종가</span><span class="lgi"><i class="sw sw-w5"></i>5주 <i class="sw sw-w10"></i>10주</span><span class="lgi"><i class="sw sw-w60"></i>60주</span><span class="lgi"><i class="sw sw-ma200"></i>200일</span></span>`;
// 다른 지수 겹쳐 보기 칩(2026-10-14): 본인 페이지 지수는 빼고, 누른 카드에만 그 지수 종가(첫날 값을 맞춘 등락 비교)를 겹쳐 그림
const XN = { kospi: '코스피', spx: 'S&P500', ndx: '나스닥' }, XC = { kospi: '#F2A65A', spx: '#5FB8E0', ndx: '#E87BA4' };
const XOTH = Object.keys(XN).filter(k => k !== CFG.key);
const XCHIPS = `<span class="xchips">${XOTH.map(k => `<button type="button" class="xchip" data-x="${k}" style="--xc:${XC[k]}" aria-pressed="false">${XN[k]}</button>`).join('')}</span>`;
const cv = (k, inner, c2, id) => `<div class="cv${c2 ? ' ' + c2 : ''}"${id ? ` id="${id}"` : ''}><span class="k">${k}</span>${inner}</div>`;
function skeleton(){
  $('c200').innerHTML = `
  <details class="sec acc live" id="live" open>
    <summary><span class="st lv-st"><span class="lv-lines"><span id="lvL1h"><span id="lvL1">${esc(CFG.name)} –</span><span id="lvL1c"></span></span><span id="lvL2"></span><span class="dim" id="lvTime">불러오는 중…</span></span><span class="lv-btns"><span id="reloadPricesLabel" style="display:none;height:26px;box-sizing:border-box;align-items:center;font-size:11px;line-height:1.3;color:var(--text-dim);"></span><button id="reloadPricesBtn" title="시세 새로고침" aria-label="시세 새로고침" style="width:26px;height:26px;flex-shrink:0;display:flex;align-items:center;justify-content:center;background:#D4FF3D;color:#111;border:none;border-radius:6px;font-size:13px;font-weight:700;cursor:pointer;">↻</button></span></span><span class="closeall"><span class="xpages">${XOTH.map(k => `<a class="xpage" style="--xc:${XC[k]}" href="${k}200.html?${/[?&]embed=1/.test(location.search) ? 'embed=1&' : ''}v=${Math.floor(Date.now() / 60000)}">▶ ${XN[k]}</a>`).join('')}</span><button type="button" id="closeAll"><i class="cchev"></i><span id="closeAllTx">전체 열기</span></button><span class="ca-sp"></span></span></summary>
    <div class="cards"><div class="case" id="lvRow">
      <div class="ch"><span class="date" id="lvDate">–</span><span id="lvChg"></span><span id="lvRecChip"></span></div>
      <div class="ch2" id="lvCh2" hidden><button type="button" class="dbtn" aria-expanded="true">세부내용 ▴</button><span class="an-cper" id="lvPer"></span><span class="issue" id="lvIssue"></span></div>
      <div class="cgrid">${LV_IDS.map(id => cv(LV_LAB[id], '–', 'dim', id)).join('')}</div>   <!-- 진행 중 국면: 세부내용 열린 채로 시작(2026-10-15) -->
      <div class="lvstat" id="lvStat" hidden></div>
      <div class="glrow" id="lvGl">${GLG.replace('종가', '현재가')}${XCHIPS}</div>
      <div class="gch" id="lvG"></div>
    </div></div>
  </details>
  <div id="bands"></div>
  ${CFG.autoNotes ? '<div class="note" id="autoNotes"></div>' : ''}`;
}

// ---------- 맨 위(현재 지수 + 진행 중 국면) ----------
// 지금 200일선 이탈 중(진행 중 국면)이면 그 국면이 속한 하락률 구간 탭을 연분홍으로(닫힌 상태일 때만, CSS)
let NOW_BAND = null;
function markBand(nm){ NOW_BAND = nm; document.querySelectorAll('details.acc[data-band]').forEach(d => d.classList.toggle('nowband', d.dataset.band === nm)); }
function render(r, live){
  const at = live.at ? live.at.slice(0, 16).replace('T', ' ') : '';
  $('lvTime').textContent = `${r.todayKey}${at && at.length > 11 ? ' · ' + at.slice(11) : ''}${live.tz || ''}`;
  const ep = r.ep && !r.ep.recovered ? r.ep : null, dayChg = ep ? ep.chg : r.chgPct;
  $('lvDate').textContent = ep ? ep.date : r.todayKey;
  $('lvChg').innerHTML = `<span class="chipv day${dayChg > 0 ? ' up' : ''}">${tri(dayChg, 2)}</span>`
    + (ep && ep.drop < 0 && ep.dropDays > 0 ? `<span class="chipv day after">이후 ${tri(ep.drop)}</span>` : '');   // 진행 중 국면도 이후 바닥까지(2026-10-15)
  const set = (id, html, c) => { const el = $(id); el.innerHTML = `<span class="k">${LV_LAB[id]}</span>` + html; el.className = 'cv' + (c ? ' ' + c : ''); };
  const prevGap = ep ? ep.prevGap : (r.prevClose / r.maPrev - 1) * 100;
  set('lvPrevGap', tri(prevGap), cls(prevGap));
  const g200 = (r.p / r.maToday - 1) * 100;
  $('lvL1').textContent = `${CFG.name} ${fmt(r.p)}`;
  $('lvL1c').innerHTML = r.chgPct != null ? tri(r.chgPct, 2) : ''; $('lvL1c').className = cls(r.chgPct);
  $('lvL2').innerHTML = `200일선 ${g200 < 0 ? '아래' : '위'} <span class="${cls(g200)}">${tri(g200, 2)}</span>`;
  LIVE_G200 = g200; statLine();
  if(ep && ep.w60 && ep.w60.days != null) set('lvW60', `${ep.w60.days ? ep.w60.days + '거래일 뒤' : '이탈일'}<span class="d">${ep.w60.pc != null ? '이탈 전날 대비 ' + tri(ep.w60.pc) : ''}</span>`);
  else if(r.w60 != null){
    const g60 = (r.p / r.w60 - 1) * 100;
    if(g60 <= 0) set('lvW60', `이미 아래<span class="d">60주선 ${tri(g60)}</span>`, 'dim');
    else set('lvW60', `<span class="chipv dn">${tri(-(r.w60 / r.p - 1) * 100)}</span><span class="d">더 빠지면 도달</span>`);
  }
  $('lvCh2').hidden = false;
  $('lvRow').classList.toggle('idle', !ep);                 // 진행 중 국면이 없으면: 날짜·칩·세부내용 없이 그래프(기간 탭·범례·겹쳐 보기)만
  if(ep){
    set('lvDrop', `${tri(ep.drop)}<span class="d">${ep.dropDays ? ep.dropDays + '거래일 뒤' : '이탈일이 최저'}</span>`, ep.drop < 0 ? 'dn' : '');
    set('lvUp', ep.nowAbove ? `<span class="big">${ep.run}거래일</span><span class="d">40거래일 유지 = 안정</span>` : `–<span class="d">200일선 아래</span>`, ep.nowAbove ? '' : 'dim');
    set('lvFail', `${ep.fail}회`);
    set('lvRec', `–<span class="d">200일선 안정 뒤 계산</span>`, 'dim');
    $('lvRecChip').innerHTML = `<span class="rchip live">이탈 후 ${ep.D.length - 1 - ep.b}거래일 진행 중</span>`;   // 이탈일 = 0(2026-10-15 통일)
    liveEp = ep; gDraw($('lvG'));
    markBand(bandOf(ep.chg));
  }else{
    ['lvDrop', 'lvUp', 'lvFail', 'lvRec'].forEach(id => set(id, '–', 'dim'));
    liveEp = { idle: true, D: r.D, C: r.C }; $('lvRecChip').innerHTML = ''; gDraw($('lvG'));
    markBand(null);
  }
}

// ---------- 붕괴 통계(2026-10-20 사용자 B안): 맨 위 카드 한 줄(①) + 요약 아래 '통계' 접힘(①②③) — 자료 crash200_stats.json(moneypier crash200_stats.py) ----------
let STATS = null, LIVE_G200 = null;
const SN = { kospi: '코스피', spx: 'S&P500', ndx: '나스닥' };
const pct = (a, b) => b ? Math.round(a / b * 100) : 0;
function statLine(){
  const el = $('lvStat'), P = STATS && STATS.prev && STATS.prev[CFG.key];
  if(!el || !P || LIVE_G200 == null) return;
  const g = LIVE_G200;
  let h = `<span>지금 200일선 ${g < 0 ? '아래' : '위'} <b class="${cls(g)}">${tri(g)}</b> · 과거 이탈 전날 중간 <b>${tri(P.med)}</b> <span class="sd">(${tri(P.min)}~${tri(P.max)}, ${P.n}건)</span></span>`;
  const X = [1, 2, 3].find(x => g > 0 && g <= x);
  if(X){
    const near = STATS.near[CFG.key] || [], a = near.find(r => r.x === X && r.h === 1), b = near.find(r => r.x === X && r.h === 5);
    if(a && b) h += `<span>200일선 위 ${X}% 이내였던 날 → 다음 날 <b>${pct(a.brk, a.brk + a.hold)}%</b> · 5거래일 안 <b>${pct(b.brk, b.brk + b.hold)}%</b> 200일선 아래로</span>`;
  }
  el.innerHTML = h; el.hidden = false;
}
function statFold(){
  if(!STATS || $('stat200')) return;
  const host = $('live');                                    // 2026-10-20: 맨 위 현재 지수 카드(그래프) 바로 아래
  if(!host) return;
  const P = STATS.prev, K = CFG.key;
  const r1 = Object.keys(SN).filter(k => P[k]).map(k => `<tr${k === K ? ' class="me"' : ''}><td>${SN[k]}</td><td>${P[k].n}건</td><td>${tri(P[k].med)}</td><td>${tri(P[k].min)}</td><td>${tri(P[k].max)}</td></tr>`).join('');
  const near = STATS.near[K] || [];
  const cell = (x, hh) => { const r = near.find(v => v.x === x && v.h === hh); return r ? `<b>${pct(r.brk, r.brk + r.hold)}%</b> <span class="sd">${r.brk}/${r.brk + r.hold}일</span>` : '–'; };
  const r2 = [1, 2, 3].map(x => `<tr><td>${x}% 이내</td><td>${cell(x, 1)}</td><td>${cell(x, 5)}</td></tr>`).join('');
  const fl = (STATS.follow || []).filter(f => f.a === K || f.b === K).map(f => `<li><b>${SN[f.a]} → ${SN[f.b]}</b> ${f.n}건 · ${SN[f.b]} 이미 국면 중 ${f.already} <span class="sd">(20거래일 이내 시작 ${f.al20} · 그 전 ${f.alOld})</span> · 이후 5거래일 안 ${f.d5} · 20일 안 ${f.d20} · 60일 안 ${f.d60} · 60일 안 없음 ${f.none}${f.med != null ? ` <span class="sd">(따라간 경우 중간 ${f.med}거래일)</span>` : ''}</li>`).join('');
  host.insertAdjacentHTML('afterend', `<details class="sec acc stat200" id="stat200"><summary><span class="st">통계 · 200일선 위치와 붕괴</span><span class="meta">1996년 이후 · 계산일 ${ymd(STATS.asof)}</span></summary>
  <div class="note">
    <b>① 이탈 전날 종가의 200일선 대비 위치</b>
    <table class="stt"><tr><th>지수</th><th>사례</th><th>중간</th><th>최소</th><th>최대</th></tr>${r1}</table>
    <b>② 종가가 200일선 위 X% 이내인 날 → 200일선 아래로 깨진 비율 (${SN[K]})</b>
    <table class="stt"><tr><th>200일선 위</th><th>다음 날</th><th>5거래일 안</th></tr>${r2}</table>
    <b>③ 한 시장이 국면 이탈한 뒤 다른 시장</b>
    <ul>${fl}</ul>
    <ul class="sd">
      <li>①③ 사례 = 붕괴 사례 페이지의 국면(안정 40거래일 기준), 진행 중 사례는 ①에서 뺌. 표본 지수별 22~26건</li>
      <li>② = 날짜 단위(하루라도 종가가 200일선 아래면 '깨짐', 돌파 후 재붕괴 포함) — 날짜가 서로 겹쳐 독립 표본이 아니고, 국면 기준보다 넓은 정의</li>
      <li>③ = 어느 쪽 200일선이 먼저 깨졌나(순서)이지 누가 위기를 일으켰나(원인)가 아님. 예: 2000년 닷컴은 코스피가 먼저 깨졌지만 진원은 미국. 미장은 같은 날짜라도 코스피 마감 뒤라 코스피 이탈 당일 미장 이탈 = 이후 1거래일</li>
      <li>'이미 국면 중'은 다른 시장이 그보다 먼저 이탈해 아직 안정 전인 경우 — 20거래일 이내 시작이면 가까운 연동, 그 전이면 이미 오래 아래</li>
    </ul>
  </div></details>`);
}
async function statLoad(){
  try{
    const r = await fetch(`crash200_stats.json?v=${CFG.v || ''}`, { cache: 'no-cache' });
    if(!r.ok) return;
    STATS = await r.json();
    statFold(); statLine();
  }catch(e){}
}

// ---------- 사례 카드 ----------
let DATA = null, BIG = null;
function issueHtml(c){
  const t = (CFG.issues || {})[c.date] || c.issue;          // 보관 사례는 파일의 issue(나중에 채움)
  const cov = c.covid && !(t || '').includes('코로나') ? '<span class="covid">+ 코로나19</span>' : '';
  if(!t) return CFG.missText ? `<span class="issue miss">이슈 확인 못 함</span>${cov}` : cov;
  return `<span class="issue${c.date === BIG ? ' big' : ''}">${esc(t)}</span>${cov}`;
}
function cardCells(c){
  const dropTxt = c.dropDays > 0 && c.drop < 0
    ? (c.date === BIG ? `<span class="chipv big">${tri(c.drop)}</span>` : tri(c.drop)) + `<span class="d">${c.dropDays === 1 ? '다음 날' : c.dropDays + '거래일 뒤'}</span>` : '없음';
  const w = c.w60 || {};
  const w60 = w.na ? cv(CELL[2], '–<span class="d">60주 자료 부족</span>', 'dim')
            : w.already ? cv(CELL[2], `이미 아래<span class="d">60주선 ${c.w60b != null ? tri(c.w60b) : ''}</span>`, 'dim')
            : w.none ? cv(CELL[2], `미도달<span class="d">60주선 ${c.w60b != null ? tri(c.w60b) + ' 위' : ''}</span>`, 'dim')
            : cv(CELL[2], `${w.days ? w.days + '거래일 뒤' : '이탈일'}<span class="d">${w.pc != null ? '이탈 전날 대비 ' + tri(w.pc) : ''}</span>`);
  const fast = c.stabDays != null && c.stabDays <= 5;
  const stab = c.stab ? cv(CELL[3], `<span class="big">${c.stabDays}거래일 뒤</span>${fast ? '<span class="badge">즉시</span>' : ''}<span class="d">이탈 전날 대비 <span class="${cls(c.stabPct)}">${tri(c.stabPct)}</span></span>`)
                      : cv(CELL[3], '–<span class="d">진행 중</span>', 'dim');
  const rec = c.rec ? cv(CELL[5], `<span class="big rchip">${c.recN - 1}거래일 뒤</span><span class="d">${c.rec}</span>`) : cv(CELL[5], '미회복', 'dim');   // 제목 칩 대신 세부내용에 연두 테두리·글자(2026-10-15)   // recN(이탈일=1) - 1 = 이탈일 0 기준
  return cv(CELL[0], tri(c.prevGap), cls(c.prevGap)) + cv(CELL[1], dropTxt, c.drop < 0 && c.dropDays > 0 && c.date !== BIG ? 'dn' : (c.dropDays > 0 ? '' : 'dim'))
       + w60 + stab + cv(CELL[4], `${c.fails}회`) + rec;
}
function card(c){
  const fast = c.stabDays != null && c.stabDays <= 5;
  return `<div class="case gclosed${fast ? ' fast' : ''}" data-case="${c.date}">
  <div class="ch"><button type="button" class="gtog" aria-expanded="false" aria-label="그래프 열기"><i></i></button><span class="date">${c.date}</span><span class="chipv day">${tri(c.chg, 2)}</span>${c.drop < 0 && c.dropDays > 0 ? `<span class="chipv day after">이후 ${tri(c.drop)}</span>` : ''}${fast ? '<span class="fastx">5거래일 내 회복</span>' : ''}</div>
  <div class="ch2"><button type="button" class="dbtn" aria-expanded="false">세부내용 ▾</button>${issueHtml(c)}</div>
  <div class="cgrid" hidden>${cardCells(c)}</div>
  <div class="glrow">${GLG}${XCHIPS}</div>
  <div class="gch" data-g="${c.date}"></div>
</div>`;
}
// 전체 열기/닫기 버튼(2026-10-14 사용자 A): 모두 닫힘 = ^ '전체 열기', 하나라도 열림 = 뒤집힌 화살표 '전체 닫기'(구간 탭과 같은 회전)
function allState(){
  const any = [...document.querySelectorAll('details.acc[data-band]')].some(d => d.open), b = $('closeAll');
  if(!b) return;
  b.classList.toggle('any', any); $('closeAllTx').textContent = any ? '전체 닫기' : '전체 열기';
}
function renderBands(){
  const cases = DATA.cases.filter(c => !c.open);
  BIG = cases.reduce((m, c) => (!m || c.drop < m.drop ? c : m), null)?.date;   // 바닥까지 하락이 가장 큰 사례 = 주황 강조
  const by = new Map(BANDS.map(([, nm]) => [nm, []]));
  cases.forEach(c => by.get(bandOf(c.chg)).push(c));
  let html = '', first = true;
  BANDS.forEach(([, nm]) => {
    const list = by.get(nm).sort((a, b) => a.date < b.date ? -1 : 1);
    if(!list.length) return;
    const pg = list.map(c => c.prevGap), st = list.map(c => c.stabDays).filter(x => x != null);
    const mn = Math.min(...pg), mx = Math.max(...pg), sg = v => v > 0 ? '▲' : v < 0 ? '▼' : '';
    const rng = mn >= 0 || mx <= 0 ? `${sg(mn || mx)}${Math.abs(mn).toFixed(1)}~${Math.abs(mx).toFixed(1)}` : `${sg(mn)}${Math.abs(mn).toFixed(1)}~${sg(mx)}${mx.toFixed(1)}`;
    const meta = `${list.length}건 · 전날 200일선 대비 ${rng}<span class="pc">%</span> · 200일선 안정 중간값 ${median(st)}거래일`;
    html += `<details class="sec acc" data-band="${nm}">
    <summary><span class="st">${nm} 하락하며 200일선 이탈</span><span class="meta">${meta}</span></summary>
    <div class="cards">${list.map(card).join('')}</div>
  </details>`;
    first = false;
  });
  $('bands').innerHTML = html;
  if(NOW_BAND) markBand(NOW_BAND);
  document.querySelectorAll('details.acc[data-band]').forEach(d => {
    const go = () => {                                         // 사례 그룹을 열면 각 사례는 닫힌 채로(그래프·세부내용, 2026-10-15) — 그래프는 열 때 그림
      if(d.open) d.querySelectorAll('.case[data-case]').forEach(cs => {
        cs.classList.add('gclosed');
        const t = cs.querySelector('.gtog'); if(t){ t.setAttribute('aria-expanded', 'false'); t.setAttribute('aria-label', '그래프 열기'); }
        const g = cs.querySelector('.cgrid'); if(g) g.hidden = true;
        const b = cs.querySelector('.dbtn'); if(b){ b.setAttribute('aria-expanded', 'false'); b.textContent = '세부내용 ▾'; }
      });
      allState();
    };
    d.addEventListener('toggle', go); go();
  });
  if(CFG.autoNotes) renderNotes(cases);
}
// 요약(2026-10-15 사용자): 맨 위 = 전체, 아래 = 구간별 — 바닥까지(하락률·저점까지 거래일)·지수회복까지 최소·최대·중간값만. 나머지 설명은 아래 '자세히' 접힘
function renderSummary(cases){
  const host = CFG.autoNotes ? $('autoNotes') : document.querySelector('.wrap > .note');
  if(!host || host.dataset.sum) return;
  host.dataset.sum = '1';
  const mm = a => a.length ? { min: Math.min(...a), max: Math.max(...a), med: median(a) } : null;
  const line = (title, l) => {
    const dr = mm(l.map(c => c.drop)), dd = mm(l.filter(c => c.drop < 0).map(c => c.dropDays)), rc = mm(l.filter(c => c.rec).map(c => c.recN - 1));
    const un = l.filter(c => !c.rec).length;
    // 하락률은 '최소' = 가장 작게 빠진 값, '최대' = 가장 크게 빠진 값
    const D = v => `<span class="sdn">${tri(v)}</span>`, G = v => `<span class="srec">${v}</span>`;   // 하락 = 하락색, 회복 거래일 = 연두
    const drop = dr ? `바닥까지 최소 ${D(dr.max)} · 최대 ${D(dr.min)} · 중간 ${D(dr.med)}` : '';
    const rec = rc ? `지수회복까지 최소 ${G(rc.min)} · 최대 ${G(rc.max)} · 중간 ${G(rc.med)}거래일${un ? ` <span class="sd">(미회복 ${un}건)</span>` : ''}` : (un ? `지수회복까지 – <span class="sd">(미회복 ${un}건)</span>` : '');
    return `<li${title === '전체' ? ' class="sall"' : ''}><b>${title} (${l.length}건)</b><br>${drop}<br>${rec}</li>`;
  };
  const by = BANDS.map(([, nm]) => [nm, cases.filter(c => bandOf(c.chg) === nm)]).filter(([, l]) => l.length);
  const top = `<ul class="sum">${line('전체', cases)}${by.map(([nm, l]) => line(nm, l)).join('')}</ul>`;
  const old = host.querySelector('ul');
  if(old){                                                     // 자세히: 200일선 안정 → 지수회복까지 → 그래프 설명 → 나머지 순(2026-10-15)
    const li = [...old.children], pick = re => { const i = li.findIndex(x => re.test(x.textContent)); return i < 0 ? null : li.splice(i, 1)[0]; };
    const a = pick(/^200일선 안정 =/), b = pick(/^지수회복까지 =/), c = pick(/^그래프:/);
    if(a) a.innerHTML = a.innerHTML.replace(/^200일선 안정/, '<span class="ssky">200일선 안정</span>');
    old.replaceChildren(...[a, b, c].filter(Boolean), ...li);
  }
  host.innerHTML = `<b>요약</b>${top}<details class="nmore"><summary>자세히</summary>${old ? old.outerHTML : ''}</details>`;
}
// 그래프 표시 설명(요약 맨 위, 2026-10-14)
const G_NOTE = '그래프: <b class="gn-r">▲</b> = 이탈 뒤 최저 종가 날(위로 빨간 점선) · <b class="gn-r">빨간 점선</b> = 200일선 상향 돌파(날짜 = 안정일 돌파) · <b class="gn-b">하늘색 영역</b> = 안정일부터 40거래일(200일선 위 유지로 안정을 확인한 구간) · 선 = 종가(흰)·200일(빨강)·5주·10주·60주(보라)';
function renderNotes(cases){
  const li = [G_NOTE];
  li.push(`200일선 안정 = 200일선 위 ${HOLD_DAYS}거래일 유지(그 첫날까지 거래일 수, 아래 줄은 이탈 전날 지수 대비 안정 첫날 지수). 이후 바닥까지 = 이탈일 종가 → 안정 전까지 최저 종가`);
  li.push('지수회복까지 = 200일선 안정일(포함) 이후 이탈 전날 종가 이상으로 처음 돌아온 날. 60주선까지 = 일봉 저가가 60주선에 처음 닿은 날(아래 줄 = 그날 60주선의 이탈 전날 종가 대비). 거래일 수는 모두 이탈일 = 0(다음 날 = 1거래일 뒤). 돌파후 재이탈 = 40거래일을 못 버티고 다시 깬 횟수');
  li.push(`사례 = 안정된 상태에서 처음 200일선을 깬 날(국면당 한 줄, ${DATA.cases[0] ? DATA.cases[0].date.slice(0, 4) : ''}~ ${cases.length}개 국면)`);
  BANDS.forEach(([, nm]) => {
    const l = cases.filter(c => bandOf(c.chg) === nm); if(!l.length) return;
    const dr = median(l.map(c => c.drop)), st = median(l.map(c => c.stabDays)), rc = median(l.filter(c => c.recN).map(c => c.recN - 1));
    li.push(`<span class="hl2">${nm} (${l.length}건): 바닥까지 중간값 ${tri(dr)} · 200일선 안정 중간값 ${st}거래일${rc != null ? ` · 지수회복 중간값 ${rc}거래일` : ''}</span>`);
  });
  $('autoNotes').innerHTML = `<b>요약</b><ul>${li.map(x => `<li>${x}</li>`).join('')}</ul>`; delete $('autoNotes').dataset.sum;
}
// 세부내용 버튼(날짜 아래·이슈 왼쪽) → 그래프 아래 칸 펼침 / 전체 닫기 = 구간 아코디언·세부내용 모두 닫음(맨 위 현재 지수는 그대로)
document.addEventListener('click', ev => {
  const xp = ev.target.closest('.xpage');
  if(xp){ ev.preventDefault(); ev.stopPropagation(); location.replace(xp.href); return; }   // 방문 기록을 쌓지 않고 이동 → '‹ 머니파이'(뒤로)가 다른 지수 페이지가 아니라 머니파이로 감
  if(ev.target.closest('#closeAll')){
    ev.preventDefault(); ev.stopPropagation();                // 회색 제목 줄 안 버튼 — 맨 위 카드는 접지 않음
    const bands = [...document.querySelectorAll('details.acc[data-band]')];
    if(!bands.some(d => d.open)){ bands.forEach(d => { d.open = true; }); return; }   // 모두 닫혀 있으면 = 전체 열기
    bands.forEach(d => { d.open = false; });
    document.querySelectorAll('.case[data-case] .cgrid').forEach(g => { g.hidden = true; });   // 맨 위 진행 중 카드 세부내용은 그대로
    document.querySelectorAll('.case[data-case]').forEach(c => { c.classList.add('gclosed'); const t = c.querySelector('.gtog'); if(t) t.setAttribute('aria-expanded', 'false'); });
    document.querySelectorAll('.case[data-case] .dbtn').forEach(b => { b.setAttribute('aria-expanded', 'false'); b.textContent = '세부내용 ▾'; });
    return;
  }
  const hit = ev.target.closest('.gtog, .dbtn'), cs = hit && hit.closest('.case[data-case]');
  if(cs){                                                      // 과거 사례: 화살표·세부내용 어느 쪽을 눌러도 그래프·세부내용을 함께 열고 닫음(2026-10-15)
    const t = cs.querySelector('.gtog'), d = cs.querySelector('.dbtn'), g = cs.querySelector('.cgrid');
    const open = cs.classList.contains('gclosed') || (g && g.hidden);
    cs.classList.toggle('gclosed', !open);
    if(t){ t.setAttribute('aria-expanded', open ? 'true' : 'false'); t.setAttribute('aria-label', open ? '닫기' : '열기'); }
    if(g) g.hidden = !open;
    if(d){ d.setAttribute('aria-expanded', open ? 'true' : 'false'); d.textContent = open ? '세부내용 ▴' : '세부내용 ▾'; }
    if(open){ const gc = cs.querySelector('.gch[data-g]'); if(gc) gDraw(gc); }
    return;
  }
  const b = ev.target.closest('.dbtn'); if(!b) return;
  const g = b.closest('.case').querySelector('.cgrid'), open = g.hidden;
  g.hidden = !open; b.setAttribute('aria-expanded', open ? 'true' : 'false'); b.textContent = open ? '세부내용 ▴' : '세부내용 ▾';
});

// ---------- 그래프 ----------
// 종가(흰색)·200일(빨강)·5주·10주·60주(투명도 0.6). 최저 종가 날 = 아래 ▲ + 빨간 점선, 200일선 상향 돌파 = 하늘색 점선(마지막 돌파 = 안정일만 빨간 점선 + 날짜),
// 안정일부터 40거래일 = 하늘색(0.3). 지수회복까지 21거래일 미만이면 앞을 채워 가운데 정렬(채운 앞쪽 = 진회색 0.3)
let liveEp = null;
const G_YEARLY = 300;
const gRoll = (a, n) => { const o = new Array(a.length).fill(null); let t = 0; for(let i = 0; i < a.length; i++){ t += a[i]; if(i >= n) t -= a[i - n]; if(i >= n - 1) o[i] = t / n; } return o; };
const gParse = s => Date.UTC(+s.slice(0, 4), +s.slice(5, 7) - 1, +s.slice(8, 10));
const gFmt = ms => { const d = new Date(ms); return `${d.getUTCFullYear()}-${pad(d.getUTCMonth() + 1)}-${pad(d.getUTCDate())}`; };
const gKey = s => gFmt(gParse(s) + ((5 - new Date(gParse(s)).getUTCDay() + 7) % 7) * 864e5);   // 그 주의 금요일
function gWeekMa(D, C, n){                                     // 주 마지막 거래일에 n주 이평, 사이는 직선 연결(V1과 같음)
  const bd = [], bv = []; let pk = null;
  D.forEach((d, i) => { const k = gKey(d); if(k === pk){ bd[bd.length - 1] = d; bv[bv.length - 1] = C[i]; } else { bd.push(d); bv.push(C[i]); pk = k; } });
  const ma = gRoll(bv, n), pos = new Map(D.map((d, i) => [d, i])), o = new Array(D.length).fill(null);
  bd.forEach((d, j) => { if(ma[j] != null) o[pos.get(d)] = ma[j]; });
  let last = -1;
  for(let i = 0; i < o.length; i++){ if(o[i] == null) continue; if(last >= 0 && i - last > 1) for(let k = last + 1; k < i; k++) o[k] = o[last] + (o[i] - o[last]) * (k - last) / (i - last); last = i; }
  return o;
}
const G_LINES = ['w5', 'w10', 'w60'];
function gChartData(D, C, a, b, o){
  o = o || {};
  const cut = x => x.slice(a, b + 1), ma = gRoll(C, 200);
  const ch = { dates: cut(D).map(s => `${s.slice(2, 4)}.${s.slice(5, 7)}.${s.slice(8, 10)}`), close: cut(C), ma200: cut(ma),
               w5: cut(gWeekMa(D, C, 5)), w10: cut(gWeekMa(D, C, 10)), w60: cut(gWeekMa(D, C, 60)) };
  const from = o.brk != null ? Math.max(a, o.brk) : a;
  ch.ups = [];
  for(let i = Math.max(o.upsAll ? a : from, 1); i <= b; i++) if(ma[i] != null && ma[i - 1] != null && C[i] > ma[i] && C[i - 1] <= ma[i - 1])
    ch.ups.push({ i: i - a, stab: i === o.stab, lab: i === o.stab ? D[i].slice(2).replace(/-/g, '.') : null });
  let lo = from; for(let i = from; i <= b; i++) if(C[i] < C[lo]) lo = i;
  ch.low = o.brk != null ? lo - a : null;                     // 국면이 없으면(평소) 최저 ▲ 없음
  ch.blue = o.stab != null && o.stab <= b ? [o.stab - a, Math.min(b, o.stab + HOLD_DAYS - 1) - a] : null;
  const gr = o.gray ? (Array.isArray(o.gray[0]) ? o.gray : [o.gray]) : [];            // 어둡게 덮을 구간들(좌·우)
  ch.gray = gr.map(r => [Math.max(r[0], a) - a, Math.min(r[1], b) - a]).filter(r => r[1] >= r[0]);
  return ch;
}
function gPath(v, x, y){ let d = '', pen = false; v.forEach((u, i) => { if(u == null){ pen = false; return; } d += (pen ? 'L' : 'M') + x(i).toFixed(1) + ',' + y(u).toFixed(1); pen = true; }); return d; }
function gSvg(ch){
  const close = ch.close, n = close.length;
  if(n < 2) return '<div class="gnone">그래프 자료 부족</div>';
  const keys = G_LINES.concat(['ma200']);
  const W = 660, PH = 170, pl = 4, pt = 4, pb = 26, H = pt + PH + pb, xr = W - 2;
  const vals = close.filter(v => v != null); keys.forEach(k => (ch[k] || []).forEach(v => { if(v != null) vals.push(v); }));
  (ch.over || []).forEach(ov => ov.v.forEach(v => { if(v != null) vals.push(v); }));
  let lo = Math.min(...vals), hi = Math.max(...vals); if(hi === lo) hi = lo + 1;
  const mg = (hi - lo) * .06; lo -= mg; hi += mg;
  const x = i => pl + (xr - pl - 2) * i / (n - 1), y = v => pt + PH * (1 - (v - lo) / (hi - lo)), half = (xr - pl - 2) / (n - 1) / 2;
  const band = (r, c) => { const x0 = Math.max(pl, x(r[0]) - half), x1 = Math.min(xr, x(r[1]) + half); return `<rect class="${c}" x="${x0.toFixed(1)}" y="${pt}" width="${Math.max(1, x1 - x0).toFixed(1)}" height="${PH}"/>`; };
  const o = [`<svg class="an-chart" viewBox="0 0 ${W} ${H}" role="img" aria-label="${esc(CFG.name)} 그래프">`, `<rect class="an-ch-bg" x="0" y="${pt}" width="${xr}" height="${PH}"/>`];
  if(ch.blue && ch.blue[1] >= ch.blue[0]) o.push(band(ch.blue, 'g-blue'));
  const yearly = n > G_YEARLY;
  for(let i = 1; i < n; i++){
    const a = yearly ? ch.dates[i].slice(0, 2) : ch.dates[i].slice(3, 5), b = yearly ? ch.dates[i - 1].slice(0, 2) : ch.dates[i - 1].slice(3, 5);
    if(a !== b){ const xv = x(i).toFixed(1); o.push(`<line class="an-ch-vl" x1="${xv}" x2="${xv}" y1="${pt}" y2="${pt + PH}"/><text class="an-ch-mo" x="${(x(i) + 2).toFixed(1)}" y="${pt + PH - 3}">${yearly ? "'" + a : parseInt(a, 10)}</text>`); }
  }
  keys.slice().reverse().forEach(k => { if(ch[k]) o.push(`<path class="an-ch-${k}" d="${gPath(ch[k], x, y)}"/>`); });
  (ch.over || []).forEach(ov => {                             // 다른 지수: 전체는 흐리게, 그 지수가 자기 200일선 아래인 날만 진하게
    o.push(`<path class="g-ov" style="stroke:${ov.color};opacity:.3" d="${gPath(ov.v, x, y)}"/>`);
    o.push(`<path class="g-ov" style="stroke:${ov.color}" d="${gPath(ov.v.map((v, i) => ov.below[i] || ov.below[i - 1] || ov.below[i + 1] ? v : null), x, y)}"/>`);
  });
  o.push(`<path class="an-ch-close" d="${gPath(close, x, y)}"/>`);
  (ch.gray || []).forEach(r => o.push(band(r, 'g-gray')));   // 핵심 구간 밖(좌우 채운 기간) = 검은색(0.5)으로 선 위를 덮음
  let lab = null;
  ch.ups.forEach(u => {                                       // 200일선 상향 돌파: 하늘색 점선, 안정일 돌파만 빨간 점선
    const xv = x(u.i).toFixed(1);
    o.push(`<line class="${u.stab ? 'g-up s' : 'g-up'}" x1="${xv}" x2="${xv}" y1="${y(close[u.i]).toFixed(1)}" y2="${pt + PH}"/>`);
    if(u.lab) lab = u;
  });
  if(ch.low != null && ch.low >= 0){                          // 최저 종가 날: 빨간 점선 + 아래 ▲
    const xv = x(ch.low);
    o.push(`<line class="g-low" x1="${xv.toFixed(1)}" x2="${xv.toFixed(1)}" y1="${y(close[ch.low]).toFixed(1)}" y2="${pt + PH}"/>`);
    o.push(`<text class="g-lowmk" x="${xv.toFixed(1)}" y="${pt + PH + 10}" text-anchor="middle">▲</text>`);
  }
  const anchor = xv => xv < 60 ? 'start' : xv > xr - 60 ? 'end' : 'middle';
  const ends = [`<text class="an-ch-t" x="${pl}" y="${H - 3}">${ch.dates[0]}</text>`, `<text class="an-ch-t" x="${x(n - 1).toFixed(1)}" y="${H - 3}" text-anchor="end">${ch.dates[n - 1]}</text>`];
  if(lab){
    const xv = x(lab.i);
    if(xv < 70) ends[0] = ''; if(xv > xr - 70) ends[1] = '';
    o.push(`<text class="g-uplab" x="${xv.toFixed(1)}" y="${H - 3}" text-anchor="${anchor(xv)}">${lab.lab}</text>`);
  }
  o.push(ends.join('') + '</svg>');
  const ly = y(close[n - 1]), lt = close[n - 1].toLocaleString('en-US', { maximumFractionDigits: 0 });
  return `<div class="an-svgbox">${o.join('')}<span class="an-lastdot" style="left:${(x(n - 1) / W * 100).toFixed(2)}%;top:${(ly / H * 100).toFixed(2)}%"></span>`
       + `<span class="an-lastlbl" style="left:min(${((x(n - 1) + 6) / W * 100).toFixed(2)}%, calc(100% - ${(lt.length * .6 + .2).toFixed(1)}em));top:calc(${(ly / H * 100).toFixed(2)}% - 5px)">${lt}</span></div>`;
}
// 진행 중 사례 기간 탭(V1과 같음). 3·5년은 머니파이 V1이 이 기기 IndexedDB에 저장한 12년 일봉(bars3:idx:<key>, 같은 사이트)을 앞에 붙임, 없으면 한 번 더 받음
const G_PER = [['3m', '3개월', 63], ['6m', '6개월', 132], ['1y', '1년', 252], ['3y', '3년', 756], ['5y', '5년', 1260]];
let gLivePer = null, gLongP = null;   // null = 기본(진행 중 국면 = 1년, 평소 = 5년), 고르면 그 기간
function gIdbGet(key){
  return new Promise(res => {
    try{
      const rq = indexedDB.open('moneypie-analysis', 1);
      rq.onupgradeneeded = () => { const db = rq.result; if(!db.objectStoreNames.contains('kv')) db.createObjectStore('kv'); };
      rq.onerror = rq.onblocked = () => res(null);
      rq.onsuccess = () => { try{ const g = rq.result.transaction('kv', 'readonly').objectStore('kv').get(key); g.onsuccess = () => res(g.result || null); g.onerror = () => res(null); }catch(e){ res(null); } };
    }catch(e){ res(null); }
  });
}
async function gLongHistory(){
  if(!gLongP) gLongP = (async () => {
    const b = await gIdbGet('bars3:idx:' + CFG.key);
    if(b && b.dates && b.dates.length > 1500) return { D: b.dates, C: b.close };
    const map = CFG.live === 'naver' ? await dailyNaver(6) : (await chartYahoo('10y')).map;
    const D = [...map.keys()].sort(); return { D, C: D.map(d => map.get(d).c) };
  })().catch(e => { gLongP = null; throw e; });
  return gLongP;
}
const XSER = {};
// 저장 파일(crash200 계산일까지) 뒤의 날짜는 실시간 일봉으로 이어 붙임(2026-10-15) — 국장 = 네이버, 미국 = 야후. 각 시장 마지막 마감까지(미장은 하루 늦은 게 정상)
const XLIVE = { kospi: { naver: 'KOSPI' }, spx: { yahoo: '^GSPC' }, ndx: { yahoo: '^IXIC' } };
async function xRecent(k, last){
  const s = XLIVE[k], out = [];
  try{
    if(s.naver){
      const st = last.replace(/-/g, ''), k2 = kstNow(), en = `${k2.getUTCFullYear()}${pad(k2.getUTCMonth() + 1)}${pad(k2.getUTCDate())}`;
      const res = await fetchViaProxy(`https://api.finance.naver.com/siseJson.naver?symbol=${s.naver}&requestType=1&startTime=${st}&endTime=${en}&timeframe=day`, 15000);
      if(res && res.ok) parseNaver(await res.text()).forEach((v, d) => { if(d > last) out.push([d, v.c]); });
    }else{
      const res = await fetchViaProxy(`https://query1.finance.yahoo.com/v8/finance/chart/${encodeURIComponent(s.yahoo)}?range=3mo&interval=1d`, 15000);
      const r = res && res.ok ? (await res.json()).chart?.result?.[0] : null;
      const ts = r?.timestamp || [], q = r?.indicators?.quote?.[0] || {};
      ts.forEach((t, i) => { const c = q.close?.[i], d = nyKey(t * 1000); if(c > 0 && d > last) out.push([d, c]); });
    }
  }catch(e){}
  return out.sort((a, b) => a[0] < b[0] ? -1 : 1);
}
function xSeries(k){
  if(!XSER[k]) XSER[k] = fetch(`crash200_series_${k}.json?v=${CFG.v || ''}`, { cache: 'no-cache' }).then(r => { if(!r.ok) throw new Error(r.status); return r.json(); })
    .then(async j => { const D = j.d.map(ymd), C = j.c.slice(); (await xRecent(k, D[D.length - 1])).forEach(([d, c]) => { D.push(d); C.push(c); }); return { D, C, M: gRoll(C, 200), last: D[D.length - 1] }; })
    .catch(e => { delete XSER[k]; throw e; });
  return XSER[k];
}
let XREADY = null;                                             // 다른 지수 일봉(처음 그래프를 그릴 때 받아 둠)
function xLoadAll(){ if(!XREADY) XREADY = Promise.all(XOTH.map(k => xSeries(k).then(v => [k, v]).catch(() => [k, null]))).then(Object.fromEntries); return XREADY; }
function xAlign(S, dates){                                     // 날짜마다 그 지수의 같은 날(없으면 직전 거래일) 종가·200일선 아래 여부
  let j = 0;
  return dates.map(d => {
    if(!S || d < S.D[0] || d > S.last) return null;
    while(j + 1 < S.D.length && S.D[j + 1] <= d) j++;
    while(j > 0 && S.D[j] > d) j--;
    return { c: S.C[j], below: S.M[j] != null && S.C[j] < S.M[j] };
  });
}
const GP = new WeakMap();                                      // 그래프 칸 → 그리기 값(칩을 누르면 다시 그림)
async function gParams(key){
  if(key === 'live'){
    const e = liveEp; if(!e) return null;
    const per = G_PER.find(p => p[0] === (gLivePer || (e.idle ? '5y' : '1y'))) || G_PER[1];
    let D = e.D, C = e.C, off = 0;   // e.idle = 진행 중 국면 없음(평소 지수 그래프)
    if(per[2] + 330 > D.length){
      try{ const L = await gLongHistory(), pre = []; for(let i = 0; i < L.D.length && L.D[i] < D[0]; i++) pre.push(i);
           if(pre.length){ D = pre.map(i => L.D[i]).concat(D); C = pre.map(i => L.C[i]).concat(C); off = pre.length; } }catch(err){}
    }
    const b = C.length - 1, a = Math.max(0, b - per[2] + 1);
    const per$ = $('lvPer');                                   // 기간 탭 = 세부내용 버튼 오른쪽(2026-10-15), 색상표·다른 지수 칩 = 그래프 바로 위(과거 사례와 같음)
    if(per$) per$.innerHTML = G_PER.map(([k, nm]) => `<button type="button" data-gper="${k}"${k === per[0] ? ' class="on"' : ''}>${nm}</button>`).join('');
    return { D, C, a, b, o: e.idle ? { upsAll: true } : { brk: e.b + off, stab: e.recovered ? e.runFromIdx + off : null, upsAll: true }, prefix: '' };   // 맨 위 그래프는 기간 안 모든 200일선 돌파 점선
  }
  const c = DATA.cases.find(x => x.date === key), g = c && c.g;
  if(!g) return null;
  const D = g.d.map(ymd);
  return { D, C: g.c, a: g.from, b: D.length - 1, o: { brk: g.brk, stab: g.stab, gray: g.gray }, prefix: '' };
}
// 그리기 + 이 카드 칩 상태(그 기간에 200일선 아래인 날이 없으면 흐리게·못 누름)
function gRender(el, P){
  if(!P){ el.innerHTML = '<div class="gnone">그래프 자료 없음</div>'; return; }
  if(P.o && P.o.gray){                                         // 짧은 사례 좌우 채움(검은색으로 덮던 부분)은 그리지 않음(2026-10-15)
    const gr = Array.isArray(P.o.gray[0]) ? P.o.gray : [P.o.gray];
    gr.forEach(r => { if(!r || r.length < 2) return; if(r[0] <= P.a) P.a = Math.max(P.a, r[1] + 1); if(r[1] >= P.b) P.b = Math.min(P.b, r[0] - 1); });
    P.o = Object.assign({}, P.o, { gray: null });
  }
  GP.set(el, P);
  const ch = gChartData(P.D, P.C, P.a, P.b, P.o), cardEl = el.closest('.case'), dates = P.D.slice(P.a, P.b + 1);
  const on = (cardEl && cardEl.dataset.x ? cardEl.dataset.x.split(',') : []).filter(Boolean);
  ch.over = [];
  const X = XREADY && XREADY.done;
  if(X) on.forEach(k => {
    const al = xAlign(X[k], dates), i0 = al.findIndex(v => v);
    if(i0 < 0) return;
    const f = P.C[P.a + i0] / al[i0].c;                        // 첫날(겹치는 첫날) 값을 같게 맞춤
    ch.over.push({ color: XC[k], v: al.map(v => v ? v.c * f : null), below: al.map(v => !!(v && v.below)) });
  });
  el.innerHTML = P.prefix + gSvg(ch);
  if(cardEl) cardEl.querySelectorAll('.xchip').forEach(b => {
    const k = b.dataset.x, has = X ? xAlign(X[k], dates).some(v => v) : true;   // 2026-10-15: 그 기간에 200일선 아래인 날이 없어도 누를 수 있음(선 전체가 연하게) — 자료가 아예 없을 때만 못 누름
    b.disabled = !has; b.classList.toggle('na', !has);
    const pressed = on.includes(k) && has; b.setAttribute('aria-pressed', pressed ? 'true' : 'false');
  });
}
async function gDraw(el){
  if(!el) return;
  const key = el.id === 'lvG' ? 'live' : el.dataset.g;
  if(key !== 'live' && el.dataset.drawn) return;
  el.dataset.drawn = '1';
  try{ gRender(el, await gParams(key)); }catch(e){ el.innerHTML = `<div class="gnone">그래프를 그리지 못함 (${esc(e.message || e)})</div>`; delete el.dataset.drawn; }
  if(!XREADY) xLoadAll().then(X => {                            // 처음 받은 뒤: 이미 그린 그래프의 칩 상태를 갱신
    XREADY.done = X;
    document.querySelectorAll('.gch').forEach(g => { const P = GP.get(g); if(P) gRender(g, P); });
  });
}
document.addEventListener('click', ev => {                     // 다른 지수 칩: 누른 카드에만 켜고 끔
  const b = ev.target.closest('.xchip'); if(!b || b.disabled) return;
  const cardEl = b.closest('.case'), g = cardEl.querySelector('.gch'), set = new Set((cardEl.dataset.x || '').split(',').filter(Boolean));
  set.has(b.dataset.x) ? set.delete(b.dataset.x) : set.add(b.dataset.x);
  cardEl.dataset.x = [...set].join(',');
  const P = GP.get(g); if(P) gRender(g, P);
});
document.addEventListener('click', ev => {
  const bt = ev.target.closest('#lvPer [data-gper]'); if(!bt) return;
  gLivePer = bt.dataset.gper; gDraw($('lvG'));
});

// ---------- 안정된 국면 자동 보관(2026-10-13 코스피 → 2026-10-14 세 지수 모두) ----------
// 진행 중 국면이 안정(200일선 위 40거래일)되면, 페이지를 열거나 리로드할 때 이 기기에 머니파이 GitHub 토큰(mp-gh-token)이 있으면
// moneypier/<key>200_cases.json에 한 줄 추가(같은 이탈일 건너뜀). 모든 기기가 이 파일을 읽어 해당 구간 끝에 카드로 붙임(다음 crash200 계산 전까지).
// 그래프는 실시간 2년 일봉으로 그림(이탈 전날 ~ 지수회복일·안정일+39 중 늦은 날)
const ARCH = { REPO: 'kangsaem/moneypier', PATH: CFG.key + '200_cases.json', KEY: 'mp-gh-token' };
let LAST = null;                                              // 마지막 실시간 일봉(현재가 포함) — 보관 카드 그래프용
let archList = [];
const ghTok = () => { try{ return localStorage.getItem(ARCH.KEY) || ''; }catch(e){ return ''; } };
const b64dec = s => new TextDecoder().decode(Uint8Array.from(atob(String(s).replace(/\s/g, '')), c => c.charCodeAt(0)));
const b64enc = s => { let x = ''; new TextEncoder().encode(s).forEach(c => { x += String.fromCharCode(c); }); return btoa(x); };
async function archFetch(){
  const tok = ghTok();
  if(tok){
    const r = await fetch(`https://api.github.com/repos/${ARCH.REPO}/contents/${ARCH.PATH}?t=${Date.now()}`, { headers: { Authorization: 'Bearer ' + tok, Accept: 'application/vnd.github+json' }, cache: 'no-store' });
    if(r.status === 404) return { list: [], sha: null };
    if(!r.ok) throw new Error('GitHub ' + r.status);
    const j = await r.json(); return { list: JSON.parse(b64dec(j.content)), sha: j.sha };
  }
  const r = await fetch(`https://raw.githubusercontent.com/${ARCH.REPO}/main/${ARCH.PATH}?t=${Date.now()}`, { cache: 'no-store' });
  if(!r.ok) return { list: [], sha: null };
  return { list: await r.json(), sha: null };
}
function archPaint(){
  const have = new Set(DATA.cases.filter(c => !c.open).map(c => c.date));   // 진행 중(open) 사례는 빼야 안정 뒤 보관 카드가 붙음
  archList.forEach(a => {
    if(have.has(a.date)) return;
    const det = document.querySelector(`details.acc[data-band="${bandOf(a.chg)}"] .cards`); if(!det) return;
    const c = { date: a.date, chg: a.chg, prevGap: a.prevGap, drop: a.drop, dropDays: a.dropDays, w60: a.w60 || { none: true }, w60b: a.w60b,
                stab: a.recovered, stabDays: a.recDays, stabPct: a.stabPct, fails: a.fail, issue: a.issue, rec: a.idxRec, recN: a.idxRecN || (a.idxRec ? a.recDays + (a.idxRecDays || 0) + 1 : null), covid: false };
    det.insertAdjacentHTML('beforeend', card(c).replace(`<div class="gch" data-g="${c.date}"></div>`, `<div class="gch" data-arch="${c.date}"></div>`));
    have.add(a.date);
  });
}
function archGraphs(){
  if(!LAST) return;
  document.querySelectorAll('.gch[data-arch]').forEach(el => {
    if(el.dataset.drawn) return;
    const a = archList.find(x => x.date === el.dataset.arch); if(!a) return;
    const D = LAST.D, C = LAST.C, b = D.indexOf(a.date), u = a.recovered ? D.indexOf(a.recovered) : -1, r = a.idxRec ? D.indexOf(a.idxRec) : -1;
    if(b < 1 || u < 0) return;                                 // 실시간 2년 안에 없으면 그래프 없이
    let R = Math.min(D.length - 1, Math.max(r >= 0 ? r : D.length - 1, u + HOLD_DAYS - 1)), L = b - 1;
    const gray = [], core = R - L + 1;
    if(core < 63){ const pl = Math.floor((63 - core) / 2), L2 = Math.max(0, L - pl), R2 = Math.min(D.length - 1, R + (63 - core - pl));
      if(L2 < L) gray.push([L2, L - 1]); if(R2 > R) gray.push([R + 1, R2]); L = L2; R = R2; }
    el.dataset.drawn = '1';
    gRender(el, { D, C, a: L, b: R, o: { brk: b, stab: u, gray }, prefix: '' });
  });
}
async function archSave(ep){
  const all = ep ? (ep.done || []).concat(ep) : [];
  if(!ghTok() || !all.some(e => e.recovered)) return '';
  const cur = await archFetch();
  const todo = all.filter(e => e.recovered && !cur.list.some(c => c.date === e.date));
  // 이미 보관했는데 그때 지수회복 전이었던 사례: 지금 회복했으면 지수회복 값만 채움(2026-10-16)
  const fill = all.filter(e => e.idxRec && cur.list.some(c => c.date === e.date && !c.idxRec));
  fill.forEach(e => { const c = cur.list.find(x => x.date === e.date); c.idxRec = e.idxRec; c.idxRecDays = e.idxRecDays; c.idxRecN = e.idxRecN; });
  if(!todo.length && !fill.length) return '';
  const recs = todo.map(e => ({ date: e.date, issue: '', chg: +e.chg.toFixed(2), prevGap: +e.prevGap.toFixed(1), drop: +e.drop.toFixed(1), dropDays: e.dropDays,
    w60: e.w60 || null, w60b: e.w60b != null ? +e.w60b.toFixed(1) : null, recovered: e.recovered, recDays: e.recDays, fail: e.fail,
    stabPct: e.stabPct != null ? +e.stabPct.toFixed(2) : null, idxRec: e.idxRec, idxRecDays: e.idxRecDays, idxRecN: e.idxRecN, savedAt: new Date().toISOString().slice(0, 10) }));
  const list = cur.list.concat(recs);
  const body = { message: `${CFG.name} 200일선 붕괴 사례 보관: ${recs.map(c => c.date + ' (회복 ' + c.recovered + ')').concat(fill.map(e => e.date + ' (지수회복 ' + e.idxRec + ')')).join(', ')} [skip ci]`, content: b64enc(JSON.stringify(list, null, 1) + '\n') };
  if(cur.sha) body.sha = cur.sha;
  const r = await fetch(`https://api.github.com/repos/${ARCH.REPO}/contents/${ARCH.PATH}`, { method: 'PUT', headers: { Authorization: 'Bearer ' + ghTok(), Accept: 'application/vnd.github+json', 'Content-Type': 'application/json' }, body: JSON.stringify(body) });
  if(!r.ok) throw new Error(r.status === 401 || r.status === 403 ? '토큰 권한 부족' : 'GitHub ' + r.status);
  archList = list; archPaint(); archGraphs();
  return fill.length && !recs.length ? '사례 지수회복 갱신' : '사례 저장됨';
}

// ---------- 불러오기·리로드 ----------
async function loadAll(){
  try{
    const { live, daily } = await loadLive();
    const r = compute(live, daily);
    LAST = { D: [...[...daily.keys()].filter(k => k < r.todayKey).sort(), r.todayKey] };
    LAST.C = LAST.D.map((d, i) => i === LAST.D.length - 1 ? r.p : daily.get(d).c);
    render(r, live);
    archGraphs();
    archSave(r.ep).then(msg => { if(msg) $('lvTime').textContent += ' · ' + msg; }).catch(e => { $('lvTime').textContent += ' · 사례 저장 실패(' + (e && e.message ? e.message : e) + ')'; });
    return true;
  }catch(e){ $('lvTime').textContent = '불러오지 못함 · ' + (e && e.message ? e.message : '네트워크 오류'); return false; }
}
const LS_KEY = CFG.key + '200:lastRefreshAt', COOLDOWN = 60 * 1000;
let lastAt = 0; try{ lastAt = parseInt(localStorage.getItem(LS_KEY), 10) || 0; }catch(e){}
let cdTimer = null;
function applyCooldown(){
  const btn = $('reloadPricesBtn'), label = $('reloadPricesLabel');
  if(cdTimer){ clearInterval(cdTimer); cdTimer = null; }
  function tick(){
    const el = Date.now() - lastAt, remain = COOLDOWN - el;
    if(remain > 0){
      btn.disabled = true; btn.style.background = '#555555'; btn.style.color = '#999999'; btn.style.cursor = 'default';
      label.style.display = 'flex'; label.textContent = el < 10000 ? '시세 갱신됨' : `${Math.ceil(remain / 60000)}분간 쿨다운`;
    }else{
      btn.disabled = false; btn.style.background = '#D4FF3D'; btn.style.color = '#111'; btn.style.cursor = 'pointer';
      label.style.display = 'none'; if(cdTimer){ clearInterval(cdTimer); cdTimer = null; }
    }
  }
  tick(); cdTimer = setInterval(tick, 1000);
}
(async function start(){
  skeleton();
  $('reloadPricesBtn').addEventListener('click', async ev => {
    ev.preventDefault(); ev.stopPropagation();
    const btn = $('reloadPricesBtn'); if(btn.disabled) return;
    btn.classList.remove('reload-spin'); void btn.offsetWidth; btn.classList.add('reload-spin');
    lastAt = Date.now(); try{ localStorage.setItem(LS_KEY, String(lastAt)); }catch(e){}
    applyCooldown(); await loadAll();
  });
  applyCooldown();
  try{
    const r = await fetch(`crash200_${CFG.key}.json?v=${CFG.v || ''}`, { cache: 'no-cache' });
    if(!r.ok) throw new Error('사례 자료 ' + r.status);
    DATA = await r.json();
  }catch(e){ $('bands').innerHTML = `<div class="note">사례 자료를 불러오지 못함 (${esc(e.message || e)})</div>`; DATA = { cases: [], made: '9999' }; }
  const open = DATA.cases.find(c => c.open);
  TRACK_FROM = open ? open.date : (DATA.made || '9999');     // 진행 중 사례가 있으면 그 이탈일부터, 없으면 마지막 계산일 이후 새 이탈
  renderBands();
  if(!CFG.autoNotes){ const ul = document.querySelector('.note ul'); if(ul) ul.insertAdjacentHTML('afterbegin', `<li>${G_NOTE}</li>`); }
  renderSummary(DATA.cases.filter(c => !c.open));
  statLoad();
  archFetch().then(x => { archList = x.list || []; archPaint(); archGraphs(); }).catch(() => {});   // 세 지수 모두
  loadAll();
})();
