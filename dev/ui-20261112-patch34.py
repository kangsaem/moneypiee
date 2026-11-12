import sys
fn=sys.argv[1]; s=open(fn,encoding='utf-8').read()
a="""  panel.innerHTML = `
    ${accountSelector}
    ${rangeSelector}
    <div style="position:relative;">"""
assert s.count(a)==1
s=s.replace(a,"""  panel.innerHTML = `
    ${rangeSelector}
    ${accountSelector}
    <div style="position:relative;">""")   # 2026-11-12 사용자: 이번달 저장 줄을 맨 위로(다른 탭과 같은 자리·높이)
open(fn,'w',encoding='utf-8').write(s); print('ok',fn)
