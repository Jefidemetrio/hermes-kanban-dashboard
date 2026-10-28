const statusEl = document.getElementById('status');
const statsBox = document.getElementById('statsBox');
const profileSelect = document.getElementById('profileSelect');
const statusSelect = document.getElementById('statusSelect');
const refreshBtn = document.getElementById('refreshBtn');
const tbody = document.querySelector('#tasksTable tbody');

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
    
    const tasksUrl = '/api/tasks?' + new URLSearchParams({
      ...(profile && {profile}),
      ...(status && {status}),
      limit: '200'
    });
    const data = await fetchJSON(tasksUrl);
    tbody.innerHTML = '';
    (data.tasks || []).forEach(t => {
      const tr = document.createElement('tr');
      tr.innerHTML = `<td>${t.id}</td><td>${t.title}</td><td>${t.status}</td><td>${t.assignee||''}</td><td>${fmt(t.created_at)}</td><td>${fmt(t.completed_at)}</td>`;
      tbody.appendChild(tr);
    });
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
