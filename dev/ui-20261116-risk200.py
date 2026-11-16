import sys
p = sys.argv[1]; s = open(p, encoding='utf-8').read()
def rep(a, b, cnt=1):
    global s
    assert s.count(a) == cnt, (a[:70], s.count(a)); s = s.replace(a, b)
# 1) 코스피 200일 이격도
rep("""  return { close: s[n-1], disp: dd ? dd.cur : null, disp_max: dd ? dd.max : null, disp_min: dd ? dd.min : null,
           rsi: anRsi(s)[n-1],""", """  const m200 = anRoll(s, 200)[n-1];
  return { close: s[n-1], disp: dd ? dd.cur : null, disp_max: dd ? dd.max : null, disp_min: dd ? dd.min : null,
           disp200: m200 ? s[n-1] / m200 * 100 : null,                // 200일선 이격도(위험 '장기 과열', 2026-11-16)
           rsi: anRsi(s)[n-1],""")
# 2) 위험 항목: VIX 25 → 200일 이격 150
rep("""    ['VIX 25 이상 또는 10일간 30% 이상 급등', vix ? anF(vix.last, 1) : '-',
      vix ? (vix.last >= 25 || (vix.pct10 != null && vix.pct10 >= 30)) : null],""",
    """    ['코스피 200일 이격도 150 이상(장기 과열)', ks && ks.disp200 != null ? anF(ks.disp200, 1) : '-',   // 전엔 VIX 25↑·급등 — 검증(risk_study)에서 VIX는 바닥 쪽으로 작동해 바꿈(2026-11-16)
      ks && ks.disp200 != null ? ks.disp200 >= 150 : null],""")
# 3) 과거 구간 계산
rep("""  const d = kb.dates, c = kb.close, n = c.length, ma = anRoll(c, 50), rs = anRsi(c);""",
    """  const d = kb.dates, c = kb.close, n = c.length, ma = anRoll(c, 50), ma200 = anRoll(c, 200), rs = anRsi(c);""")
rep("""    const R = [disp >= 120, anOk(rr) && rr >= 70, vx != null && (vx >= 25 || (vp != null && vp >= 30)), y10 != null && y10 >= 0.3];""",
    """    const d200 = ma200[i] ? c[i] / ma200[i] * 100 : null;
    const R = [disp >= 120, anOk(rr) && rr >= 70, d200 != null && d200 >= 150, y10 != null && y10 >= 0.3];   // 3번째: 200일 이격 150↑(전엔 VIX 25↑·급등)""")
rep("""  const z = { d: [], r: [], b: [], rm: [], bm: [], disp: [], rsi: [], fh: [], vx: [], vp: [], yc: [] };""",
    """  const z = { d: [], r: [], b: [], rm: [], bm: [], disp: [], d200: [], rsi: [], fh: [], vx: [], vp: [], yc: [] };""")
rep("""    z.disp.push(r1(disp)); z.rsi.push(r1(rr));""", """    z.disp.push(r1(disp)); z.d200.push(r1(d200)); z.rsi.push(r1(rr));""")
rep("""const AN_ZR = ['코스피 이격도 120↑', '코스피 RSI 70↑', 'VIX 25↑·급등',""", """const AN_ZR = ['코스피 이격도 120↑', '코스피 RSI 70↑', '200일 이격 150↑',""")
# 4) 판정 기록: 위험 3번째 항목 뜻이 바뀜 → 한 번 옮김
rep("""const anMlogP = (async () => { try{ anMlog = (await anDB.get('mlog1')) || {}; }catch(e){ anMlog = {}; } return anMlog; })();""",
    """const anMlogP = (async () => {
  try{ anMlog = (await anDB.get('mlog1')) || {}; }catch(e){ anMlog = {}; }
  try{                                                          // v2(2026-11-16): 위험 3번째 항목 VIX 25↑ → 200일 이격 150↑. 다시 계산한 날(G·C)은 지우고 다음 분석 때 새로 만듦,
    if((await anDB.get('mlogv')) !== 2){                        // 그날 판정(L)은 3번째 비트를 지우고 시장 계산이 생기면 채움(e[9] = 2 표시)
      Object.keys(anMlog).forEach(d => { const e = anMlog[d]; if(!Array.isArray(e)) return; if(e[4] !== 'L'){ delete anMlog[d]; return; }
        e[2] &= ~4; let c = 0; for(let m = e[2]; m; m >>= 1) c += m & 1; e[0] = c; e[9] = 0; });
      await anDB.set('mlog1', anMlog); await anDB.set('mlogv', 2);
    }
  }catch(e){}
  return anMlog;
})();""")
rep("""  const last = b.d[b.d.length - 1], rm = mask(msig.risk.items), bm = mask(msig.bottom.items);""",
    """  b.d.forEach((d, i) => { const e = anMlog[d]; if(e && e[4] === 'L' && e[9] === 0){ e[2] = (e[2] & ~4) | (b.rm[i] & 4); e[0] = cnt(e[2]); e[9] = 2; } });   // 옮긴 그날 판정에 200일 이격 채움
  const last = b.d[b.d.length - 1], rm = mask(msig.risk.items), bm = mask(msig.bottom.items);""")
open(p, 'w', encoding='utf-8').write(s)
