import sys
p = sys.argv[1]; s = open(p, encoding='utf-8').read()
def rep(a, b, cnt=1):
    global s
    assert s.count(a) == cnt, (a[:60], s.count(a)); s = s.replace(a, b)
# 1) 종목별 과거 RSI·배열 줄 모으기
rep("const found = [], failed = [], unresolved = [], stale = [], todayPatched = [], todayMissing = [];",
    "const found = [], failed = [], unresolved = [], stale = [], todayPatched = [], todayMissing = [], zstock = [];")
rep("          const r = anAnalyze(bars, spec.code, h.name);\n",
    "          const r = anAnalyze(bars, spec.code, h.name);\n          try{ zstock.push(Object.assign({ key: spec.key }, anZoneStock(bars))); }catch(e){}   /* 지수 차트 바닥·위험 구간 재계산용(2026-11-16) */\n")
rep("    const msig = anMarketSignals(snap, results);\n    const result = {",
    "    const msig = anMarketSignals(snap, results);\n    try{ const zk = new Set(); await anZoneLog(msig, zstock.filter(x => !x.key || (zk.has(x.key) ? false : (zk.add(x.key), true)))); }catch(e){}\n    const result = {")
rep("    res.msig = anMarketSignals(snap, res.results || []);\n    res.mktAt = Date.now();",
    "    res.msig = anMarketSignals(snap, res.results || []);\n    try{ await anZoneLog(res.msig, null); }catch(e){}\n    res.mktAt = Date.now();")
# 2) 시장 계산 → 기록과 합치기
rep("  try{ if(zsrc.kospi && zsrc.vix){ anZones = anMarketZones(zsrc.kospi, zsrc.vix, zsrc.y10); anDB.set('mzones1', anZones).catch(() => {}); } }catch(e){}",
    "  try{ if(zsrc.kospi && zsrc.vix){ anZoneBase = anMarketZones(zsrc.kospi, zsrc.vix, zsrc.y10); await anMlogP; anZoneApply(); } }catch(e){}")
rep("""// 날마다 '시장 위험·바닥 지표'를 과거 자료로 다시 셈. 과거 자료가 있는 항목만(위험 4: 이격도 120↑·RSI 70↑·VIX 25↑ 또는 10일 30%↑ 급등·미국채 10년 10일 +0.3%p↑ /
// 바닥 4: 이격도 90↓·RSI 35↓·52주 고점 -20%↓이면서 20거래일 신저점 없음·VIX 30↑). 신용잔고 비율·'내 종목' 두 항목은 과거 자료가 없어 뺌
""", """// 기준 = V1의 '시장 위험(6)·바닥(5) 지표' 그대로. 분석할 때마다 그날 판정을 브라우저에 저장(mlog1, 'L')하고 그 기록을 씀.
// 기록이 없는 날은 최근 1년만 지금 기준으로 다시 셈('G': 시장 4항목 + 지금 종목들의 그날 RSI·일봉 배열, 신용잔고는 과거 자료가 없어 빠짐). 1년보다 오래된 날은 표시 안 함
""")
rep("let anZones = null;\n", """let anZones = null, anZoneBase = null, anMlog = null;
const anMlogP = (async () => { try{ anMlog = (await anDB.get('mlog1')) || {}; }catch(e){ anMlog = {}; } return anMlog; })();
function anZoneStock(bars){   // 종목 하나의 최근 300일: RSI 35↓ / 일봉 역배열(5선 ≤ 10선) — '1'·'0'·'-'(자료 없음)
  const c = bars.close, n = c.length, k0 = Math.max(0, n - 300), rs = anRsi(c), s5 = anRoll(c, 5), l10 = anRoll(c, 10);
  let low = '', bear = '';
  for(let i = k0; i < n; i++){ low += anOk(rs[i]) ? (rs[i] <= 35 ? '1' : '0') : '-'; bear += l10[i] != null ? (s5[i] > l10[i] ? '0' : '1') : '-'; }
  return { d: bars.dates.slice(k0), low, bear };
}
function anZoneApply(){   // 차트용 = 시장 계산(값·VIX 띠) + 판정 기록(개수·항목)
  const b = anZoneBase; if(!b || !anMlog) return;
  const z = Object.assign({}, b, { r: [], b: [], rm: [], bm: [], src: [], wk: [], br: [] });
  b.d.forEach(d => { const e = anMlog[d]; z.r.push(e ? e[0] : 0); z.b.push(e ? e[1] : 0); z.rm.push(e ? e[2] : 0); z.bm.push(e ? e[3] : 0); z.src.push(e ? e[4] : ''); z.wk.push(e ? e[5] : null); z.br.push(e ? e[6] : null); });
  anZones = z; anDB.set('mzones1', z).catch(() => {});
}
async function anZoneLog(msig, zs){   // 오늘 판정 저장 + 기록 없는 최근 1년은 지금 기준으로 채움(한 번 채운 날은 그대로)
  await anMlogP; const b = anZoneBase; if(!b || !b.d.length || !msig || !msig.risk || !msig.bottom) return;
  const cnt = m => { let c = 0; for(; m; m >>= 1) c += m & 1; return c; };
  const mask = it => it.reduce((m, x, k) => m | (x[2] ? 1 << k : 0), 0);
  const pf = s => { const m = /^(\\d+)%$/.exec(s || ''); return m ? +m[1] : null; };
  const last = b.d[b.d.length - 1], rm = mask(msig.risk.items), bm = mask(msig.bottom.items);
  anMlog[last] = [cnt(rm), cnt(bm), rm, bm, 'L', pf((msig.bottom.items[4] || [])[1]), pf((msig.risk.items[4] || [])[1])];
  if(zs && zs.length){
    const cut = new Date(Date.parse(last + 'T00:00:00Z') - 365 * 864e5).toISOString().slice(0, 10);
    b.d.forEach((d, i) => {
      if(d < cut || d === last || anMlog[d]) return;
      let n = 0, nw = 0, nb = 0;
      zs.forEach(s => { const k = anZoneAt(s.d, d); if(k < 0) return; n++; if(s.low[k] === '1') nw++; if(s.bear[k] === '1') nb++; });
      if(!n) return;
      const wk = nw / n, br = nb / n, R = (b.rm[i] & 15) | (br >= 0.7 ? 16 : 0), B = (b.bm[i] & 15) | (wk >= 0.3 ? 16 : 0);
      anMlog[d] = [cnt(R), cnt(B), R, B, 'G', Math.round(wk * 100), Math.round(br * 100)];
    });
  }
  try{ await anDB.set('mlog1', anMlog); }catch(e){}
  anZoneApply();
}
""")
rep("const AN_ZR = ['코스피 이격도 120↑', '코스피 RSI 70↑', 'VIX 25↑·급등', '미국채10년 +0.3%p↑'], AN_ZB = ['코스피 이격도 90↓', '코스피 RSI 35↓', '고점 -20%↓·신저점 없음', 'VIX 30↑'];",
    "const AN_ZR = ['코스피 이격도 120↑', '코스피 RSI 70↑', 'VIX 25↑·급등', '미국채10년 +0.3%p↑', '내 종목 70%↑ 역배열', '신용잔고 비율 상위'], AN_ZB = ['코스피 이격도 90↓', '코스피 RSI 35↓', '고점 -20%↓·신저점 없음', 'VIX 30↑', '내 종목 30%↑ RSI 35↓'];")
rep("""(kind === 'r' ? ` · 금리10일 ${z.yc[pk] != null ? (z.yc[pk] >= 0 ? '+' : '') + z.yc[pk] + '%p' : '-'}` : ` · 고점대비 ${z.fh[pk] ?? '-'}%`);
  return `${kind === 'r' ? '시장 위험' : '시장 바닥'} 지표 최대 ${arr[pk]}개 · ${i0} ~ ${i1}\\n${on.join(', ')}\\n${anShort(z.d[pk])}: ${val}`;""",
    """(kind === 'r' ? ` · 금리10일 ${z.yc[pk] != null ? (z.yc[pk] >= 0 ? '+' : '') + z.yc[pk] + '%p' : '-'} · 내 종목 역배열 ${z.br && z.br[pk] != null ? z.br[pk] + '%' : '-'}` : ` · 고점대비 ${z.fh[pk] ?? '-'}% · 내 종목 RSI35↓ ${z.wk && z.wk[pk] != null ? z.wk[pk] + '%' : '-'}`);
  const src = z.src && z.src[pk] === 'L' ? '그날 판정 기록' : '지금 기준으로 다시 계산' + (kind === 'r' ? '(신용잔고 제외)' : '');
  return `${kind === 'r' ? '시장 위험' : '시장 바닥'} 지표 최대 ${arr[pk]}개 · ${i0} ~ ${i1}\\n${on.join(', ')}\\n${anShort(z.d[pk])}: ${val}\\n${src}`;""")
open(p, 'w', encoding='utf-8').write(s)
