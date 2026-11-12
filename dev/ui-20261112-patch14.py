import sys
fn=sys.argv[1]; s=open(fn,encoding='utf-8').read()
def rep(a,b,cnt=1):
    global s
    n=s.count(a); assert n==cnt,(fn,a[:70],n); s=s.replace(a,b)
rep("""        const hf = (on) => `<div class="rg-head rg-fold${g === other ? ' rg-sep' : ''}" data-region-fold="${g}" data-region-folded="1"${on ? '' : off}><span>▸</span><b>${nm} ${cnt[g]}종목</b>${live}<span class="rg-cap">눌러서 펼치기</span><button type="button" class="rg-reload" title="시세 새로고침">↻</button></div>`;
        const ho = (on) => `<div class="rg-head${g === other ? ' rg-sep' : ''}" data-region-fold="${g}" data-region-folded="0"${on ? '' : off}><span>▾</span><b>${nm}</b>${live}<span class="rg-cap">${cap}</span></div>`;""",
    """        // 2026-11-12 사용자: 끝에는 '등락률·비중·평가액' 글자 대신 그 지역의 전체 대비 비중. 첫 지역 줄 가운데에 모두 펴기/접기
        const rpct = DONUT_ONE ? `<span class="rg-cap sec-pct num" style="font-size:13px;">${_.sumBy(data.filter(d => gOf(d) === g), 'pct').toFixed(1)}<span class="pct-sign">%</span></span>` : null;
        const allB = (DONUT_ONE && g !== other && !mpWideList()) ? `<span class="sec-all" data-reg-all style="margin-left:auto;">${(!folded.domestic && !folded.overseas) ? '▴ 모두 접기' : '▾ 모두 펴기'}</span>` : '';
        const hf = (on) => `<div class="rg-head rg-fold${g === other ? ' rg-sep' : ''}" data-region-fold="${g}" data-region-folded="1"${on ? '' : off}><span>▸</span><b>${nm} ${cnt[g]}종목</b>${live}${allB}${rpct || '<span class="rg-cap">눌러서 펼치기</span>'}<button type="button" class="rg-reload" title="시세 새로고침">↻</button></div>`;
        const ho = (on) => `<div class="rg-head${g === other ? ' rg-sep' : ''}" data-region-fold="${g}" data-region-folded="0"${on ? '' : off}><span>▾</span><b>${nm}</b>${live}${allB}${rpct || `<span class="rg-cap">${cap}</span>`}</div>`;""")
rep("""  const g = el.dataset.regionFold, nowFolded = el.dataset.regionFolded !== '1';
  stockRegionFold[g] = nowFolded;
  const box = el.closest('#stock-sortable-chart'), body = box && mpFoldBody(box, 'reg', g);
  if(!DONUT_ONE || !body){ renderPreservingOpenChartAccordions(); return; }
  box.querySelectorAll('[data-region-fold="' + g + '"]').forEach(h => { h.style.display = ((h.dataset.regionFolded === '1') === nowFolded) ? '' : 'none'; });
  mpFold(body, !nowFolded); mpDonutSync();
  try{ assetPanelEnhance(); }catch(e){}
});""","""  const g = el.dataset.regionFold, nowFolded = el.dataset.regionFolded !== '1';
  const box = el.closest('#stock-sortable-chart'), body = box && mpFoldBody(box, 'reg', g);
  if(!DONUT_ONE || !body){ stockRegionFold[g] = nowFolded; renderPreservingOpenChartAccordions(); return; }
  mpRegionSet(box, g, nowFolded);
});
function mpRegionSet(box, g, nowFolded){
  stockRegionFold[g] = nowFolded;
  box.querySelectorAll('[data-region-fold="' + g + '"]').forEach(h => { h.style.display = ((h.dataset.regionFolded === '1') === nowFolded) ? '' : 'none'; });
  mpFold(mpFoldBody(box, 'reg', g), !nowFolded); mpDonutSync();
  const f = stockRegionFoldState().folded, t = (!f.domestic && !f.overseas) ? '▴ 모두 접기' : '▾ 모두 펴기';
  box.querySelectorAll('[data-reg-all]').forEach(b => { b.textContent = t; });
  try{ assetPanelEnhance(); }catch(e){}
}
document.addEventListener('click', e => {
  const b = e.target.closest && e.target.closest('[data-reg-all]'); if(!b) return;
  e.stopPropagation();
  const box = b.closest('#stock-sortable-chart'); if(!box) return;
  const f = stockRegionFoldState().folded, fold = !f.domestic && !f.overseas;   // 둘 다 펼쳐져 있으면 모두 접기, 아니면 모두 펴기
  ['domestic', 'overseas'].forEach(g => { if(f[g] !== fold) mpRegionSet(box, g, fold); });
}, true);""")
open(fn,'w',encoding='utf-8').write(s); print('ok',fn)
