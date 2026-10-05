import pytest

from app import create_app


@pytest.fixture
def app():
    return create_app(testing=True)


@pytest.fixture
def client(app):
    return app.test_client()


# =========================================================
# HEALTH
# =========================================================

def test_health(client):

    response = client.get("/api/health")

    assert response.status_code == 200

    data = response.get_json()

    assert data["success"] is True
    assert data["data"]["status"] == "online"


# =========================================================
# INITIAL STATUS
# =========================================================

def test_initial_status(client):

    response = client.get("/api/status")

    assert response.status_code == 200

    data = response.get_json()["data"]

    assert data["ev_count"] == 0
    assert data["station_count"] == 0
    assert data["waiting_normal"] == 0
    assert data["waiting_priority"] == 0
    assert data["waiting_special"] == 0
    assert data["charging"] == 0
    assert data["completed"] == 0
    assert data["event_count"] == 0


# =========================================================
# INITIAL SNAPSHOT
# =========================================================

def test_initial_snapshot(client):

    response = client.get("/api/snapshot")

    assert response.status_code == 200

    data = response.get_json()["data"]

    assert data["queues"]["normal"] == []
    assert data["queues"]["priority"] == []
    assert data["queues"]["special"] == []

    assert data["charging"] == []
    assert data["completed"] == []
    assert data["stations"] == []
    assert data["events"] == []


# =========================================================
# ADD GRAPH VERTEX
# =========================================================

def test_add_graph_vertex(client):

    response = client.post(
        "/api/graph/vertices",
        json={
            "vertex": "F"
        }
    )

    assert response.status_code == 201

    data = response.get_json()

    assert data["success"] is True
    assert data["data"]["vertex"] == "F"


# =========================================================
# ADD GRAPH EDGE
# =========================================================

def test_add_graph_edge(client):

    client.post(
        "/api/graph/vertices",
        json={
            "vertex": "F"
        }
    )

    response = client.post(
        "/api/graph/edges",
        json={
            "source": "E",
            "destination": "F",
            "weight": 3
        }
    )

    assert response.status_code == 201

    data = response.get_json()["data"]

    assert data["source"] == "E"
    assert data["destination"] == "F"
    assert data["weight"] == 3


# =========================================================
# ADD STATION
# =========================================================

def test_add_station(client):

    response = client.post(
        "/api/stations",
        json={
            "station_id": "S1",
            "location": "A",
            "charging_slots": 2
        }
    )

    assert response.status_code == 201

    data = response.get_json()["data"]

    assert data["station_id"] == "S1"
    assert data["location"] == "A"
    assert data["charging_slots"] == 2
    assert data["available_slots"] == 2


# =========================================================
# DUPLICATE STATION
# =========================================================

def test_duplicate_station(client):

    station = {
        "station_id": "S1",
        "location": "A",
        "charging_slots": 2
    }

    first = client.post(
        "/api/stations",
        json=station
    )

    second = client.post(
        "/api/stations",
        json=station
    )

    assert first.status_code == 201
    assert second.status_code == 409


# =========================================================
# INVALID STATION LOCATION
# =========================================================

def test_station_invalid_location(client):

    response = client.post(
        "/api/stations",
        json={
            "station_id": "S1",
            "location": "UNKNOWN",
            "charging_slots": 2
        }
    )

    assert response.status_code == 400


# =========================================================
# GET STATIONS
# =========================================================

def test_get_stations(client):

    client.post(
        "/api/stations",
        json={
            "station_id": "S1",
            "location": "A",
            "charging_slots": 2
        }
    )

    response = client.get("/api/stations")

    assert response.status_code == 200

    data = response.get_json()["data"]

    assert data["count"] == 1
    assert data["stations"][0]["station_id"] == "S1"


# =========================================================
# ADD NORMAL EV
# =========================================================

def test_add_normal_ev(client):

    response = client.post(
        "/api/evs",
        json={
            "ev_id": "EV001",
            "battery_level": 80,
            "battery_capacity": 100,
            "charging_required": True,
            "priority": 0,
            "location": "A",
            "type": "normal"
        }
    )

    assert response.status_code == 201

    data = response.get_json()["data"]

    assert data["ev"]["ev_id"] == "EV001"
    assert data["queue"] == "normal"


# =========================================================
# ADD PRIORITY EV
# =========================================================

def test_add_priority_ev(client):

    response = client.post(
        "/api/evs",
        json={
            "ev_id": "EV001",
            "battery_level": 10,
            "battery_capacity": 100,
            "charging_required": True,
            "priority": 1,
            "location": "A",
            "type": "priority"
        }
    )

    assert response.status_code == 201

    data = response.get_json()["data"]

    assert data["queue"] == "priority"


# =========================================================
# AUTOMATIC CLASSIFICATION
# =========================================================

def test_automatic_priority_classification(client):

    response = client.post(
        "/api/evs/automatic",
        json={
            "ev_id": "EV001",
            "battery_level": 10,
            "battery_capacity": 100,
            "charging_required": True,
            "priority": 1,
            "location": "A"
        }
    )

    assert response.status_code == 201

    data = response.get_json()["data"]

    assert data["queue"] == "priority"


def test_automatic_normal_classification(client):

    response = client.post(
        "/api/evs/automatic",
        json={
            "ev_id": "EV001",
            "battery_level": 80,
            "battery_capacity": 100,
            "charging_required": True,
            "priority": 0,
            "location": "A"
        }
    )

    assert response.status_code == 201

    data = response.get_json()["data"]

    assert data["queue"] == "normal"


# =========================================================
# DUPLICATE EV
# =========================================================

def test_duplicate_ev(client):

    ev = {
        "ev_id": "EV001",
        "battery_level": 80,
        "battery_capacity": 100,
        "location": "A",
        "type": "normal"
    }

    first = client.post(
        "/api/evs",
        json=ev
    )

    second = client.post(
        "/api/evs",
        json=ev
    )

    assert first.status_code == 201
    assert second.status_code == 409


# =========================================================
# GET EVS
# =========================================================

def test_get_evs(client):

    client.post(
        "/api/evs",
        json={
            "ev_id": "EV001",
            "battery_level": 80,
            "battery_capacity": 100,
            "location": "A",
            "type": "normal"
        }
    )

    response = client.get("/api/evs")

    assert response.status_code == 200

    data = response.get_json()["data"]

    assert data["count"] == 1
    assert data["evs"][0]["ev_id"] == "EV001"


# =========================================================
# EVENTS
# =========================================================

def test_events(client):

    client.post(
        "/api/evs",
        json={
            "ev_id": "EV001",
            "battery_level": 80,
            "battery_capacity": 100,
            "location": "A",
            "type": "normal"
        }
    )

    response = client.get("/api/events")

    assert response.status_code == 200

    data = response.get_json()["data"]

    assert data["count"] == 2
    assert data["events"][0]["type"] == "ev_arrived"
    assert data["events"][1]["type"] == "queue_insert"


def test_events_limit(client):

    client.post(
        "/api/evs",
        json={
            "ev_id": "EV001",
            "battery_level": 80,
            "battery_capacity": 100,
            "location": "A",
            "type": "normal"
        }
    )

    response = client.get(
        "/api/events?limit=1"
    )

    assert response.status_code == 200

    data = response.get_json()["data"]

    assert data["count"] == 1


# =========================================================
# SHORTEST ROUTE
# =========================================================

def test_calculate_route(client):

    response = client.get(
        "/api/routes?start=A&destination=E"
    )

    assert response.status_code == 200

    data = response.get_json()["data"]

    assert data["start"] == "A"
    assert data["destination"] == "E"

    assert data["distance"] == 5
    assert data["path"] == [
        "A",
        "C",
        "D",
        "E"
    ]


# =========================================================
# NEAREST STATION
# =========================================================

def test_nearest_station(client):

    client.post(
        "/api/stations",
        json={
            "station_id": "S1",
            "location": "E",
            "charging_slots": 2
        }
    )

    response = client.get(
        "/api/stations/nearest?start=A"
    )

    assert response.status_code == 200

    data = response.get_json()["data"]

    assert data["station"]["station_id"] == "S1"
    assert data["distance"] == 5
    assert data["path"] == [
        "A",
        "C",
        "D",
        "E"
    ]


# =========================================================
# PROCESS EV
# =========================================================

def test_process_ev(client):

    client.post(
        "/api/stations",
        json={
            "station_id": "S1",
            "location": "E",
            "charging_slots": 2
        }
    )

    client.post(
        "/api/evs",
        json={
            "ev_id": "EV001",
            "battery_level": 80,
            "battery_capacity": 100,
            "location": "A",
            "type": "normal"
        }
    )

    response = client.post(
        "/api/process"
    )

    assert response.status_code == 200

    data = response.get_json()["data"]

    assert data["ev"]["ev_id"] == "EV001"
    assert data["station"]["station_id"] == "S1"
    assert data["distance"] == 5
    assert data["path"] == [
        "A",
        "C",
        "D",
        "E"
    ]
    assert data["status"] == "charging"


# =========================================================
# COMPLETE CHARGING
# =========================================================

def test_complete_charging(client):

    client.post(
        "/api/stations",
        json={
            "station_id": "S1",
            "location": "A",
            "charging_slots": 2
        }
    )

    client.post(
        "/api/evs",
        json={
            "ev_id": "EV001",
            "battery_level": 80,
            "battery_capacity": 100,
            "location": "A",
            "type": "normal"
        }
    )

    process_response = client.post(
        "/api/process"
    )

    assert process_response.status_code == 200

    response = client.post(
        "/api/charging/complete",
        json={
            "ev_id": "EV001",
            "station_id": "S1"
        }
    )

    assert response.status_code == 200

    data = response.get_json()["data"]

    assert data["ev"]["ev_id"] == "EV001"
    assert data["station"]["station_id"] == "S1"
    assert data["status"] == "completed"


# =========================================================
# PROCESS WITH NO EV
# =========================================================

def test_process_without_ev(client):

    response = client.post(
        "/api/process"
    )

    assert response.status_code == 409

    data = response.get_json()

    assert data["success"] is False


# =========================================================
# RESET
# =========================================================

def test_reset(client):

    client.post(
        "/api/stations",
        json={
            "station_id": "S1",
            "location": "A",
            "charging_slots": 2
        }
    )

    client.post(
        "/api/evs",
        json={
            "ev_id": "EV001",
            "battery_level": 80,
            "battery_capacity": 100,
            "location": "A",
            "type": "normal"
        }
    )

    response = client.post(
        "/api/reset"
    )

    assert response.status_code == 200

    data = response.get_json()["data"]["status"]

    assert data["ev_count"] == 0
    assert data["station_count"] == 1
    assert data["event_count"] == 0


# =========================================================
# CLEAR
# =========================================================

def test_clear(client):

    client.post(
        "/api/stations",
        json={
            "station_id": "S1",
            "location": "A",
            "charging_slots": 2
        }
    )

    client.post(
        "/api/evs",
        json={
            "ev_id": "EV001",
            "battery_level": 80,
            "battery_capacity": 100,
            "location": "A",
            "type": "normal"
        }
    )

    response = client.post(
        "/api/clear"
    )

    assert response.status_code == 200

    data = response.get_json()["data"]["status"]

    assert data["ev_count"] == 0
    assert data["station_count"] == 0
    assert data["event_count"] == 0

# =========================================================
# GRAPH API
# =========================================================

def test_get_graph(client):

    response = client.get("/api/graph")

    assert response.status_code == 200

    data = response.get_json()

    assert data["success"] is True

    graph = data["data"]

    assert graph["directed"] is False

    assert graph["vertices"] == [
        "A",
        "B",
        "C",
        "D",
        "E"
    ]

    assert graph["vertex_count"] == 5
    assert graph["edge_count"] == 7

    assert {
        "source": "A",
        "destination": "B",
        "weight": 4
    } in graph["edges"]

    assert {
        "source": "A",
        "destination": "C",
        "weight": 2
    } in graph["edges"]

    assert {
        "source": "C",
        "destination": "D",
        "weight": 1
    } in graph["edges"]


def test_graph_api_returns_unique_undirected_edges(client):

    response = client.get("/api/graph")

    graph = response.get_json()["data"]

    edges = graph["edges"]

    # There should be exactly 7 roads in the demo graph,
    # not 14 adjacency-list entries.
    assert len(edges) == 7