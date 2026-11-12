import sys
fn=sys.argv[1]; s=open(fn,encoding='utf-8').read()
def rep(a,b,cnt=1):
    global s
    n=s.count(a); assert n==cnt,(fn,a[:70],n); s=s.replace(a,b)
rep("""  if(!on || !dw || !panel){ mpSnapArrow(); return; }
  const H = window.innerHeight,""","""  if(panel) mpSnapLayout.top = Math.round(panel.getBoundingClientRect().top + window.scrollY);
  if(!on || !dw || !panel){ mpSnapArrow(); return; }
  const H = window.innerHeight,""")
rep("""  window.addEventListener('mp-fold-done', () => { try{ mpSnapArrow(); }catch(e){} });""",
    """  window.addEventListener('mp-fold-done', () => { try{ mpSnapArrow(); }catch(e){} });
  // 탭 위쪽(지표 카드 등)이 늦게 그려져 높이가 바뀌면 첫 화면 맞춤을 다시 계산
  document.addEventListener('DOMContentLoaded', () => { try{
    new ResizeObserver(() => { const p = document.getElementById('panel'); if(!p) return;
      const t = Math.round(p.getBoundingClientRect().top + window.scrollY); if(t !== mpSnapLayout.top){ try{ mpSnapLayout(); }catch(e){} } else mpSnapArrow(); }).observe(document.body);
  }catch(e){} });""")
open(fn,'w',encoding='utf-8').write(s); print('ok',fn)
