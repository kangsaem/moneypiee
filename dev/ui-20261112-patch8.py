import sys
fn=sys.argv[1]; s=open(fn,encoding='utf-8').read()
def rep(a,b,cnt=1):
    global s
    n=s.count(a); assert n==cnt,(fn,a[:70],n); s=s.replace(a,b)
rep("""  #marketTicker.mkt-pin{position:fixed;""","""  #marketTicker.mkt-min .mkt-card > .mkt-change ~ *{visibility:hidden;}   /* 다 줄어든 상태: 등락률 줄 아래(그래프·이격도 줄)는 완전히 숨김 — 카드 아래 여백에 그래프 찌꺼기가 보이던 것 */
  #marketTicker.mkt-pin{position:fixed;""")
rep("""      tk.style.setProperty('--mkt-h', Math.max(Math.min(minH, cardH), Math.min(cardH, cardH + top)) + 'px');""",
    """      const hNow = Math.max(Math.min(minH, cardH), Math.min(cardH, cardH + top)), vis = Math.max(0, hNow - minH);
      tk.style.setProperty('--mkt-h', hNow + 'px');
      tk.classList.toggle('mkt-min', vis < 1);
      tk.querySelectorAll('.mkt-card > svg').forEach(v => { v.style.clipPath = svgH ? `inset(0 0 ${Math.max(0, svgH - vis).toFixed(1)}px 0)` : ''; });   // 그래프는 카드 아래 여백(7px) 안쪽까지만 보이게""")
rep("""      tk.classList.remove('mkt-pin'); hold.style.height""","""      tk.classList.remove('mkt-pin', 'mkt-min'); tk.querySelectorAll('.mkt-card > svg').forEach(v => { v.style.clipPath = ''; }); hold.style.height""")
open(fn,'w',encoding='utf-8').write(s); print('ok',fn)
