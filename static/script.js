const statusEl = document.getElementById('status');
const refreshBtn = document.getElementById('refreshBtn');
const leaderList = document.getElementById('leader-list');

async function renderLeaders() {
  statusEl.textContent = 'Loading data...';
  try {
    const response = await fetch('/api/leaders');
    if (!response.ok) throw new Error('Failed to fetch leaders');
    const leaders = await response.json();
    const categories = leaders.reduce((acc, leader) => {
      acc[leader.category] = acc[leader.category] || [];
      acc[leader.category].push(leader);
      return acc;
    }, {});

    leaderList.innerHTML = Object.entries(categories)
      .map(([category, items]) => `
        <article class="category-card">
          <h2>${category}</h2>
          <table>
            <thead>
              <tr><th>Rank</th><th>Player</th><th>Value</th></tr>
            </thead>
            <tbody>
              ${items
                .map(
                  item => `
                    <tr>
                      <td>${item.rank}</td>
                      <td>${item.player_name}</td>
                      <td>${item.value}</td>
                    </tr>`
                )
                .join('')}
            </tbody>
          </table>
        </article>`
      )
      .join('');

    statusEl.textContent = `Loaded ${leaders.length} records.`;
  } catch (error) {
    statusEl.textContent = error.message;
  }
}

refreshBtn.addEventListener('click', async () => {
  statusEl.textContent = 'Refreshing data...';
  try {
    const response = await fetch('/api/scrape', { method: 'POST' });
    if (!response.ok) throw new Error('Refresh failed');
    const data = await response.json();
    statusEl.textContent = `Refreshed ${data.records} records.`;
    await renderLeaders();
  } catch (error) {
    statusEl.textContent = error.message;
  }
});

renderLeaders();
