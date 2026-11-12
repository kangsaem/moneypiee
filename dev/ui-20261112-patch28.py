import sys
fn=sys.argv[1]; s=open(fn,encoding='utf-8').read()
a="""    chartOpts.dense = points.length > 1 ? HIDX.filter(c => !historyLineOff[c.name]).map(c => hidxDense(c, labels, points[0].value)).filter(Boolean) : [];
    if(sorted.length) hidxEnsure(normalizeLabel(sorted[0].label));"""
assert s.count(a)==1
s=s.replace(a,"""    if(sorted.length) hidxEnsure(normalizeLabel(sorted[0].label));   // 먼저 호출: 저장해 둔 지수 자료를 여기서 읽어 옴(새로고침 뒤 첫 화면에 지수선이 안 보이던 것 — 2026-11-12)
    chartOpts.dense = points.length > 1 ? HIDX.filter(c => !historyLineOff[c.name]).map(c => hidxDense(c, labels, points[0].value)).filter(Boolean) : [];""")
open(fn,'w',encoding='utf-8').write(s); print('ok')
