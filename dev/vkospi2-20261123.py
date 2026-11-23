# 바닥 6번째 항목 규칙 변경(2026-11-23 사용자): 'VKOSPI 꺾임 + 코스피 회복' 3단계 — 판정은 리포트(market_report.vk_rule)가 하고
# market.json vkospi {last, d5, on, stage 0~3, wait, wait_max, ma, thr, spike, peak, peak_d, k, kma, nolow, ma_ok, klo, klo_d, rule, chart{d,v,ma,k,kma,klo,st}, hist{d,v,on}}
# 앱: 게이지 줄 = 이름 + 단계 점(●●○) + 값(VKOSPI), 대기(2단계)면 속 빈 점. 줄을 누르면 6개월 그래프 팝업(위 VKOSPI · 아래 코스피 회복 기준)
# 사용: python dev/vkospi2-20261123.py test.html   (dev/vkospi-20261123.py 다음)
import sys
path = sys.argv[1]; s = open(path, encoding='utf-8').read()
def rep(old, new, n=1):
    global s
    c = s.count(old)
    if c != n: raise SystemExit(f'찾은 개수 {c} != {n}: {old[:90]!r}')
    s = s.replace(old, new)

# 1) 6번째 항목
rep("""    // 6번째(2026-11-23, B안): 변동성 진정 확인 — 하락이 끝날 때 마지막에 켜지는 항목. 자료 = 리포트(KRX Open API)
    [`VKOSPI ${AN_VK.TH} 이하\\n(최근 ${AN_VK.WIN}거래일 안에 ${AN_VK.TH} 넘은 뒤)`,
      snap.vk ? anF(snap.vk.last, 1) + (snap.vk.max60 > AN_VK.TH ? ` · 최고 ${anF(snap.vk.max60, 0)}` : '') : '-',
      snap.vk ? !!snap.vk.on : null]
  ];""",
"""    // 6번째(2026-11-23): VKOSPI 꺾임 + 코스피 회복(3단계, 판정 = 리포트 market_report.vk_rule). 게이지에서 단계 점·그래프 팝업(anVkPopup)
    [AN_VK_NAME, snap.vk && snap.vk.stage != null ? anF(snap.vk.last, 1) : '-', snap.vk && snap.vk.stage != null ? !!snap.vk.on : null]
  ];
  anVkNow = snap.vk && snap.vk.stage != null ? snap.vk : null;""")
rep("""const AN_VK = { TH: 30, WIN: 60 };   // 리포트 market_report.VK_TH·VK_WIN과 같음""",
"""const AN_VK_NAME = 'VKOSPI 꺾임 + 코스피 회복';
let anVkNow = null;   // 마지막 시장 자료의 VKOSPI 판정(팝업용)""")
rep("""'VIX 30↑', '내 종목 30%↑ RSI 35↓', 'VKOSPI 30↓(진정)'];""", """'VIX 30↑', '내 종목 30%↑ RSI 35↓', 'VKOSPI 꺾임+코스피 회복'];""")

# 2) 게이지 줄
rep("""  const rows = ord.map(k => g.items[k]).filter(Boolean).map(([lb, val, st]) => `<li class="${st ? 'on' : st == null ? 'na' : 'off'}"><span class="an-dot"></span><span class="an-gt">${anE(lb)}</span><b>${anE(val)}</b></li>`).join('');""",
"""  const rows = ord.map(k => g.items[k]).filter(Boolean).map(([lb, val, st]) => {
    const cls = st ? 'on' : st == null ? 'na' : 'off';
    if(key === 'bottom' && lb === AN_VK_NAME && anVkNow)     // 단계 점 + 누르면 그래프(2026-11-23)
      return `<li class="${cls} an-vkli${anVkNow.stage === 2 ? ' wt' : ''}" onclick="anVkPopup()" title="누르면 그래프"><span class="an-dot"></span><span class="an-gt">${anE(lb)}${anVkDots(anVkNow.stage)}</span><b>${anE(val)}</b></li>`;
    return `<li class="${cls}"><span class="an-dot"></span><span class="an-gt">${anE(lb)}</span><b>${anE(val)}</b></li>`;
  }).join('');""")

# 3) 팝업·그래프
rep("""function anGauge(msig, key, title){""",
"""function anVkDots(stage){ return '<span class="an-vkst">' + [0, 1, 2].map(k => `<i${k < stage ? ' class="f"' : ''}></i>`).join('') + '</span>'; }
function anVkSvg(vk){   // 6개월: 위 VKOSPI(20일 평균·급등 기준) · 아래 코스피(20일선·20일 최저) · 꺾임 뒤 기다림(옅게)·켜짐(조금 진하게) 구간
  const c = vk.chart || {}, d = c.d || [], v = c.v || [], ma = c.ma || [], k = c.k || [], kma = c.kma || [], klo = c.klo || [], st = c.st || '', n = d.length;
  if(n < 2) return '';
  const W = 330, x = i => +(i * W / (n - 1)).toFixed(1), ok = a => a != null && isFinite(a);
  const band = (vals, y0, y1) => { const xs = vals.filter(ok); let lo = Math.min(...xs), hi = Math.max(...xs); const p = (hi - lo) * 0.08 || 1; lo -= p; hi += p;
    return a => +(y1 - (a - lo) / (hi - lo) * (y1 - y0)).toFixed(1); };
  const vmax = Math.max(...v.filter(ok)), thr = vk.thr, useT = ok(thr) && thr < vmax * 1.6;
  const yv = band(v.concat(ma, useT ? [thr] : []), 14, 84), yk = band(k.concat(kma, klo), 104, 168);
  const line = (vals, y, col, w, dash) => `<polyline fill="none" stroke="${col}" stroke-width="${w}"${dash ? ` stroke-dasharray="${dash}"` : ''} points="${vals.map((a, i) => ok(a) ? `${x(i)},${y(a)}` : '').filter(Boolean).join(' ')}"/>`;
  let sh = '';
  for(let i = 0; i < n; i++){ if(st[i] !== '2' && st[i] !== '3') continue; let j = i; while(j + 1 < n && (st[j + 1] === '2' || st[j + 1] === '3')) j++;
    sh += `<rect x="${x(i)}" y="0" width="${Math.max(x(j) - x(i), 2)}" height="176" fill="#4FD1C0" opacity="${st[j] === '3' ? 0.16 : 0.08}"/>`; i = j; }
  let tl = '';
  if(useT){ const ty = yv(thr); if(ty >= 14 && ty <= 84) tl = `<line x1="0" y1="${ty}" x2="${W}" y2="${ty}" stroke="#C080F0" stroke-width=".8" stroke-dasharray="3 3"/><text x="${W / 2}" y="${ty + (ty < 24 ? 9 : -3)}" font-size="8" fill="#C080F0" text-anchor="middle">급등 기준 ${thr.toFixed(1)}</text>`; }
  let pi = 0; v.forEach((a, i) => { if(ok(a) && a > v[pi]) pi = i; });
  const pr = x(pi) < W - 90, sd = s => s.slice(2).replace(/-/g, '.');
  return `<svg width="100%" viewBox="0 0 ${W} 186" aria-hidden="true">${sh}<line x1="0" y1="94" x2="${W}" y2="94" stroke="var(--border)" stroke-width=".8"/>`
    + `<text x="2" y="9" font-size="8.5" fill="#C080F0">VKOSPI ${anF(vk.last, 1)}</text>${tl}` + line(ma, yv, '#6A6B70', 1, '2 2') + line(v, yv, '#C080F0', 1.6)
    + `<circle cx="${x(pi)}" cy="${yv(v[pi])}" r="2.5" fill="#C080F0"/><text x="${pr ? x(pi) + 5 : x(pi) - 5}" y="${yv(v[pi]) + 3}" font-size="8" fill="#C080F0"${pr ? '' : ' text-anchor="end"'}>최고 ${v[pi].toFixed(1)} (${d[pi].slice(5).replace('-', '.')})</text>`
    + `<circle cx="${x(n - 1)}" cy="${yv(v[n - 1])}" r="2.5" fill="${(vk.d5 || 0) < 0 ? 'var(--an-dn)' : 'var(--an-up)'}"/>`
    + `<text x="2" y="104" font-size="8.5" fill="var(--text)">코스피 ${ok(k[n - 1]) ? Math.round(k[n - 1]).toLocaleString() : '-'}</text>`
    + line(kma, yk, '#F0DA8C', 1, '3 2') + line(klo, yk, '#5FB8E0', 1, '1.5 2.5') + line(k, yk, 'var(--text)', 1.6)
    + `<text x="0" y="184" font-size="8" fill="var(--text-dim)">${sd(d[0])}</text><text x="${W}" y="184" font-size="8" fill="var(--text-dim)" text-anchor="end">${sd(d[n - 1])}</text></svg>`;
}
function anVkPopup(){   // 게이지 6번째 줄을 누르면: 6개월 그래프 + 세 단계 설명(바깥·× 누르면 닫힘)
  const vk = anVkNow; if(!vk) return;
  document.getElementById('anVkModal')?.remove();
  const st = vk.stage, r = vk.rule || {}, sd = s => (s || '').slice(5).replace('-', '.');
  const oc = b => b ? '<span style="color:var(--an-up)">○</span>' : '<span style="color:var(--an-dn)">✕</span>';
  const dot = on => `<span class="an-vkd${on ? ' f' : ''}"></span>`;
  const n0 = x => x == null ? '-' : Math.round(x).toLocaleString();
  const s1 = `급등: 60일 최고 ${anF(vk.peak, 1)}(${sd(vk.peak_d)}) · 기준 ${anF(vk.thr, 1)}(6개월 중간값×${r.spike || 1.5}) ${vk.spike || st >= 2 ? '넘음' : '못 넘음'}`;
  const s2 = `꺾임: 5일 전보다 낮음 ${r.neg || 3}일 연속 + 20일 평균(${anF(vk.ma, 1)}) 아래 ${st >= 2 ? '맞음' : '아직'}`;
  const s3 = st === 3 ? '코스피 회복: 켜짐' : st === 2 ? `코스피 회복 대기 ${vk.wait}/${vk.wait_max}일` : '코스피 회복: 꺾임 뒤에 봄';
  const s3d = `20일선 위 ${oc(vk.ma_ok)} (${n0(vk.k)} / ${n0(vk.kma)}) · 20거래일 신저점 없음 ${oc(vk.nolow)} (20일 최저 ${n0(vk.klo)}, ${sd(vk.klo_d)})`;
  const lg = [['#C080F0', 'solid', 'VKOSPI'], ['#6A6B70', 'dashed', '20일 평균'], ['#C080F0', 'dashed', '급등 기준'], ['var(--text)', 'solid', '코스피'], ['#F0DA8C', 'dashed', '20일선'], ['#5FB8E0', 'dotted', '20일 최저']]
    .map(([c, t, nm]) => `<span><s style="border-top:${t === 'solid' ? 1.6 : 1.2}px ${t} ${c}"></s>${nm}</span>`).join('');
  const m = document.createElement('div'); m.id = 'anVkModal'; m.className = 'an-vkmodal';
  m.innerHTML = `<div class="an-vkcard"><div class="an-vkh"><b>${AN_VK_NAME} ${anVkDots(st)}</b><button type="button" aria-label="닫기">×</button></div>`
    + `<div class="an-vkm">최근 6개월 · VKOSPI ${anShort(String(vk.date).slice(0, 10))} 기준 · 꺾임 뒤 기다림·켜짐 구간 = 연한 칸</div>${anVkSvg(vk)}<div class="an-vklg">${lg}</div>`
    + `<div class="an-vkbox"><div>${dot(st >= 1 || vk.spike)} ${anE(s1)}</div><div>${dot(st >= 2)} ${anE(s2)}</div><div>${dot(st >= 3)} ${anE(s3)}<div class="an-vkm" style="padding-left:14px">${s3d}</div></div></div>`
    + `<div class="an-vkm" style="margin-top:6px">켜지면 ${r.on || 20}거래일 유지 · 꺾임 뒤 ${r.wait || 20}거래일 안에 코스피 회복이 없으면 처음부터 · 자료 KRX(리포트가 하루 한 번 받음)</div></div>`;
  m.addEventListener('click', e => { if(e.target === m || e.target.closest('.an-vkh button')) m.remove(); });
  document.body.appendChild(m);
}
function anGauge(msig, key, title){""")

# 4) CSS
rep(""".an-dot { width:9px; height:9px; border-radius:50%; background:var(--border); flex:none; }""",
""".an-dot { width:9px; height:9px; border-radius:50%; background:var(--border); flex:none; }
.an-vkst { display:inline-flex; gap:3px; margin-left:6px; padding:2px 4px; border:1px solid var(--border); border-radius:6px; vertical-align:middle; }   /* VKOSPI 단계 점(2026-11-23) */
.an-vkst i { width:6px; height:6px; border-radius:50%; border:1px solid #6A6B70; box-sizing:border-box; } .an-vkst i.f { background:var(--an-ok); border-color:var(--an-ok); }
.an-gauge li.an-vkli { cursor:pointer; } .an-gauge li.an-vkli.wt { color:var(--text); } .an-gauge li.an-vkli.wt .an-dot { background:transparent; border:1.5px solid var(--an-ok); box-sizing:border-box; }
.an-vkmodal { --an-ok:#4FD1C0; --an-up:#E87BA4; --an-dn:#5FB8E0; position:fixed; inset:0; z-index:10000; background:rgba(0,0,0,.5); display:flex; align-items:center; justify-content:center; }
.an-vkcard { background:var(--surface); border:1px solid var(--border); border-radius:12px; width:min(400px, 94vw); max-height:92vh; overflow:auto; padding:12px 14px; color:var(--text); font-size:12px; }
.an-vkh { display:flex; align-items:center; margin-bottom:4px; } .an-vkh b { flex:1; font-size:13px; } .an-vkh button { border:0; background:none; color:var(--text-dim); font-size:20px; cursor:pointer; line-height:1; }
.an-vkm { color:var(--text-dim); font-size:11px; }
.an-vklg { display:flex; flex-wrap:wrap; gap:3px 10px; font-size:10.5px; color:var(--text-dim); margin:2px 0 8px; } .an-vklg s { display:inline-block; width:12px; vertical-align:middle; margin-right:3px; text-decoration:none; }
.an-vkbox { background:#1E1F22; border-radius:8px; padding:7px 9px; line-height:1.7; font-size:11.5px; }
.an-vkd { display:inline-block; width:7px; height:7px; border-radius:50%; border:1px solid #6A6B70; vertical-align:middle; } .an-vkd.f { background:var(--an-ok); border-color:var(--an-ok); }""")

open(path, 'w', encoding='utf-8').write(s); print('ok', path)
