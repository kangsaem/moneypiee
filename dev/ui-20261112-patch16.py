import sys
fn=sys.argv[1]; s=open(fn,encoding='utf-8').read()
def rep(a,b,cnt=1):
    global s
    n=s.count(a); assert n==cnt,(fn,a[:70],n); s=s.replace(a,b)
rep("""function mpWideList(){ try{ return !donutCarOn() && window.innerWidth >= 900; }catch(e){ return false; } }""",
    """function mpWideList(){ try{ return !donutCarOn() && window.innerWidth >= 900; }catch(e){ return false; } }
// 중간 폭(641~899px)도 도넛을 왼쪽에 두고 목록 한 줄을 옆에(2026-11-12 사용자: 이 구간에서 도넛이 작아지던 것). 900px↑는 목록 두 줄
function mpSideOn(){ try{ return !donutCarOn() && window.innerWidth > 640; }catch(e){ return false; } }""")
rep("""(function(){ let was = null; window.addEventListener('resize', () => { const w = mpWideList(); if""","""(function(){ let was = null; const lv = () => (mpSideOn() ? 1 : 0) + (mpWideList() ? 1 : 0); window.addEventListener('resize', () => { const w = lv(); if""")
rep("""} was = w; }); was = mpWideList(); })();""","""} was = w; }); was = lv(); })();""")
rep("""  return `<div class="chart-box${U && mpWideList() ? ' side' : ''}" id="stock-sortable-chart\"""","""  return `<div class="chart-box${U && mpSideOn() ? ' side' : ''}" id="stock-sortable-chart\"""")
rep("""  #stock-sortable-chart.side{display:flex;align-items:center;justify-content:center;gap:44px;text-align:left;}""",
    """  #stock-sortable-chart.side{display:flex;align-items:center;justify-content:center;gap:36px;text-align:left;}
  #stock-sortable-chart.side > .legend{flex:0 1 268px;min-width:0;margin:0;}""")
rep("""  @media(min-width:900px){ #stock-sortable-chart .donut-wrap-md""","""  @media(min-width:641px){ #stock-sortable-chart .donut-wrap-md""")
open(fn,'w',encoding='utf-8').write(s); print('ok',fn)
