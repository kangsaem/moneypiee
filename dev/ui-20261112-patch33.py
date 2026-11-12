import sys
fn=sys.argv[1]; s=open(fn,encoding='utf-8').read()
def rep(a,b,cnt=1):
    global s
    n=s.count(a); assert n==cnt,(fn,a[:70],n); s=s.replace(a,b)
A="""  html += `<div class="tab total ${isAsset?'active':''}" data-tab="__total__">자산</div>`;
"""
H="""  html += `<div class="tab total ${state.activeId==='__history__'?'active':''}" data-tab="__history__">월별</div>`;
"""
rep(A+H, H+A)   # 2026-11-12 사용자: 월별·자산·V1·관심·⚠·관리 순
rep("""data-tab="__analysis__" style="color:#D4FF3D;">V1</div>`;""","""data-tab="__analysis__">V1</div>`;""")
rep("""data-tab="${WATCHLIST_ID}" style="color:rgba(212,255,61,0.8);">관심</div>`;""","""data-tab="${WATCHLIST_ID}">관심</div>`;""")
rep("""  .tab.total{color:var(--accent);}""","""  .tab.total{color:var(--accent);}
  .tabs .tab[data-tab]{color:var(--text-dim);}   /* 2026-11-12 사용자: 탭 제목은 모두 관리 탭과 같은 회색(⚠는 그대로) */""")
rep("const order = ['__total__', '__history__', '__analysis__', WATCHLIST_ID, '__deleteAccounts__'];","const order = ['__history__', '__total__', '__analysis__', WATCHLIST_ID, '__deleteAccounts__'];")
rep("const cur = ['__total__', '__domestic__', '__overseas__'].includes(state.activeId) ? 0 : order.indexOf(state.activeId);","const cur = ['__total__', '__domestic__', '__overseas__'].includes(state.activeId) ? 1 : order.indexOf(state.activeId);")
open(fn,'w',encoding='utf-8').write(s); print('ok',fn)
