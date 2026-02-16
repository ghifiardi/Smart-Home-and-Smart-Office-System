"""
Dashboard - HTML monitoring dashboard for the Semantic Firewall.
"""

from __future__ import annotations


def render_dashboard() -> str:
    """Render the real-time monitoring dashboard as HTML."""
    return _DASHBOARD_HTML


_DASHBOARD_HTML = """\
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Semantic Firewall - Monitoring Dashboard</title>
  <script src="https://cdn.tailwindcss.com"></script>
  <script src="https://cdn.jsdelivr.net/npm/chart.js@4"></script>
  <style>
    body { background: #0f172a; color: #e2e8f0; font-family: 'Inter', system-ui, sans-serif; }
    .card { background: #1e293b; border: 1px solid #334155; border-radius: 12px; }
    .glow-green { box-shadow: 0 0 20px rgba(34, 197, 94, 0.15); }
    .glow-red { box-shadow: 0 0 20px rgba(239, 68, 68, 0.15); }
    .glow-yellow { box-shadow: 0 0 20px rgba(234, 179, 8, 0.15); }
    .verdict-pass { color: #22c55e; }
    .verdict-warn { color: #eab308; }
    .verdict-block { color: #ef4444; }
    .pulse { animation: pulse 2s infinite; }
    @keyframes pulse { 0%, 100% { opacity: 1; } 50% { opacity: 0.5; } }
    .scanner-badge { display: inline-block; padding: 2px 10px; border-radius: 9999px; font-size: 0.75rem; font-weight: 600; }
  </style>
</head>
<body class="min-h-screen p-6">
  <div class="max-w-7xl mx-auto">
    <!-- Header -->
    <div class="flex items-center justify-between mb-8">
      <div>
        <h1 class="text-3xl font-bold text-white flex items-center gap-3">
          <svg class="w-8 h-8 text-cyan-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z"/>
          </svg>
          Semantic Firewall
        </h1>
        <p class="text-slate-400 mt-1">Real-time AI security monitoring</p>
      </div>
      <div class="flex items-center gap-3">
        <span id="status-indicator" class="pulse inline-block w-3 h-3 rounded-full bg-green-400"></span>
        <span id="status-text" class="text-sm text-slate-400">Active</span>
        <span class="text-sm text-slate-500 ml-4" id="last-update"></span>
      </div>
    </div>

    <!-- Overview Cards -->
    <div class="grid grid-cols-1 md:grid-cols-4 gap-4 mb-8">
      <div class="card p-5 glow-green">
        <div class="text-sm text-slate-400 uppercase tracking-wide">Total Scans</div>
        <div class="text-3xl font-bold text-white mt-1" id="total-scans">0</div>
        <div class="text-xs text-slate-500 mt-1">All traffic analyzed</div>
      </div>
      <div class="card p-5 glow-red">
        <div class="text-sm text-slate-400 uppercase tracking-wide">Blocked</div>
        <div class="text-3xl font-bold text-red-400 mt-1" id="blocks">0</div>
        <div class="text-xs text-slate-500 mt-1" id="block-rate">0% block rate</div>
      </div>
      <div class="card p-5 glow-yellow">
        <div class="text-sm text-slate-400 uppercase tracking-wide">Warnings</div>
        <div class="text-3xl font-bold text-yellow-400 mt-1" id="warnings">0</div>
        <div class="text-xs text-slate-500 mt-1" id="warn-rate">0% warn rate</div>
      </div>
      <div class="card p-5 glow-green">
        <div class="text-sm text-slate-400 uppercase tracking-wide">Passed</div>
        <div class="text-3xl font-bold text-green-400 mt-1" id="passes">0</div>
        <div class="text-xs text-slate-500 mt-1">Clean traffic</div>
      </div>
    </div>

    <!-- Charts Row -->
    <div class="grid grid-cols-1 md:grid-cols-2 gap-6 mb-8">
      <div class="card p-5">
        <h3 class="text-lg font-semibold text-white mb-4">Traffic Direction</h3>
        <canvas id="traffic-chart" height="200"></canvas>
      </div>
      <div class="card p-5">
        <h3 class="text-lg font-semibold text-white mb-4">Findings by Category</h3>
        <canvas id="findings-chart" height="200"></canvas>
      </div>
    </div>

    <!-- Policy & Scanners -->
    <div class="grid grid-cols-1 md:grid-cols-2 gap-6 mb-8">
      <div class="card p-5">
        <h3 class="text-lg font-semibold text-white mb-4">Active Policy</h3>
        <div id="policy-info" class="space-y-2 text-sm">
          <div class="flex justify-between"><span class="text-slate-400">Name</span><span id="policy-name" class="text-white">-</span></div>
          <div class="flex justify-between"><span class="text-slate-400">Active Rules</span><span id="active-rules" class="text-white">-</span></div>
          <div class="flex justify-between"><span class="text-slate-400">Block Threshold</span><span id="block-threshold" class="text-red-400">-</span></div>
          <div class="flex justify-between"><span class="text-slate-400">Warn Threshold</span><span id="warn-threshold" class="text-yellow-400">-</span></div>
        </div>
      </div>
      <div class="card p-5">
        <h3 class="text-lg font-semibold text-white mb-4">Registered Scanners</h3>
        <div id="scanners-list" class="flex flex-wrap gap-2"></div>
      </div>
    </div>

    <!-- Recent Events -->
    <div class="card p-5">
      <h3 class="text-lg font-semibold text-white mb-4">Recent Security Events</h3>
      <div class="overflow-x-auto">
        <table class="w-full text-sm">
          <thead>
            <tr class="text-slate-400 border-b border-slate-700">
              <th class="text-left py-2 px-3">Time</th>
              <th class="text-left py-2 px-3">Direction</th>
              <th class="text-left py-2 px-3">Verdict</th>
              <th class="text-left py-2 px-3">Risk Score</th>
              <th class="text-left py-2 px-3">Findings</th>
              <th class="text-left py-2 px-3">Endpoint</th>
              <th class="text-left py-2 px-3">User</th>
            </tr>
          </thead>
          <tbody id="events-table"></tbody>
        </table>
      </div>
      <div id="no-events" class="text-center text-slate-500 py-8">No events yet. The firewall is monitoring traffic.</div>
    </div>

    <!-- Test Scanner -->
    <div class="card p-5 mt-8">
      <h3 class="text-lg font-semibold text-white mb-4">Test Scanner</h3>
      <p class="text-sm text-slate-400 mb-4">Test content against the firewall to tune policies.</p>
      <div class="flex gap-4">
        <select id="test-direction" class="bg-slate-800 border border-slate-600 rounded-lg px-3 py-2 text-sm text-white">
          <option value="inbound">Inbound</option>
          <option value="outbound">Outbound</option>
        </select>
        <input id="test-input" type="text" placeholder="Enter content to scan..." class="flex-1 bg-slate-800 border border-slate-600 rounded-lg px-4 py-2 text-sm text-white placeholder-slate-500">
        <button onclick="runTestScan()" class="bg-cyan-600 hover:bg-cyan-700 text-white px-6 py-2 rounded-lg text-sm font-semibold transition">Scan</button>
      </div>
      <div id="test-result" class="mt-4 hidden">
        <pre class="bg-slate-900 rounded-lg p-4 text-xs overflow-x-auto text-slate-300"></pre>
      </div>
    </div>
  </div>

  <script>
    const CATEGORY_COLORS = {
      prompt_injection: '#ef4444',
      jailbreak_attempt: '#dc2626',
      pii_leakage: '#f97316',
      data_exfiltration: '#eab308',
      sensitive_data_exposure: '#a855f7',
      malicious_payload: '#e11d48',
      content_safety: '#3b82f6',
      schema_violation: '#6366f1',
      rate_anomaly: '#14b8a6',
      token_abuse: '#64748b',
      policy_violation: '#8b5cf6',
    };

    const SCANNER_COLORS = {
      prompt_injection: 'bg-red-900 text-red-300',
      malicious_payload: 'bg-rose-900 text-rose-300',
      input_validation: 'bg-blue-900 text-blue-300',
      pii_detector: 'bg-orange-900 text-orange-300',
      data_exfiltration: 'bg-yellow-900 text-yellow-300',
      content_safety: 'bg-purple-900 text-purple-300',
    };

    let trafficChart, findingsChart;

    function initCharts() {
      const ctx1 = document.getElementById('traffic-chart').getContext('2d');
      trafficChart = new Chart(ctx1, {
        type: 'doughnut',
        data: {
          labels: ['Inbound', 'Outbound'],
          datasets: [{ data: [0, 0], backgroundColor: ['#3b82f6', '#22c55e'], borderWidth: 0 }]
        },
        options: {
          responsive: true,
          plugins: { legend: { labels: { color: '#94a3b8' } } }
        }
      });

      const ctx2 = document.getElementById('findings-chart').getContext('2d');
      findingsChart = new Chart(ctx2, {
        type: 'bar',
        data: { labels: [], datasets: [{ data: [], backgroundColor: [], borderWidth: 0 }] },
        options: {
          responsive: true,
          indexAxis: 'y',
          plugins: { legend: { display: false } },
          scales: {
            x: { ticks: { color: '#94a3b8' }, grid: { color: '#1e293b' } },
            y: { ticks: { color: '#94a3b8' }, grid: { display: false } },
          }
        }
      });
    }

    async function fetchMetrics() {
      try {
        const res = await fetch('/firewall/metrics');
        const data = await res.json();
        updateDashboard(data);
      } catch (e) {
        document.getElementById('status-indicator').className = 'inline-block w-3 h-3 rounded-full bg-red-400';
        document.getElementById('status-text').textContent = 'Connection Error';
      }
    }

    function updateDashboard(data) {
      const ov = data.overview;
      document.getElementById('total-scans').textContent = ov.total_scans.toLocaleString();
      document.getElementById('blocks').textContent = ov.blocks.toLocaleString();
      document.getElementById('warnings').textContent = ov.warnings.toLocaleString();
      document.getElementById('passes').textContent = ov.passes.toLocaleString();
      document.getElementById('block-rate').textContent = ov.block_rate + '% block rate';
      document.getElementById('warn-rate').textContent = ov.warn_rate + '% warn rate';

      // Traffic chart
      trafficChart.data.datasets[0].data = [data.traffic.inbound_scans, data.traffic.outbound_scans];
      trafficChart.update();

      // Findings chart
      const cats = Object.entries(data.findings_by_category).sort((a, b) => b[1] - a[1]);
      findingsChart.data.labels = cats.map(([k]) => k.replace(/_/g, ' '));
      findingsChart.data.datasets[0].data = cats.map(([, v]) => v);
      findingsChart.data.datasets[0].backgroundColor = cats.map(([k]) => CATEGORY_COLORS[k] || '#64748b');
      findingsChart.update();

      // Policy
      const p = data.policy;
      document.getElementById('policy-name').textContent = p.policy_name;
      document.getElementById('active-rules').textContent = p.active_rules;
      document.getElementById('block-threshold').textContent = p.block_threshold;
      document.getElementById('warn-threshold').textContent = p.warn_threshold;

      // Scanners
      const sl = document.getElementById('scanners-list');
      sl.innerHTML = data.scanners.map(s =>
        `<span class="scanner-badge ${SCANNER_COLORS[s] || 'bg-slate-700 text-slate-300'}">${s.replace(/_/g, ' ')}</span>`
      ).join('');

      // Events
      const events = data.recent_events || [];
      const tbody = document.getElementById('events-table');
      const noEvents = document.getElementById('no-events');
      if (events.length > 0) {
        noEvents.classList.add('hidden');
        tbody.innerHTML = events.reverse().map(e => `
          <tr class="border-b border-slate-800 hover:bg-slate-800/50">
            <td class="py-2 px-3 text-slate-400">${new Date(e.timestamp).toLocaleTimeString()}</td>
            <td class="py-2 px-3">${e.direction}</td>
            <td class="py-2 px-3 verdict-${e.verdict} font-semibold">${e.verdict.toUpperCase()}</td>
            <td class="py-2 px-3">${(e.risk_score * 100).toFixed(0)}%</td>
            <td class="py-2 px-3">${e.finding_count}</td>
            <td class="py-2 px-3 text-slate-400">${e.endpoint || '-'}</td>
            <td class="py-2 px-3 text-slate-400">${e.user_id || '-'}</td>
          </tr>
        `).join('');
      }

      document.getElementById('last-update').textContent = 'Updated ' + new Date().toLocaleTimeString();
      document.getElementById('status-indicator').className = 'pulse inline-block w-3 h-3 rounded-full bg-green-400';
      document.getElementById('status-text').textContent = 'Active';
    }

    async function runTestScan() {
      const content = document.getElementById('test-input').value;
      const direction = document.getElementById('test-direction').value;
      if (!content) return;

      try {
        const res = await fetch(`/firewall/scan/test?content=${encodeURIComponent(content)}&direction=${direction}`, { method: 'POST' });
        const data = await res.json();
        const container = document.getElementById('test-result');
        container.classList.remove('hidden');
        container.querySelector('pre').textContent = JSON.stringify(data, null, 2);
        fetchMetrics(); // Refresh dashboard after test
      } catch (e) {
        alert('Scan failed: ' + e.message);
      }
    }

    // Initialize
    initCharts();
    fetchMetrics();
    setInterval(fetchMetrics, 5000); // Auto-refresh every 5s
  </script>
</body>
</html>
"""
