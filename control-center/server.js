const express = require('express');
const { WebSocketServer } = require('ws');
const http = require('http');
const si = require('systeminformation');
const { execSync } = require('child_process');
const fs = require('fs');
const path = require('path');

const app = express();
const server = http.createServer(app);
const wss = new WebSocketServer({ server, path: '/ws' });
const PORT = process.env.PORT || 3777;

// Serve static files
app.use(express.static(path.join(__dirname, 'public')));

// REST fallback endpoint
app.get('/api/system', async (req, res) => {
  try {
    const data = await collectData();
    res.json(data);
  } catch (e) {
    res.status(500).json({ error: e.message });
  }
});

// Collect all system data
async function collectData() {
  const [cpu, mem, os, load, time, disks, netStats, procs] = await Promise.all([
    si.currentLoad(),
    si.mem(),
    si.osInfo(),
    si.fullLoad(),
    si.time(),
    si.fsSize(),
    si.networkStats(),
    si.processes()
  ]);

  // Temperatures (may not be available on all systems)
  let temps = { cpu: null, gpu: null, board: null, disk: null };
  try {
    const t = await si.cpuTemperature();
    temps.cpu = t.main || t.cores?.[0] || null;
  } catch {}

  // Try lm-sensors as fallback
  try {
    const out = execSync('sensors -j 2>/dev/null || true', { encoding: 'utf-8' });
    if (out) {
      const j = JSON.parse(out);
      for (const [chip, sensors] of Object.entries(j)) {
        for (const [key, val] of Object.entries(sensors)) {
          const [name, ...rest] = key.split('_');
          const suffix = rest.join('_');
          if (suffix === 'input' && typeof val === 'number') {
            const k = name.toLowerCase();
            if (k.includes('cpu') || k.includes('core')) temps.cpu = val;
            else if (k.includes('gpu')) temps.gpu = val;
            else if (k.includes('board') || k.includes('mother') || k.includes('sys')) temps.board = val;
            else if (k.includes('sd') || k.includes('nvme') || k.includes('hdd')) temps.disk = val;
          }
        }
      }
    }
  } catch {}

  // Uptime in seconds
  const uptimeSec = os.uptime;

  // Users
  let users = 0;
  try {
    const u = await si.users();
    users = u.length;
  } catch {}

  // Network interfaces (active only)
  const netInterfaces = netStats
    .filter(n => n.operstate === 'up' && n.iface !== 'lo')
    .map(n => `${n.iface} (${n.ip4 || n.ip6 || 'no IP'})`);

  // TCP connections count
  let tcpCount = 0;
  try {
    const netstat = execSync("cat /proc/net/tcp 2>/dev/null | wc -l || echo 0", { encoding: 'utf-8' });
    tcpCount = parseInt(netstat.trim()) - 1;
  } catch {}

  // Top 10 processes by CPU
  const topProcs = (procs.list || [])
    .filter(p => p.pid && p.name && p.name !== 'System Idle Process')
    .sort((a, b) => (b.pcpu || 0) - (a.pcpu || 0))
    .slice(0, 10)
    .map(p => ({
      pid: p.pid,
      name: p.name,
      cpu: +(p.pcpu || 0).toFixed(1),
      mem: +(p.pmem || 0).toFixed(1),
      state: p.status === 'running' ? 'R' : p.status === 'sleeping' ? 'S' : p.status?.[0]?.toUpperCase() || '?'
    }));

  // Network I/O totals
  let netIO = { rx_sec: 0, tx_sec: 0 };
  const activeIfaces = netStats.filter(n => n.operstate === 'up' && n.iface !== 'lo');
  if (activeIfaces.length) {
    netIO.rx_sec = activeIfaces.reduce((s, n) => s + (n.rx_sec || 0), 0);
    netIO.tx_sec = activeIfaces.reduce((s, n) => s + (n.tx_sec || 0), 0);
  }

  // System logs (last few lines from journal or syslog)
  let logs = [];
  try {
    const lines = execSync('journalctl -n 8 --no-pager -o short-iso 2>/dev/null || tail -8 /var/log/syslog 2>/dev/null || tail -8 /var/log/messages 2>/dev/null', { encoding: 'utf-8' });
    logs = lines.trim().split('\n').filter(Boolean).slice(-8).map(line => {
      // Parse severity
      let type = '';
      const lower = line.toLowerCase();
      if (lower.includes('error') || lower.includes('fail') || lower.includes('critical')) type = 'error';
      else if (lower.includes('warn') || lower.includes('alert')) type = 'warn';
      else if (lower.includes('ok') || lower.includes('success') || lower.includes('started')) type = 'ok';
      return { msg: line.slice(20).trim().slice(0, 100), type };
    });
  } catch {}

  return {
    hostname: os.hostname,
    kernel: os.kernel,
    arch: os.arch,
    platform: os.platform,
    uptimeSec,
    users,
    cpuPct: cpu.currentLoad,
    cpuCores: cpu.cpus?.length || 0,
    memTotal: mem.total,
    memUsed: mem.used,
    memActive: mem.active,
    swapTotal: mem.swaptotal,
    swapUsed: mem.swapused,
    temps,
    disks: disks.map(d => ({
      name: d.fs,
      mount: d.mount,
      total: d.size,
      used: d.used,
      available: d.available,
      use: d.use
    })),
    processes: topProcs,
    netIO,
    netInterfaces,
    tcpCount,
    loadAvg: load.avgLoad ? load.avgLoad.join(' ') : '0 0 0',
    logs
  };
}

// WebSocket broadcast
wss.on('connection', (ws) => {
  console.log('Client connected');
  // Send data immediately
  collectData().then(data => ws.send(JSON.stringify(data))).catch(e => console.error(e));
});

// Push data every 3 seconds to all connected clients
setInterval(async () => {
  const data = await collectData().catch(e => ({ error: e.message }));
  const msg = JSON.stringify(data);
  wss.clients.forEach(client => {
    if (client.readyState === 1) client.send(msg);
  });
}, 3000);

server.listen(PORT, () => {
  console.log(`Control Center running on http://0.0.0.0:${PORT}`);
});
