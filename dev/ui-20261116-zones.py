import sys
fn=sys.argv[1]; s=open(fn,encoding='utf-8').read()
def rep(a,b,n=1):
    global s
    assert s.count(a)==n,(fn,a[:70],s.count(a)); s=s.replace(a,b)
# 1) 자료 모으기
rep("""  const snap = { ks: null, vix: null, y10: null, idx: {}, err: [] };""","""  const snap = { ks: null, vix: null, y10: null, idx: {}, err: [] };
  const zsrc = {};   // 지수 차트의 위험·바닥·VIX 구간 계산용 일봉(2026-11-16)""")
rep("""      if(key === 'kospi') snap.ks = anKs(b);""","""      if(key === 'kospi'){ snap.ks = anKs(b); zsrc.kospi = b; }""")
rep("""        let b = await anGetBars({ key: 'idx:' + key, market: 'US', fetchers: [() => anFetchYahoo(sym, 0.3)] });""",
    """        let b = await anGetBars({ key: 'idx:' + key + 'L', market: 'US', fetchers: [() => anFetchYahoo(sym, 6)] });   // 6년치(차트 5년 구간의 과거 위험·바닥 계산용, 2026-11-16 — 전엔 0.3년)""")
rep("""        snap[key] = anRateInfo(b);""","""        snap[key] = anRateInfo(b); zsrc[key] = b;""")
rep("""  await Promise.all(jobs);
  return snap;
}""","""  await Promise.all(jobs);
  try{ if(zsrc.kospi && zsrc.vix){ anZones = anMarketZones(zsrc.kospi, zsrc.vix, zsrc.y10); anDB.set('mzones1', anZones).catch(() => {}); } }catch(e){}
  return snap;
}

// ── 지수 차트의 위험·바닥 구간(2026-11-16 사용자) ─────────────────────────────────────────────
// 날마다 '시장 위험·바닥 지표'를 과거 자료로 다시 셈. 과거 자료가 있는 항목만(위험 4: 이격도 120↑·RSI 70↑·VIX 25↑ 또는 10일 30%↑ 급등·미국채 10년 10일 +0.3%p↑ /
// 바닥 4: 이격도 90↓·RSI 35↓·52주 고점 -20%↓이면서 20거래일 신저점 없음·VIX 30↑). 신용잔고 비율·'내 종목' 두 항목은 과거 자료가 없어 뺌
// 3개 이상인 날을 차트 뒤에 칠함(개수가 많을수록 진하게), VIX 25↑는 차트 아래 띠. 글자는 없고 마우스를 대거나 누르면 내용
let anZones = null;
const AN_ZONE_A = { 3: 0.14, 4: 0.30, 5: 0.50 };   // 3개·4개·5개 이상 진하기
function anMarketZones(kb, vb, yb){
  const d = kb.dates, c = kb.close, n = c.length, ma = anRoll(c, 50), rs = anRsi(c);
  const vd = vb.dates, vc = vb.close, yd = yb ? yb.dates : [], yc = yb ? yb.close : [];
  const at = (ds, x) => { let lo = 0, hi = ds.length - 1, r = -1; while(lo <= hi){ const m = (lo + hi) >> 1; if(ds[m] <= x){ r = m; lo = m + 1; } else hi = m - 1; } return r; };
  const r1 = v => anOk(v) ? Math.round(v * 10) / 10 : null, r2 = v => anOk(v) ? Math.round(v * 100) / 100 : null;
  const z = { d: [], r: [], b: [], rm: [], bm: [], disp: [], rsi: [], fh: [], vx: [], vp: [], yc: [] };
  for(let i = Math.max(0, n - 1400); i < n; i++){
    if(ma[i] == null) continue;
    const disp = c[i] / ma[i] * 100, rr = rs[i];
    let hi = -Infinity, lo = Infinity, li = i;
    for(let k = Math.max(0, i - 249); k <= i; k++){ if(c[k] > hi) hi = c[k]; if(c[k] < lo){ lo = c[k]; li = k; } }
    const fh = (c[i] / hi - 1) * 100, dsl = i - li;
    const vi = at(vd, d[i]), vx = vi >= 0 ? vc[vi] : null, vp = vi >= 10 ? (vc[vi] / vc[vi - 10] - 1) * 100 : null;
    const yi = at(yd, d[i]), y10 = yi >= 10 ? yc[yi] - yc[yi - 10] : null;
    const R = [disp >= 120, anOk(rr) && rr >= 70, vx != null && (vx >= 25 || (vp != null && vp >= 30)), y10 != null && y10 >= 0.3];
    const B = [disp <= 90, anOk(rr) && rr <= 35, fh <= -20 && dsl >= 20, vx != null && vx >= 30];
    z.d.push(d[i]); z.r.push(R.filter(Boolean).length); z.b.push(B.filter(Boolean).length);
    z.rm.push(R.reduce((m, v, k) => m | (v ? 1 << k : 0), 0)); z.bm.push(B.reduce((m, v, k) => m | (v ? 1 << k : 0), 0));
    z.disp.push(r1(disp)); z.rsi.push(r1(rr)); z.fh.push(r1(fh)); z.vx.push(r1(vx)); z.vp.push(r1(vp)); z.yc.push(r2(y10));
  }
  const vs = Math.max(0, vd.length - 1500); z.vd = vd.slice(vs); z.vc = vc.slice(vs).map(r1); z.at = Date.now();
  return z;
}
function anZoneAt(ds, full){ let lo = 0, hi = ds.length - 1, r = -1; while(lo <= hi){ const m = (lo + hi) >> 1; if(ds[m] <= full){ r = m; lo = m + 1; } else hi = m - 1; } return r; }
const AN_ZR = ['코스피 이격도 120↑', '코스피 RSI 70↑', 'VIX 25↑·급등', '미국채10년 +0.3%p↑'], AN_ZB = ['코스피 이격도 90↓', '코스피 RSI 35↓', '고점 -20%↓·신저점 없음', 'VIX 30↑'];
function anZoneTip(kind, i0, i1, ids){   // 구간 설명: 기간 + 가장 많이 켜진 날의 항목과 값
  const z = anZones, arr = kind === 'r' ? z.r : z.b; let pk = ids[0];
  ids.forEach(k => { if(arr[k] > arr[pk]) pk = k; });
  const m = kind === 'r' ? z.rm[pk] : z.bm[pk], names = kind === 'r' ? AN_ZR : AN_ZB, on = names.filter((_, k) => m & (1 << k));
  const val = `이격 ${z.disp[pk] ?? '-'} · RSI ${z.rsi[pk] ?? '-'} · VIX ${z.vx[pk] ?? '-'}` + (kind === 'r' ? ` · 금리10일 ${z.yc[pk] != null ? (z.yc[pk] >= 0 ? '+' : '') + z.yc[pk] + '%p' : '-'}` : ` · 고점대비 ${z.fh[pk] ?? '-'}%`);
  return `${kind === 'r' ? '시장 위험' : '시장 바닥'} 지표 최대 ${arr[pk]}개 · ${i0} ~ ${i1}\\n${on.join(', ')}\\n${anShort(z.d[pk])}: ${val}`;
}
// 차트 그림에 넣을 구간 사각형(가격 영역 뒤) + VIX 띠. dates = 차트 날짜(yy.mm.dd)
function anZoneSvg(dates, n, x, pt, PH, vy, vh, pl, xr){
  const z = anZones; if(!z || !z.d || !z.d.length) return { back: '', strip: '' };
  const full = s => `20${s.slice(0, 2)}-${s.slice(3, 5)}-${s.slice(6, 8)}`;
  const lv = c => c >= 3 ? Math.min(5, c) : 0;
  const zi = dates.slice(0, n).map(s => anZoneAt(z.d, full(s)));
  const day = j => zi[j] >= 0 ? zi[j] : -1;
  const X0 = j => Math.max(pl, x(j - 0.5)), X1 = j => Math.min(xr, x(j + 0.5));
  let back = '', strip = '';
  // 위험·바닥: 같은 단계가 이어지는 날끼리 한 덩어리. 둘 다 켜진 날은 위(위험)·아래(바닥) 반씩
  for(let j = 0; j < n;){
    const k = day(j), a = k >= 0 ? lv(z.r[k]) : 0, b = k >= 0 ? lv(z.b[k]) : 0;
    let e = j; while(e + 1 < n){ const k2 = day(e + 1); if((k2 >= 0 ? lv(z.r[k2]) : 0) !== a || (k2 >= 0 ? lv(z.b[k2]) : 0) !== b) break; e++; }
    if(a || b){
      const ids = []; for(let q = j; q <= e; q++) if(day(q) >= 0) ids.push(day(q));
      const x0 = X0(j), w = Math.max(1.2, X1(e) - x0), both = a && b, hh = both ? PH / 2 : PH;
      if(a) back += `<rect class="an-zone" x="${x0.toFixed(1)}" y="${pt}" width="${w.toFixed(1)}" height="${hh.toFixed(1)}" fill="rgba(95,184,224,${AN_ZONE_A[a]})" data-zt="${anE(anZoneTip('r', dates[j], dates[e], ids))}"/>`;
      if(b) back += `<rect class="an-zone" x="${x0.toFixed(1)}" y="${(pt + (both ? PH / 2 : 0)).toFixed(1)}" width="${w.toFixed(1)}" height="${hh.toFixed(1)}" fill="rgba(232,123,164,${AN_ZONE_A[b]})" data-zt="${anE(anZoneTip('b', dates[j], dates[e], ids))}"/>`;
    }
    j = e + 1;
  }
  // VIX 띠(25↑ 옅게, 30↑ 진하게)
  const vi = dates.slice(0, n).map(s => anZoneAt(z.vd, full(s)));
  const vl = j => { const v = vi[j] >= 0 ? z.vc[vi[j]] : null; return v == null ? 0 : v >= 30 ? 2 : v >= 25 ? 1 : 0; };
  strip += `<rect class="an-ch-bg" x="0" y="${vy}" width="${xr}" height="${vh}"/>`;
  for(let j = 0; j < n;){
    const a = vl(j); let e = j; while(e + 1 < n && vl(e + 1) === a) e++;
    if(a){ let mx = -Infinity; for(let q = j; q <= e; q++){ const v = z.vc[vi[q]]; if(v > mx) mx = v; }
      const x0 = X0(j), w = Math.max(1.2, X1(e) - x0);
      strip += `<rect class="an-zone" x="${x0.toFixed(1)}" y="${vy}" width="${w.toFixed(1)}" height="${vh}" fill="${a === 2 ? 'rgba(242,166,90,0.85)' : 'rgba(242,166,90,0.40)'}" data-zt="${anE(`VIX ${a === 2 ? '30' : '25'} 이상 · ${dates[j]} ~ ${dates[e]}\\n최고 ${mx}`)}"/>`; }
    j = e + 1;
  }
  return { back, strip };
}
try{ anDB.get('mzones1').then(z => { if(z && z.d && !anZones){ anZones = z; try{ if(state.activeId === '__analysis__') render(); }catch(e){} } }).catch(() => {}); }catch(e){}
// 구간에 마우스를 대거나 누르면 내용(글자는 평소에 안 보임)
(function(){
  let tip = null;
  const show = (el, cx, cy) => { if(!tip){ tip = document.createElement('div'); tip.className = 'mp-tip an-ztip'; document.body.appendChild(tip); }
    tip.textContent = el.getAttribute('data-zt'); tip.style.display = 'block';
    const w = Math.min(260, window.innerWidth - 16); tip.style.left = Math.max(8 + w / 2, Math.min(window.innerWidth - 8 - w / 2, cx)) + 'px'; tip.style.top = cy + 'px'; };
  const hide = () => { if(tip) tip.style.display = 'none'; };
  document.addEventListener('mouseover', e => { const z = e.target.closest && e.target.closest('.an-zone'); if(z) show(z, e.clientX, e.clientY); else if(tip && tip.style.display === 'block' && !(e.target.closest && e.target.closest('.an-chart'))) hide(); });
  document.addEventListener('mousemove', e => { const z = e.target.closest && e.target.closest('.an-zone'); if(z) show(z, e.clientX, e.clientY); else hide(); }, { passive: true });
  document.addEventListener('click', e => { const z = e.target.closest && e.target.closest('.an-zone'); if(z) show(z, e.clientX, e.clientY); else hide(); }, true);
  window.addEventListener('scroll', hide, { passive: true });
})();""")
# 2) 지수 차트 표시
rep("""  ch.lastLabel = '종가';                                // 지수 차트 범례(장중 실시간이면 아래에서 '현재가')""",
    """  ch.lastLabel = '종가';                                // 지수 차트 범례(장중 실시간이면 아래에서 '현재가')
  ch.zone = true;                                      // 위험·바닥·VIX 구간 표시(2026-11-16)""")
rep("""    const W = 660, PH = 170, RH = ch.rsi ? 54 : 0, gap = RH ? 10 : 0, pl = 4, pt = 4, pb = 16;
    const H = pt + PH + gap + RH + pb, xr = W - 2, tx = xr - 4;""","""    const W = 660, PH = 170, RH = ch.rsi ? 54 : 0, gap = RH ? 10 : 0, pl = 4, pt = 4, pb = 16;
    const ZON = !!(anZones && (ch.zone || 'ma200' in ch)), VH = ZON ? 8 : 0, vgap = ZON ? 4 : 0;   // 지수 차트: 위험·바닥 구간 + VIX 띠
    const H = pt + PH + gap + RH + vgap + VH + pb, xr = W - 2, tx = xr - 4;""")
rep("""    o.push(`<rect class="an-ch-bg" x="0" y="${pt}" width="${xr}" height="${PH}"/>`);
    if(F) o.push(""","""    o.push(`<rect class="an-ch-bg" x="0" y="${pt}" width="${xr}" height="${PH}"/>`);
    const ZS = ZON ? anZoneSvg(ch.dates, n, x, pt, PH, pt + PH + gap + RH + vgap, VH, pl, xr) : null;
    if(ZS) o.push(ZS.back + ZS.strip);
    if(F) o.push(""")
rep("""  .mp-tip{position:fixed;z-index:9999;""","""  .an-ztip{white-space:pre-line !important;max-width:260px;text-align:left;line-height:1.45;}
  .an-zone{cursor:pointer;}
  .mp-tip{position:fixed;z-index:9999;""")
open(fn,'w',encoding='utf-8').write(s); print('ok',fn)
