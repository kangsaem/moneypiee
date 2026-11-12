import sys
fn=sys.argv[1]; s=open(fn,encoding='utf-8').read()
def rep(a,b,cnt=1):
    global s
    n=s.count(a); assert n==cnt,(fn,a[:70],n); s=s.replace(a,b)
# 링을 호(path)로: 아주 작은 조각이 점선 방식에서 12시에 덩어리로 튀어나오던 것 방지
rep("""function ringSegmentsSVG(data, type, cx, cy, radius, strokeWidth, ringName, opacity){
  const total = _.sumBy(data, 'amount') || 1;""","""function ringSegmentsSVG(data, type, cx, cy, radius, strokeWidth, ringName, opacity, arcs){
  const total = _.sumBy(data, 'amount') || 1;
  if(arcs && data.length > 1){
    // 통일 도넛(2026-11-12): 조각을 채운 호로 그림 — 점선(dasharray) 방식은 0.1% 안팎 조각이 일부 기기에서 12시 방향에 덩어리로 삐져나옴(사용자 화면)
    const r0 = radius - strokeWidth/2, r1 = radius + strokeWidth/2, op = (opacity !== undefined && opacity !== null) ? ` opacity="${opacity}"` : '';
    const pt = (r, a) => (cx + r*Math.cos(a*Math.PI/180)).toFixed(2) + ',' + (cy + r*Math.sin(a*Math.PI/180)).toFixed(2);
    let ang = -90, out = '';
    data.forEach((d, i) => {
      const sweep = Math.min(359.99, (d.amount / total) * 360); if(!(sweep > 0)) return;
      const rank = d.rank !== undefined ? d.rank : i, rankCount = d.rankCount !== undefined ? d.rankCount : data.length;
      const color = d.color || rankColor(d.label, rank, rankCount, type), end = ang + sweep, lg = sweep > 180 ? 1 : 0;
      out += `<path d="M${pt(r1, ang)} A${r1},${r1} 0 ${lg} 1 ${pt(r1, end)} L${pt(r0, end)} A${r0},${r0} 0 ${lg} 0 ${pt(r0, ang)} Z" fill="${color}"${op}${d.attrs || ''} transform="translate(${2*cx},0) scale(-1,1)" data-ring="${ringName}" data-slice-idx="${i}"><title>${escapeHTML(d.label)} ${d.pct.toFixed(1)}%</title></path>`;
      ang = end;
    });
    return out;
  }""")
rep("""    return ringSegmentsSVG(ordered, spec.type, cx, cy, r, ringW, spec.name, spec.opacity);""",
    """    return ringSegmentsSVG(ordered, spec.type, cx, cy, r, ringW, spec.name, spec.opacity, spec.arcs);""")
rep("""    if(U && spec.name === 'decorative-sector' && U.secRing) return { ...spec, data: U.secRing, preOrdered: true, opacity: null };   // 종목 순서와 맞춘 섹터 링(지역순이면 지역별 섹터 비중)
    if(U && spec.name === 'decorative-region'){
      if(stockLegendSortMode === 'group') opacity = 0;                                  // 섹터순에서는 지역 링 숨김(자리는 유지해 도넛 크기가 안 변함)
      else if(U.regRing) return { ...spec, data: U.regRing, preOrdered: true, opacity: 1 };
    }
    return { ...spec, opacity };""","""    // 종목 순서와 맞춘 섹터 링(지역순이면 지역별 섹터 비중). 지역순에서는 톤다운(0.7), 섹터순의 지역 링도 톤다운(0.7) — 2026-11-12 사용자
    if(U && spec.name === 'decorative-sector' && U.secRing) return { ...spec, data: U.secRing, preOrdered: true, opacity: stockLegendSortMode === 'region' ? 0.7 : null, arcs: true };
    if(U && spec.name === 'decorative-region' && stockLegendSortMode === 'region' && U.regRing) return { ...spec, data: U.regRing, preOrdered: true, opacity: 1, arcs: true };
    return { ...spec, opacity, arcs: !!U };""")
# 도넛 크기는 줄이지 않음
rep("""  const size = Math.round(Math.max(150, Math.min(H - top - ARW, r.height * 1.25, (box.clientWidth || 300) - 24)));
  const spare = Math.max(0, H - ARW - top - size);
  dw.style.width = dw.style.height = size + 'px';""","""  const size = r.height;   // 도넛 크기는 그대로(2026-11-12 사용자: 줄이지 말 것). 화면이 낮으면 도넛 아래가 첫 화면을 조금 넘어감
  const spare = Math.max(0, H - ARW - top - size);""")
# 끌기: 첫 움직임부터 기본 스크롤을 막고(아이폰), 그래도 흘러간 스크롤은 멈춘 뒤 가까운 단계로 붙임
rep("""    if(mode === 0){
      if(Math.abs(dx) < 3 && Math.abs(dy) < 3) return;
      if(Math.abs(dy) <= Math.abs(dx)){ mode = -1; return; }          // 가로 끌기(지표 카드 넘기기 등)는 그대로
      if(dy > 0 && window.scrollY <= 0){ mode = -1; return; }         // 맨 위에서 아래로 당기기(새로고침)는 그대로
      mode = 1;
    }""","""    if(mode === 0){
      // 첫 움직임에서 바로 판정: 아이폰은 첫 touchmove를 막지 않으면 기본 스크롤이 시작돼 그 뒤로는 못 막음(사용자: 딱딱 안 붙음)
      if(Math.abs(dx) > Math.abs(dy)){ mode = -1; return; }           // 가로 끌기(지표 카드 넘기기 등)는 그대로
      if(dy > 0 && window.scrollY <= 0){ mode = -1; return; }         // 맨 위에서 아래로 당기기(새로고침)는 그대로
      mode = 1;
    }""")
rep("""  document.addEventListener('touchstart', e => {
    mode = (e.touches.length === 1 && mpSnapActive() && !own(e.target)) ? 0 : -1;""","""  let fingers = 0, rest = 0, idle = null;
  // 기본 스크롤이 흘러가 버린 경우(막지 못한 끌기·관성): 멈추면 움직인 방향의 다음 단계로 붙임
  const settle = () => {
    if(!mpSnapActive() || mpSnapAnim || fingers > 0) return;
    const st = mpSnapStages(), cur = window.scrollY;
    if(st.some(y => Math.abs(y - cur) <= 6)){ rest = cur; return; }
    const dir = cur > rest ? 1 : -1; window.scrollTo(0, cur);
    const before = window.scrollY; mpSnapGo(dir); setTimeout(() => { if(Math.abs(window.scrollY - before) < 2 && !mpSnapAnim) mpSnapGo(-dir); }, 60);
  };
  window.addEventListener('scroll', () => { clearTimeout(idle); if(!mpSnapAnim) idle = setTimeout(settle, 130); else rest = window.scrollY; }, { passive: true });
  document.addEventListener('touchstart', e => { fingers = e.touches.length; }, { passive: true });
  ['touchend', 'touchcancel'].forEach(n => document.addEventListener(n, e => { fingers = e.touches.length; clearTimeout(idle); idle = setTimeout(settle, 130); }, { passive: true }));
  document.addEventListener('touchstart', e => {
    mode = (e.touches.length === 1 && mpSnapActive() && !own(e.target)) ? 0 : -1;""")
open(fn,'w',encoding='utf-8').write(s); print('ok',fn)
