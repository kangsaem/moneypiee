import sys
p = sys.argv[1]; s = open(p, encoding='utf-8').read()
def rep(a, b, cnt=1):
    global s
    assert s.count(a) == cnt, (a[:70], s.count(a)); s = s.replace(a, b)
rep("${anChartTabs(anState.idxPer[v.key] || '6m', v.chart)}", "${anChartTabs(anState.chartPer || '6m', v.chart)}")
rep("""  const per = anState.idxPer[v.key] || '6m';
  let ch = v.chart;""", """  const per = anState.chartPer || '6m';                 // 기간은 지수·종목 차트 모두 같이(2026-11-17 사용자)
  let ch = v.chart;""")
rep("""    if(isl){ anState.idxPer[isl.dataset.anIchart] = b.dataset.cper; anDrawIdxChart(isl); return; }   // 지수 차트: 그 지수만
    anState.chartPer = b.dataset.cper;
    root.querySelectorAll('[data-an-chart][data-drawn]').forEach(sl => anDrawChartSlot(sl));""",
"""    anState.chartPer = b.dataset.cper;                                   // 지수·종목 차트 모두 같은 기간으로(2026-11-17 사용자, 전엔 지수는 따로)
    root.querySelectorAll('[data-an-chart][data-drawn]').forEach(sl => anDrawChartSlot(sl));
    root.querySelectorAll('[data-an-ichart]').forEach(sl => anDrawIdxChart(sl));""")
rep("""  root.querySelectorAll('[data-an-ichart]').forEach(sl => { if((anState.idxPer[sl.dataset.anIchart] || '6m') !== '6m') anDrawIdxChart(sl); });""",
    """  root.querySelectorAll('[data-an-ichart]').forEach(sl => { if((anState.chartPer || '6m') !== '6m') anDrawIdxChart(sl); });""")
open(p, 'w', encoding='utf-8').write(s)
