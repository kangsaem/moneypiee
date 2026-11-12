import sys
fn=sys.argv[1]; s=open(fn,encoding='utf-8').read()
a="  .mkt-card{background:var(--surface2);border-color:var(--accent-dim);}"
assert s.count(a)==1
s=s.replace(a,"  .mkt-card{transition:background-color .2s, border-color .2s;} #marketTicker.mkt-min .mkt-card{background:var(--surface2);border-color:var(--accent-dim);}")
s=s.replace("/* 2026-11-12 사용자: 지표 카드 색 = 활성화된 탭(자산 탭)과 같은 바탕·테두리 */","/* 2026-11-12 사용자: 평소엔 원래 어두운 색, 다 줄어들어 고정된 상태에서만 활성 탭 색 */")
open(fn,'w',encoding='utf-8').write(s); print('ok')
