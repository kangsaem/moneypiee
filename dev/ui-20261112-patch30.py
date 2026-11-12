import sys
fn=sys.argv[1]; s=open(fn,encoding='utf-8').read()
w="""  html += `<div class="tab ${state.activeId===WATCHLIST_ID?'active':''}" data-tab="${WATCHLIST_ID}" style="color:rgba(212,255,61,0.8);">관심</div>`;
"""
v="""  html += `<div class="tab ${state.activeId==='__analysis__'?'active':''}" data-tab="__analysis__" style="color:#D4FF3D;">V1</div>`;
"""
assert s.count(w+v)==1
s=s.replace(w+v, v+w)   # 2026-11-12 사용자: 자산·월별·V1·관심·⚠·관리 순
a="const order = ['__total__', '__history__', WATCHLIST_ID, '__analysis__', '__deleteAccounts__'];"
assert s.count(a)==1
s=s.replace(a,"const order = ['__total__', '__history__', '__analysis__', WATCHLIST_ID, '__deleteAccounts__'];   // 탭 줄 순서와 같게")
open(fn,'w',encoding='utf-8').write(s); print('ok')
