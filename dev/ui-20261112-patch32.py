import sys
fn=sys.argv[1]; s=open(fn,encoding='utf-8').read()
def rep(a,b,cnt=1):
    global s
    n=s.count(a); assert n==cnt,(fn,a[:70],n); s=s.replace(a,b)
rep("""    if(!donutCarOn()) return;   // 새로고침 버튼은 휴대폰 보기에서만(2026-11-11 사용자)""","""    if(!mpOneCol()) return;   // 새로고침 버튼은 한 줄 보기(휴대폰, 또는 PC 좁은 창)에서만(2026-11-12 사용자: PC 한 줄 보기에도)""")
rep("""  const ch0 = panel.querySelector('.charts'); if(ch0) ch0.classList.toggle('mp-phone', donutCarOn());""","""  const ch0 = panel.querySelector('.charts'); if(ch0) ch0.classList.toggle('mp-phone', mpOneCol());""")
rep("""function mpSideOn(){""","""function mpOneCol(){ try{ return donutCarOn() || window.innerWidth <= 640; }catch(e){ return false; } }   // 도넛 위·목록 아래 한 줄 보기
function mpSideOn(){""")
open(fn,'w',encoding='utf-8').write(s); print('ok',fn)
