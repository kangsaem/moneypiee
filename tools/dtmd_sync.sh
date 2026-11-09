#!/usr/bin/env bash
# DTMD 복제본(GitHub kangsaem/DTMD → https://scuba.kangyonz.com) 맞추기.
# 사용: bash tools/dtmd_sync.sh /경로/DTMD   (moneypiee 저장소 루트에서 실행)
# 원본 = moneypiee(www.moneypie.kr/scuba). 새 버전을 낼 때마다 실행해서 DTMD 저장소에도 커밋·푸시할 것.
# 복제본 규칙: 대표 주소(canonical)는 moneypie.kr 유지, 앱은 / 에서 바로(/scuba → /), CNAME = scuba.kangyonz.com
set -euo pipefail
DST="${1:?DTMD 저장소 경로를 주세요}"
SRC="$(cd "$(dirname "$0")/.." && pwd)"
cd "$SRC"
FILES=(scuba.html dtmd.html plan.html dive.html sample-jack.jpg scuba-splash.mp4 og-scuba3.jpg)
FILES+=(dtmd-*.html dtmd*.webmanifest dtmd-*.png)
DIRS=(tut dtmd-launch)
for f in "${FILES[@]}"; do cp -p "$f" "$DST/"; done
for d in "${DIRS[@]}"; do rm -rf "$DST/$d"; cp -rp "$d" "$DST/"; done
# 대표 주소 표시: 복제본 scuba.html에만 canonical(검색엔진 중복 방지)
python3 - "$DST/scuba.html" <<'PY'
import sys
p=sys.argv[1];s=open(p,encoding='utf-8').read()
tag='<link rel="canonical" href="https://www.moneypie.kr/scuba">'
if tag not in s:
    s=s.replace('<meta charset="utf-8">','<meta charset="utf-8">\n'+tag,1)
open(p,'w',encoding='utf-8').write(s)
PY
echo 'scuba.kangyonz.com' > "$DST/CNAME"
# 앱은 주소 / 에서 바로(11/09 사용자 결정): index.html = 앱, scuba.html(/scuba) = / 로 이동(예전 주소 호환)
# 설치 정보(webmanifest) 시작 주소·범위 = /, 공유 페이지·dtmd·plan·dive의 'scuba.html' 이동 = /
python3 - "$DST" <<'PY'
import sys,re,glob,os
d=sys.argv[1]
app=open(os.path.join(d,'scuba.html'),encoding='utf-8').read()
# 카카오 애드핏: 광고 단위는 도메인별 → 복제본(scuba.kangyonz.com)은 사용자가 받은 단위로(11/09)
assert app.count('data-ad-unit="DAN-blDFwvjdoelHWCGb"')==1, '원본 광고 단위가 바뀜 — dtmd_sync.sh 확인'
app=app.replace('data-ad-unit="DAN-blDFwvjdoelHWCGb"','data-ad-unit="DAN-F3MZMbNZPoka4ze1"')
open(os.path.join(d,'index.html'),'w',encoding='utf-8').write(app)
open(os.path.join(d,'scuba.html'),'w',encoding='utf-8').write('<!DOCTYPE html>\n<html lang="ko"><head><meta charset="utf-8"><title>DTMD</title>\n<link rel="canonical" href="https://www.moneypie.kr/scuba">\n<script>location.replace(\'/\'+location.hash);</script></head>\n<body style="font-family:sans-serif;padding:20px"><a href="/">DTMD</a></body></html>\n')
for f in glob.glob(os.path.join(d,'dtmd*.webmanifest')):
    t=open(f,encoding='utf-8').read()
    t=re.sub(r'"(id|start_url|scope)"\s*:\s*"/scuba"',lambda m:'"'+m.group(1)+'": "/"',t)
    open(f,'w',encoding='utf-8').write(t)
for f in glob.glob(os.path.join(d,'dtmd*.html'))+[os.path.join(d,x) for x in ('plan.html','dive.html')]:
    t=open(f,encoding='utf-8').read()
    t=re.sub(r'(?<![\w/.])scuba\.html',"/",t)
    open(f,'w',encoding='utf-8').write(t)
PY
cat > "$DST/README.md" <<'MD'
# DTMD (복제본)
https://scuba.kangyonz.com — 원본은 kangsaem/moneypiee 저장소(www.moneypie.kr/scuba).
이 저장소의 파일은 원본에서 `tools/dtmd_sync.sh`로 복사됨. 여기서 직접 고치지 말 것.
MD
echo "synced to $DST"
