import sys
fn=sys.argv[1]; s=open(fn,encoding='utf-8').read()
a="  .mkt-card{height:var(--mkt-h, 115px);display:flex;flex-direction:column;overflow:hidden;}"
assert s.count(a)==1
s=s.replace(a,a+"\n  .mkt-card{background:var(--surface2);border-color:var(--accent-dim);}   /* 2026-11-12 사용자: 지표 카드 색 = 활성화된 탭(자산 탭)과 같은 바탕·테두리 */")
open(fn,'w',encoding='utf-8').write(s); print('ok')
