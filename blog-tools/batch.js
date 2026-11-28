// 채수학 블로그 자동화: 여러 글을 한 번에 임시저장 / 발행
// 프로그램(node server.js)이 켜져 있는 상태에서, 다른 까만 창을 하나 더 열어 실행한다.
//   node batch.js 임시저장      → 검토 대기·승인된 글을 모두 네이버 '임시저장'
//   node batch.js 발행          → 승인된 글(이 글 승인하기 누른 글)만 차례로 발행
//   node batch.js 발행 3        → 글 사이 간격을 3분으로 (기본 5분)
const URL = process.env.BATCH_URL || 'http://localhost:3777';
const mode = (process.argv[2] || '').trim();
const gapMin = Math.max(1, Number(process.argv[3]) || 5);
const sleep = (ms) => new Promise((r) => setTimeout(r, ms));
const api = async (p, opt = {}) => {
  const res = await fetch(URL + p, { headers: { 'Content-Type': 'application/json' }, ...opt });
  const data = await res.json().catch(() => ({}));
  if (!res.ok) throw new Error(data.error || `${res.status}`);
  return data;
};

async function waitIdle() {
  for (;;) {
    const st = await api('/api/status');
    if (!st.job) return;
    process.stdout.write(`  (다른 작업 "${st.job.label}" 끝나기를 기다리는 중...)\r`);
    await sleep(5000);
  }
}

async function runJob(post, apiMode) {
  await waitIdle();
  const { jobId } = await api(`/api/posts/${post.id}/publish`, { method: 'POST', body: JSON.stringify({ mode: apiMode }) });
  let shown = 0;
  for (;;) {
    await sleep(3000);
    const j = await api(`/api/jobs/${jobId}`);
    const logs = j.logs || [];
    for (const l of logs.slice(shown)) {
      const text = typeof l === 'string' ? l : l.text || l.message || JSON.stringify(l);
      if (/태그|완료|오류|실패|⚠️/.test(text)) console.log('    ' + text);
    }
    shown = logs.length;
    if (j.status && j.status !== 'running' && j.status !== 'queued') {
      const ok = !j.error && !/error|fail|cancel|interrupt/i.test(j.status);
      return { ok, error: j.error || (ok ? '' : j.status) };
    }
  }
}

(async () => {
  if (!['임시저장', '발행'].includes(mode)) {
    console.log('\n사용법:\n  node batch.js 임시저장\n  node batch.js 발행\n  node batch.js 발행 3   (글 사이 3분 쉬기)\n');
    process.exit(1);
  }
  try {
    await api('/api/status');
  } catch {
    console.log('\n[실패] 프로그램이 꺼져 있어요. 먼저 다른 창에서  node server.js  를 켜 주세요.\n');
    process.exit(1);
  }

  const posts = await api('/api/posts');
  const isDraft = mode === '임시저장';
  const targets = posts.filter((p) => (isDraft ? ['draft', 'approved', 'failed'] : ['approved', 'failed']).includes(p.status)); // 발행 실패한 글도 다시 시도
  if (!targets.length) {
    console.log(isDraft ? '\n임시저장할 글이 없어요. (검토 대기·승인된 글이 없음)\n' : '\n발행할 글이 없어요. 대시보드에서 [이 글 승인하기]를 먼저 눌러 주세요.\n');
    return;
  }

  console.log(`\n${targets.length}편을 차례로 ${mode}합니다. 글 사이 ${gapMin}분씩 쉬어요. (멈추려면 Ctrl+C)\n`);
  targets.forEach((p, i) => console.log(`  ${i + 1}. ${p.title}`));
  console.log('');

  let okCount = 0;
  for (const [i, p] of targets.entries()) {
    console.log(`[${i + 1}/${targets.length}] ${p.title}`);
    try {
      const r = await runJob(p, isDraft ? 'draft' : 'publish');
      if (r.ok) {
        okCount++;
        console.log(`  ✅ ${mode} 완료`);
      } else console.log(`  ❌ 실패: ${r.error}`);
    } catch (e) {
      console.log(`  ❌ 실패: ${e.message}`);
    }
    if (i < targets.length - 1) {
      const wait = gapMin * 60000 + Math.floor(Math.random() * 60000); // 기계처럼 보이지 않게 조금씩 다르게
      console.log(`  … 다음 글까지 약 ${Math.round(wait / 60000)}분 쉬어요\n`);
      await sleep(wait);
    }
  }
  console.log(`\n===== ${targets.length}편 중 ${okCount}편 ${mode} 완료 =====`);
  if (isDraft) console.log('네이버 블로그 글쓰기 화면 오른쪽 위 "저장" 숫자를 누르면 임시저장 글이 보여요.');
  console.log('');
})();
