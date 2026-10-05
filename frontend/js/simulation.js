/**
 * Smart EV Charging Queue & Route Optimizer
 * Live Simulation Controller, DS Trace & Complexity & Export Report Manager
 */

class SimulationController {
    constructor() {
        this.autoSimInterval = null;
        this.isRunning = false;
        this.speed = 2000; // ms
        this.evCounter = 100;
        this.locations = ['A', 'B', 'C', 'D', 'E'];
        this.tickCallback = null;
        this.dsTraceLog = [];
    }

    startAutoSim(onTickCallback) {
        if (this.isRunning) return;
        this.isRunning = true;
        this.tickCallback = onTickCallback;
        
        this.autoSimInterval = setInterval(async () => {
            if (!this.isRunning) return;
            
            // Randomly decide whether to Add EV or Process Next
            const action = Math.random() > 0.4 ? 'add' : 'process';

            if (action === 'add') {
                this.evCounter++;
                const newId = `EV${this.evCounter}`;
                const battery = Math.floor(Math.random() * 85) + 10;
                const loc = this.locations[Math.floor(Math.random() * this.locations.length)];
                const isCritical = battery <= 20;
                const priority = isCritical ? Math.floor(Math.random() * 5) + 1 : 0;

                try {
                    await addEVAutomatically({
                        evId: newId,
                        batteryLevel: battery,
                        location: loc,
                        priority: priority
                    });
                    this.logDSTrace({
                        step: this.dsTraceLog.length + 1,
                        ds: isCritical ? 'MIN-HEAP' : 'SIMPLE QUEUE',
                        op: isCritical ? 'insert(priority=' + priority + ')' : 'enqueue(FIFO)',
                        complexity: isCritical ? 'O(log n)' : 'O(1)',
                        target: newId,
                        details: `Added ${newId} (Battery: ${battery}%, Loc: ${loc})`
                    });
                } catch (e) {
                    console.warn("Auto add error:", e);
                }
            } else {
                try {
                    const res = await processNextEV();
                    if (res && res.ev) {
                        this.logDSTrace({
                            step: this.dsTraceLog.length + 1,
                            ds: 'GRAPH + DIJKSTRA',
                            op: 'extract_min() & calculate_route()',
                            complexity: 'O((V + E) log V)',
                            target: res.ev.ev_id,
                            details: `Routed ${res.ev.ev_id} ➔ Station ${res.station?.station_id} (Dist: ${res.distance})`
                        });

                        // Automatically complete charging after a short delay
                        setTimeout(async () => {
                            if (res.ev && res.station) {
                                try {
                                    await completeCharging(res.ev.ev_id, res.station.station_id);
                                    if (onTickCallback) onTickCallback();
                                } catch (err) {}
                            }
                        }, 1200);
                    }
                } catch (e) {
                    // No EV to process or station full
                }
            }

            if (onTickCallback) onTickCallback();
        }, this.speed);
    }

    pauseAutoSim() {
        this.isRunning = false;
        if (this.autoSimInterval) {
            clearInterval(this.autoSimInterval);
            this.autoSimInterval = null;
        }
    }

    setSpeed(ms) {
        this.speed = ms;
        if (this.isRunning) {
            this.pauseAutoSim();
            this.startAutoSim(this.tickCallback);
        }
    }

    logDSTrace(logEntry) {
        this.dsTraceLog.unshift(logEntry);
        if (this.dsTraceLog.length > 50) this.dsTraceLog.pop();
        this.renderDSTrace();
    }

    renderDSTrace() {
        const container = document.getElementById("dsTraceList");
        if (!container) return;

        if (!this.dsTraceLog.length) {
            container.innerHTML = `<div class="empty-state">No DS trace logged yet</div>`;
            return;
        }

        container.innerHTML = this.dsTraceLog.map(log => `
            <div class="ds-trace-item">
                <div class="trace-header">
                    <span class="trace-step">#${log.step}</span>
                    <span class="trace-ds-tag">${log.ds}</span>
                    <span class="trace-complexity">${log.complexity}</span>
                </div>
                <div class="trace-body">
                    <strong>${log.op}</strong> — ${log.details}
                </div>
            </div>
        `).join('');
    }

    exportEventsJSON(events) {
        const dataStr = "data:text/json;charset=utf-8," + encodeURIComponent(JSON.stringify(events, null, 2));
        const downloadAnchor = document.createElement('a');
        downloadAnchor.setAttribute("href", dataStr);
        downloadAnchor.setAttribute("download", `ev_simulation_events_${Date.now()}.json`);
        document.body.appendChild(downloadAnchor);
        downloadAnchor.click();
        downloadAnchor.remove();
    }

    exportEventsCSV(events) {
        if (!events || !events.length) return;
        const headers = ["Step", "Event Message", "EV ID", "Station ID"];
        const rows = events.map(e => [e.step, `"${e.message}"`, e.ev_id || "", e.station_id || ""]);
        const csvContent = "data:text/csv;charset=utf-8," + [headers.join(","), ...rows.map(r => r.join(","))].join("\n");
        const encodedUri = encodeURI(csvContent);
        const link = document.createElement("a");
        link.setAttribute("href", encodedUri);
        link.setAttribute("download", `ev_simulation_report_${Date.now()}.csv`);
        document.body.appendChild(link);
        link.click();
        link.remove();
    }
}
