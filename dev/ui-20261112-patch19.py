import sys
fn=sys.argv[1]; s=open(fn,encoding='utf-8').read()
a="isSelected ? stepBg : 'var(--border)'"
assert s.count(a)==2
s=s.replace(a,"isSelected ? stepBg : '#5A5B61'")
b="  .hz-btn{width:26px;height:26px;border:1px solid var(--border);"
assert s.count(b)==1
s=s.replace(b,"""  /* 2026-11-12 사용자: 계좌명·계좌유형 버튼, 확대·축소 버튼 테두리를 밝게(--border → --accent-dim) */
  [data-account-filter].btn, #historyAccSelector .btn, #historyAccTypeSelector .btn{border-color:#5A5B61;}
  .hz-btn{width:26px;height:26px;border:1px solid #5A5B61;""")
open(fn,'w',encoding='utf-8').write(s); print('ok')
