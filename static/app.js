const statusEl = document.getElementById('status');
const statsBox = document.getElementById('statsBox');
const tasksBox = document.getElementById('tasksBox');

async function fetchJSON(url){
  const res = await fetch(url);
  return res.json();
}

async function refresh(){
  statusEl.textContent = 'Atualizando...';
  try{
    const stats = await fetchJSON('/api/stats');
    statsBox.textContent = stats.raw || JSON.stringify(stats,null,2);
    const tasks = await fetchJSON('/api/tasks');
    tasksBox.textContent = tasks.raw || tasks.lines.join('\n') || JSON.stringify(tasks,null,2);
    statusEl.textContent = 'Atualizado em ' + new Date().toLocaleTimeString();
  }catch(e){
    statusEl.textContent = 'Erro ao atualizar';
    console.error(e);
  }
}

refresh();
setInterval(refresh, 5000);
