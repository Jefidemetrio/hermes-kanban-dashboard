const statusEl = document.getElementById('status');
const statsBox = document.getElementById('statsBox');
const assigneeSummary = document.getElementById('assigneeSummary');
const profileSelect = document.getElementById('profileSelect');
const statusSelect = document.getElementById('statusSelect');
const refreshBtn = document.getElementById('refreshBtn');
const tbody = document.querySelector('#tasksTbody');
const taskCount = document.getElementById('taskCount');

async function fetchJSON(url){
  const res = await fetch(url);
  return res.json();
}

function fmt(ts){
  if(!ts) return '-';
  return new Date(ts*1000).toLocaleString('pt-BR');
}

async function refresh(){
  const profile = profileSelect.value;
  const status = statusSelect.value;
  statusEl.textContent = 'Atualizando...';
  try{
    const statsUrl = '/api/stats' + (profile ? `?profile=${encodeURIComponent(profile)}` : '');
    const stats = await fetchJSON(statsUrl);
    statsBox.textContent = JSON.stringify(stats,null,2);
    if(assigneeSummary){
      const by = stats.by_assignee || {};
      assigneeSummary.innerHTML = Object.entries(by).map(([k,v])=>`<span class="badge bg-light text-dark me-1 mb-1">${k}: ${v}</span>`).join('');
    }
    
    const tasksUrl = '/api/tasks?' + new URLSearchParams({
      ...(profile && {profile}),
      ...(status && {status}),
      limit: '200'
    });
    const data = await fetchJSON(tasksUrl);
    tbody.innerHTML = '';
    (data.tasks || []).forEach(t => {
      const tr = document.createElement('tr');
      tr.innerHTML = `<td><code>${t.id}</code></td><td>${t.title}</td><td><span class="badge bg-secondary">${t.status}</span></td><td>${t.assignee||''}</td><td>${fmt(t.created_at)}</td><td>${fmt(t.completed_at)}</td>`;
      tbody.appendChild(tr);
    });
    if(taskCount) taskCount.textContent = (data.tasks||[]).length;
    statusEl.textContent = 'Atualizado em ' + new Date().toLocaleTimeString();
  }catch(e){
    statusEl.textContent = 'Erro ao atualizar';
    console.error(e);
  }
}

refreshBtn.addEventListener('click', refresh);
profileSelect.addEventListener('change', refresh);
statusSelect.addEventListener('change', refresh);
refresh();
setInterval(refresh, 5000);
