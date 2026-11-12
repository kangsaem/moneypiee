import sys
fn=sys.argv[1]; s=open(fn,encoding='utf-8').read()
def rep(a,b,cnt=1):
    global s
    n=s.count(a); assert n==cnt,(fn,a[:70],n); s=s.replace(a,b)
rep("""    if(rs) ordered = bySector(part(fs.first)).concat(bySector(part(fs.second)));""","""    if(rs) ordered = bySector(part(fs.mk.side)).concat(bySector(part(fs.other)));   // 도넛 순서는 항상 장 기준(반대쪽 지역을 봐도 도넛 그림은 그대로, 보이는 지역만 바뀜 — 2026-11-12 사용자)""")
rep("""  const regRing = rs ? [fs.first, fs.second].flatMap(g => [""","""  const regRing = rs ? [fs.mk.side, fs.other].flatMap(g => [""")
rep("""  const total = _.sumBy(ordered, 'amount') || 1, n = ordered.length, useBase = mode === 'group' || rs;""","""  ordered = ordered.map((d, i) => ({ ...d, rank: d.rank !== undefined ? d.rank : i, rankCount: d.rankCount !== undefined ? d.rankCount : ordered.length }));   // 색 순번을 도넛 순서로 고정(목록 순서가 달라도 같은 색)
  const total = _.sumBy(ordered, 'amount') || 1, n = ordered.length, useBase = mode === 'group' || rs;""")
open(fn,'w',encoding='utf-8').write(s); print('ok')
