import sys
fn=sys.argv[1]; s=open(fn,encoding='utf-8').read()
a="""amount: regTot[g] - regCash[g], pct: (regTot[g] - regCash[g]) / total * 100, rank: g === 'domestic' ? 0 : 1, rankCount: 2 }"""
assert s.count(a)==1
s=s.replace(a,"""amount: regTot[g] - regCash[g], pct: (regTot[g] - regCash[g]) / total * 100, rank: g === 'domestic' ? 0 : 1, rankCount: 2,
      color: g === fs.mk.side ? REGION_LIGHT : REGION_STRONG }   // 지역순: 장중인 쪽 = 밝은 색, 아닌 쪽 = 어두운 색(2026-11-12 사용자)""")
open(fn,'w',encoding='utf-8').write(s); print('ok')
