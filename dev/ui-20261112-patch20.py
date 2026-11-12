import sys
fn=sys.argv[1]; s=open(fn,encoding='utf-8').read()
def rep(a,b,cnt=1):
    global s
    n=s.count(a); assert n==cnt,(fn,a[:70],n); s=s.replace(a,b)
rep("""  const maxVal = Math.max(...points.map(p=>p.value), 1, denseMax);
  const minVal = Math.min(0, ...points.map(p=>p.value));""","""  let maxVal = Math.max(...points.map(p=>p.value), 1, denseMax);
  let minVal = Math.min(0, ...points.map(p=>p.value));
  // 2026-11-12 사용자: 자산선과 지수선만 볼 때는 0부터가 아니라 선들이 실제로 움직인 범위(가장 벌어진 곳 기준)로 아래위를 확대
  if((opts.dense || []).length > 0 && !(extraSeries || []).length){
    let lo = Math.min(...points.map(p=>p.value)), hi = maxVal;
    opts.dense.forEach(sr => sr.pts.forEach(p => { if(p[1] < lo) lo = p[1]; }));
    if(hi > lo){ const pad = (hi - lo) * 0.06; minVal = lo - pad; maxVal = hi + pad; }
  }""")
open(fn,'w',encoding='utf-8').write(s); print('ok')
