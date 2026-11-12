import sys
fn=sys.argv[1]; s=open(fn,encoding='utf-8').read()
def rep(a,b,cnt=1):
    global s
    n=s.count(a); assert n==cnt,(fn,a[:70],n); s=s.replace(a,b)
rep("""  ordered = ordered.map((d, i) => ({ ...d, rank:""","""  // 섹터순·금액순: 외화 조각은 맨 끝으로 → 원화(12시 한쪽)·외화(12시 다른 쪽)가 12시에서 맞붙고, 바깥 지역 링(원화·국내·해외·외화 순)과도 맞음(2026-11-12 사용자)
  if(!rs && ordered.some(d => d.label === '외화')) ordered = ordered.filter(d => d.label !== '외화').concat(ordered.filter(d => d.label === '외화'));
  ordered = ordered.map((d, i) => ({ ...d, rank:""")
rep("""    ${stockLegendWithDividers(ordered, stockLegendSortMode, !!compactTotalMode)}""",
    """    ${stockLegendWithDividers(U ? ordered.filter(d => isCashLikeLabel(d.label)).concat(ordered.filter(d => !isCashLikeLabel(d.label))) : ordered, stockLegendSortMode, !!compactTotalMode)}""")
open(fn,'w',encoding='utf-8').write(s); print('ok',fn)
