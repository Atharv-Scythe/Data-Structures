const API_BASE = "/api";

async function apiRequest(
    endpoint,
    options = {}
) {
    const response = await fetch(
        `${API_BASE}${endpoint}`,
        {
            headers: {
                "Content-Type": "application/json",
                ...(options.headers || {})
            },
            ...options
        }
    );

    let body;

    try {
        body = await response.json();
    } catch (error) {
        throw new Error(
            `Server returned invalid JSON (${response.status})`
        );
    }

    if (!response.ok || body.success === false) {

        const message =
            body?.error?.message ||
            `Request failed with status ${response.status}`;

        throw new Error(message);
    }

    return body.data;
}


// =========================================================
// READ OPERATIONS
// =========================================================

async function getHealth() {

    return apiRequest("/health");
}


async function getStatus() {

    return apiRequest("/status");
}


async function getSnapshot() {

    return apiRequest("/snapshot");
}


async function getEvents(limit = null) {

    const endpoint = limit
        ? `/events?limit=${limit}`
        : "/events";

    return apiRequest(endpoint);
}


// =========================================================
// EV OPERATIONS
// =========================================================

// =========================================================
// GRAPH OPERATIONS
// =========================================================

async function getGraph() {

    return apiRequest("/graph");
}


async function addVertex(vertex) {

    return apiRequest(
        "/graph/vertices",
        {
            method: "POST",

            body: JSON.stringify({
                vertex: vertex
            })
        }
    );
}


async function addEdge(source, destination, weight) {

    return apiRequest(
        "/graph/edges",
        {
            method: "POST",

            body: JSON.stringify({
                source: source,
                destination: destination,
                weight: Number(weight)
            })
        }
    );
}


// =========================================================
// EV OPERATIONS
// =========================================================

async function addEV({
    evId,
    batteryLevel,
    location,
    batteryCapacity = 100,
    chargingRequired = true,
    priority = 0,
    type = "normal"
}) {

    return apiRequest(
        "/evs",
        {
            method: "POST",

            body: JSON.stringify({
                ev_id: evId,
                battery_level: batteryLevel,
                battery_capacity: batteryCapacity,
                charging_required: chargingRequired,
                priority: priority,
                location: location,
                type: type
            })
        }
    );
}


async function addEVAutomatically({
    evId,
    batteryLevel,
    location,
    batteryCapacity = 100,
    chargingRequired = true,
    priority = 0
}) {

    return apiRequest(
        "/evs/automatic",
        {
            method: "POST",

            body: JSON.stringify({
                ev_id: evId,
                battery_level: batteryLevel,
                battery_capacity: batteryCapacity,
                charging_required: chargingRequired,
                priority: priority,
                location: location
            })
        }
    );
}


async function getEVs() {

    return apiRequest("/evs");
}


async function processNextEV() {

    return apiRequest(
        "/process",
        {
            method: "POST"
        }
    );
}


// =========================================================
// STATION OPERATIONS
// =========================================================

async function addStation({
    stationId,
    location,
    chargingSlots = 2
}) {

    return apiRequest(
        "/stations",
        {
            method: "POST",

            body: JSON.stringify({
                station_id: stationId,
                location: location,
                charging_slots: chargingSlots
            })
        }
    );
}


async function getStations() {

    return apiRequest("/stations");
}


// =========================================================
// ROUTING
// =========================================================

async function getRoute(
    start,
    destination
) {

    return apiRequest(
        `/routes?start=${encodeURIComponent(start)}&destination=${encodeURIComponent(destination)}`
    );
}


async function getNearestStation(start) {

    return apiRequest(
        `/stations/nearest?start=${encodeURIComponent(start)}`
    );
}


// =========================================================
// CHARGING
// =========================================================

async function completeCharging(
    evId,
    stationId
) {

    return apiRequest(
        "/charging/complete",
        {
            method: "POST",

            body: JSON.stringify({
                ev_id: evId,
                station_id: stationId
            })
        }
    );
}


// =========================================================
// SIMULATION CONTROL
// =========================================================

async function resetSimulation() {

    return apiRequest(
        "/reset",
        {
            method: "POST"
        }
    );
}


async function clearSimulation() {

    return apiRequest(
        "/clear",
        {
            method: "POST"
        }
    );
}
