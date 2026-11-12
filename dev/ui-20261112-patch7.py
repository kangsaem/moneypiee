import sys
fn=sys.argv[1]; s=open(fn,encoding='utf-8').read()
def rep(a,b,cnt=1):
    global s
    n=s.count(a); assert n==cnt,(fn,a[:70],n); s=s.replace(a,b)
# 1) 다른 정렬의 지역 링 색도 장 기준
rep("""    return { ...spec, opacity, arcs: !!U };""","""    if(U && spec.name === 'decorative-region'){   // 금액순·섹터순·이름순의 지역 링도 장중인 쪽 = 밝은 색(2026-11-12 사용자)
      const side = mpMarketSide().side, col = g => g === side ? REGION_LIGHT : REGION_STRONG;
      return { ...spec, opacity, arcs: true, data: spec.data.map(d => d.label === '국내' ? { ...d, color: col('domestic') } : (d.label === '해외' ? { ...d, color: col('overseas') } : d)) };
    }
    return { ...spec, opacity, arcs: !!U };""")
# 2) 경제지표 줄: 위에 고정 + 아래부터 줄어듦
rep("""  .mkt-card{height:115px;display:flex;flex-direction:column;overflow:hidden;}""",
    """  .mkt-card{height:var(--mkt-h, 115px);display:flex;flex-direction:column;overflow:hidden;}
  /* 2026-11-12 사용자: 스크롤해도 경제지표 줄은 화면 위에 남음 — 아래(그래프)부터 줄어들다 이름·값·등락률만 남으면 그 상태로 고정 */
  #marketTicker.mkt-pin{position:fixed;top:0;z-index:900;background:var(--bg);margin:0 !important;box-shadow:-12px 0 0 var(--bg), 12px 0 0 var(--bg), 0 1px 0 var(--border);box-sizing:border-box;}""")
rep("""const MP_SNAP_ON = true;""","""(function(){
  let hold = null, natH = 0, cardH = 115, svgH = 0, minH = 62, raf = 0;
  const upd = () => {
    raf = 0;
    const tk = document.getElementById('marketTicker'); if(!tk) return;
    if(!hold){ hold = document.createElement('div'); hold.id = 'mktHold'; hold.style.marginBottom = tk.style.marginBottom || '8px'; tk.parentNode.insertBefore(hold, tk); hold.appendChild(tk); tk.style.marginBottom = '0'; }
    const pinned = tk.classList.contains('mkt-pin');
    if(!pinned){   // 고정 전의 원래 크기를 재 둠
      natH = tk.offsetHeight;
      const c = tk.querySelector('.mkt-card[data-mktkey]'), ch = c && c.querySelector('.mkt-change'), sv = c && c.querySelector(':scope > svg');
      if(c){ cardH = c.offsetHeight || cardH; if(ch) minH = Math.ceil(ch.offsetTop - c.offsetTop + ch.offsetHeight + 7); if(sv) svgH = sv.getBoundingClientRect().height || svgH; }
    }
    const ad = document.getElementById('adfit-bottom'), off = ad && ad.offsetHeight ? ad.offsetHeight : 0;
    const top = hold.getBoundingClientRect().top - off;
    if(top < 0 && natH > 0 && tk.querySelector('.mkt-card')){
      const r = hold.getBoundingClientRect();
      if(!pinned){ hold.style.height = natH + 'px'; tk.classList.add('mkt-pin'); }
      tk.style.top = off + 'px'; tk.style.left = r.left + 'px'; tk.style.width = r.width + 'px';
      tk.style.setProperty('--mkt-h', Math.max(Math.min(minH, cardH), Math.min(cardH, cardH + top)) + 'px');
      if(svgH) tk.querySelectorAll('.mkt-card > svg').forEach(v => { if(!v.dataset.fz){ v.dataset.fz = '1'; v.style.flex = '0 0 ' + svgH + 'px'; } });   // 그래프는 찌그러지지 않고 아래부터 가려짐
    } else if(pinned){
      tk.classList.remove('mkt-pin'); hold.style.height = ''; tk.style.top = tk.style.left = tk.style.width = ''; tk.style.removeProperty('--mkt-h');
      tk.querySelectorAll('.mkt-card > svg').forEach(v => { delete v.dataset.fz; v.style.flex = ''; });
    }
  };
  const req = () => { if(!raf) raf = requestAnimationFrame(upd); };
  window.addEventListener('scroll', req, { passive: true });
  window.addEventListener('resize', req);
  document.addEventListener('DOMContentLoaded', () => { const tk = document.getElementById('marketTicker'); if(!tk) return;
    try{ new MutationObserver(req).observe(tk, { childList: true }); }catch(e){} req(); });
})();
const MP_SNAP_ON = true;""")
open(fn,'w',encoding='utf-8').write(s); print('ok',fn)
