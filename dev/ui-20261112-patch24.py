import sys
fn=sys.argv[1]; s=open(fn,encoding='utf-8').read()
def rep(a,b,cnt=1):
    global s
    n=s.count(a); assert n==cnt,(fn,a[:70],n); s=s.replace(a,b)
rep("const STOCK_SORT_CYCLE_FULL = ['region', 'group', 'amount', 'name'];","const STOCK_SORT_CYCLE_FULL = ['region', 'group', 'amount'];")
rep("const STOCK_SORT_CYCLE_NO_REGION = ['group', 'amount', 'name'];","const STOCK_SORT_CYCLE_NO_REGION = ['group', 'amount'];   // 이름순 삭제(2026-11-12 사용자)")
open(fn,'w',encoding='utf-8').write(s); print('ok')
