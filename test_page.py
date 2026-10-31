"""테스트 페이지(test.html) ↔ 메인(index.html) 변환 (2026-10-31)

  python test_page.py make      index.html → test.html  (메인을 테스트로 새로 복사)
  python test_page.py promote   test.html  → index.html (테스트에서 확인한 내용을 메인에 반영)

test.html 이 메인과 다른 곳은 두 군데뿐:
  1) <!--TEST:BEGIN--> ~ <!--TEST:END--> 블록(저장 분리 · TEST 띠 · 검색 제외) — promote 때 통째로 빠짐
  2) 광고 스크립트를 <!--TEST:OFF ... TEST:OFF--> 주석으로 꺼 둠 — promote 때 다시 켜짐
나머지 코드는 같고, 테스트에서만 달라야 하는 동작은 코드 안에서 window.MP_TEST 로 나눔
(예: IndexedDB 이름, GitHub 종목 동기화 끄기). 메인에는 MP_TEST 가 없으므로 그대로 동작.
"""
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
MAIN, TEST = ROOT / "index.html", ROOT / "test.html"

SHIM = r"""<!--TEST:BEGIN-->
<meta name="robots" content="noindex, nofollow">
<script>
// ===== 테스트 페이지 전용: 메인(index.html)과 저장 공간 분리 =====
// localStorage 키 앞에 'test:'를 붙여 따로 씀. 처음 열 때 메인 데이터를 한 번 복사(GitHub 토큰은 복사 안 함 = 종목 동기화 꺼짐).
// IndexedDB는 'moneypie-analysis-test'에 쓰고, 테스트 쪽에 없는 값은 메인 DB에서 읽기만 함(anDB 참고).
(function(){
  window.MP_TEST = true;
  var P = 'test:', ls = window.localStorage, pr = Storage.prototype;
  var g = pr.getItem, s = pr.setItem, r = pr.removeItem;
  try{
    if(g.call(ls, P + '__copied') !== '1'){
      var keys = [];
      for(var i = 0; i < ls.length; i++) keys.push(ls.key(i));
      keys.forEach(function(k){ if(k && k.indexOf(P) !== 0 && k !== 'mp-gh-token') s.call(ls, P + k, g.call(ls, k)); });
      s.call(ls, P + '__copied', '1');
      s.call(ls, P + '__copiedAt', new Date().toISOString());
    }
  }catch(e){}
  pr.getItem = function(k){ return g.call(this, this === ls ? P + k : k); };
  pr.setItem = function(k, v){ return s.call(this, this === ls ? P + k : k, v); };
  pr.removeItem = function(k){ return r.call(this, this === ls ? P + k : k); };
  // 메인 데이터 다시 복사: test: 키 전부 지우고 테스트 DB 삭제 → 새로고침
  window.mpTestReset = function(){
    if(!confirm('테스트 데이터를 지우고 메인 데이터를 다시 복사할까요? (메인은 그대로)')) return;
    var del = [];
    for(var i = 0; i < ls.length; i++){ var k = ls.key(i); if(k && k.indexOf(P) === 0) del.push(k); }
    del.forEach(function(k){ r.call(ls, k); });
    try{ var q = indexedDB.deleteDatabase('moneypie-analysis-test'); q.onsuccess = q.onerror = q.onblocked = function(){ location.reload(); }; }
    catch(e){ location.reload(); }
  };
  document.addEventListener('DOMContentLoaded', function(){
    var b = document.createElement('div');
    b.id = 'mpTestBand';
    b.innerHTML = 'TEST · 메인과 저장 분리 · 동기화·광고 꺼짐 <button type="button" onclick="mpTestReset()">메인 데이터 다시 복사</button>';
    document.body.insertBefore(b, document.body.firstChild);
  });
})();
</script>
<style>
#mpTestBand{ position:relative; z-index:5000; background:#D4FF3D; color:#111; font:600 12px/1.2 sans-serif;
  padding:6px 10px; display:flex; align-items:center; gap:8px; justify-content:center; }
#mpTestBand button{ font:inherit; font-weight:500; background:#111; color:#D4FF3D; border:0; border-radius:4px; padding:3px 8px; }
</style>
<!--TEST:END-->
"""

ADS = [
    re.compile(r'<script async src="https://pagead2\.googlesyndication\.com[^>]*>\s*</script>', re.S),
    re.compile(r'<div id="adfit-bottom">.*?</div>', re.S),
]


def make():
    h = MAIN.read_text(encoding="utf-8")
    assert "TEST:BEGIN" not in h, "index.html 에 테스트 블록이 있음"
    h = h.replace('<meta charset="UTF-8">', '<meta charset="UTF-8">\n' + SHIM.rstrip("\n"), 1)
    for rx in ADS:
        h, n = rx.subn(lambda m: "<!--TEST:OFF" + m.group(0) + "TEST:OFF-->", h, count=1)
        assert n == 1, rx.pattern
    h = h.replace("<title>머니파이 MONEY PIE</title>", "<title>[TEST] 머니파이 MONEY PIE</title>", 1)
    TEST.write_text(h, encoding="utf-8")
    print("test.html 만듦")


def promote():
    h = TEST.read_text(encoding="utf-8")
    h, n = re.subn(r"\n<!--TEST:BEGIN-->.*?<!--TEST:END-->", "", h, flags=re.S)
    assert n == 1
    h, n = re.subn(r"<!--TEST:OFF(.*?)TEST:OFF-->", lambda m: m.group(1), h, flags=re.S)
    assert n == len(ADS)
    h = h.replace("<title>[TEST] 머니파이 MONEY PIE</title>", "<title>머니파이 MONEY PIE</title>", 1)
    assert "MP_TEST = true" not in h
    MAIN.write_text(h, encoding="utf-8")
    print("index.html 갱신")


if __name__ == "__main__":
    {"make": make, "promote": promote}[sys.argv[1]]()
