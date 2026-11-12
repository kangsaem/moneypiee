import sys
fn=sys.argv[1]; s=open(fn,encoding='utf-8').read()
a="""  if(!on || !dw || !panel){ mpSnapArrow(); return; }
  const H = window.innerHeight,"""
assert s.count(a)==1
s=s.replace(a,"""  if(!on || !dw || !panel || !MP_SNAP_FIT){ mpSnapArrow(); return; }   // 첫 화면 맞춤(도넛 위아래 여백)은 끔: 끌기 붙임을 뺀 뒤로는 빈 공간만 생김(2026-11-12 사용자)
  const H = window.innerHeight,""")
b="const MP_SNAP_DRAG = false;"
assert s.count(b)==1
s=s.replace(b,"const MP_SNAP_FIT = false;    // 도넛 위아래 여백으로 첫 화면을 꽉 채우는 맞춤\n"+b)
open(fn,'w',encoding='utf-8').write(s); print('ok',fn)
