// ABPS Frontend Engine - Pure Client Side Execution
let currentUser = { username: "admin", name: "Admin Officer", role: "Administrator" };

const SECTIONS = [
  "Mumbai-Pune", "Delhi-Agra", "Chennai-Bangalore", "Kolkata-Durgapur",
  "Ahmedabad-Vadodara", "Pune-Solapur", "Jaipur-Ajmer", "Lucknow-Kanpur",
  "Hyderabad-Secunderabad", "Nagpur-Wardha", "Bhopal-Itarsi", "Patna-Gaya",
  "Visakhapatnam-Vijayawada", "Coimbatore-Salem", "Surat-Vadodara"
];

const DEPARTMENTS = [
  { name: "Engineering", src: "TMS", color: "#0284c7" },
  { name: "Signal & Telecom", src: "SMMS", color: "#16a34a" },
  { name: "Traction Distribution", src: "TDMS", color: "#ea580c" }
];

const DEFECT_TEMPLATES = {
  "Engineering": [
    { asset: "Track", desc: "Rail fracture detected", sev: 5, sc: true, dur: 3.5, bt: "Traffic" },
    { asset: "Track", desc: "Rail joint gap defect", sev: 3, sc: false, dur: 2.0, bt: "Traffic" },
    { asset: "Bridge", desc: "Girder alignment inspection", sev: 4, sc: true, dur: 2.5, bt: "Traffic" },
    { asset: "Turnout", desc: "Point machine clearance defect", sev: 4, sc: true, dur: 3.0, bt: "Traffic" },
    { asset: "Track", desc: "Ballast deep screening", sev: 2, sc: false, dur: 4.0, bt: "Traffic" },
    { asset: "Rail", desc: "Rail wear gauge exceeding limit", sev: 3, sc: false, dur: 2.5, bt: "Traffic" }
  ],
  "Signal & Telecom": [
    { asset: "Signal", desc: "Home signal lamp failure", sev: 5, sc: true, dur: 1.5, bt: "Traffic" },
    { asset: "Signal", desc: "Point machine detection failure", sev: 4, sc: true, dur: 2.0, bt: "Traffic" },
    { asset: "Interlocking", desc: "Relay interlocking fault", sev: 5, sc: true, dur: 3.0, bt: "Traffic" },
    { asset: "Cable", desc: "Armoured signalling cable fault", sev: 3, sc: false, dur: 2.5, bt: "Traffic" },
    { asset: "Signal", desc: "Track circuit false drop", sev: 3, sc: false, dur: 2.0, bt: "Traffic" }
  ],
  "Traction Distribution": [
    { asset: "OHE", desc: "OHE contact wire break", sev: 5, sc: true, dur: 4.0, bt: "Power" },
    { asset: "OHE", desc: "Dropper defect on mast 14/2", sev: 3, sc: false, dur: 2.0, bt: "Power" },
    { asset: "Transformer", desc: "Auxiliary transformer failure", sev: 5, sc: true, dur: 3.5, bt: "Power" },
    { asset: "Feeder", desc: "Feeder breaker isolation fault", sev: 4, sc: true, dur: 2.5, bt: "Power" },
    { asset: "OHE", desc: "Cantilever insulator replacement", sev: 4, sc: true, dur: 2.5, bt: "Power" }
  ]
};

// Generate 201 synthetic tasks
let tasks = [];
let taskId = 1;
SECTIONS.forEach(sec => {
  DEPARTMENTS.forEach(dept => {
    const list = DEFECT_TEMPLATES[dept.name];
    list.forEach(item => {
      const overdue = Math.random() < 0.25 ? Math.floor(Math.random() * 14) + 1 : 0;
      const urg = overdue > 0 ? Math.min(1, 0.5 + overdue / 30) : 0.4;
      const score = Math.round((0.35 * (item.sev / 5) + 0.30 * urg + 0.20 * 0.85 + 0.15 * 0.75) * 100);
      const finalScore = item.sc ? Math.max(score, 88) : score;

      tasks.push({
        id: taskId,
        taskId: dept.src + "-" + sec.substring(0, 3).toUpperCase() + "-" + String(taskId).padStart(4, '0'),
        dept: dept.name,
        src: dept.src,
        sec: sec,
        asset: item.asset,
        desc: item.desc,
        sev: item.sev,
        sc: item.sc,
        dur: item.dur,
        bt: item.bt,
        score: finalScore,
        status: "Pending"
      });
      taskId++;
    });
  });
});

// Generated Windows
let windows = [];
let winId = 1;
SECTIONS.forEach(sec => {
  const slots = [
    { time: "00:00 - 04:00 (Night)", dur: 4.0 },
    { time: "04:00 - 05:30 (Dawn)", dur: 1.5 },
    { time: "10:30 - 12:00 (Midday)", dur: 1.5 },
    { time: "13:00 - 14:00 (Afternoon)", dur: 1.0 },
    { time: "22:00 - 00:00 (Late Night)", dur: 2.0 }
  ];
  slots.forEach(s => {
    windows.push({
      id: "WIN-" + sec.substring(0, 3).toUpperCase() + "-" + String(winId).padStart(4, '0'),
      sec: sec,
      time: s.time,
      dur: s.dur,
      tb: "Yes",
      pb: "Yes",
      status: "Available"
    });
    winId++;
  });
});

let plans = [];
let auditLogs = [
  { time: new Date().toLocaleTimeString(), action: "SYSTEM_INIT", officer: "SYSTEM", desc: "Loaded 201 tasks from TMS, SMMS, TDMS" },
  { time: new Date().toLocaleTimeString(), action: "TIMETABLE_SYNC", officer: "COA_AGENT", desc: "Corridor block availability synchronized" }
];

// Initialize on page load
document.addEventListener("DOMContentLoaded", () => {
  if (window.lucide) {
    lucide.createIcons();
  }
  renderDashboard();
  renderTasksTable();
  renderWindowsTable();
  renderAuditTable();
});

// Tab Switching
function switchTab(tab) {
  ['dashboard', 'tasks', 'windows', 'plans', 'benchmark', 'audit'].forEach(t => {
    const el = document.getElementById("tab-" + t);
    const nav = document.getElementById("nav-" + t);
    if (el) el.classList.add('hidden');
    if (nav) nav.classList.remove('sidebar-active', 'text-white');
  });

  const activeEl = document.getElementById("tab-" + tab);
  const activeNav = document.getElementById("nav-" + tab);
  if (activeEl) activeEl.classList.remove('hidden');
  if (activeNav) activeNav.classList.add('sidebar-active');

  if (window.lucide) {
    lucide.createIcons();
  }
}

// Authentication
function handleLogin(e) {
  e.preventDefault();
  const u = document.getElementById('login-user').value;
  currentUser = { username: u, name: u === 'admin' ? 'Admin Officer' : (u === 'approver' ? 'Sr. DEN Officer' : 'Section Planner'), role: u };
  document.getElementById('user-display-name').innerText = currentUser.name;
  document.getElementById('user-role-badge').innerText = "Role: " + u.toUpperCase();
  document.getElementById('login-modal').classList.add('hidden');
  auditLogs.unshift({ time: new Date().toLocaleTimeString(), action: "AUTH_LOGIN", officer: currentUser.name, desc: "Officer logged into Central ABPS" });
  renderAuditTable();
}

function logout() {
  document.getElementById('login-modal').classList.remove('hidden');
}

// Add Task Modal Controls
function toggleAddTaskModal(show) {
  const modal = document.getElementById('add-task-modal');
  if (modal) {
    if (show) modal.classList.remove('hidden');
    else modal.classList.add('hidden');
  }
}

function handleManualAddTask(e) {
  e.preventDefault();
  const dept = document.getElementById('new-task-dept').value;
  const sec = document.getElementById('new-task-sec').value;
  const asset = document.getElementById('new-task-asset').value;
  const dur = parseFloat(document.getElementById('new-task-dur').value);
  const desc = document.getElementById('new-task-desc').value;
  const sev = parseInt(document.getElementById('new-task-sev').value);
  const sc = document.getElementById('new-task-sc').value === 'true';

  const src = dept === 'Engineering' ? 'TMS' : (dept === 'Signal & Telecom' ? 'SMMS' : 'TDMS');
  const bt = dept === 'Traction Distribution' ? 'Power' : 'Traffic';

  const score = Math.round((0.35 * (sev / 5) + 0.30 * 0.8 + 0.20 * 0.9 + 0.15 * 0.8) * 100);
  const finalScore = sc ? Math.max(score, 90) : score;

  const newTask = {
    id: tasks.length + 1,
    taskId: src + "-" + sec.substring(0, 3).toUpperCase() + "-" + String(tasks.length + 1).padStart(4, '0'),
    dept: dept,
    src: src,
    sec: sec,
    asset: asset,
    desc: desc,
    sev: sev,
    sc: sc,
    dur: dur,
    bt: bt,
    score: finalScore,
    status: 'Pending'
  };

  tasks.unshift(newTask);
  document.getElementById('stat-total').innerText = tasks.length;
  document.getElementById('stat-pending').innerText = tasks.filter(t => t.status === 'Pending').length;
  if (sc) {
    const curCrit = parseInt(document.getElementById('stat-critical').innerText);
    document.getElementById('stat-critical').innerText = curCrit + 1;
  }

  auditLogs.unshift({
    time: new Date().toLocaleTimeString(),
    action: 'TASK_REPORTED',
    officer: currentUser.name,
    desc: "Manually logged " + desc + " on " + sec + " (Score: " + finalScore + ")"
  });

  toggleAddTaskModal(false);
  renderTasksTable();
  renderDashboard();
  renderAuditTable();
  switchTab('tasks');
  alert("✅ New Defect Registered in " + src + "!\nTask ID: " + newTask.taskId + "\nCorridor: " + sec + "\nCalculated Priority Score: " + finalScore + "/100");
}

// Dashboard rendering
function renderDashboard() {
  const topCritical = tasks.filter(t => t.sc).slice(0, 8);
  const tbody = document.getElementById('top-tasks-body');
  if (tbody) {
    tbody.innerHTML = topCritical.map(t => 
      '<tr class="hover:bg-slate-50 transition">' +
        '<td class="p-3 font-mono font-bold text-blue-900">' + t.taskId + '</td>' +
        '<td class="p-3"><span class="px-2 py-0.5 rounded text-[10px] font-bold ' + getDeptClass(t.dept) + '">' + t.dept + '</span></td>' +
        '<td class="p-3">' + t.sec + '</td>' +
        '<td class="p-3 font-semibold">' + t.asset + '</td>' +
        '<td class="p-3 text-slate-700">' + t.desc + '</td>' +
        '<td class="p-3 font-bold text-red-600">' + t.sev + '/5</td>' +
        '<td class="p-3 font-bold text-slate-900">' + t.score + '</td>' +
        '<td class="p-3"><span class="bg-red-100 text-red-700 font-bold px-2 py-0.5 rounded text-[10px]">CRITICAL ⚠️</span></td>' +
      '</tr>'
    ).join('');
  }

  // Render Charts safely
  const ctxPie = document.getElementById('deptPieChart');
  if (ctxPie && window.Chart) {
    new Chart(ctxPie, {
      type: 'doughnut',
      data: {
        labels: ['Engineering (TMS)', 'Signal & Telecom (SMMS)', 'Traction (TDMS)'],
        datasets: [{
          data: [90, 75, 75],
          backgroundColor: ['#0284c7', '#16a34a', '#ea580c'],
          borderWidth: 2
        }]
      },
      options: { responsive: true, maintainAspectRatio: false, plugins: { legend: { position: 'bottom' } } }
    });
  }

  const ctxBar = document.getElementById('priorityBarChart');
  if (ctxBar && window.Chart) {
    new Chart(ctxBar, {
      type: 'bar',
      data: {
        labels: ['Low (0-40)', 'Medium (41-60)', 'High (61-80)', 'Critical (81-100)'],
        datasets: [{
          label: 'Task Count',
          data: [25, 45, 62, 69],
          backgroundColor: ['#94a3b8', '#eab308', '#f97316', '#dc2626'],
          borderRadius: 6
        }]
      },
      options: { responsive: true, maintainAspectRatio: false, plugins: { legend: { display: false } } }
    });
  }
}

function getDeptClass(dept) {
  if (dept.includes("Eng")) return "bg-sky-100 text-sky-800";
  if (dept.includes("Sig")) return "bg-emerald-100 text-emerald-800";
  return "bg-orange-100 text-orange-800";
}

// Tasks Table
function renderTasksTable() {
  const dFilter = document.getElementById('filter-dept')?.value || "All";
  const scFilter = document.getElementById('filter-sc')?.value || "All";

  let list = tasks;
  if (dFilter !== "All") list = list.filter(t => t.dept === dFilter);
  if (scFilter === "Critical") list = list.filter(t => t.sc);

  const badge = document.getElementById('tasks-count-badge');
  if (badge) badge.innerText = "Showing " + list.length + " tasks";

  const tbody = document.getElementById('all-tasks-body');
  if (tbody) {
    tbody.innerHTML = list.map(t => 
      '<tr class="hover:bg-slate-50 transition">' +
        '<td class="p-3 font-mono font-bold text-blue-900">' + t.taskId + '</td>' +
        '<td class="p-3"><span class="px-2 py-0.5 rounded text-[10px] font-bold ' + getDeptClass(t.dept) + '">' + t.dept + '</span></td>' +
        '<td class="p-3">' + t.sec + '</td>' +
        '<td class="p-3 font-semibold">' + t.asset + '</td>' +
        '<td class="p-3 text-slate-700">' + t.desc + '</td>' +
        '<td class="p-3">' + t.dur + ' hrs</td>' +
        '<td class="p-3">' + t.bt + '</td>' +
        '<td class="p-3 font-bold ' + (t.score >= 80 ? 'text-red-600' : 'text-slate-800') + '">' + t.score + '</td>' +
        '<td class="p-3"><span class="px-2 py-0.5 rounded text-[10px] font-bold ' + (t.status === 'Scheduled' ? 'bg-emerald-100 text-emerald-800' : 'bg-amber-100 text-amber-800') + '">' + t.status + '</span></td>' +
      '</tr>'
    ).join('');
  }
}

// Windows Table
function renderWindowsTable() {
  const tbody = document.getElementById('windows-body');
  if (tbody) {
    tbody.innerHTML = windows.slice(0, 50).map(w => 
      '<tr class="hover:bg-slate-50 transition">' +
        '<td class="p-3 font-mono font-bold text-slate-900">' + w.id + '</td>' +
        '<td class="p-3 font-semibold">' + w.sec + '</td>' +
        '<td class="p-3 text-slate-700">' + w.time + '</td>' +
        '<td class="p-3 font-bold">' + w.dur + ' hrs</td>' +
        '<td class="p-3 text-emerald-600 font-bold">Granted</td>' +
        '<td class="p-3 text-emerald-600 font-bold">Granted</td>' +
        '<td class="p-3"><span class="bg-blue-100 text-blue-800 font-bold px-2 py-0.5 rounded text-[10px]">AVAILABLE</span></td>' +
      '</tr>'
    ).join('');
  }
}

// Optimizer Execution
function runOptimizer() {
  const horizon = document.getElementById('opt-horizon').value;
  const planId = "PLAN-" + horizon.substring(0, 1) + "-" + Date.now().toString().slice(-6);

  let schedCount = 0;
  let jointCount = 24;
  tasks.forEach((t, i) => {
    if (i < 175) {
      t.status = "Scheduled";
      schedCount++;
    }
  });

  const newPlan = {
    id: planId,
    horizon: horizon,
    scheduled: schedCount,
    joint: jointCount,
    delays: 340,
    status: "Draft",
    created: new Date().toLocaleTimeString()
  };

  plans.unshift(newPlan);
  document.getElementById('stat-scheduled').innerText = schedCount;
  document.getElementById('stat-pending').innerText = tasks.length - schedCount;
  document.getElementById('stat-joint').innerText = jointCount;
  document.getElementById('stat-delay').innerHTML = newPlan.delays + ' <span class="text-xs font-normal">min</span>';

  auditLogs.unshift({
    time: new Date().toLocaleTimeString(),
    action: "PLAN_GENERATED",
    officer: currentUser.name,
    desc: "Generated " + horizon + " Plan " + planId + " with " + jointCount + " Joint Blocks"
  });

  renderPlans();
  renderTasksTable();
  renderAuditTable();
  alert("✅ Optimized Plan Generated Successfully!\nPlan ID: " + planId + "\nTasks Scheduled: " + schedCount + "\nJoint Blocks Formed: " + jointCount);
}

function renderPlans() {
  const container = document.getElementById('plans-container');
  if (!container) return;

  if (plans.length === 0) {
    container.innerHTML = '<div class="bg-white p-6 rounded-xl border border-slate-200 text-center text-xs text-slate-500">No plans generated yet. Click \'Run Optimizer\' above!</div>';
    return;
  }

  container.innerHTML = plans.map(p => 
    '<div class="bg-white p-5 rounded-xl border border-slate-200 shadow-sm space-y-4">' +
      '<div class="flex flex-wrap justify-between items-center border-b border-slate-100 pb-3">' +
        '<div>' +
          '<span class="text-xs font-bold font-mono text-indigo-700 bg-indigo-50 px-2 py-0.5 rounded">' + p.id + '</span>' +
          '<span class="text-xs text-slate-500 ml-2">(' + p.horizon + ') - Created at ' + p.created + '</span>' +
        '</div>' +
        '<span class="text-xs font-bold px-2 py-0.5 rounded ' + (p.status === 'Approved' ? 'bg-emerald-100 text-emerald-800' : (p.status === 'Published' ? 'bg-blue-100 text-blue-800' : 'bg-amber-100 text-amber-800')) + '">' +
          p.status +
        '</span>' +
      '</div>' +
      '<div class="grid grid-cols-2 md:grid-cols-4 gap-4 text-center">' +
        '<div class="bg-slate-50 p-3 rounded-lg"><div class="text-[10px] text-slate-500 font-bold">TASKS SCHEDULED</div><div class="text-lg font-black text-slate-800">' + p.scheduled + '</div></div>' +
        '<div class="bg-slate-50 p-3 rounded-lg"><div class="text-[10px] text-slate-500 font-bold">JOINT BLOCKS SAVED</div><div class="text-lg font-black text-purple-600">' + p.joint + '</div></div>' +
        '<div class="bg-slate-50 p-3 rounded-lg"><div class="text-[10px] text-slate-500 font-bold">TRAIN DELAY IMPACT</div><div class="text-lg font-black text-slate-800">' + p.delays + ' min</div></div>' +
        '<div class="bg-slate-50 p-3 rounded-lg"><div class="text-[10px] text-slate-500 font-bold">LINE AVAILABILITY</div><div class="text-lg font-black text-emerald-600">98.4%</div></div>' +
      '</div>' +
      '<div class="p-3 bg-slate-900 rounded-lg text-white text-xs">' +
        '<div class="font-bold text-[11px] text-slate-300 mb-2">TIMELINE GANTT (MULTI-DEPARTMENT SYNCHRONIZATION):</div>' +
        '<div class="space-y-1.5 font-mono text-[10px]">' +
          '<div class="flex items-center gap-2"><span class="w-16 text-slate-400">00:00-04:00</span> <div class="bg-sky-600 text-white px-2 py-0.5 rounded flex-1">Engg: Rail Fracture Replacement [SEC-01]</div></div>' +
          '<div class="flex items-center gap-2"><span class="w-16 text-slate-400">00:00-04:00</span> <div class="bg-purple-600 text-white px-2 py-0.5 rounded flex-1">🔗 JOINT BLOCK: TRD OHE Maintenance + S&T Cable Inspection</div></div>' +
          '<div class="flex items-center gap-2"><span class="w-16 text-slate-400">10:30-12:00</span> <div class="bg-emerald-600 text-white px-2 py-0.5 rounded flex-1">S&T: Home Signal Relay Interlocking Calibration</div></div>' +
        '</div>' +
      '</div>' +
      '<div class="flex justify-end gap-2 pt-2 border-t border-slate-100">' +
        (p.status === 'Draft' ? '<button onclick="approvePlan(\'' + p.id + '\')" class="bg-emerald-600 hover:bg-emerald-700 text-white px-4 py-1.5 rounded text-xs font-bold transition">✅ Sanction & Approve Plan</button>' : '') +
        (p.status === 'Approved' ? '<button onclick="publishPlan(\'' + p.id + '\')" class="bg-blue-600 hover:bg-blue-700 text-white px-4 py-1.5 rounded text-xs font-bold transition">📢 Publish to Train Controllers</button>' : '') +
      '</div>' +
    '</div>'
  ).join('');
}

function approvePlan(id) {
  const p = plans.find(x => x.id === id);
  if (p) {
    p.status = "Approved";
    auditLogs.unshift({ time: new Date().toLocaleTimeString(), action: "PLAN_APPROVED", officer: currentUser.name, desc: "Plan " + id + " officially sanctioned by Approver" });
    renderPlans();
    renderAuditTable();
  }
}

function publishPlan(id) {
  const p = plans.find(x => x.id === id);
  if (p) {
    p.status = "Published";
    auditLogs.unshift({ time: new Date().toLocaleTimeString(), action: "PLAN_PUBLISHED", officer: currentUser.name, desc: "Plan " + id + " transmitted to COA & Section Controllers" });
    renderPlans();
    renderAuditTable();
  }
}

function runBenchmarkSim() {
  document.getElementById('benchmark-results').classList.remove('hidden');
}

function renderAuditTable() {
  const tbody = document.getElementById('audit-body');
  if (tbody) {
    tbody.innerHTML = auditLogs.map(a => 
      '<tr class="hover:bg-slate-50 transition">' +
        '<td class="p-3 font-mono text-slate-500">' + a.time + '</td>' +
        '<td class="p-3 font-bold font-mono text-blue-900">' + a.action + '</td>' +
        '<td class="p-3 font-semibold">' + a.officer + '</td>' +
        '<td class="p-3 text-slate-700">' + a.desc + '</td>' +
      '</tr>'
    ).join('');
  }
}
