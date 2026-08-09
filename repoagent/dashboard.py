from __future__ import annotations

DASHBOARD_HTML = r"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width,initial-scale=1">
  <title>RepoAgent Observatory</title>
  <style>
    :root { color-scheme: dark; --bg:#0b1020; --panel:#121a2e; --line:#26314d;
      --text:#e8edf7; --muted:#95a2ba; --cyan:#56d6c9; --amber:#ffbe63; --red:#ff7185; }
    * { box-sizing:border-box } body { margin:0; font-family:Inter,ui-sans-serif,system-ui;
      background:radial-gradient(circle at 15% -10%,#17335c 0,transparent 33%),var(--bg); color:var(--text) }
    main { max-width:1280px; margin:auto; padding:36px 24px 64px }
    header { display:flex; justify-content:space-between; gap:24px; align-items:end; margin-bottom:28px }
    h1 { margin:0; font-size:clamp(28px,4vw,46px); letter-spacing:-.04em }
    header p,.muted { color:var(--muted) } .badge { border:1px solid #286b68; color:var(--cyan);
      padding:7px 11px; border-radius:999px; font:12px ui-monospace,monospace }
    .metrics { display:grid; grid-template-columns:repeat(4,1fr); gap:12px; margin-bottom:20px }
    .card,.panel { border:1px solid var(--line); background:rgba(18,26,46,.86); border-radius:14px }
    .card { padding:17px } .card b { display:block; font-size:28px; margin-top:7px }
    .layout { display:grid; grid-template-columns:minmax(300px,.8fr) minmax(420px,1.4fr); gap:16px }
    .panel { overflow:hidden } .panel h2 { font-size:14px; letter-spacing:.08em; text-transform:uppercase;
      color:var(--muted); margin:0; padding:17px 19px; border-bottom:1px solid var(--line) }
    #runs { max-height:720px; overflow:auto } button.run { width:100%; color:inherit; background:none; border:0;
      border-bottom:1px solid var(--line); padding:16px 19px; text-align:left; cursor:pointer }
    button.run:hover,button.run.active { background:#18233d } .row { display:flex; justify-content:space-between; gap:12px }
    .status { font:11px ui-monospace,monospace; text-transform:uppercase; color:var(--cyan) }
    .status.failed { color:var(--red) } .summary { color:var(--muted); margin-top:7px; line-height:1.45 }
    #detail { padding:20px; min-height:420px } pre { white-space:pre-wrap; overflow-wrap:anywhere; font:12px/1.65
      ui-monospace,SFMono-Regular,monospace; background:#090e1a; border:1px solid var(--line); padding:14px;
      border-radius:10px; max-height:390px; overflow:auto } .trace { display:grid; gap:8px }
    .event { border-left:2px solid var(--line); padding:7px 11px } .event strong { color:var(--amber); font-size:12px }
    @media (max-width:800px) { .metrics { grid-template-columns:repeat(2,1fr) } .layout { grid-template-columns:1fr } }
  </style>
</head>
<body><main>
  <header><div><h1>RepoAgent Observatory</h1><p>Execution quality, tool trajectories, and repository changes.</p></div>
  <span class="badge">LOCAL · AUDITABLE</span></header>
  <section class="metrics">
    <div class="card"><span class="muted">Runs</span><b id="m-runs">—</b></div>
    <div class="card"><span class="muted">Completion</span><b id="m-rate">—</b></div>
    <div class="card"><span class="muted">Tool calls</span><b id="m-tools">—</b></div>
    <div class="card"><span class="muted">Tool errors</span><b id="m-errors">—</b></div>
  </section>
  <section class="layout"><div class="panel"><h2>Run history</h2><div id="runs"></div></div>
  <div class="panel"><h2>Run detail</h2><div id="detail" class="muted">Select a run to inspect its result and trajectory.</div></div></section>
</main><script>
const esc=s=>String(s??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
async function boot(){
  const report=await fetch('/history').then(r=>r.json());
  document.querySelector('#m-runs').textContent=report.total_runs;
  document.querySelector('#m-rate').textContent=Math.round(report.completion_rate*100)+'%';
  document.querySelector('#m-tools').textContent=report.tool_calls;
  document.querySelector('#m-errors').textContent=report.tool_errors;
  const host=document.querySelector('#runs');
  if(!report.runs.length){host.innerHTML='<p class="summary" style="padding:18px">No completed run records yet.</p>';return}
  report.runs.forEach((run,i)=>{const b=document.createElement('button');b.className='run';
    b.innerHTML=`<div class="row"><strong>${esc(run.run_id)}</strong><span class="status ${esc(run.status)}">${esc(run.status)}</span></div><div class="summary">${esc(run.summary)}</div>`;
    b.onclick=()=>show(run.run_id,b);host.appendChild(b);if(i===0)b.click()});
}
async function show(id,button){document.querySelectorAll('.run').forEach(x=>x.classList.remove('active'));button.classList.add('active');
  const data=await fetch('/runs/'+encodeURIComponent(id)).then(r=>r.json()); const r=data.result;
  document.querySelector('#detail').innerHTML=`<div class="row"><h3>${esc(r.status)}</h3><span class="badge">${esc(r.changed_files.length)} files</span></div>
    <p>${esc(r.summary)}</p><h3>Metrics</h3><pre>${esc(JSON.stringify(r.metrics,null,2))}</pre><h3>Diff</h3><pre>${esc(r.diff||'No applied diff')}</pre>
    <h3>Trajectory</h3><div class="trace">${data.trace.map(e=>`<div class="event"><strong>${esc(e.event)}</strong><div class="summary">${esc(JSON.stringify(e.payload))}</div></div>`).join('')}</div>`;
}
boot().catch(e=>document.querySelector('#detail').textContent=e);
</script></body></html>"""
