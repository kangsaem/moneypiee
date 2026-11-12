import sys
fn=sys.argv[1]; s=open(fn,encoding='utf-8').read()
def rep(a,b,cnt=1):
    global s
    n=s.count(a); assert n==cnt,(fn,a[:70],n); s=s.replace(a,b)
rep("""    if(historyZoom !== 1){   // 확대·축소: 그래프 폭을 배율만큼(화면 폭보다 좁아지지는 않음). 글자 밀도는 점 간격에 맞춤
      const baseW = (chartResp || land) ? contW : 860;
      const minZ = contW / baseW; if(historyZoom < minZ) historyZoom = minZ;
      chartW = Math.round(Math.max(contW, baseW * historyZoom)); chartResp = false; chartLm = byStep(chartW);
    }""","""    const w0 = chartW, r0 = chartResp, l0 = chartLm, baseW = (chartResp || land) ? contW : 860, minZ = contW / baseW;
    // 배율 z일 때의 그래프 크기(확대·축소: 그래프 폭을 배율만큼, 화면 폭보다 좁아지지는 않음. 글자 밀도는 점 간격에 맞춤)
    histSize = z => { if(z === 1) return { w: w0, r: r0, l: l0 }; const w = Math.round(Math.max(contW, baseW * Math.max(minZ, z))); return { w, r: false, l: byStep(w) }; };
    histZoomRange = [minZ, 5];
    if(historyZoom < minZ) historyZoom = minZ;
    if(historyZoom !== 1){ const z = histSize(historyZoom); chartW = z.w; chartResp = z.r; chartLm = z.l; }""")
rep("""  const lineSeries = [];
""","""  const lineSeries = [];
  let histSize = null, histZoomRange = [0.3, 5];   // 확대·축소 크기 계산(아래 HIST_NEW 블록에서 채움)
""")
rep("""    const tw = panel.querySelector('.trend-wrap');
    if(tw){ let d0 = 0, d1 = 0; const dist = t => Math.hypot(t[0].clientX - t[1].clientX, t[0].clientY - t[1].clientY);
      tw.addEventListener('touchstart', ev => { if(ev.touches.length === 2){ d0 = d1 = dist(ev.touches); } }, { passive: true });
      tw.addEventListener('touchmove', ev => { if(ev.touches.length === 2 && d0){ d1 = dist(ev.touches); if(ev.cancelable) ev.preventDefault(); } }, { passive: false });
      tw.addEventListener('touchend', ev => { if(d0 && ev.touches.length < 2){ const f = d1 / d0; d0 = 0; if(Math.abs(f - 1) > 0.08) zoomBy(f); } }, { passive: true });""",
    """    const tw = panel.querySelector('.trend-wrap');
    // 두 손가락 확대·축소: 손가락을 움직이는 동안 그래프를 바로 다시 그림(두 손가락 가운데 지점이 제자리에 남게). 손을 떼면 전체를 다시 그려 마무리(2026-11-12 사용자)
    if(tw){ let d0 = 0, z0 = 1, zNow = 1, mid = 0, frac = 0, raf = 0;
      const dist = t => Math.hypot(t[0].clientX - t[1].clientX, t[0].clientY - t[1].clientY);
      const sc = () => tw.querySelector('.trend-scroll');
      const draw = () => { raf = 0; if(!histSize) return; const z = histSize(zNow), el0 = sc(), left = el0 ? el0.getBoundingClientRect().left : 0;
        tw.innerHTML = lineChartSVG(points, lineSeries, z.w, chartH, z.l, false, chartOpts);
        const el = sc(); if(el) el.scrollLeft = Math.max(0, frac * el.scrollWidth - (mid - left)); };
      // 그리는 동안 손가락 아래 요소가 교체돼 문서에서 빠져도 터치 이벤트는 처음 닿은 요소로 계속 감 → 그 요소에도 같은 처리기를 붙임
      const onMove = ev => { if(ev.touches.length !== 2 || !d0) return; if(ev.cancelable) ev.preventDefault();
        zNow = Math.max(histZoomRange[0], Math.min(histZoomRange[1], z0 * dist(ev.touches) / d0));
        if(!raf) raf = requestAnimationFrame(draw); };
      const onEnd = ev => { if(!d0 || ev.touches.length >= 2) return; d0 = 0; if(raf){ cancelAnimationFrame(raf); raf = 0; }
        if(Math.abs(zNow - z0) < 0.02) return;
        const el = sc(), keep = el ? el.scrollLeft : null;
        historyZoom = Math.abs(zNow - 1) < 0.06 ? 1 : zNow; render();
        const el2 = document.querySelector('#panel .trend-scroll'); if(el2 && keep != null) el2.scrollLeft = keep; };
      tw.addEventListener('touchstart', ev => { if(ev.touches.length !== 2) return; const el = sc(); if(!el) return;
        d0 = dist(ev.touches); z0 = zNow = historyZoom; mid = (ev.touches[0].clientX + ev.touches[1].clientX) / 2;
        frac = (mid - el.getBoundingClientRect().left + el.scrollLeft) / Math.max(1, el.scrollWidth);
        const tg = ev.target; if(tg && tg !== tw && !tg._pz){ tg._pz = 1; tg.addEventListener('touchmove', e2 => { if(!tw.contains(tg)) onMove(e2); }, { passive: false }); tg.addEventListener('touchend', e2 => { if(!tw.contains(tg)) onEnd(e2); }, { passive: true }); tg.addEventListener('touchcancel', e2 => { if(!tw.contains(tg)) onEnd(e2); }, { passive: true }); }
      }, { passive: true });
      tw.addEventListener('touchmove', onMove, { passive: false });
      tw.addEventListener('touchend', onEnd, { passive: true }); tw.addEventListener('touchcancel', onEnd, { passive: true });""")
open(fn,'w',encoding='utf-8').write(s); print('ok',fn)
