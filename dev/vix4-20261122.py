import sys
p = sys.argv[1]; s = open(p, encoding='utf-8').read()
def rep(a, b, cnt=1):
    global s
    assert s.count(a) == cnt, (p, a[:60], s.count(a)); s = s.replace(a, b)
LV = "v >= 40 ? 4 : v >= 35 ? 3 : v >= 30 ? 2 : v >= 25 ? 1 : 0"
if p.endswith('.html'):
    rep("const vl = j => { const v = vi[j] >= 0 ? z.vc[vi[j]] : null; return v == null ? 0 : v >= 30 ? 2 : v >= 25 ? 1 : 0; };",
        "const vl = j => { const v = vi[j] >= 0 ? z.vc[vi[j]] : null; return v == null ? 0 : " + LV + "; };")
    rep("""fill="${a === 2 ? 'rgba(242,166,90,0.85)' : 'rgba(242,166,90,0.40)'}" data-zt="${anE(`VIX ${a === 2 ? '30' : '25'} 이상 · ${dates[j]}""",
        """fill="${AN_VIX_FILL[a]}" data-zt="${anE(`VIX ${AN_VIX_TH[a]} 이상 · ${dates[j]}""")
    rep("  // VIX 띠(25↑ 옅게, 30↑ 진하게)\n",
        "  // VIX 띠(25↑ 옅은 주황, 30↑ 진한 주황, 35↑ 붉은 주황, 40↑ 진한 빨강 — 2026-11-22 사용자: 35·40 더 강조)\n")
    rep("const AN_ZONE_A = {", "const AN_VIX_FILL = [null, 'rgba(242,166,90,0.40)', 'rgba(242,166,90,0.85)', '#E8704A', '#D93A3A'], AN_VIX_TH = [0, 25, 30, 35, 40];\nconst AN_ZONE_A = {")
else:
    rep("lv = j => { const v = val(j); return v == null ? 0 : v >= 30 ? 2 : v >= 25 ? 1 : 0; };",
        "lv = j => { const v = val(j); return v == null ? 0 : " + LV + "; };   // 35·40 단계(2026-11-22)")
    rep("""fill="${a === 2 ? 'rgba(242,166,90,0.85)' : 'rgba(242,166,90,0.40)'}" data-zt="${esc(`VIX ${a === 2 ? '30' : '25'} 이상 ·""",
        """fill="${['', 'rgba(242,166,90,0.40)', 'rgba(242,166,90,0.85)', '#E8704A', '#D93A3A'][a]}" data-zt="${esc(`VIX ${[0, 25, 30, 35, 40][a]} 이상 ·""")
    rep("""아래 띠 = VIX <b class="gn-v1">25 이상</b>·<b class="gn-v2">30 이상</b>(V1과 같음""",
        """아래 띠 = VIX <b class="gn-v1">25 이상</b>·<b class="gn-v2">30 이상</b>·<b class="gn-v3">35 이상</b>·<b class="gn-v4">40 이상</b>(V1과 같음""")
open(p, 'w', encoding='utf-8').write(s)
