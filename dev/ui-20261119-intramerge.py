import sys
p = sys.argv[1]; s = open(p, encoding='utf-8').read()
def rep(a, b, cnt=1):
    global s
    assert s.count(a) == cnt, (a[:70], s.count(a)); s = s.replace(a, b)
rep("""  if(isIntraday){
    const points = [];
    for(let i=0; i<timestamps.length; i++){
      if(rawCloses[i] !== null && rawCloses[i] !== undefined){
        points.push({ ts: timestamps[i], close: rawCloses[i] });
      }
    }
    const trading = meta.currentTradingPeriod && meta.currentTradingPeriod.regular;
    return {
      price: meta.regularMarketPrice,
      closes: closesRaw,""", """  if(isIntraday){
    let points = [];
    for(let i=0; i<timestamps.length; i++){
      if(rawCloses[i] !== null && rawCloses[i] !== undefined){
        points.push({ ts: timestamps[i], close: rawCloses[i] });
      }
    }
    const trading = meta.currentTradingPeriod && meta.currentTradingPeriod.regular;
    points = mpIntraMerge(symbol, points, trading, wideIntraday);   // 받은 장중 시세를 저장본과 합침(빠진 구간은 저장본으로)
    return {
      price: meta.regularMarketPrice,
      closes: points.map(p => p.close),""")
rep("""async function fetchYahooChart(symbol, range, wideIntraday""", """// 지표 카드 1일 장중 시세 저장·합치기(2026-11-19 사용자): 야후가 요청마다 중간 구간이 빠진 2분 자료를 줄 때가 있어(장 끝난 뒤 정상·비정상이 번갈아)
// 한 번 받은 그날 시세를 기기에 저장해 두고, 새로 받을 때마다 시각별로 합침(같은 시각은 새 값). 하루치만: 지금 장(또는 마지막 장) 구간 밖은 버림
function mpIntraMerge(symbol, points, trading, wide){
  const K = 'mp-intra:' + symbol;
  try{
    const lastTs = points.length ? points[points.length - 1].ts : 0;
    let old = null; try{ old = JSON.parse(localStorage.getItem(K) || 'null'); }catch(e){}
    const m = new Map();
    if(old && Array.isArray(old.p)) old.p.forEach(([t, c]) => m.set(t, c));
    points.forEach(p => m.set(p.ts, p.close));
    let all = [...m.entries()].sort((a, b) => a[0] - b[0]);
    const last = all.length ? all[all.length - 1][0] : lastTs;
    // 남길 구간: 장 구간이 마지막 시세를 포함하면 그 장 시작부터(2일 보기 종목은 하루 더), 아니면(야후가 다음 장 시간을 줄 때) 마지막 시세에서 거슬러 하루치
    const from = trading && trading.start <= last ? trading.start - (wide ? 86400 : 0) : last - (wide ? 2 : 1) * 86400 + 3600;
    all = all.filter(([t]) => t >= from);
    try{ localStorage.setItem(K, JSON.stringify({ at: Date.now(), p: all })); }catch(e){}
    return all.map(([ts, close]) => ({ ts, close }));
  }catch(e){ return points; }
}

async function fetchYahooChart(symbol, range, wideIntraday""")
open(p, 'w', encoding='utf-8').write(s)
