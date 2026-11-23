# 배당 표시 위치(2026-11-23, 사용자 A+B-1): A = '지표 ▾' 접힘 줄 옆 배당 칸(펼치면 숨김) · B-1 = 미국채 10년보다 높으면 이름 바로 뒤 연두 점
import sys
path = sys.argv[1]; s = open(path, encoding='utf-8').read()
def rep(old, new, n=1):
    global s
    c = s.count(old)
    if c != n: raise SystemExit(f'찾은 개수 {c} != {n}: {old[:80]!r}')
    s = s.replace(old, new)
# 미국채 비교를 함수로
rep("""function anDivTag(r){
  const dy = r.dy;
  if(!dy || !anOk(dy.pct)) return '';
  const t = typeof marketData !== 'undefined' && marketData.us10y && marketData.us10y.price;
  const hasT = anOk(t) && t > 0, gap = hasT ? dy.pct - t : null;""",
"""function anDivGap(r){   // 배당 − 미국채 10년(%p), 비교할 수 없으면 null
  const dy = r && r.dy, t = typeof marketData !== 'undefined' && marketData.us10y && marketData.us10y.price;
  return dy && anOk(dy.pct) && anOk(t) && t > 0 ? { gap: dy.pct - t, t } : null;
}
function anDivDot(r){   // B-1: 고배당(미국채 10년보다 높음) 종목 이름 뒤 연두 점
  const g = anDivGap(r);
  return g && g.gap > 0 ? `<i class="an-dvdot" title="${anE(`배당 ${r.dy.pct.toFixed(2)}% · 미국채 10년 ${g.t.toFixed(2)}%보다 ${anS(g.gap, 2)}%p`)}"></i>` : '';
}
function anDivTag(r){
  const dy = r.dy;
  if(!dy || !anOk(dy.pct)) return '';
  const g = anDivGap(r), hasT = !!g, t = g ? g.t : null, gap = g ? g.gap : null;""")
# B-1: 이름 뒤
rep("""<b title="${anE(r.name)}">${anE(anNm16(r.name))}</b> ${gchips}""",
"""<b title="${anE(r.name)}">${anE(anNm16(r.name))}</b>${anDivDot(r)} ${gchips}""")
# A: 접힘 줄
rep("""><summary>지표</summary>${mh}</details>`""",
"""><summary><span class="an-mfl">지표</span>${(() => { const dv = anDivTag(r); return dv ? `<span class="an-dvs">${dv}</span>` : ''; })()}</summary>${mh}</details>`""")
rep(""".an-mfold > summary::-webkit-details-marker { display:none; } .an-mfold > summary::after { content:' ▾'; } .an-mfold[open] > summary::after { content:' ▴'; }""",
""".an-mfold > summary::-webkit-details-marker { display:none; } .an-mfold > summary > .an-mfl::after { content:' ▾'; } .an-mfold[open] > summary > .an-mfl::after { content:' ▴'; }
.an-mfold > summary > .an-dvs { margin-left:6px; } .an-mfold[open] > summary > .an-dvs { display:none; }   /* 배당: 접힌 줄에만(펼치면 안쪽 칸, 2026-11-23) */
.an-dvdot { display:inline-block; width:5px; height:5px; border-radius:50%; background:#9BD266; margin:0 3px 0 2px; vertical-align:middle; flex-shrink:0; }""")
open(path, 'w', encoding='utf-8').write(s); print('ok', path)
