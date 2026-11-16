import re
p='crash200.js'; s=open(p,encoding='utf-8').read()
def rep(a,b,cnt=1):
    global s
    assert s.count(a)==cnt,(a[:70],s.count(a)); s=s.replace(a,b)
rep("""const G_NOTE = '그래프: <b class="gn-r">▲</b> = 이탈 뒤 최저 종가 날(위로 빨간 점선) · <b class="gn-r">빨간 점선</b> = 200일선 상향 돌파(날짜 = 안정일 돌파) · <b class="gn-b">하늘색 영역</b> = 안정일부터 40거래일(200일선 위 유지로 안정을 확인한 구간) · 선 = 종가(흰)·200일(빨강)·5주·10주·60주(보라)';""",
    """const G_NOTE = '그래프: <b class="gn-r">▲</b> = 이탈 뒤 최저 종가 날(위로 빨간 점선) · <b class="gn-r">빨간 점선</b> = 200일선 상향 돌파(날짜 = 안정일 돌파) · <b class="gn-b">연두색 영역</b> = 안정일부터 40거래일(200일선 위 유지로 안정을 확인한 구간) · 선 = 종가(흰)·200일(빨강)·5주·10주·60주(보라) · 아래 띠 = VIX <b class="gn-v1">25 이상</b>·<b class="gn-v2">30 이상</b>(V1과 같음, 대거나 누르면 기간·최고값)';""")
rep("""  const cut = x => x.slice(a, b + 1), ma = gRoll(C, 200);
  const ch = { dates:""", """  const cut = x => x.slice(a, b + 1), ma = gRoll(C, 200);
  const ch = { full: cut(D), dates:""")
# svg: VIX 띠
rep("""  const W = 660, PH = 170, pl = 4, pt = 4, pb = 26, H = pt + PH + pb, xr = W - 2;""",
    """  const VO = VIX ? 12 : 0, W = 660, PH = 170, pl = 4, pt = 4, pb = 26 + VO, H = pt + PH + pb, xr = W - 2;   // VO = VIX 띠(높이 8 + 위 간격 4, 2026-11-16)""")
rep("""    o.push(`<text class="g-lowmk" x="${xv.toFixed(1)}" y="${pt + PH + 10}" text-anchor="middle">▲</text>`);""",
    """    o.push(`<text class="g-lowmk" x="${xv.toFixed(1)}" y="${pt + PH + VO + 10}" text-anchor="middle">▲</text>`);""")
rep("""  const anchor = xv => xv < 60 ? 'start' : xv > xr - 60 ? 'end' : 'middle';""",
    """  if(VO) o.push(gVixStrip(ch.full, n, x, half, pt + PH + 4, 8, pl, xr));
  const anchor = xv => xv < 60 ? 'start' : xv > xr - 60 ? 'end' : 'middle';""")
rep("""function gPath(v, x, y){""", """// VIX 띠(V1 지수 차트와 같은 색: 25↑ 옅은 주황 0.40, 30↑ 진한 주황 0.85). 야후 ^VIX 1990년~ 일봉, 하루 한 번 받아 이 기기에 저장
let VIX = null;
function gVixStrip(full, n, x, half, vy, vh, pl, xr){
  const at = d => { let lo = 0, hi = VIX.d.length - 1, r = -1; while(lo <= hi){ const m = (lo + hi) >> 1; if(VIX.d[m] <= d){ r = m; lo = m + 1; } else hi = m - 1; } return r; };
  const vi = full.slice(0, n).map(at), val = j => vi[j] >= 0 ? VIX.c[vi[j]] : null, lv = j => { const v = val(j); return v == null ? 0 : v >= 30 ? 2 : v >= 25 ? 1 : 0; };
  let s = `<rect class="an-ch-bg" x="0" y="${vy}" width="${xr}" height="${vh}"/>`;
  for(let j = 0; j < n;){
    const a = lv(j); let e = j; while(e + 1 < n && lv(e + 1) === a) e++;
    if(a){ let mx = -Infinity; for(let q = j; q <= e; q++){ const v = val(q); if(v > mx) mx = v; }
      const x0 = Math.max(pl, x(j) - half), w = Math.max(1.2, Math.min(xr, x(e) + half) - x0), f = d => d.slice(2).replace(/-/g, '.');
      s += `<rect class="g-vix" x="${x0.toFixed(1)}" y="${vy}" width="${w.toFixed(1)}" height="${vh}" fill="${a === 2 ? 'rgba(242,166,90,0.85)' : 'rgba(242,166,90,0.40)'}" data-zt="${esc(`VIX ${a === 2 ? '30' : '25'} 이상 · ${f(full[j])} ~ ${f(full[e])}\\n최고 ${Math.round(mx * 10) / 10}`)}"/>`; }
    j = e + 1;
  }
  return s;
}
(async function(){
  const K = 'c200:vix1', today = new Date(Date.now() + 9 * 3600e3).toISOString().slice(0, 10);
  let c = null; try{ c = JSON.parse(localStorage.getItem(K) || 'null'); }catch(e){}
  const use = v => { VIX = v; document.querySelectorAll('.gch').forEach(g => { const P = GP.get(g); if(P) gRender(g, P); }); };
  if(c && c.d && c.d.length) use(c);
  if(c && c.at === today) return;
  try{
    const res = await fetchViaProxy('https://query1.finance.yahoo.com/v8/finance/chart/%5EVIX?range=max&interval=1d', 20000);
    const r = (await res.json())?.chart?.result?.[0], ts = r?.timestamp || [], q = r?.indicators?.quote?.[0]?.close || [];
    const d = [], cl = [];
    ts.forEach((t, i) => { const v = q[i]; if(v == null || !isFinite(v)) return; const k = new Date((t + (r.meta?.gmtoffset || 0)) * 1000).toISOString().slice(0, 10); if(d.length && d[d.length - 1] === k){ cl[cl.length - 1] = Math.round(v * 100) / 100; return; } d.push(k); cl.push(Math.round(v * 100) / 100); });
    if(d.length > 1000){ const v = { d, c: cl, at: today }; try{ localStorage.setItem(K, JSON.stringify(v)); }catch(e){} use(v); }
  }catch(e){}
})();
(function(){                                                   // 띠에 마우스를 대거나 누르면 기간·최고값
  let tip = null;
  const show = (el, cx, cy) => { if(!tip){ tip = document.createElement('div'); tip.className = 'g-tip'; document.body.appendChild(tip); }
    tip.textContent = el.getAttribute('data-zt'); tip.style.display = 'block';
    const w = Math.min(240, innerWidth - 16); tip.style.left = Math.max(8 + w / 2, Math.min(innerWidth - 8 - w / 2, cx)) + 'px'; tip.style.top = cy + 'px'; };
  const hide = () => { if(tip) tip.style.display = 'none'; };
  document.addEventListener('mousemove', e => { const z = e.target.closest && e.target.closest('.g-vix'); if(z) show(z, e.clientX, e.clientY); else hide(); }, { passive: true });
  document.addEventListener('click', e => { const z = e.target.closest && e.target.closest('.g-vix'); if(z) show(z, e.clientX, e.clientY); else hide(); }, true);
  addEventListener('scroll', hide, { passive: true });
})();
function gPath(v, x, y){""")
open(p,'w',encoding='utf-8').write(s)
c=open('crash200.css',encoding='utf-8').read()
c=c.replace(".gch .g-blue{fill:#5FB8E0;opacity:.3}", ".gch .g-blue{fill:#A3E635;opacity:.3}   /* 안정 40거래일 = 연두(2026-11-16, 전엔 하늘색) */")
c=c.replace(".note .gn-r{color:#FF3B30;font-weight:600} .note .gn-b{color:#5FB8E0;font-weight:600}", ".note .gn-r{color:#FF3B30;font-weight:600} .note .gn-b{color:#A3E635;font-weight:600}")
c+="""/* 2026-11-16 VIX 띠(V1과 같은 색) */
.note .gn-v1{color:rgba(242,166,90,.6);font-weight:600} .note .gn-v2{color:#F2A65A;font-weight:600}
.gch .g-vix{cursor:pointer}
.g-tip{position:fixed;z-index:9999;display:none;transform:translate(-50%,calc(-100% - 10px));max-width:240px;padding:6px 9px;border-radius:8px;background:#2A2B30;border:1px solid #3A3B40;color:#E6E6E6;font-size:12px;line-height:1.45;white-space:pre-line;pointer-events:none;box-shadow:0 4px 14px rgba(0,0,0,.4)}
"""
open('crash200.css','w',encoding='utf-8').write(c)
for f in ['kospi200.html','spx200.html','ndx200.html']:
    h=open(f,encoding='utf-8').read()
    h=h.replace('crash200.css?v=20261103a','crash200.css?v=20261116a').replace('crash200.js?v=20261022a','crash200.js?v=20261116a')
    open(f,'w',encoding='utf-8').write(h)
