import sys
fn=sys.argv[1]; s=open(fn,encoding='utf-8').read()
def rep(a,b,cnt=1):
    global s
    n=s.count(a); assert n==cnt,(fn,a[:70],n); s=s.replace(a,b)
rep("""  .sec-all{flex-shrink:0;""","""  /* 넓은 화면: 도넛은 왼쪽, 목록은 오른쪽에 두 줄(2026-11-12 사용자) */
  #stock-sortable-chart.side{display:flex;align-items:center;justify-content:center;gap:44px;text-align:left;}
  #stock-sortable-chart.side > .donut-wrap{flex:0 0 auto;margin:0;}   /* 목록 높이의 위아래 가운데 */
  #stock-sortable-chart.side > .legend.wide2{flex:1 1 0;min-width:0;max-width:600px;width:auto;margin:0;columns:220px 2;column-gap:44px;}
  .sec-all{flex-shrink:0;""")
rep("""  return `<div class="chart-box" id="stock-sortable-chart" data-umode=""","""  return `<div class="chart-box${U && mpWideList() ? ' side' : ''}" id="stock-sortable-chart" data-umode=""")
open(fn,'w',encoding='utf-8').write(s); print('ok',fn)
