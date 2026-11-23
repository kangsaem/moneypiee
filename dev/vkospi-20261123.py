# 바닥 지표 6번째 VKOSPI(2026-11-23, B안): 'VKOSPI 30 이하 + 최근 60거래일 안에 30을 넘은 적 있음'
# 자료 = 리포트(moneypier)가 KRX Open API로 받아 market.json vkospi {last, chg, date, max60, over60, on, th, win, hist{d, v, on}}
# 판정 기록(mlog1): 바닥 비트 32(6번째) 추가만. e[10] = VKOSPI 반영 여부(1). 반영 안 된 날은 자료가 생기면 비트만 채움(L) / 다시 셈(G·C)
# 칠하는 단계(바닥 3·4·5개 이상) 그대로. 사용: python dev/vkospi-20261123.py test.html
import sys
path = sys.argv[1]; s = open(path, encoding='utf-8').read()
def rep(old, new, n=1):
    global s
    c = s.count(old)
    if c != n: raise SystemExit(f'찾은 개수 {c} != {n}: {old[:90]!r}')
    s = s.replace(old, new)

# 1) market.json 받기: snap.vk(요약만 — 결과 저장이 커지지 않게 hist는 따로)
rep("""if(res && res.ok){ const j = await res.json(); snap.credit = j.credit || null; snap.credit_time = j.time; if(j.credit && j.credit.hist && j.credit.hist.d) anCreditHist = j.credit.hist; }""",
"""if(res && res.ok){ const j = await res.json(); snap.credit = j.credit || null; snap.credit_time = j.time; if(j.credit && j.credit.hist && j.credit.hist.d) anCreditHist = j.credit.hist;
        if(j.vkospi && anOk(j.vkospi.last)){ const { hist, ...vk } = j.vkospi; snap.vk = vk; if(hist && hist.d && hist.d.length) anVkHist = hist; } }   /* VKOSPI(KRX, 2026-11-23) */""")
rep("""let anZones = null, anZoneBase = null, anMlog = null, anCreditHist = null;""",
"""let anVkHist = null;   // 리포트가 내보낸 날짜별 VKOSPI {d, v, on}(2026-11-23)
let anZones = null, anZoneBase = null, anMlog = null, anCreditHist = null;""")
# 받기 실패면 이전 값 유지
rep("""    if(!snap.credit && res.snap && res.snap.credit){ snap.credit = res.snap.credit; snap.credit_time = res.snap.credit_time; }""",
"""    if(!snap.credit && res.snap && res.snap.credit){ snap.credit = res.snap.credit; snap.credit_time = res.snap.credit_time; }
    if(!snap.vk && res.snap && res.snap.vk) snap.vk = res.snap.vk;""")

# 2) 바닥 6번째 항목
rep("""    ['내 종목 30% 이상이 RSI 35 이하', weak != null ? pc(weak) : '-', weak != null ? weak >= 0.3 : null]
  ];""",
"""    ['내 종목 30% 이상이 RSI 35 이하', weak != null ? pc(weak) : '-', weak != null ? weak >= 0.3 : null],
    // 6번째(2026-11-23, B안): 변동성 진정 확인 — 하락이 끝날 때 마지막에 켜지는 항목. 자료 = 리포트(KRX Open API)
    [`VKOSPI ${AN_VK.TH} 이하\\n(최근 ${AN_VK.WIN}거래일 안에 ${AN_VK.TH} 넘은 뒤)`,
      snap.vk ? anF(snap.vk.last, 1) + (snap.vk.max60 > AN_VK.TH ? ` · 최고 ${anF(snap.vk.max60, 0)}` : '') : '-',
      snap.vk ? !!snap.vk.on : null]
  ];""")
rep("""function anMarketSignals(snap, results){""",
"""const AN_VK = { TH: 30, WIN: 60 };   // 리포트 market_report.VK_TH·VK_WIN과 같음
function anMarketSignals(snap, results){""")

# 3) 구간 이름·설명
rep("""'VIX 30↑', '내 종목 30%↑ RSI 35↓'];""", """'VIX 30↑', '내 종목 30%↑ RSI 35↓', 'VKOSPI 30↓(진정)'];""")
rep("""` · 고점대비 ${z.fh[pk] ?? '-'}% · 내 종목 RSI35↓ ${z.wk && z.wk[pk] != null ? z.wk[pk] + '%' : '-'}`);""",
"""` · 고점대비 ${z.fh[pk] ?? '-'}% · 내 종목 RSI35↓ ${z.wk && z.wk[pk] != null ? z.wk[pk] + '%' : '-'}` + (() => { const k = anVkAt(z.d[pk]); return k >= 0 ? ` · VKOSPI ${anVkHist.v[k]}` : ''; })());""")
rep("""    : (sc === 'C' ? '마감 뒤 값이 없어 그날 종가로 다시 계산' : '기록이 없어 지금 기준으로 다시 계산') + (kind === 'r' && !(z.cr && z.cr[pk]) ? '(신용잔고 제외)' : '');""",
"""    : (sc === 'C' ? '마감 뒤 값이 없어 그날 종가로 다시 계산' : '기록이 없어 지금 기준으로 다시 계산') + (kind === 'r' && !(z.cr && z.cr[pk]) ? '(신용잔고 제외)' : '') + (kind === 'b' && !(z.vkf && z.vkf[pk]) ? '(VKOSPI 제외)' : '');""")

# 4) 날짜별 VKOSPI 위치
rep("""const AN_ZONE_FROM = '2025-06-01';""",
"""function anVkAt(d){   // 그날 이전 가장 가까운 VKOSPI 기록 위치(7일 넘게 떨어지면 없음 -1)
  const h = anVkHist; if(!h || !h.d || !h.d.length || d < h.d[0]) return -1;
  const k = anZoneAt(h.d, d); return k >= 0 && (Date.parse(d) - Date.parse(h.d[k])) <= 7 * 864e5 ? k : -1;
}
const AN_ZONE_FROM = '2025-06-01';""")

# 5) 판정 기록: 그날 판정(L)은 비트만 채움, 다시 셈(G·C)은 VKOSPI 포함
rep("""  b.d.forEach((d, i) => { const e = anMlog[d]; if(e && e[4] === 'L' && e[9] === 0){ e[2] = (e[2] & ~4) | (b.rm[i] & 4); e[0] = cnt(e[2]); e[9] = 2; } });   // 옮긴 그날 판정에 200일 이격 채움""",
"""  b.d.forEach((d, i) => { const e = anMlog[d]; if(e && e[4] === 'L' && e[9] === 0){ e[2] = (e[2] & ~4) | (b.rm[i] & 4); e[0] = cnt(e[2]); e[9] = 2; } });   // 옮긴 그날 판정에 200일 이격 채움
  b.d.forEach(d => { const e = anMlog[d]; if(!e || e[4] !== 'L' || e[10]) return; const k = anVkAt(d); if(k < 0) return;   /* 그날 판정(L)에 VKOSPI 비트만 더함(2026-11-23) */
    e[3] = (e[3] & ~32) | (anVkHist.on[k] === '1' ? 32 : 0); e[1] = cnt(e[3]); e[10] = 1; });""")
rep("""  if(!(anMlog[last] && anMlog[last][7])) anMlog[last] = [cnt(rm), cnt(bm), rm, bm, 'L', pf((msig.bottom.items[4] || [])[1]), pf((msig.risk.items[4] || [])[1]), fin(last) ? 1 : 0];""",
"""  if(!(anMlog[last] && anMlog[last][7])){ anMlog[last] = [cnt(rm), cnt(bm), rm, bm, 'L', pf((msig.bottom.items[4] || [])[1]), pf((msig.risk.items[4] || [])[1]), fin(last) ? 1 : 0];
    if(msig.bottom.items[5] && msig.bottom.items[5][2] != null) anMlog[last][10] = 1; }   /* VKOSPI 반영(2026-11-23) */""")
rep("""      const old = anMlog[d], ci = anCreditAt(d);
      const redo = old && old[4] !== 'L' && !old[8] && ci >= 0;   /* 신용잔고 없이 만든 날은 그 자료가 생기면 한 번 다시 셈 */""",
"""      const old = anMlog[d], ci = anCreditAt(d), vi = anVkAt(d);
      const redo = old && old[4] !== 'L' && ((!old[8] && ci >= 0) || (!old[10] && vi >= 0));   /* 신용잔고·VKOSPI 없이 만든 날은 그 자료가 생기면 한 번 다시 셈 */""")
rep("""      const wk = nw / n, br = nb / n, R = (b.rm[i] & 15) | (br >= 0.7 ? 16 : 0) | cr, B = (b.bm[i] & 15) | (wk >= 0.3 ? 16 : 0);
      const src = old ? (old[4] === 'L' ? 'C' : old[4]) : 'G';
      anMlog[d] = [cnt(R), cnt(B), R, B, src, Math.round(wk * 100), Math.round(br * 100), 1, ci >= 0 || src === 'C' ? 1 : 0];""",
"""      const vk = vi >= 0 ? (anVkHist.on[vi] === '1' ? 32 : 0) : (old ? old[3] & 32 : 0);
      const wk = nw / n, br = nb / n, R = (b.rm[i] & 15) | (br >= 0.7 ? 16 : 0) | cr, B = (b.bm[i] & 15) | (wk >= 0.3 ? 16 : 0) | vk;
      const src = old ? (old[4] === 'L' ? 'C' : old[4]) : 'G';
      anMlog[d] = [cnt(R), cnt(B), R, B, src, Math.round(wk * 100), Math.round(br * 100), 1, ci >= 0 || src === 'C' || (old && old[8]) ? 1 : 0, undefined, vi >= 0 ? 1 : 0];""")
# 차트용: VKOSPI 반영 여부
rep("""  const z = Object.assign({}, b, { r: [], b: [], rm: [], bm: [], src: [], wk: [], br: [], fin: [], cr: [] });
  b.d.forEach(d => { const e = anMlog[d]; z.cr.push(e ? e[8] || 0 : 0);""",
"""  const z = Object.assign({}, b, { r: [], b: [], rm: [], bm: [], src: [], wk: [], br: [], fin: [], cr: [], vkf: [] });
  b.d.forEach(d => { const e = anMlog[d]; z.cr.push(e ? e[8] || 0 : 0); z.vkf.push(e ? e[10] || 0 : 0);""")

open(path, 'w', encoding='utf-8').write(s); print('ok', path)
