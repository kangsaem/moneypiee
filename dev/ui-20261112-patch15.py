import sys
fn=sys.argv[1]; s=open(fn,encoding='utf-8').read()
def rep(a,b,cnt=1):
    global s
    n=s.count(a); assert n==cnt,(fn,a[:70],n); s=s.replace(a,b)
rep("function stockSecOpen(k){ return mpWideList() || !!stockSectorOpen[k]; }",
    "const WIDE_ALL_OPEN = false;   // 넓은 PC에서 접힘 없이 다 펼칠지(2026-11-12 사용자: 아니오 — 휴대폰과 같은 접힘·같은 버튼)\nfunction stockSecOpen(k){ return (WIDE_ALL_OPEN && mpWideList()) || !!stockSectorOpen[k]; }")
rep("  if(mpWideList()) return { mk, other, folded: { domestic: false, overseas: false } };","  if(WIDE_ALL_OPEN && mpWideList()) return { mk, other, folded: { domestic: false, overseas: false } };")
rep("  if(DONUT_ONE && mpWideList()) return;   // 넓은 화면은 항상 펼침","  if(DONUT_ONE && WIDE_ALL_OPEN && mpWideList()) return;")
rep("if(!box || mpWideList()) return;","if(!box || (WIDE_ALL_OPEN && mpWideList())) return;")
rep("const secAllBtn = (uniSec && !mpWideList() && secKeysAll.length > 1)","const secAllBtn = (uniSec && !(WIDE_ALL_OPEN && mpWideList()) && secKeysAll.length > 1)")
rep("const allB = (DONUT_ONE && g !== other && !mpWideList())","const allB = (DONUT_ONE && g !== other && !(WIDE_ALL_OPEN && mpWideList()))")
rep("  .stock-sortable-legend.wide2 .sec-head{margin:10px 0 4px;padding:2px 0;cursor:default;break-inside:avoid;break-after:avoid;}","  .stock-sortable-legend.wide2 .sec-head{margin:4px 0 2px;padding:3px 0;break-inside:avoid;break-after:avoid;}")
rep("  .stock-sortable-legend.wide2 .rg-head{cursor:default;break-after:avoid;}","  .stock-sortable-legend.wide2 .rg-head{break-after:avoid;}")
open(fn,'w',encoding='utf-8').write(s); print('ok',fn)
