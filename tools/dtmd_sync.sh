#!/usr/bin/env bash
# DTMD 복제본(GitHub kangsaem/DTMD → https://scuba.kangyonz.com) 맞추기.
# 사용: bash tools/dtmd_sync.sh /경로/DTMD   (moneypiee 저장소 루트에서 실행)
# 원본 = moneypiee(www.moneypie.kr/scuba). 새 버전을 낼 때마다 실행해서 DTMD 저장소에도 커밋·푸시할 것.
# 복제본 규칙: 대표 주소(canonical)는 moneypie.kr 유지, / 로 들어오면 /scuba 로 이동, CNAME = scuba.kangyonz.com
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
cat > "$DST/index.html" <<'HTML'
<!DOCTYPE html>
<html lang="ko"><head><meta charset="utf-8"><title>DTMD</title>
<link rel="canonical" href="https://www.moneypie.kr/scuba">
<script>location.replace('/scuba'+location.hash);</script></head>
<body style="font-family:sans-serif;padding:20px"><a href="/scuba">DTMD</a></body></html>
HTML
cat > "$DST/README.md" <<'MD'
# DTMD (복제본)
https://scuba.kangyonz.com — 원본은 kangsaem/moneypiee 저장소(www.moneypie.kr/scuba).
이 저장소의 파일은 원본에서 `tools/dtmd_sync.sh`로 복사됨. 여기서 직접 고치지 말 것.
MD
echo "synced to $DST"
