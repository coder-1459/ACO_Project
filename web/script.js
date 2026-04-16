const COLORS = [
  "#2563eb",
  "#dc2626",
  "#16a34a",
  "#ca8a04",
  "#9333ea",
  "#0891b2",
  "#be123c",
  "#4f46e5",
  "#0f766e",
  "#a16207",
];

async function loadData() {
  const response = await fetch("../results/results.json");
  if (!response.ok) {
    throw new Error("results/results.json not found. Run: python run_cli.py");
  }
  return response.json();
}

function setMetrics(metrics) {
  document.getElementById("baselineMakespan").textContent = metrics.baselineMakespan.toFixed(2);
  document.getElementById("bestMakespan").textContent = metrics.bestMakespan.toFixed(2);
  document.getElementById("improvement").textContent = `${metrics.improvementPercent.toFixed(2)}%`;
  document.getElementById("idleChange").textContent = `${metrics.baselineIdle.toFixed(2)} -> ${metrics.bestIdle.toFixed(2)}`;
}

function renderSequence(sequence) {
  document.getElementById("bestSequence").textContent = sequence.join(" -> ");
}

function renderDatasetTable(rows) {
  const tableHead = document.querySelector("#datasetTable thead");
  const tableBody = document.querySelector("#datasetTable tbody");
  tableHead.innerHTML = "";
  tableBody.innerHTML = "";
  if (!rows.length) return;

  const columns = Object.keys(rows[0]);
  const headRow = document.createElement("tr");
  columns.forEach((col) => {
    const th = document.createElement("th");
    th.textContent = col;
    headRow.appendChild(th);
  });
  tableHead.appendChild(headRow);

  rows.forEach((row) => {
    const tr = document.createElement("tr");
    columns.forEach((col) => {
      const td = document.createElement("td");
      td.textContent = row[col];
      tr.appendChild(td);
    });
    tableBody.appendChild(tr);
  });
}

function renderConvergenceChart(convergence) {
  const ctx = document.getElementById("convergenceChart");
  new Chart(ctx, {
    type: "line",
    data: {
      labels: convergence.map((_, i) => i + 1),
      datasets: [
        {
          label: "Best Makespan",
          data: convergence,
          borderColor: "#0f766e",
          borderWidth: 2,
          tension: 0.2,
          fill: false,
        },
      ],
    },
    options: {
      responsive: true,
      scales: {
        x: { title: { display: true, text: "Iteration" } },
        y: { title: { display: true, text: "Makespan" } },
      },
    },
  });
}

function renderUtilizationChart(machineUtilization) {
  const ctx = document.getElementById("utilizationChart");
  new Chart(ctx, {
    type: "bar",
    data: {
      labels: machineUtilization.map((x) => x.machine),
      datasets: [
        {
          label: "Utilization (%)",
          data: machineUtilization.map((x) => x.utilizationPercent),
          backgroundColor: "#2563eb",
        },
      ],
    },
    options: {
      responsive: true,
      scales: {
        y: { beginAtZero: true, max: 100, title: { display: true, text: "Percent" } },
      },
    },
  });
}

function renderGantt(ganttRows, machineCols) {
  const container = document.getElementById("ganttContainer");
  container.innerHTML = "";
  const maxEnd = Math.max(...ganttRows.map((r) => r.end));

  const rowsByMachine = {};
  machineCols.forEach((m) => {
    rowsByMachine[m] = ganttRows.filter((r) => r.machine === m);
  });

  machineCols.forEach((machine, machineIdx) => {
    const row = document.createElement("div");
    row.className = "gantt-row";

    const label = document.createElement("div");
    label.className = "gantt-label";
    label.textContent = machine;

    const track = document.createElement("div");
    track.className = "gantt-track";

    rowsByMachine[machine].forEach((task, idx) => {
      const bar = document.createElement("div");
      bar.className = "gantt-bar";
      bar.style.left = `${(task.start / maxEnd) * 100}%`;
      bar.style.width = `${(task.duration / maxEnd) * 100}%`;
      bar.style.backgroundColor = COLORS[(idx + machineIdx) % COLORS.length];
      bar.title = `${task.jobId}: ${task.start.toFixed(1)} - ${task.end.toFixed(1)}`;
      bar.textContent = task.jobId;
      track.appendChild(bar);
    });

    row.appendChild(label);
    row.appendChild(track);
    container.appendChild(row);
  });
}

async function init() {
  try {
    const data = await loadData();
    setMetrics(data.metrics);
    renderSequence(data.bestSequence);
    renderDatasetTable(data.dataset.rows);
    renderConvergenceChart(data.convergence);
    renderUtilizationChart(data.machineUtilization);
    renderGantt(data.gantt, data.dataset.machineColumns);
  } catch (error) {
    const container = document.querySelector("main");
    const errorCard = document.createElement("section");
    errorCard.className = "card";
    errorCard.innerHTML = `<h2>Error</h2><p>${error.message}</p>`;
    container.prepend(errorCard);
  }
}

init();
