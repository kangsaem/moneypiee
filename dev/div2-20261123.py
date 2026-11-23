# 배당수익률 2단계(2026-11-23): 국내 종목·ETF = 네이버 m.stock /api/stock/{코드}/integration (하루 한 번 저장)
#  종목: totalInfos[code=dividendYieldRatio].value '0.95%' · [code=dividend].value '1,668원' · valueDesc '2025.12.'(결산)
#  ETF : etfKeyIndicator.dividendYieldTtm 1.11 (최근 12개월, 0이면 분배 없음)
# 확인: moneypier results/div_probe.txt. 프록시 ALLOW에 m.stock.naver.com '/api/stock/' 추가 필요(사용자 배포).
# 사용: python dev/div2-20261123.py test.html
import sys

path = sys.argv[1]
s = open(path, encoding='utf-8').read()

def rep(old, new, n=1):
    global s
    c = s.count(old)
    if c != n:
        raise SystemExit(f'찾은 개수 {c} != {n}: {old[:80]!r}')
    s = s.replace(old, new)

# 1) 결과에 붙이기: 야후 배당이 없는 국내 코드 종목은 네이버
rep("""          try{ r.dy = anDivYield(bars); }catch(e){ r.dy = null; }   // 배당수익률(2026-11-23)""",
"""          try{ r.dy = anDivYield(bars); }catch(e){ r.dy = null; }   // 배당수익률(2026-11-23)
          if(!r.dy && spec.market === 'KR' && anIsKrCode(spec.code)){ try{ r.dy = await anNaverDiv(spec.code); }catch(e){ r.dy = null; } }   // 국내·ETF = 네이버(하루 한 번)""")

# 2) 네이버 배당 받기 + 하루 캐시
rep("""function anDivTag(r){""",
"""// 네이버 종목 정보 배당(2026-11-23): 하루(KST 날짜) 한 번 받아 저장, 실패는 1시간 뒤 다시. 배당 없음 = { none: true } 저장 → null
async function anNaverDiv(code){
  const ck = 'div:' + code, today = anFmtMs(Date.now() + 9 * 3600e3);
  const c = await anDB.get(ck);
  if(c && (c.d === today || (c.fail && Date.now() - c.at < 3600e3))) return c.v || null;
  let v = null;
  try{
    const res = await fetchViaProxy(`https://m.stock.naver.com/api/stock/${encodeURIComponent(code)}/integration`, 10000);
    if(!res || !res.ok) throw new Error('네이버 ' + (res ? res.status : '응답 없음'));
    const j = await res.json(), num = x => parseFloat(String(x == null ? '' : x).replace(/[^0-9.\\-]/g, ''));
    const ek = j && j.etfKeyIndicator;
    if(ek && ek.dividendYieldTtm != null){                 // ETF: 최근 12개월 분배 수익률
      const p = num(ek.dividendYieldTtm);
      if(p > 0) v = { pct: p, src: 'naver-etf', asof: today };
    }else{
      const ti = (j && j.totalInfos) || [], f = k => ti.find(x => x && x.code === k);
      const y = f('dividendYieldRatio'), dps = f('dividend'), p = y ? num(y.value) : NaN;
      if(p > 0) v = { pct: p, dps: dps ? dps.value : null, per: (y.valueDesc || '').replace(/\\.$/, ''), src: 'naver', asof: today };
    }
  }catch(e){
    await anDB.set(ck, { fail: true, at: Date.now(), v: c && c.v || null });
    return c && c.v || null;
  }
  await anDB.set(ck, { d: today, v });
  return v;
}
function anDivTag(r){""")

# 3) 툴팁: 출처별 '연 배당'·'기준'
rep("""  const L = [`배당 ${dy.pct.toFixed(2)}%`, `연 배당 ${anPrice(dy.sum)}`];
  if(hasT) L.push(`미국채 10년 ${t.toFixed(2)}%보다 ${anS(gap, 2)}%p`);
  L.push(`기준: 최근 12개월 배당 ${dy.n}회 합 ÷ ${anShort(dy.asof)} 종가 ${anPrice(dy.px)}`);""",
"""  const L = [`배당 ${dy.pct.toFixed(2)}%`];
  if(dy.src === 'yahoo') L.push(`연 배당 ${anPrice(dy.sum)}`); else if(dy.dps) L.push(`연 배당 ${dy.dps}`);
  if(hasT) L.push(`미국채 10년 ${t.toFixed(2)}%보다 ${anS(gap, 2)}%p`);
  L.push(dy.src === 'yahoo' ? `기준: 최근 12개월 배당 ${dy.n}회 합 ÷ ${anShort(dy.asof)} 종가 ${anPrice(dy.px)}`
       : dy.src === 'naver-etf' ? `기준: 네이버 ETF 최근 12개월 분배 수익률 (${anShort(dy.asof)} 받음)`
       : `기준: 네이버 배당수익률${dy.per ? ' · ' + dy.per + ' 결산 배당' : ''} (${anShort(dy.asof)} 받음)`);""")

open(path, 'w', encoding='utf-8').write(s)
print('ok', path)
