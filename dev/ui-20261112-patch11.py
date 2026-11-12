import sys
fn=sys.argv[1]; s=open(fn,encoding='utf-8').read()
def rep(a,b,cnt=1):
    global s
    n=s.count(a); assert n==cnt,(fn,a[:70],n); s=s.replace(a,b)
rep("""background:transparent;margin:0 !important;box-sizing:border-box;pointer-events:none;} #marketTicker.mkt-pin .mkt-card{pointer-events:auto;}""",
    """background:transparent;margin:0 !important;box-sizing:border-box;}
  /* 고정된 카드 뒤에 배경색 그림자(아래로 부드럽게 사라짐) — 누름은 통과(2026-11-12 사용자) */
  #mktShade{position:fixed;z-index:899;display:none;pointer-events:none;background:linear-gradient(to bottom, var(--bg) 0, var(--bg) calc(100% - 8px), rgba(30,31,34,0) 100%);}""")
rep("""      tk.style.setProperty('--mkt-h', hNow + 'px');""","""      tk.style.setProperty('--mkt-h', hNow + 'px');
      let sh = document.getElementById('mktShade'); if(!sh){ sh = document.createElement('div'); sh.id = 'mktShade'; document.body.appendChild(sh); }
      sh.style.display = 'block'; sh.style.top = off + 'px'; sh.style.left = '0px'; sh.style.width = '100%'; sh.style.height = (hNow + 6 + 8) + 'px';""")
rep("""      tk.classList.remove('mkt-pin', 'mkt-min');""","""      tk.classList.remove('mkt-pin', 'mkt-min'); { const sh = document.getElementById('mktShade'); if(sh) sh.style.display = 'none'; }""")
open(fn,'w',encoding='utf-8').write(s); print('ok',fn)
