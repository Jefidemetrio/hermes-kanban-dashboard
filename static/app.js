$(function(){
  const $statusEl = $('#status');
  const $statsBox = $('#statsBox');
  const $assigneeSummary = $('#assigneeSummary');
  const $profileSelect = $('#profileSelect');
  const $statusSelect = $('#statusSelect');
  const $refreshBtn = $('#refreshBtn');
  const $tbody = $('#tasksTbody');
  const $taskCount = $('#taskCount');

  let statusChart, assigneeChart;

  function fmt(ts){
    if(!ts) return '-';
    return new Date(ts*1000).toLocaleString('pt-BR');
  }

  function renderStats(stats){
    $statsBox.text(JSON.stringify(stats,null,2));
    const byStatus = stats.by_status || {};
    const categories = Object.keys(byStatus);
    const data = Object.values(byStatus);
    if(statusChart) statusChart.destroy();
    statusChart = new ApexCharts(document.querySelector('#statusChart'), {
      chart:{type:'bar',height:280,toolbar:{show:false}},
      series:[{name:'Tarefas',data:data}],
      xaxis:{categories:categories},
      colors:['#3b82f6']
    });
    statusChart.render();

    const byAssignee = stats.by_assignee || {};
    const aCats = Object.keys(byAssignee);
    const aData = Object.values(byAssignee);
    if(assigneeChart) assigneeChart.destroy();
    assigneeChart = new ApexCharts(document.querySelector('#assigneeChart'), {
      chart:{type:'donut',height:260},
      series:aData,
      labels:aCats,
      legend:{position:'bottom'}
    });
    assigneeChart.render();

    const badges = aCats.map(k=>`<span class="badge bg-light text-dark me-1 mb-1">${k}: ${byAssignee[k]}</span>`).join('');
    $assigneeSummary.html(badges);
  }

  async function refresh(){
    const profile = $profileSelect.val();
    const status = $statusSelect.val();
    $statusEl.text('Atualizando...');
    try{
      const statsUrl = '/api/stats' + (profile ? `?profile=${encodeURIComponent(profile)}` : '');
      const stats = await $.getJSON(statsUrl);
      renderStats(stats);

      const tasksUrl = '/api/tasks?' + $.param({
        ...(profile && {profile}),
        ...(status && {status}),
        limit:200
      });
      const data = await $.getJSON(tasksUrl);
      $tbody.empty();
      (data.tasks||[]).forEach(t=>{
        const tr = `<tr>
          <td><code>${t.id}</code></td>
          <td>${t.title}</td>
          <td><span class="badge bg-secondary">${t.status}</span></td>
          <td>${t.assignee||''}</td>
          <td>${fmt(t.created_at)}</td>
          <td>${fmt(t.completed_at)}</td>
        </tr>`;
        $tbody.append(tr);
      });
      $taskCount.text((data.tasks||[]).length);
      $statusEl.text('Atualizado em ' + new Date().toLocaleTimeString());
    }catch(e){
      $statusEl.text('Erro ao atualizar');
      console.error(e);
    }
  }

  $refreshBtn.on('click', refresh);
  $profileSelect.on('change', refresh);
  $statusSelect.on('change', refresh);
  refresh();
  setInterval(refresh, 5000);
});
