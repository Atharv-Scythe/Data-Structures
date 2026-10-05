/**
 * Smart EV Charging Queue & Route Optimizer
 * Main Integration & Application Orchestrator
 */

let refreshTimer = null;
let graphViz = null;
let heapViz = null;
let queueViz = null;
let dequeViz = null;
let simController = null;

let currentGraphData = null;
let currentActiveRoute = null;
let currentTheme = "dark";
let lastSnapshotData = null;

// =========================================================
// DOM HELPERS
// =========================================================

function element(id) {
    return document.getElementById(id);
}

function setConnection(online, message) {
    const dot = element("connectionDot");
    const text = element("connectionText");
    if (!dot || !text) return;

    dot.classList.remove("online", "offline");
    dot.classList.add(online ? "online" : "offline");
    text.textContent = message;
}

function setLastAction(message) {
    const el = element("lastAction");
    if (el) {
        el.textContent = message;
        const parent = el.closest(".status-inner");
        if (parent) {
            parent.style.transform = "scale(1.02)";
            parent.style.borderColor = "var(--accent)";
            setTimeout(() => {
                parent.style.transform = "scale(1)";
                parent.style.borderColor = "var(--panel-border)";
            }, 300);
        }
    }
}

function escapeHTML(value) {
    return String(value)
        .replaceAll("&", "&amp;")
        .replaceAll("<", "&lt;")
        .replaceAll(">", "&gt;")
        .replaceAll('"', "&quot;")
        .replaceAll("'", "&#039;");
}

// =========================================================
// RENDERERS
// =========================================================

function renderStatus(status) {
    const waiting = (status.waiting_normal || 0) + (status.waiting_priority || 0) + (status.waiting_special || 0);

    if (element("evCount")) element("evCount").textContent = status.ev_count || 0;
    if (element("waitingCount")) element("waitingCount").textContent = waiting;
    if (element("chargingCount")) element("chargingCount").textContent = status.charging || 0;
    if (element("completedCount")) element("completedCount").textContent = status.completed || 0;
    if (element("stationCount")) element("stationCount").textContent = status.station_count || 0;
    if (element("eventCount")) element("eventCount").textContent = status.event_count || 0;
}

function renderCharging(items) {
    const containers = [element("chargingList"), element("chargingListOverview")].filter(Boolean);
    if (!containers.length) return;

    if (!items || !items.length) {
        containers.forEach(c => {
            c.className = "queue-container empty-state";
            c.textContent = "No EVs charging";
        });
        return;
    }

    const html = items.map(ev => {
        const battery = Math.max(0, Math.min(100, Number(ev.battery_level)));
        return `
            <div class="charging-item">
                <div class="charging-top">
                    <span class="charging-id">🚗 ${escapeHTML(ev.ev_id)}</span>
                    <span class="charging-status">CHARGING NOW</span>
                </div>
                <div class="ev-card-meta">
                    <span>⚡ Station: ${escapeHTML(ev.station_id)}</span>
                    <span>Battery: ${battery}%</span>
                </div>
                <div class="battery-bar">
                    <div class="battery-fill" style="width: ${battery}%"></div>
                </div>
            </div>
        `;
    }).join("");

    containers.forEach(c => {
        c.className = "queue-container";
        c.innerHTML = html;
    });
}

function renderStations(stations) {
    const container = element("stationList");
    if (!container) return;

    if (!stations || !stations.length) {
        container.className = "station-list empty-state";
        container.textContent = "No charging stations";
        return;
    }

    container.className = "station-list";
    container.innerHTML = stations.map(station => `
        <div class="station-item">
            <div>
                <div class="station-name">⚡ Station ${escapeHTML(station.station_id)}</div>
                <div class="station-location">Location: Node ${escapeHTML(station.location)}</div>
            </div>
            <div class="station-capacity">
                <div><strong>${station.available_slots}</strong> / ${station.charging_slots} slots</div>
                <div>Available</div>
            </div>
        </div>
    `).join("");
}

function renderEvents(events) {
    const container = element("eventList");
    if (!container) return;

    if (element("eventBadge")) element("eventBadge").textContent = events.length;

    if (!events || !events.length) {
        container.className = "event-list empty-state";
        container.textContent = "No events yet";
        return;
    }

    container.className = "event-list";
    container.innerHTML = [...events].reverse().map(event => {
        const evText = event.ev_id ? `EV ${event.ev_id}` : "System";
        const stationText = event.station_id ? ` • Station ${event.station_id}` : "";

        return `
            <div class="event-row">
                <div class="event-step">#${event.step}</div>
                <div>
                    <div class="event-message">${escapeHTML(event.message)}</div>
                    <div class="event-meta">${escapeHTML(evText)}${escapeHTML(stationText)}</div>
                </div>
            </div>
        `;
    }).join("");
}

// =========================================================
// DASHBOARD REFRESH
// =========================================================

async function refreshDashboard() {
    try {
        const status = await getStatus();
        const snapshot = await getSnapshot();
        const graphData = await getGraph();

        currentGraphData = graphData;
        lastSnapshotData = snapshot;

        renderStatus(status);
        
        if (queueViz) queueViz.render(snapshot.queues.normal);
        if (heapViz) heapViz.render(snapshot.queues.priority);
        if (dequeViz) dequeViz.render(snapshot.queues.special);
        
        renderCharging(snapshot.charging);
        renderStations(snapshot.stations);
        renderEvents(snapshot.events);

        if (graphViz && graphData) {
            graphViz.render(graphData, snapshot.stations, currentActiveRoute);
        }

        setConnection(true, "API Connected");

    } catch (error) {
        console.error(error);
        setConnection(false, "API Offline");
    }
}

// =========================================================
// EVENT HANDLERS
// =========================================================

async function handleAddEV() {
    const button = element("addEvButton");
    const evId = element("evId").value.trim();
    const batteryLevel = Number(element("batteryLevel").value);
    const location = element("location").value;
    const targetQueue = element("queueTypeSelect").value;

    if (!evId) {
        setLastAction("Enter an EV ID");
        return;
    }

    button.disabled = true;

    try {
        let result;
        let dsUsed = "SIMPLE QUEUE";
        let opType = "enqueue()";

        if (targetQueue === "auto") {
            result = await addEVAutomatically({ evId, batteryLevel, location });
            dsUsed = result.queue === "priority" ? "MIN-HEAP" : "SIMPLE QUEUE";
            opType = result.queue === "priority" ? "insert(priority)" : "enqueue(FIFO)";
        } else if (targetQueue === "priority") {
            result = await addEV({ evId, batteryLevel, location, priority: 5, type: "priority" });
            dsUsed = "MIN-HEAP";
            opType = "insert(priority=5)";
        } else if (targetQueue === "special") {
            result = await addEV({ evId, batteryLevel, location, type: "special" });
            dsUsed = "DEQUE";
            opType = "add_rear()";
        } else if (targetQueue === "special_front") {
            result = await addEV({ evId, batteryLevel, location, type: "special" });
            dsUsed = "DEQUE";
            opType = "add_front()";
        } else {
            result = await addEV({ evId, batteryLevel, location, type: "normal" });
            dsUsed = "SIMPLE QUEUE";
            opType = "enqueue()";
        }

        setLastAction(`${evId} → ${result.queue.toUpperCase()}`);

        simController.logDSTrace({
            step: element("eventCount") ? element("eventCount").textContent : 1,
            ds: dsUsed,
            op: opType,
            complexity: dsUsed === "MIN-HEAP" ? "O(log n)" : "O(1)",
            target: evId,
            details: `Enqueued ${evId} at Node ${location}`
        });

        await refreshDashboard();

    } catch (error) {
        setLastAction(error.message);
    } finally {
        button.disabled = false;
    }
}

async function handleProcess() {
    const button = element("processButton");
    button.disabled = true;

    try {
        const result = await processNextEV();

        setLastAction(`${result.ev.ev_id} → Station ${result.station.station_id} (${result.distance} units)`);

        currentActiveRoute = {
            start: result.ev.location,
            destination: result.station.location,
            distance: result.distance,
            path: result.path
        };

        simController.logDSTrace({
            step: element("eventCount") ? element("eventCount").textContent : 1,
            ds: "GRAPH + DIJKSTRA",
            op: "find_nearest_station() & extract_min()",
            complexity: "O((V + E) log V)",
            target: result.ev.ev_id,
            details: `Calculated path [${result.path.join(" ➔ ")}] to Station ${result.station.station_id}`
        });

        await refreshDashboard();

        // Animate EV moving along Dijkstra route on the Graph visualizer!
        if (graphViz && result.path) {
            await graphViz.animateEVAlongPath(result.path);
        }

    } catch (error) {
        setLastAction(error.message);
    } finally {
        button.disabled = false;
    }
}

async function handleFindRoute() {
    const start = element("startLocation").value;
    const dest = element("destLocation").value;

    try {
        const routeData = await getRoute(start, dest);
        currentActiveRoute = routeData;
        setLastAction(`Route ${start} → ${dest}: ${routeData.distance} units`);

        simController.logDSTrace({
            step: "Route",
            ds: "GRAPH + DIJKSTRA",
            op: "calculate_route()",
            complexity: "O((V + E) log V)",
            target: `${start} ➔ ${dest}`,
            details: `Shortest path: [${routeData.path.join(" ➔ ")}] (${routeData.distance} units)`
        });

        await refreshDashboard();

        if (graphViz && routeData.path) {
            await graphViz.animateEVAlongPath(routeData.path);
        }
    } catch (err) {
        setLastAction(err.message);
    }
}

async function handleFindNearest() {
    const start = element("startLocation").value;

    try {
        const result = await getNearestStation(start);
        currentActiveRoute = {
            start: start,
            destination: result.station.location,
            distance: result.distance,
            path: result.path
        };

        setLastAction(`Nearest to ${start}: Station ${result.station.station_id} at ${result.station.location}`);
        await refreshDashboard();

        if (graphViz && result.path) {
            await graphViz.animateEVAlongPath(result.path);
        }
    } catch (err) {
        setLastAction(err.message);
    }
}

async function handleAutoSimToggle() {
    const btn = element("autoSimBtn");
    if (simController.isRunning) {
        simController.pauseAutoSim();
        btn.textContent = "▶ Auto Simulation";
        btn.className = "btn accent";
        setLastAction("Auto simulation paused");
    } else {
        const speed = Number(element("autoSimSpeed").value);
        simController.setSpeed(speed);
        simController.startAutoSim(() => {
            refreshDashboard();
        });
        btn.textContent = "⏸ Pause Auto Sim";
        btn.className = "btn warning";
        setLastAction("Auto simulation active...");
    }
}

async function handleSampleData() {
    try {
        setLastAction("Populating sample EVs & Stations...");
        // Add sample stations if needed
        try { await addStation({ stationId: "S1", location: "A", chargingSlots: 2 }); } catch(e){}
        try { await addStation({ stationId: "S2", location: "E", chargingSlots: 2 }); } catch(e){}

        // Add sample EVs into different queues to demonstrate features
        await addEVAutomatically({ evId: "EV-NORMAL-1", batteryLevel: 85, location: "A" });
        await addEVAutomatically({ evId: "EV-CRITICAL-1", batteryLevel: 12, location: "B", priority: 1 });
        await addEVAutomatically({ evId: "EV-CRITICAL-2", batteryLevel: 5, location: "C", priority: 2 });
        await addEV({ evId: "EV-VIP-SPECIAL", batteryLevel: 90, location: "D", type: "special" });

        setLastAction("Sample data populated across all 3 Data Structures!");
        await refreshDashboard();
    } catch (err) {
        setLastAction(err.message);
    }
}

async function handleReset() {
    try {
        await resetSimulation();
        currentActiveRoute = null;
        setLastAction("Simulation reset");
        await refreshDashboard();
    } catch (err) {
        setLastAction(err.message);
    }
}

async function handleClear() {
    try {
        await clearSimulation();
        currentActiveRoute = null;
        setLastAction("Simulation cleared");
        await refreshDashboard();
    } catch (err) {
        setLastAction(err.message);
    }
}

async function handleDemoReport() {
    const modal = element("reportModal");
    const body = element("reportModalBody");
    if (!modal || !body) return;

    try {
        const status = await getStatus();
        const events = await getEvents();
        const evs = await getEVs();

        body.innerHTML = `
            <div class="report-summary">
                <p>Execution trace report generated from live REST snapshot.</p>
                <div class="report-grid">
                    <div class="report-stat-box">
                        <div class="val">${status.ev_count}</div>
                        <div class="lbl">Total EVs Handled</div>
                    </div>
                    <div class="report-stat-box">
                        <div class="val">${status.completed}</div>
                        <div class="lbl">Sessions Completed</div>
                    </div>
                    <div class="report-stat-box">
                        <div class="val">${status.waiting_priority}</div>
                        <div class="lbl">Priority EVs (Min-Heap)</div>
                    </div>
                    <div class="report-stat-box">
                        <div class="val">${status.waiting_normal}</div>
                        <div class="lbl">Normal EVs (FIFO Queue)</div>
                    </div>
                    <div class="report-stat-box">
                        <div class="val">${status.waiting_special}</div>
                        <div class="lbl">Special EVs (Deque)</div>
                    </div>
                    <div class="report-stat-box">
                        <div class="val">${status.event_count}</div>
                        <div class="lbl">Total DS Events</div>
                    </div>
                </div>
            </div>
        `;
        modal.classList.remove("hidden");
    } catch (err) {
        alert("Failed to load report data: " + err.message);
    }
}

// =========================================================
// TAB NAVIGATION & ROUTING
// =========================================================

function navigateToTab(tabId) {
    if (!tabId) tabId = "overview";
    const tabs = document.querySelectorAll(".nav-tab");
    const panes = document.querySelectorAll(".tab-pane");

    tabs.forEach(tab => {
        const isActive = tab.getAttribute("data-tab") === tabId;
        tab.classList.toggle("active", isActive);
        tab.setAttribute("aria-selected", isActive ? "true" : "false");
    });

    panes.forEach(pane => {
        pane.classList.remove("active");
    });

    const targetPaneId = "view" + tabId.charAt(0).toUpperCase() + tabId.slice(1);
    const targetPane = document.getElementById(targetPaneId);
    if (targetPane) {
        targetPane.classList.add("active");
    }

    if (window.location.hash !== "#" + tabId) {
        window.history.replaceState(null, "", "#" + tabId);
    }

    // Refresh visualizer layouts upon tab visibility change
    setTimeout(() => {
        if (graphViz && currentGraphData && lastSnapshotData) {
            graphViz.render(currentGraphData, lastSnapshotData.stations, currentActiveRoute);
        }
        if (heapViz && lastSnapshotData && lastSnapshotData.queues) {
            heapViz.render(lastSnapshotData.queues.priority);
        }
    }, 50);
}

// Expose navigateToTab to window for inline HTML onclick attributes
window.navigateToTab = navigateToTab;

// =========================================================
// THEME MANAGEMENT (DARK / LIGHT MODE)
// =========================================================

function initTheme() {
    const saved = localStorage.getItem("ev_theme") || 
        (window.matchMedia && window.matchMedia("(prefers-color-scheme: light)").matches ? "light" : "dark");
    setTheme(saved);
}

function setTheme(theme) {
    currentTheme = theme;
    document.documentElement.setAttribute("data-theme", theme);
    localStorage.setItem("ev_theme", theme);

    const label = element("themeLabel");
    if (label) {
        label.textContent = theme === "dark" ? "Dark" : "Light";
    }

    // Re-render SVG visualizers with updated theme colors
    if (graphViz && currentGraphData && lastSnapshotData) {
        graphViz.render(currentGraphData, lastSnapshotData.stations, currentActiveRoute);
    }
    if (heapViz && lastSnapshotData && lastSnapshotData.queues) {
        heapViz.render(lastSnapshotData.queues.priority);
    }
}

function toggleTheme() {
    const next = currentTheme === "dark" ? "light" : "dark";
    setTheme(next);
}

// =========================================================
// INITIALIZATION
// =========================================================

function initialize() {
    graphViz = new GraphVisualizer("graphSvg", "routeInfoPanel");
    heapViz = new HeapVisualizer("heapTreeContainer", "heapArrayContainer");
    queueViz = new QueueVisualizer("normalQueue");
    dequeViz = new DequeVisualizer("specialQueue");
    simController = new SimulationController();

    // Tab switcher listeners
    document.querySelectorAll(".nav-tab").forEach(tab => {
        tab.addEventListener("click", () => {
            const tabId = tab.getAttribute("data-tab");
            navigateToTab(tabId);
        });
    });

    // Theme toggle button
    if (element("themeToggleBtn")) {
        element("themeToggleBtn").addEventListener("click", toggleTheme);
    }

    // Handle hash change
    window.addEventListener("hashchange", () => {
        const hashTab = window.location.hash.replace("#", "");
        if (hashTab) navigateToTab(hashTab);
    });

    // Event listeners
    if (element("addEvButton")) element("addEvButton").addEventListener("click", handleAddEV);
    if (element("processButton")) element("processButton").addEventListener("click", handleProcess);
    if (element("findRouteBtn")) element("findRouteBtn").addEventListener("click", handleFindRoute);
    if (element("findNearestBtn")) element("findNearestBtn").addEventListener("click", handleFindNearest);
    if (element("autoSimBtn")) element("autoSimBtn").addEventListener("click", handleAutoSimToggle);
    if (element("sampleDataBtn")) element("sampleDataBtn").addEventListener("click", handleSampleData);
    if (element("resetButton")) element("resetButton").addEventListener("click", handleReset);
    if (element("clearBtn")) element("clearBtn").addEventListener("click", handleClear);

    if (element("demoReportBtn")) element("demoReportBtn").addEventListener("click", handleDemoReport);
    if (element("closeReportBtn")) element("closeReportBtn").addEventListener("click", () => {
        element("reportModal").classList.add("hidden");
    });

    if (element("exportJsonBtn")) element("exportJsonBtn").addEventListener("click", async () => {
        const eventsData = await getEvents();
        simController.exportEventsJSON(eventsData.events || []);
    });

    if (element("exportCsvBtn")) element("exportCsvBtn").addEventListener("click", async () => {
        const eventsData = await getEvents();
        simController.exportEventsCSV(eventsData.events || []);
    });

    // Initial theme & tab
    initTheme();
    const initialTab = window.location.hash.replace("#", "") || "overview";
    navigateToTab(initialTab);

    refreshDashboard();
    refreshTimer = setInterval(refreshDashboard, 2000);
}

document.addEventListener("DOMContentLoaded", initialize);

