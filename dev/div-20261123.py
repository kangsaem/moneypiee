# 배당수익률 칸(2026-11-23) — 1단계: 해외(야후 events.dividends). 국내·ETF(네이버)는 응답 형식 확인 뒤 2단계.
# 사용: python dev/div-20261123.py test.html
import sys

path = sys.argv[1]
s = open(path, encoding='utf-8').read()

def rep(old, new, n=1):
    global s
    c = s.count(old)
    if c != n:
        raise SystemExit(f'찾은 개수 {c} != {n}: {old[:80]!r}')
    s = s.replace(old, new)

# 1) anFromMap: 배당 목록을 같이 넘김
rep("""function anFromMap(map){
  const keys = Array.from(map.keys()).sort();
  return { dates: keys,""",
"""function anFromMap(map, div){
  const keys = Array.from(map.keys()).sort();
  return { div: div || null, dates: keys,""")

# 2) anFetchYahoo: events.dividends → [[날짜, 금액], ...] (분할 반영 금액 = 종가와 같은 기준)
rep("""  if(map.size < 2) throw new Error('야후 데이터 부족');
  return anFromMap(map);""",
"""  if(map.size < 2) throw new Error('야후 데이터 부족');
  const dv = r.events && r.events.dividends;   // 배당(2026-11-23): {ts: {amount, date}} — 없으면 빈 목록(= 배당 없음)
  const div = dv ? Object.values(dv).filter(x => x && x.amount > 0 && x.date).map(x => [anFmtMs((x.date + off) * 1000), x.amount])
                     .sort((a, b) => a[0] < b[0] ? -1 : 1) : [];
  return anFromMap(map, div);""")

# 3) 저장 형식: div 추가 → AN_BARS_V 3
rep("""const AN_BARS_V = 2;    // 2 = 야후 마지막 날 빈 종가를 meta 가격으로 채움(2026-10-13)""",
"""const AN_BARS_V = 3;    // 2 = 야후 마지막 날 빈 종가를 meta 가격으로 채움(2026-10-13) · 3 = 야후 배당 목록(div) 저장(2026-11-23)""")
rep("""const rec = { dates: b.dates, close: b.close, high: b.high, low: b.low, vol: b.vol, fetchedAt""",
"""const rec = { dates: b.dates, close: b.close, high: b.high, low: b.low, vol: b.vol, div: b.div || null, fetchedAt""")

# 4) 종목 결과에 배당 붙이기(야후 출처만 — 네이버 일봉은 div 없음 → 2단계)
rep("""          r.key = spec.key;                          // 신호 기록에서 이 종목 시세 캐시를 다시 찾을 때 씀""",
"""          r.key = spec.key;                          // 신호 기록에서 이 종목 시세 캐시를 다시 찾을 때 씀
          try{ r.dy = anDivYield(bars); }catch(e){ r.dy = null; }   // 배당수익률(2026-11-23)""")

# 5) 계산·표시 함수 — anMetricsHtml 앞
rep("""function anMetricsHtml(r, side, lv, flags, emph){""",
"""// 배당수익률(2026-11-23): 마지막 종가 날짜 기준 최근 12개월(365일) 배당 합 ÷ 마지막 종가. 배당 목록이 없으면(출처에 정보 없음) null, 12개월 합 0이면 null(칸 없음)
function anDivYield(bars){
  if(!bars || !Array.isArray(bars.div) || !bars.dates || !bars.dates.length) return null;
  const last = bars.dates[bars.dates.length - 1], px = bars.close[bars.close.length - 1];
  const t = Date.parse(last + 'T00:00:00Z'), from = anFmtMs(t - 365 * 864e5);
  const got = bars.div.filter(([d]) => d > from && d <= last);
  const sum = got.reduce((a, [, v]) => a + v, 0);
  if(!(sum > 0) || !(px > 0)) return null;
  return { pct: sum / px * 100, sum, n: got.length, px, asof: last, src: 'yahoo' };
}
function anDivTag(r){
  const dy = r.dy;
  if(!dy || !anOk(dy.pct)) return '';
  const t = typeof marketData !== 'undefined' && marketData.us10y && marketData.us10y.price;
  const hasT = anOk(t) && t > 0, gap = hasT ? dy.pct - t : null;
  const L = [`배당 ${dy.pct.toFixed(2)}%`, `연 배당 ${anPrice(dy.sum)}`];
  if(hasT) L.push(`미국채 10년 ${t.toFixed(2)}%보다 ${anS(gap, 2)}%p`);
  L.push(`기준: 최근 12개월 배당 ${dy.n}회 합 ÷ ${anShort(dy.asof)} 종가 ${anPrice(dy.px)}`);
  return `<span class="an-mt an-dv${hasT && gap > 0 ? ' hi' : ''}" title="${anE(L.join(' · '))}">배당 ${dy.pct.toFixed(1)}%</span>`;
}
function anMetricsHtml(r, side, lv, flags, emph){""")

# 6) 지표 1줄 끝(상대강도 뒤)에 배당 칸
rep("""    if(anOk(r.rs60)) nums.push(tag('', `상대강도 ${anS(r.rs60, 1)}%p`, r.rs60 >= 0 ? 'up' : 'dn', '최근 60거래일 수익률 - 지수 수익률'));""",
"""    if(anOk(r.rs60)) nums.push(tag('', `상대강도 ${anS(r.rs60, 1)}%p`, r.rs60 >= 0 ? 'up' : 'dn', '최근 60거래일 수익률 - 지수 수익률'));
    { const dv = anDivTag(r); if(dv) nums.push(dv); }""")

# 7) 색: 미국채 10년보다 높으면 연두 글자·테두리(1안). 아니면 기본 회색 칸
rep(""".an-mt.an-tp { background:transparent; color:var(--an-dn); border-color:var(--an-dn); font-weight:700; }""",
""".an-mt.an-tp { background:transparent; color:var(--an-dn); border-color:var(--an-dn); font-weight:700; }
.an-mt.an-dv.hi { background:transparent; color:#9BD266; border-color:#9BD266; }   /* 배당 > 미국채 10년(2026-11-23) */""")

open(path, 'w', encoding='utf-8').write(s)
print('ok', path)
