// moneypie-proxy (허용 목록판, 2026-10-22)
// 바뀐 점: ① 허용한 사이트·경로만 중계 ② 머니파이 도메인에서 온 요청만 처리 ③ GET만 ④ 리다이렉트도 허용 목록 안에서만
// 허용된 요청의 응답은 기존과 같음(User-Agent·헤더·CORS·캐시 30초).

// 대상: 코드 전수 조사(2026-10-22, index.html·crash200.js·lab-bt.html)에서 나온 4곳
const ALLOW = {
  'query1.finance.yahoo.com': ['/v8/finance/chart/'],            // 야후 일봉·현재가
  'polling.finance.naver.com': ['/api/realtime/domestic/'],      // 네이버 실시간 지수·종목
  'api.finance.naver.com': ['/siseJson.naver'],                   // 네이버 일봉
  'm.stock.naver.com': ['/front-api/search/autoComplete'],        // 네이버 종목 검색
};
// 요청 출처(브라우저가 보내는 Origin)
const ORIGINS = ['https://www.moneypie.kr', 'https://moneypie.kr'];

const CORS = {
  'Access-Control-Allow-Origin': '*',
  'Access-Control-Allow-Methods': 'GET, OPTIONS',
};

function deny(status, msg) {
  return new Response(msg + '\n', { status, headers: { ...CORS, 'Content-Type': 'text/plain; charset=utf-8' } });
}

// 허용 목록 검사: https, 기본 포트, 계정 정보 없음, 호스트 정확히 일치, 경로 앞부분 일치
function allowed(raw) {
  let u;
  try { u = new URL(raw); } catch (e) { return null; }
  if (u.protocol !== 'https:' || u.port !== '' || u.username || u.password) return null;
  const paths = ALLOW[u.hostname];
  if (!paths || !paths.some((p) => u.pathname.startsWith(p))) return null;
  return u;
}

export default {
  async fetch(request) {
    const origin = request.headers.get('Origin');
    if (!origin || !ORIGINS.includes(origin)) return deny(403, 'forbidden origin');

    if (request.method === 'OPTIONS') {
      return new Response(null, {
        status: 204,
        headers: { ...CORS, 'Access-Control-Allow-Headers': '*', 'Access-Control-Max-Age': '86400' },
      });
    }
    if (request.method !== 'GET') return deny(405, 'method not allowed');

    const target = new URL(request.url).searchParams.get('url');
    if (!target) return deny(400, 'Missing url parameter');
    let u = allowed(target);
    if (!u) return deny(403, 'target not allowed');

    try {
      let res;
      for (let hop = 0; ; hop++) {   // 리다이렉트는 직접 따라가며 매번 허용 목록 확인(최대 3번)
        res = await fetch(u.toString(), {
          redirect: 'manual',
          headers: {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'application/json, text/plain, */*',
            'Accept-Language': 'ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7',
          },
        });
        if (res.status < 300 || res.status >= 400 || !res.headers.get('Location')) break;
        if (hop >= 3) return deny(502, 'too many redirects');
        u = allowed(new URL(res.headers.get('Location'), u).toString());
        if (!u) return deny(403, 'redirect target not allowed');
      }

      const newHeaders = new Headers(res.headers);
      newHeaders.set('Access-Control-Allow-Origin', '*');
      newHeaders.set('Access-Control-Allow-Methods', 'GET, OPTIONS');
      newHeaders.set('Cache-Control', 'public, max-age=30');
      newHeaders.delete('content-encoding');
      newHeaders.delete('content-length');
      newHeaders.delete('set-cookie');

      return new Response(res.body, { status: res.status, statusText: res.statusText, headers: newHeaders });
    } catch (err) {
      return new Response(JSON.stringify({ error: err.message }), {
        status: 500,
        headers: { 'Content-Type': 'application/json', ...CORS },
      });
    }
  },
};
