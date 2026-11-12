import sys
fn=sys.argv[1]; s=open(fn,encoding='utf-8').read()
a="""  const rawData = computeStockDataWithMeta(holdings, fallbackAccId);
  const U = (DONUT_ONE && compactTotalMode) ? stockUnifiedPlan(rawData, holdings, stockLegendSortMode) : null;"""
assert s.count(a)==1
s=s.replace(a,"""  let rawData = computeStockDataWithMeta(holdings, fallbackAccId);
  // 2026-11-12 사용자: 외화 현금은 국내가 아니라 해외로 — 원화·외화가 둘 다 있으면 '원화'(국내, 진한 회색)·'외화'(해외, 옅은 회색) 두 줄로 나눔
  if(DONUT_ONE && compactTotalMode){
    const cashH = holdings.filter(isCashHolding), dom = cashH.filter(h => (h.region || 'domestic') !== 'overseas'), ovs = cashH.filter(h => h.region === 'overseas');
    const ci = rawData.findIndex(d => d.label === '현금');
    if(ci >= 0 && ovs.length && _.sumBy(ovs, 'amount') > 0){
      const c = rawData[ci], tot = _.sumBy(holdings, 'amount') || 1, mk = (lb, hs, rg) => ({ ...c, label: lb, amount: _.sumBy(hs, 'amount'), region: rg, holdId: hs[0].id, accId: hs[0]._accId || c.accId, pct: _.sumBy(hs, 'amount') / tot * 100 });
      const parts = (dom.length && _.sumBy(dom, 'amount') > 0) ? [mk('원화', dom, 'domestic'), mk('외화', ovs, 'overseas')] : [{ ...c, region: 'overseas' }];
      rawData = rawData.slice(0, ci).concat(parts, rawData.slice(ci + 1));
    }
  }
  const U = (DONUT_ONE && compactTotalMode) ? stockUnifiedPlan(rawData, holdings, stockLegendSortMode) : null;""")
open(fn,'w',encoding='utf-8').write(s); print('ok',fn)
