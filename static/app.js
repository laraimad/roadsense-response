const state = {
  incidents: [], selectedId: null, status: "all", severity: "all", search: "", sort: "priority",
};

const statusLabels = {
  new: "New",
  verified: "Verified",
  scheduled: "Scheduled",
  in_repair: "In repair",
  resolved: "Resolved",
  dismissed: "Dismissed",
};

const escapeHtml = (value = "") => String(value)
  .replaceAll("&", "&amp;")
  .replaceAll("<", "&lt;")
  .replaceAll(">", "&gt;")
  .replaceAll('"', "&quot;")
  .replaceAll("'", "&#039;");

async function api(url, options) {
  const response = await fetch(url, options);
  const payload = await response.json();
  if (!response.ok) throw new Error(payload.error || "Request failed");
  return payload;
}

function filteredIncidents() {
  const query = state.search.trim().toLowerCase();
  const incidents = state.incidents.filter((incident) => {
    const statusMatch = state.status === "all" || incident.status === state.status;
    const severityMatch = state.severity === "all" || incident.severity_level === state.severity;
    const searchValues = [incident.id, incident.road, incident.segment, incident.assignee, incident.notes]
      .join(" ").toLowerCase();
    return statusMatch && severityMatch && (!query || searchValues.includes(query));
  });
  return incidents.sort((a, b) => {
    if (state.sort === "newest") return new Date(b.captured_at) - new Date(a.captured_at);
    if (state.sort === "updated") {
      return new Date(b.updated_at || b.captured_at) - new Date(a.updated_at || a.captured_at);
    }
    return b.severity_score - a.severity_score;
  });
}

function formatDate(value) {
  return new Intl.DateTimeFormat("en-MY", {
    day: "numeric", month: "short", hour: "2-digit", minute: "2-digit",
  }).format(new Date(value));
}

function showToast(message, error = false) {
  const toast = document.querySelector("#toast");
  toast.textContent = message;
  toast.className = `toast visible${error ? " error" : ""}`;
  window.setTimeout(() => { toast.className = "toast"; }, 2600);
}

function renderSummary(summary) {
  document.querySelector("#stat-active").textContent = summary.active;
  document.querySelector("#stat-urgent").textContent = summary.urgent;
  document.querySelector("#stat-resolved").textContent = summary.resolved;
  document.querySelector("#stat-average").textContent = summary.average_severity;
}

function markerPosition(incident) {
  const latitudes = state.incidents.map((item) => item.latitude);
  const longitudes = state.incidents.map((item) => item.longitude);
  const minLat = Math.min(...latitudes), maxLat = Math.max(...latitudes);
  const minLon = Math.min(...longitudes), maxLon = Math.max(...longitudes);
  const x = 12 + ((incident.longitude - minLon) / (maxLon - minLon || 1)) * 76;
  const y = 84 - ((incident.latitude - minLat) / (maxLat - minLat || 1)) * 68;
  return { x, y };
}

function renderMap() {
  const markers = document.querySelector("#map-markers");
  markers.innerHTML = filteredIncidents().map((incident) => {
    const { x, y } = markerPosition(incident);
    const selected = incident.id === state.selectedId ? " selected" : "";
    return `<button class="map-marker ${incident.severity_level}${selected}" style="left:${x}%;top:${y}%" data-id="${incident.id}" aria-label="${incident.id}, ${incident.road}"><span>${incident.severity_score}</span></button>`;
  }).join("");
  markers.querySelectorAll("button").forEach((button) => button.addEventListener("click", () => selectIncident(button.dataset.id)));
}

function renderList() {
  const incidents = filteredIncidents();
  document.querySelector("#queue-count").textContent = `${incidents.length} incident${incidents.length === 1 ? "" : "s"}`;
  const list = document.querySelector("#incident-list");
  list.innerHTML = incidents.length ? incidents.map((incident) => `
    <button class="incident-row${incident.id === state.selectedId ? " active" : ""}" data-id="${incident.id}">
      <span class="severity-dot ${incident.severity_level}"></span>
      <span class="incident-main"><strong>${incident.id}</strong><small>${escapeHtml(incident.road)} / ${escapeHtml(incident.segment)}</small></span>
      <span class="incident-score"><strong>${incident.severity_score}</strong><small>${incident.severity_level}</small></span>
      <span class="status-pill ${incident.status}">${statusLabels[incident.status]}</span>
    </button>`).join("") : `<div class="list-empty">No incidents match these filters.</div>`;
  list.querySelectorAll("button").forEach((button) => button.addEventListener("click", () => selectIncident(button.dataset.id)));
}

function evidenceBar(label, value) {
  return `<div class="evidence-row"><div><span>${label}</span><strong>${value}%</strong></div><div class="bar"><i style="width:${value}%"></i></div></div>`;
}

function renderHistory(history = []) {
  const items = [...history].reverse();
  if (!items.length) return `<p class="history-empty">No workflow updates yet.</p>`;
  return `<ol class="history-list">${items.map((entry) => `
    <li><i></i><div><strong>${escapeHtml(entry.summary)}</strong><span>${formatDate(entry.timestamp)}${entry.assignee ? ` / ${escapeHtml(entry.assignee)}` : ""}</span></div></li>
  `).join("")}</ol>`;
}

function renderDetail() {
  const incident = state.incidents.find((item) => item.id === state.selectedId);
  const detail = document.querySelector("#incident-detail");
  if (!incident) return;
  detail.innerHTML = `
    <div class="detail-image"><img src="/static/images/${encodeURIComponent(incident.image)}" alt="Road evidence for ${incident.id}"><span class="image-badge">Vehicle capture</span></div>
    <div class="detail-content">
      <div class="detail-title-row"><div><span>${incident.id}</span><h3>${escapeHtml(incident.road)}</h3><p>${escapeHtml(incident.segment)} / ${formatDate(incident.captured_at)}</p></div><div class="score-ring ${incident.severity_level}"><strong>${incident.severity_score}</strong><span>severity</span></div></div>
      <div class="decision-callout"><span>Recommended action</span><p>${escapeHtml(incident.recommended_action)}</p></div>
      <section class="evidence-section"><div class="subheading"><h4>Why this priority?</h4><span>${incident.repeat_count} detection${incident.repeat_count === 1 ? "" : "s"}</span></div>
        ${evidenceBar("Visual confidence", incident.evidence.visual)}
        ${evidenceBar("Impact strength", incident.evidence.impact)}
        ${evidenceBar("Route recurrence", incident.evidence.recurrence)}
        <div class="sensor-grid"><div><span>Model confidence</span><strong>${Math.round(incident.confidence * 100)}%</strong></div><div><span>IMU delta</span><strong>${incident.imu_delta} m/s2</strong></div><div><span>Vehicle speed</span><strong>${incident.speed_kmh} km/h</strong></div></div>
        <p class="model-disclaimer">Experimental priority aid. Field verification is required before safety or repair decisions.</p>
      </section>
      <form id="workflow-form" class="workflow-form">
        <div class="subheading"><h4>Repair workflow</h4><span>Saved locally</span></div>
        <div class="form-grid"><label>Status<select name="status">${Object.entries(statusLabels).map(([value, label]) => `<option value="${value}"${incident.status === value ? " selected" : ""}>${label}</option>`).join("")}</select></label><label>Assigned team<input name="assignee" maxlength="120" value="${escapeHtml(incident.assignee)}" placeholder="Add a team or reviewer"></label></div>
        <label>Operator notes<textarea name="notes" maxlength="1000" rows="4">${escapeHtml(incident.notes)}</textarea></label>
        <button class="button primary" type="submit">Save workflow update</button>
      </form>
      <section class="history-section"><div class="subheading"><h4>Activity history</h4><span>Latest first</span></div>${renderHistory(incident.history)}</section>
    </div>`;
  detail.querySelector("#workflow-form").addEventListener("submit", saveWorkflow);
}

function selectIncident(id) {
  state.selectedId = id;
  renderMap(); renderList(); renderDetail();
  if (window.innerWidth < 980) document.querySelector("#incident-detail").scrollIntoView({ behavior: "smooth", block: "start" });
}

function refreshTriage() {
  const visible = filteredIncidents();
  if (!visible.some((incident) => incident.id === state.selectedId)) {
    state.selectedId = visible[0]?.id || null;
  }
  renderMap(); renderList();
  if (state.selectedId) {
    renderDetail();
  } else {
    document.querySelector("#incident-detail").innerHTML = `<div class="empty-state"><span>0</span><h3>No matching incidents</h3><p>Clear or adjust the filters to return to the repair queue.</p></div>`;
  }
}

async function saveWorkflow(event) {
  event.preventDefault();
  const button = event.currentTarget.querySelector("button[type=submit]");
  button.disabled = true; button.textContent = "Saving...";
  const data = new FormData(event.currentTarget);
  try {
    const updated = await api(`/api/incidents/${state.selectedId}`, {
      method: "PATCH", headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ status: data.get("status"), assignee: data.get("assignee"), notes: data.get("notes") }),
    });
    state.incidents = state.incidents.map((item) => item.id === updated.id ? updated : item);
    renderMap(); renderList(); renderDetail();
    renderSummary(await api("/api/summary"));
    showToast(`${updated.id} workflow updated`);
  } catch (error) { showToast(error.message, true); }
}

async function load() {
  try {
    const [incidents, summary] = await Promise.all([api("/api/incidents"), api("/api/summary")]);
    state.incidents = incidents;
    renderSummary(summary);
    state.selectedId = [...incidents].sort((a, b) => b.severity_score - a.severity_score)[0]?.id || null;
    refreshTriage();
  } catch (error) { showToast(error.message, true); }
}

document.querySelectorAll(".nav-link").forEach((button) => button.addEventListener("click", () => {
  document.querySelectorAll(".nav-link").forEach((item) => item.classList.toggle("active", item === button));
  document.querySelectorAll(".view").forEach((view) => view.classList.toggle("active", view.id === `${button.dataset.view}-view`));
}));
document.querySelector("#search-filter").addEventListener("input", (event) => { state.search = event.target.value; refreshTriage(); });
document.querySelector("#status-filter").addEventListener("change", (event) => { state.status = event.target.value; refreshTriage(); });
document.querySelector("#severity-filter").addEventListener("change", (event) => { state.severity = event.target.value; refreshTriage(); });
document.querySelector("#sort-filter").addEventListener("change", (event) => { state.sort = event.target.value; refreshTriage(); });
document.querySelector("#clear-filters").addEventListener("click", () => {
  state.search = ""; state.status = "all"; state.severity = "all"; state.sort = "priority";
  document.querySelector("#search-filter").value = "";
  document.querySelector("#status-filter").value = "all";
  document.querySelector("#severity-filter").value = "all";
  document.querySelector("#sort-filter").value = "priority";
  refreshTriage();
});
document.querySelector("#reset-demo").addEventListener("click", async () => {
  if (!window.confirm("Reset all workflow changes to the original demo data?")) return;
  try { await api("/api/reset", { method: "POST" }); await load(); showToast("Demo data reset"); } catch (error) { showToast(error.message, true); }
});

load();
