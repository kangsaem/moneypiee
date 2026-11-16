import sys
p = sys.argv[1]; s = open(p, encoding='utf-8').read()
def rep(a, b, cnt=1):
    global s
    assert s.count(a) == cnt, (a[:70], s.count(a)); s = s.replace(a, b)
# 1) 마감 뒤 확정
rep("""  const last = b.d[b.d.length - 1], rm = mask(msig.risk.items), bm = mask(msig.bottom.items);
  anMlog[last] = [cnt(rm), cnt(bm), rm, bm, 'L', pf((msig.bottom.items[4] || [])[1]), pf((msig.risk.items[4] || [])[1])];
  if(zs && zs.length){""", """  const last = b.d[b.d.length - 1], rm = mask(msig.risk.items), bm = mask(msig.bottom.items);
  const kt = anKstNow(), fin = d => kt.date > d || (kt.date === d && kt.hm >= 2000);   /* 국장 일봉 확정(20:00 KST) 뒤 첫 값으로 확정, 그 뒤로는 덮어쓰지 않음 */
  if(!(anMlog[last] && anMlog[last][7])) anMlog[last] = [cnt(rm), cnt(bm), rm, bm, 'L', pf((msig.bottom.items[4] || [])[1]), pf((msig.risk.items[4] || [])[1]), fin(last) ? 1 : 0];
  if(zs && zs.length){""")
rep("""      if(d < cut || d === last || anMlog[d]) return;""",
    """      const old = anMlog[d];
      if(d === last || (old && (old[7] || old[4] !== 'L')) || (!old && d < cut)) return;   /* 확정됐거나 이미 만든 날은 그대로 · 마감 전 값만 남은 날은 마감 기준으로 다시 셈 */""")
rep("""      const wk = nw / n, br = nb / n, R = (b.rm[i] & 15) | (br >= 0.7 ? 16 : 0), B = (b.bm[i] & 15) | (wk >= 0.3 ? 16 : 0);
      anMlog[d] = [cnt(R), cnt(B), R, B, 'G', Math.round(wk * 100), Math.round(br * 100)];""",
    """      const wk = nw / n, br = nb / n, R = (b.rm[i] & 15) | (br >= 0.7 ? 16 : 0) | (old ? old[2] & 32 : 0), B = (b.bm[i] & 15) | (wk >= 0.3 ? 16 : 0);
      anMlog[d] = [cnt(R), cnt(B), R, B, old ? 'C' : 'G', Math.round(wk * 100), Math.round(br * 100), 1];""")
rep("""  const z = Object.assign({}, b, { r: [], b: [], rm: [], bm: [], src: [], wk: [], br: [] });
  b.d.forEach(d => { const e = anMlog[d]; z.r.push(e ? e[0] : 0); z.b.push(e ? e[1] : 0); z.rm.push(e ? e[2] : 0); z.bm.push(e ? e[3] : 0); z.src.push(e ? e[4] : ''); z.wk.push(e ? e[5] : null); z.br.push(e ? e[6] : null); });""",
    """  const z = Object.assign({}, b, { r: [], b: [], rm: [], bm: [], src: [], wk: [], br: [], fin: [] });
  b.d.forEach(d => { const e = anMlog[d]; z.r.push(e ? e[0] : 0); z.b.push(e ? e[1] : 0); z.rm.push(e ? e[2] : 0); z.bm.push(e ? e[3] : 0); z.src.push(e ? e[4] : ''); z.wk.push(e ? e[5] : null); z.br.push(e ? e[6] : null); z.fin.push(e ? e[7] || 0 : 0); });""")
rep("""  const src = z.src && z.src[pk] === 'L' ? '그날 판정 기록' : '지금 기준으로 다시 계산' + (kind === 'r' ? '(신용잔고 제외)' : '');""",
    """  const sc = z.src ? z.src[pk] : '', src = sc === 'L' ? (z.fin && z.fin[pk] ? '그날 마감 뒤 판정 기록' : '그날 판정 기록 · 마감 전 값(다음 분석 때 마감 기준으로 확정)')
    : (sc === 'C' ? '마감 뒤 값이 없어 그날 종가로 다시 계산' : '기록이 없어 지금 기준으로 다시 계산') + (kind === 'r' ? '(신용잔고 제외)' : '');""")
# 2) 내보내기·불러오기
rep("""  const payload = { version: DATA_VERSION, accounts: state.accounts, snapshots: state.snapshots, creditLines: state.creditLines, watchlist: state.watchlist ? state.watchlist.holdings : [], hist, exportedAt: new Date().toISOString() };""",
    """  let mlog = {};
  try{ mlog = (await anDB.get('mlog1')) || {}; }catch(e){}                      // 지수 차트 위험·바닥 판정 기록(2026-11-16)
  const payload = { version: DATA_VERSION, accounts: state.accounts, snapshots: state.snapshots, creditLines: state.creditLines, watchlist: state.watchlist ? state.watchlist.holdings : [], hist, mlog, exportedAt: new Date().toISOString() };""")
rep("""      XLSX.utils.book_append_sheet(wb, XLSX.utils.aoa_to_sheet(rows), '분석기록');
    }
  }catch(e){}
""", """      XLSX.utils.book_append_sheet(wb, XLSX.utils.aoa_to_sheet(rows), '분석기록');
    }
  }catch(e){}
  // 시장판정: 지수 차트 위험·바닥 구간 기록(날짜 하나 = 한 줄, 2026-11-16)
  try{
    const ml = (await anDB.get('mlog1')) || {}, ks = Object.keys(ml).sort();
    if(ks.length){
      const nm = (m, names) => names.filter((_, k) => m & (1 << k)).join(', ');
      const rows = [AN_MLOG_XLSX_HEAD];
      ks.forEach(d => { const e = ml[d]; rows.push([d, e[0], e[1], nm(e[2], AN_ZR), nm(e[3], AN_ZB), e[5] == null ? '' : e[5], e[6] == null ? '' : e[6], e[4], e[7] ? 1 : 0, e[2], e[3]]); });
      XLSX.utils.book_append_sheet(wb, XLSX.utils.aoa_to_sheet(rows), '시장판정');
    }
  }catch(e){}
""")
rep("""      if(newAccounts.length === 0 && newSnapshots.length === 0){
        throw new Error('빈 파일');""", """      const mlogRecs = {};
      sheetRows('시장판정').forEach(r => {
        const d = String(r[0] || ''); if(!/^\\d{4}-\\d{2}-\\d{2}$/.test(d)) return;
        const num = v => v === '' || v == null ? null : Number(v);
        mlogRecs[d] = [Number(r[1]) || 0, Number(r[2]) || 0, Number(r[9]) || 0, Number(r[10]) || 0, String(r[7] || 'L'), num(r[5]), num(r[6]), Number(r[8]) ? 1 : 0];
      });

      if(newAccounts.length === 0 && newSnapshots.length === 0){
        throw new Error('빈 파일');""")
rep("""        if(Object.keys(histRecs).length){
          try{ const all = (await anDB.get('hist')) || {}; Object.assign(all, histRecs); await anDB.set('hist', all); }catch(e){}
        }""", """        if(Object.keys(histRecs).length){
          try{ const all = (await anDB.get('hist')) || {}; Object.assign(all, histRecs); await anDB.set('hist', all); }catch(e){}
        }
        try{ await anMlogMerge(mlogRecs); }catch(e){}""")
rep("""            await anDB.set('hist', all); }catch(e){}
        }
        render();
        showNoticeModal('데이터를 불러왔습니다.');""", """            await anDB.set('hist', all); }catch(e){}
        }
        try{ await anMlogMerge(payload.mlog); }catch(e){}
        render();
        showNoticeModal('데이터를 불러왔습니다.');""")
rep("""function anZoneApply(){""", """const AN_MLOG_XLSX_HEAD = ['날짜', '위험 개수', '바닥 개수', '위험 항목', '바닥 항목', '내 종목 RSI35↓%', '내 종목 역배열%', '출처(L 그날·C 마감 재계산·G 생성)', '확정', '위험 비트', '바닥 비트'];
async function anMlogMerge(src){   // 불러오기: 같은 날은 파일 쪽, 단 기기 쪽이 확정이고 파일 쪽이 미확정이면 기기 쪽 유지
  if(!src || typeof src !== 'object') return; await anMlogP;
  let ch = 0;
  Object.keys(src).forEach(d => { const e = src[d]; if(!Array.isArray(e) || e.length < 5 || !/^\\d{4}-\\d{2}-\\d{2}$/.test(d)) return;
    const o = anMlog[d]; if(o && o[7] && !e[7]) return; anMlog[d] = e; ch++; });
  if(ch){ await anDB.set('mlog1', anMlog); anZoneApply(); }
}
function anZoneApply(){""")
open(p, 'w', encoding='utf-8').write(s)
