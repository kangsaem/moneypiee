import sys
fn=sys.argv[1]; s=open(fn,encoding='utf-8').read()
def rep(a,b,cnt=1):
    global s
    n=s.count(a); assert n==cnt,(fn,a[:70],n); s=s.replace(a,b)
rep("""    if(rs){ const a2 = bySector(part(fs.other)), cs = a2.filter(d => stockSecKey(d) === '현금');   // 뒤쪽 지역의 현금(외화 등)은 맨 끝으로 → 두 현금이 12시에서 맞붙음(2026-11-12 사용자)
      ordered = bySector(part(fs.mk.side)).concat(a2.filter(d => stockSecKey(d) !== '현금'), cs); }""",
    """    if(rs) ordered = bySector(part(fs.mk.side)).concat(bySector(part(fs.other)));""")
rep("""  // 섹터순·금액순: 외화 조각은 맨 끝으로 → 원화(12시 한쪽)·외화(12시 다른 쪽)가 12시에서 맞붙고, 바깥 지역 링(원화·국내·해외·외화 순)과도 맞음(2026-11-12 사용자)
  if(!rs && ordered.some(d => d.label === '외화')) ordered = ordered.filter(d => d.label !== '외화').concat(ordered.filter(d => d.label === '외화'));""",
    """  // 현금은 모든 정렬에서 12시부터 시계 반대 방향으로 외화 → 원화, 그다음 나머지(2026-11-12 사용자)
  { const cash = ordered.filter(d => stockSecKey(d) === '현금');
    if(cash.length){ const rk = d => stockRegKey(d) === 'overseas' ? 0 : 1; cash.sort((a, b) => rk(a) - rk(b)); ordered = cash.concat(ordered.filter(d => stockSecKey(d) !== '현금')); } }""")
rep("""  const regRing = rs ? [fs.mk.side, fs.other].flatMap(g => [
    { label: g === 'domestic' ? '원화' : '외화', amount: regCash[g], pct: regCash[g] / total * 100, rank: 0, rankCount: 2 },
    { label: g === 'domestic' ? '국내' : '해외', amount: regTot[g] - regCash[g], pct: (regTot[g] - regCash[g]) / total * 100, rank: g === 'domestic' ? 0 : 1, rankCount: 2,
      color: g === fs.mk.side ? REGION_LIGHT : REGION_STRONG }   // 지역순: 장중인 쪽 = 밝은 색, 아닌 쪽 = 어두운 색(2026-11-12 사용자)
  ]).filter(d => d.amount > 0) : null;""","""  // 지역 링 = 도넛 순서 그대로(외화·원화·앞 지역·뒤 지역). 지역순: 장중인 쪽 = 밝은 색, 아닌 쪽 = 어두운 색(2026-11-12 사용자)
  const regRing = rs ? (() => { const out = [];
    ordered.forEach(d => { const g = stockRegKey(d), c = stockSecKey(d) === '현금', k = g + (c ? 'c' : 's'), l = out[out.length - 1]; if(l && l.k === k) l.amount += d.amount; else out.push({ k, g, c, amount: d.amount }); });
    return out.filter(o => o.amount > 0).map(o => ({ label: o.c ? (o.g === 'domestic' ? '원화' : '외화') : (o.g === 'domestic' ? '국내' : '해외'), amount: o.amount, pct: o.amount / total * 100,
      rank: o.c ? 0 : (o.g === 'domestic' ? 0 : 1), rankCount: 2, ...(o.c ? {} : { color: o.g === fs.mk.side ? REGION_LIGHT : REGION_STRONG }) })); })() : null;""")
rep("""      return { ...spec, opacity, arcs: true, data: spec.data.map(d => d.label === '국내' ? { ...d, color: col('domestic') } : (d.label === '해외' ? { ...d, color: col('overseas') } : d)) };""",
    """      const dd = spec.data.map(d => d.label === '국내' ? { ...d, color: col('domestic') } : (d.label === '해외' ? { ...d, color: col('overseas') } : d));
      return { ...spec, opacity, arcs: true, data: dd.filter(d => d.label === '외화').concat(dd.filter(d => d.label !== '외화')) };   // 외화를 맨 앞으로 → 도넛의 현금(12시부터 외화·원화)과 맞음""")
open(fn,'w',encoding='utf-8').write(s); print('ok',fn)
