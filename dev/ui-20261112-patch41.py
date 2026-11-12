import sys
fn=sys.argv[1]; s=open(fn,encoding='utf-8').read()
def rep(a,b,cnt=1):
    global s
    n=s.count(a); assert n==cnt,(fn,a[:70],n); s=s.replace(a,b)
rep("""    if(rs) ordered = bySector(part(fs.mk.side)).concat(bySector(part(fs.other)));""",
    """    if(rs){ const a2 = bySector(part(fs.other)), cs = a2.filter(d => stockSecKey(d) === '현금');   // 뒤쪽 지역의 현금(외화 등)은 맨 끝으로 → 두 현금이 12시에서 맞붙음(2026-11-12 사용자)
      ordered = bySector(part(fs.mk.side)).concat(a2.filter(d => stockSecKey(d) !== '현금'), cs); }""")
rep("""  const cash = data.filter(d => d.label === '현금');
  const rest = data.filter(d => d.label !== '현금');""","""  const cash = data.filter(d => isCashLikeLabel(d.label));   // 현금·원화·외화는 함께 맨 앞(12시)
  const rest = data.filter(d => !isCashLikeLabel(d.label));""")
rep("""      data = data.filter(d => gOf(d) === mk.side).concat(data.filter(d => gOf(d) === other));""",
    """      const cf = xs => xs.filter(d => isCashLikeLabel(d.label)).concat(xs.filter(d => !isCashLikeLabel(d.label)));   // 목록에서는 지역마다 현금을 맨 위로
      data = cf(data.filter(d => gOf(d) === mk.side)).concat(cf(data.filter(d => gOf(d) === other)));""")
open(fn,'w',encoding='utf-8').write(s); print('ok',fn)
