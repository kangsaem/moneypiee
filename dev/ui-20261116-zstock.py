import sys
p = sys.argv[1]; s = open(p, encoding='utf-8').read()
def rep(a, b, cnt=1):
    global s
    assert s.count(a) == cnt, (a[:70], s.count(a)); s = s.replace(a, b)
rep('fill="rgba(95,184,224,${AN_ZONE_A[a]})" data-zt="${anE(anZoneTip(\'r\'', 'fill="rgba(232,123,164,${AN_ZONE_A[a]})" data-zt="${anE(anZoneTip(\'r\'')
rep('fill="rgba(232,123,164,${AN_ZONE_A[b]})" data-zt="${anE(anZoneTip(\'b\'', 'fill="rgba(95,184,224,${AN_ZONE_A[b]})" data-zt="${anE(anZoneTip(\'b\'')
rep("  ch = Object.assign({}, ch, { showChg: true });       // 현재가(종가) 점 아래 등락률(종목 차트만)",
    "  ch = Object.assign({}, ch, { showChg: true, zone: true });       // 현재가(종가) 점 아래 등락률(종목 차트만) · 위험·바닥·VIX 구간(2026-11-16)")
rep("const ZON = !!(anZones && (ch.zone || 'ma200' in ch)), VH = ZON ? 8 : 0, vgap = ZON ? 4 : 0;   // 지수 차트: 위험·바닥 구간 + VIX 띠",
    "const ZON = !!(anZones && (ch.zone || 'ma200' in ch)), VH = ZON ? 8 : 0, vgap = ZON ? 4 : 0;   // 지수·종목 차트: 위험(분홍)·바닥(하늘) 구간 + VIX 띠")
open(p, 'w', encoding='utf-8').write(s)
