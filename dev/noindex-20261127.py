# 2026-11-27 사용자: 모든 주소 검색 제외 — 모든 .html의 첫 <head> 바로 뒤에 robots noindex (이미 있으면 건너뜀)
import re, pathlib, sys
TAG = '<meta name="robots" content="noindex, nofollow">'
root = pathlib.Path(sys.argv[1])
done = skip = 0
for p in sorted(root.rglob('*.html')):
    if '.git' in p.parts: continue
    s = p.read_text(encoding='utf-8')
    if re.search(r'<meta[^>]+name=["\']robots["\']', s, re.I): skip += 1; continue
    m = re.search(r'<head\b[^>]*>', s, re.I)
    if not m: print('NO HEAD', p); continue
    p.write_text(s[:m.end()] + '\n' + TAG + s[m.end():], encoding='utf-8'); done += 1
print('added', done, 'skipped', skip)
