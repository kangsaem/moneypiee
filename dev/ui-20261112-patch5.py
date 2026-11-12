import sys
fn=sys.argv[1]; s=open(fn,encoding='utf-8').read()
def rep(a,b,cnt=1):
    global s
    n=s.count(a); assert n==cnt,(fn,a[:70],n); s=s.replace(a,b)
rep("const MP_SNAP_ON = true;","const MP_SNAP_ON = true;\nconst MP_SNAP_DRAG = false;   // 끌 때 단계로 붙는 동작(2026-11-12 사용자: 없앰 — 접힘 줄 누르기 힘듦). ▼ 누름과 첫 화면 맞춤만 남김")
rep("    if(!mpSnapActive() || mpSnapAnim || fingers > 0) return;","    if(!MP_SNAP_DRAG || !mpSnapActive() || mpSnapAnim || fingers > 0) return;")
rep("    mode = (e.touches.length === 1 && mpSnapActive() && !own(e.target)) ? 0 : -1;","    mode = (MP_SNAP_DRAG && e.touches.length === 1 && mpSnapActive() && !own(e.target)) ? 0 : -1;")
rep("  .sec-head{display:flex;align-items:center;gap:8px;margin:8px 0 4px;width:100%;cursor:pointer;","  .sec-head{display:flex;align-items:center;gap:8px;margin:-7px 0;padding:7px 0;width:100%;box-sizing:border-box;cursor:pointer;")
open(fn,'w',encoding='utf-8').write(s); print('ok',fn)
