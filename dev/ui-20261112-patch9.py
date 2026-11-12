import sys
fn=sys.argv[1]; s=open(fn,encoding='utf-8').read()
a="#marketTicker.mkt-pin{position:fixed;top:0;z-index:900;background:var(--bg);margin:0 !important;box-shadow:-12px 0 0 var(--bg), 12px 0 0 var(--bg), 0 1px 0 var(--border);box-sizing:border-box;}"
assert s.count(a)==1
s=s.replace(a,"#marketTicker.mkt-pin{position:fixed;top:0;z-index:900;background:transparent;margin:0 !important;box-sizing:border-box;pointer-events:none;} #marketTicker.mkt-pin .mkt-card{pointer-events:auto;}   /* A안(2026-11-12 사용자): 띠 배경 없음 — 둥근 카드만 떠 있고 틈으로 본문이 지나감. 틈을 누르면 아래 본문이 눌림 */")
open(fn,'w',encoding='utf-8').write(s); print('ok')
