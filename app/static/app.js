const $ = (id) => document.getElementById(id);

async function api(path, options = {}) {
  const res = await fetch(path, {
    headers: { 'Content-Type': 'application/json' },
    ...options,
  });
  if (!res.ok) throw new Error(await res.text());
  return res.json();
}

async function checkHealth() {
  try {
    const data = await api('/health');
    $('health').textContent = `OK · ${data.provider} · ${data.knowledge_chunks} chunks`;
  } catch (e) {
    $('health').textContent = 'offline';
  }
}

function renderAssist(data) {
  const citations = data.citations.map(c => `
    <div class="citation">
      <b>${c.source} / ${c.section}</b> <span class="badge">score ${c.score}</span>
      <div>${escapeHtml(c.content)}</div>
    </div>`).join('');
  $('answer').classList.remove('empty');
  $('answer').innerHTML = `
    <div class="meta">
      <div><b>等级</b>${data.severity}</div>
      <div><b>责任团队</b>${data.owner_team}</div>
      <div><b>SLA</b>${data.suggested_sla}</div>
    </div>
    <h3>建议</h3>
    <div>${escapeHtml(data.answer)}</div>
    <h3>Checklist</h3>
    <ol>${data.checklist.map(x => `<li>${escapeHtml(x)}</li>`).join('')}</ol>
    <h3>引用依据</h3>
    ${citations || '无'}
  `;
}

async function ask() {
  const btn = $('askBtn');
  btn.disabled = true;
  btn.textContent = '生成中...';
  try {
    const data = await api('/api/assist', {
      method: 'POST',
      body: JSON.stringify({ question: $('question').value, scenario: $('scenario').value })
    });
    renderAssist(data);
  } catch (e) {
    $('answer').textContent = e.message;
  } finally {
    btn.disabled = false;
    btn.textContent = '生成处置建议';
  }
}

async function createTicket() {
  const btn = $('ticketBtn');
  btn.disabled = true;
  btn.textContent = '创建中...';
  try {
    await api('/api/tickets', {
      method: 'POST',
      body: JSON.stringify({
        title: $('ticketTitle').value,
        description: $('ticketDescription').value,
        scenario: $('scenario').value,
      })
    });
    await loadTickets();
  } catch (e) {
    alert(e.message);
  } finally {
    btn.disabled = false;
    btn.textContent = '创建工单';
  }
}

async function loadTickets() {
  const tickets = await api('/api/tickets');
  if (!tickets.length) {
    $('tickets').textContent = '暂无数据';
    $('tickets').classList.add('empty');
    return;
  }
  $('tickets').classList.remove('empty');
  $('tickets').innerHTML = tickets.map(t => `
    <div class="ticket">
      <b>#${t.id} ${escapeHtml(t.title)}</b>
      <span class="badge">${escapeHtml(t.severity)}</span>
      <p>${escapeHtml(t.description)}</p>
      <small>${escapeHtml(t.owner_team)} · ${escapeHtml(t.status)}</small>
    </div>
  `).join('');
}

function escapeHtml(str) {
  return String(str).replace(/[&<>'"]/g, c => ({'&':'&amp;', '<':'&lt;', '>':'&gt;', "'":'&#39;', '"':'&quot;'}[c]));
}

$('askBtn').addEventListener('click', ask);
$('ticketBtn').addEventListener('click', createTicket);
checkHealth();
loadTickets();
