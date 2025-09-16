(() => {
  const baseApiUrl = (window.APP_CONFIG && window.APP_CONFIG.apiUrl) || "/devices";
  const eventName = (window.APP_CONFIG && window.APP_CONFIG.eventName) || "device_status";

  // UI elements
  const tbody = document.getElementById("devicesTbody");
  const loading = document.getElementById("loadingState");
  const empty = document.getElementById("emptyState");
  const errorState = document.getElementById("errorState");
  const errorText = document.getElementById("errorText");
  const lastUpdated = document.getElementById("lastUpdated");
  const deviceCount = document.getElementById("deviceCount");
  const searchInput = document.getElementById("searchInput");
  const statusFilter = document.getElementById("statusFilter");
  const devicesCountInput = document.getElementById("devicesCountInput");
  const clearBtn = document.getElementById("clearBtn");
  const connBadge = document.getElementById("connBadge");

  let data = [];
  let sortKey = "id";
  let sortAsc = true;

  function pad2(n) { return String(n).padStart(2, "0"); }
  function formatTimestamp(d) {
    return `${d.getFullYear()}-${pad2(d.getMonth() + 1)}-${pad2(d.getDate())} ${pad2(d.getHours())}:${pad2(d.getMinutes())}:${pad2(d.getSeconds())}`;
  }

  function setView(state) {
    // states: loading | ready | empty | error
    loading.classList.toggle("d-none", state !== "loading");
    empty.classList.toggle("d-none", state !== "empty");
    errorState.classList.toggle("d-none", state !== "error");
    document.querySelector(".table").classList.toggle("d-none", state !== "ready");
  }

  function clampN(n) {
    n = Number.isFinite(n) ? n : 10;
    return Math.max(1, Math.min(n, 500));
  }

  function buildApiUrl() {
    const n = clampN(parseInt(devicesCountInput.value, 10));
    const url = new URL(baseApiUrl, window.location.origin);
    url.searchParams.set("n", String(n));
    return url.toString();
  }

  function fmtStatus(s) {
    const good = String(s).toLowerCase() === "up";
    return `<span class="badge ${good ? "bg-success" : "bg-danger"}">${s}</span>`;
  }

  function renderRows(rows) {
    tbody.innerHTML = rows.map(d => `
      <tr>
        <td class="text-muted">${d.id}</td>
        <td class="fw-medium">${d.name}</td>
        <td><code>${d.ip_address}</code></td>
        <td>${fmtStatus(d.status)}</td>
      </tr>
    `).join("");
    deviceCount.textContent = rows.length;
  }

  function applyFilters() {
    const q = searchInput.value.trim().toLowerCase();
    const statusVal = statusFilter.value;

    let rows = data.filter(d => {
      const matchesText =
        !q ||
        String(d.id).includes(q) ||
        (d.name || "").toLowerCase().includes(q) ||
        (d.ip_address || "").toLowerCase().includes(q) ||
        String(d.status || "").toLowerCase().includes(q);

    const matchesStatus =
      !statusVal || String(d.status).toLowerCase() === statusVal.toLowerCase();

    return matchesText && matchesStatus;
    });

    rows.sort((a, b) => {
      const va = a[sortKey];
      const vb = b[sortKey];
      if (sortKey === "id") return sortAsc ? va - vb : vb - va;
      const ra = String(va).toLowerCase(), rb = String(vb).toLowerCase();
      if (ra < rb) return sortAsc ? -1 : 1;
      if (ra > rb) return sortAsc ? 1 : -1;
      return a.id - b.id; // tie-breaker
    });

    renderRows(rows);
    setView(rows.length ? "ready" : "empty");
  }

  async function initialFetch() {
    try {
      setView("loading");
      const res = await fetch(buildApiUrl(), { headers: { "Accept": "application/json" } });
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      const body = await res.json();
      data = Array.isArray(body) ? body : [];
      lastUpdated.textContent = formatTimestamp(new Date()); // fixed timestamp at arrival
      applyFilters();
    } catch (err) {
      console.error(err);
      errorText.textContent = `Initial fetch failed: ${err.message || err}`;
      setView("error");
    }
  }

  // Sorting
  document.querySelectorAll("th.sortable").forEach(th => {
    th.style.cursor = "pointer";
    th.addEventListener("click", () => {
      const key = th.dataset.key;
      if (sortKey === key) sortAsc = !sortAsc; else { sortKey = key; sortAsc = true; }
      applyFilters();
    });
  });

  // Search/filter
  searchInput.addEventListener("input", applyFilters);
  statusFilter.addEventListener("change", applyFilters);

  // Clear table
  clearBtn.addEventListener("click", () => {
    data = [];
    applyFilters();
  });

  // SOCKET.IO — subscribe per client
  function subscribe(socket) {
    const n = clampN(parseInt(devicesCountInput.value, 10));
    socket.emit("subscribe_devices", { n });
  }

  const socket = io("/", { transports: ["websocket", "polling"] });
  socket.on("connect", () => {
    connBadge.textContent = "Connected";
    connBadge.className = "badge bg-success";
    subscribe(socket); // send initial N
  });
  socket.on("disconnect", () => {
    connBadge.textContent = "Disconnected";
    connBadge.className = "badge bg-secondary";
  });
  socket.on("connect_error", (e) => {
    connBadge.textContent = "Error";
    connBadge.className = "badge bg-danger";
    errorText.textContent = `Socket error: ${e.message || e}`;
    setView("error");
  });

  // Accept full array or single device updates
  socket.on(eventName, payload => {
    if (Array.isArray(payload)) {
      data = payload;
    } else if (payload && typeof payload === "object" && "id" in payload) {
      const idx = data.findIndex(d => d.id === payload.id);
      if (idx >= 0) data[idx] = { ...data[idx], ...payload };
      else data.push(payload);
    }
    lastUpdated.textContent = formatTimestamp(new Date()); // fixed timestamp at each push
    applyFilters();
  });

  // Reselect N => re-subscribe and reseed
  devicesCountInput.addEventListener("change", () => {
    devicesCountInput.value = clampN(parseInt(devicesCountInput.value, 10));
    subscribe(socket);
    initialFetch(); // reseed immediately; socket will keep pushing every 5s
  });

  // Seed table once, then rely on 5s server pushes
  devicesCountInput.value = clampN(parseInt(devicesCountInput.value, 10));
  initialFetch();
})();
