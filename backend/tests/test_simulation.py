from src.algorithms.graph import Graph
from src.models.ev import EV
from src.models.station import ChargingStation
from src.services.simulation import EVChargingSimulation


# ---------------------------------------------------------
# HELPERS
# ---------------------------------------------------------

def create_graph():
    """
    Road network:

        A ----4---- B
        |           |
        2           5
        |           |
        C ----1---- D
        |           |
        6           2
        |           |
        E ----------
    """

    graph = Graph()

    graph.add_edge("A", "B", 4)
    graph.add_edge("A", "C", 2)
    graph.add_edge("B", "D", 5)
    graph.add_edge("C", "D", 1)
    graph.add_edge("C", "E", 6)
    graph.add_edge("D", "E", 2)

    return graph


def create_ev(
    ev_id,
    location="A",
    battery_level=50,
    priority=5
):
    return EV(
        ev_id=ev_id,
        battery_level=battery_level,
        battery_capacity=60,
        charging_required=50,
        priority=priority,
        location=location
    )


def create_station(
    station_id,
    location,
    slots=1
):
    return ChargingStation(
        station_id=station_id,
        location=location,
        charging_slots=slots
    )


# ---------------------------------------------------------
# INITIALIZATION
# ---------------------------------------------------------

def test_create_simulation():
    graph = create_graph()

    simulation = EVChargingSimulation(graph)

    assert simulation.graph == graph
    assert simulation.station_count() == 0
    assert len(simulation.evs) == 0


# ---------------------------------------------------------
# STATION MANAGEMENT
# ---------------------------------------------------------

def test_add_station():
    simulation = EVChargingSimulation(
        create_graph()
    )

    station = create_station("S001", "D")

    simulation.add_station(station)

    assert simulation.station_count() == 1
    assert station in simulation.stations


def test_add_multiple_stations():
    simulation = EVChargingSimulation(
        create_graph()
    )

    station1 = create_station("S001", "C")
    station2 = create_station("S002", "D")

    simulation.add_station(station1)
    simulation.add_station(station2)

    assert simulation.station_count() == 2


def test_duplicate_station():
    simulation = EVChargingSimulation(
        create_graph()
    )

    station = create_station("S001", "C")

    simulation.add_station(station)
    simulation.add_station(station)

    assert simulation.station_count() == 1


def test_remove_station():
    simulation = EVChargingSimulation(
        create_graph()
    )

    station = create_station("S001", "C")

    simulation.add_station(station)

    assert simulation.remove_station(station) is True
    assert simulation.station_count() == 0


def test_remove_nonexistent_station():
    simulation = EVChargingSimulation(
        create_graph()
    )

    station = create_station("S001", "C")

    assert simulation.remove_station(station) is False


# ---------------------------------------------------------
# EV MANAGEMENT
# ---------------------------------------------------------

def test_add_normal_ev():
    simulation = EVChargingSimulation(
        create_graph()
    )

    ev = create_ev("EV001")

    assert simulation.add_ev(ev, "normal") is True

    assert ev in simulation.evs
    assert simulation.charging_manager.normal_queue.size() == 1


def test_add_priority_ev():
    simulation = EVChargingSimulation(
        create_graph()
    )

    ev = create_ev(
        "EV001",
        battery_level=10,
        priority=1
    )

    assert simulation.add_ev(ev, "priority") is True

    assert simulation.charging_manager.priority_queue.size() == 1


def test_add_special_ev():
    simulation = EVChargingSimulation(
        create_graph()
    )

    ev = create_ev("EV001")

    assert simulation.add_ev(ev, "special") is True

    assert simulation.charging_manager.special_deque.size() == 1


def test_duplicate_ev():
    simulation = EVChargingSimulation(
        create_graph()
    )

    ev = create_ev("EV001")

    assert simulation.add_ev(ev) is True
    assert simulation.add_ev(ev) is False

    assert len(simulation.evs) == 1


def test_invalid_ev_type():
    simulation = EVChargingSimulation(
        create_graph()
    )

    ev = create_ev("EV001")

    try:
        simulation.add_ev(ev, "invalid")
        assert False
    except ValueError:
        assert True


def test_invalid_ev_object():
    simulation = EVChargingSimulation(
        create_graph()
    )

    try:
        simulation.add_ev("not an ev")
        assert False
    except TypeError:
        assert True


# ---------------------------------------------------------
# AUTOMATIC CLASSIFICATION
# ---------------------------------------------------------

def test_automatic_priority_classification():
    simulation = EVChargingSimulation(
        create_graph()
    )

    ev = create_ev(
        "EV001",
        battery_level=10
    )

    category = simulation.add_ev_automatically(ev)

    assert category == "priority"
    assert simulation.charging_manager.priority_queue.size() == 1


def test_automatic_normal_classification():
    simulation = EVChargingSimulation(
        create_graph()
    )

    ev = create_ev(
        "EV001",
        battery_level=50
    )

    category = simulation.add_ev_automatically(ev)

    assert category == "normal"
    assert simulation.charging_manager.normal_queue.size() == 1


def test_automatic_duplicate_ev():
    simulation = EVChargingSimulation(
        create_graph()
    )

    ev = create_ev("EV001")

    simulation.add_ev_automatically(ev)

    assert simulation.add_ev_automatically(ev) is None


# ---------------------------------------------------------
# EV SELECTION
# ---------------------------------------------------------

def test_get_next_priority_ev_first():
    simulation = EVChargingSimulation(
        create_graph()
    )

    normal = create_ev("NORMAL")
    priority = create_ev(
        "PRIORITY",
        battery_level=10,
        priority=1
    )

    simulation.add_ev(normal, "normal")
    simulation.add_ev(priority, "priority")

    next_ev = simulation.get_next_ev()

    assert next_ev == priority


def test_get_next_special_when_no_priority():
    simulation = EVChargingSimulation(
        create_graph()
    )

    normal = create_ev("NORMAL")
    special = create_ev("SPECIAL")

    simulation.add_ev(normal, "normal")
    simulation.add_ev(special, "special")

    next_ev = simulation.get_next_ev()

    assert next_ev == special


def test_get_next_normal_when_no_priority_or_special():
    simulation = EVChargingSimulation(
        create_graph()
    )

    normal = create_ev("NORMAL")

    simulation.add_ev(normal, "normal")

    assert simulation.get_next_ev() == normal


def test_get_next_ev_empty():
    simulation = EVChargingSimulation(
        create_graph()
    )

    assert simulation.get_next_ev() is None


# ---------------------------------------------------------
# PROCESSING
# ---------------------------------------------------------

def test_process_next_ev():
    simulation = EVChargingSimulation(
        create_graph()
    )

    station = create_station("S001", "C")

    simulation.add_station(station)

    ev = create_ev("EV001")

    simulation.add_ev(ev)

    result = simulation.process_next_ev()

    assert result["success"] is True
    assert result["ev"] == ev
    assert result["station"] == station
    assert result["distance"] == 2
    assert result["path"] == ["A", "C"]
    assert result["status"] == "charging"

    assert ev in station.active_evs


def test_process_empty_simulation():
    simulation = EVChargingSimulation(
        create_graph()
    )

    assert simulation.process_next_ev() is None


def test_process_without_station():
    simulation = EVChargingSimulation(
        create_graph()
    )

    ev = create_ev("EV001")

    simulation.add_ev(ev)

    result = simulation.process_next_ev()

    assert result["success"] is False
    assert result["reason"] == "No available charging station"


def test_process_selects_nearest_station():
    simulation = EVChargingSimulation(
        create_graph()
    )

    far_station = create_station("S001", "D")
    near_station = create_station("S002", "C")

    simulation.add_station(far_station)
    simulation.add_station(near_station)

    ev = create_ev("EV001")

    simulation.add_ev(ev)

    result = simulation.process_next_ev()

    assert result["station"] == near_station
    assert result["distance"] == 2
    assert result["path"] == ["A", "C"]


def test_process_ignores_full_nearest_station():
    simulation = EVChargingSimulation(
        create_graph()
    )

    near_station = create_station(
        "S001",
        "C",
        slots=1
    )

    far_station = create_station(
        "S002",
        "D",
        slots=1
    )

    near_station.start_charging("occupied")

    simulation.add_station(near_station)
    simulation.add_station(far_station)

    ev = create_ev("EV001")

    simulation.add_ev(ev)

    result = simulation.process_next_ev()

    assert result["success"] is True
    assert result["station"] == far_station
    assert result["distance"] == 3


# ---------------------------------------------------------
# COMPLETE CHARGING
# ---------------------------------------------------------

def test_complete_charging():
    simulation = EVChargingSimulation(
        create_graph()
    )

    station = create_station("S001", "C")

    simulation.add_station(station)

    ev = create_ev("EV001")

    simulation.add_ev(ev)
    simulation.process_next_ev()

    result = simulation.complete_charging(
        ev,
        station
    )

    assert result is True
    assert ev not in station.active_evs
    assert ev in simulation.charging_manager.completed_evs


def test_complete_non_charging_ev():
    simulation = EVChargingSimulation(
        create_graph()
    )

    station = create_station("S001", "C")
    ev = create_ev("EV001")

    assert simulation.complete_charging(
        ev,
        station
    ) is False


# ---------------------------------------------------------
# STATUS
# ---------------------------------------------------------

def test_initial_status():
    simulation = EVChargingSimulation(
        create_graph()
    )

    status = simulation.get_status()

    assert status["ev_count"] == 0
    assert status["station_count"] == 0
    assert status["waiting_normal"] == 0
    assert status["waiting_priority"] == 0
    assert status["waiting_special"] == 0
    assert status["charging"] == 0
    assert status["completed"] == 0
    assert status["processed"] == 0


def test_status_after_processing():
    simulation = EVChargingSimulation(
        create_graph()
    )

    station = create_station("S001", "C")

    simulation.add_station(station)

    ev = create_ev("EV001")

    simulation.add_ev(ev)
    simulation.process_next_ev()

    status = simulation.get_status()

    assert status["ev_count"] == 1
    assert status["station_count"] == 1
    assert status["charging"] == 1
    assert status["processed"] == 1


# ---------------------------------------------------------
# RESET
# ---------------------------------------------------------

def test_reset():
    simulation = EVChargingSimulation(
        create_graph()
    )

    station = create_station("S001", "C")

    simulation.add_station(station)

    ev = create_ev("EV001")

    simulation.add_ev(ev)
    simulation.process_next_ev()

    simulation.reset()

    assert len(simulation.evs) == 0
    assert len(simulation.processed_evs) == 0
    assert simulation.charging_manager.waiting_count() == 0
    assert simulation.charging_manager.charging_count() == 0
    assert simulation.charging_manager.completed_count() == 0

    # Stations remain registered after reset.
    assert simulation.station_count() == 1


# ---------------------------------------------------------
# CLEAR
# ---------------------------------------------------------

def test_clear():
    simulation = EVChargingSimulation(
        create_graph()
    )

    station = create_station("S001", "C")
    ev = create_ev("EV001")

    simulation.add_station(station)
    simulation.add_ev(ev)

    simulation.clear()

    assert simulation.station_count() == 0
    assert len(simulation.evs) == 0
    assert len(simulation.processed_evs) == 0
    assert simulation.charging_manager.waiting_count() == 0

# =========================================================
# EVENT HISTORY TESTS
# =========================================================

def test_event_history_after_station_addition():
    graph = Graph()

    simulation = EVChargingSimulation(graph)

    station = ChargingStation(
        "S1",
        "A",
        2
    )

    simulation.add_station(station)

    history = simulation.get_event_history()

    assert len(history) == 1

    assert history[0]["type"] == "station_added"
    assert history[0]["station_id"] == "S1"
    assert history[0]["step"] == 1


def test_event_history_after_ev_addition():
    graph = Graph()

    simulation = EVChargingSimulation(graph)

    ev = EV(
        "EV001",
        80,
        100,
        True,
        location="A"
    )

    simulation.add_ev(ev, "normal")

    history = simulation.get_event_history()

    assert len(history) == 2

    assert history[0]["type"] == "ev_arrived"
    assert history[1]["type"] == "queue_insert"

    assert history[0]["ev_id"] == "EV001"
    assert history[1]["ev_id"] == "EV001"

    assert history[1]["details"]["queue"] == "normal"


def test_event_history_automatic_priority():
    graph = Graph()

    simulation = EVChargingSimulation(graph)

    ev = EV(
        "EV001",
        10,
        100,
        True,
        location="A"
    )

    result = simulation.add_ev_automatically(ev)

    assert result == "priority"

    history = simulation.get_event_history()

    assert len(history) == 2

    assert history[0]["type"] == "ev_arrived"
    assert history[1]["type"] == "queue_insert"

    assert history[1]["details"]["queue"] == "priority"


def test_event_history_automatic_normal():
    graph = Graph()

    simulation = EVChargingSimulation(graph)

    ev = EV(
        "EV001",
        80,
        100,
        True,
        location="A"
    )

    result = simulation.add_ev_automatically(ev)

    assert result == "normal"

    history = simulation.get_event_history()

    assert len(history) == 2

    assert history[1]["details"]["queue"] == "normal"


def test_event_history_selection():
    graph = Graph()

    simulation = EVChargingSimulation(graph)

    ev = EV(
        "EV001",
        10,
        100,
        True,
        priority=1,
        location="A"
    )

    simulation.add_ev(ev, "priority")

    simulation.get_next_ev()

    history = simulation.get_event_history()

    assert len(history) == 3

    assert history[2]["type"] == "ev_selected"
    assert history[2]["ev_id"] == "EV001"
    assert history[2]["details"]["queue"] == "priority"


def test_event_history_clear():
    graph = Graph()

    simulation = EVChargingSimulation(graph)

    ev = EV(
        "EV001",
        80,
        100,
        True,
        location="A"
    )

    simulation.add_ev(ev, "normal")

    assert len(simulation.get_event_history()) > 0

    simulation.clear_event_history()

    assert simulation.get_event_history() == []

    # Event numbering should restart
    simulation.add_ev_automatically(
        EV(
            "EV002",
            80,
            100,
            True,
            location="A"
        )
    )

    history = simulation.get_event_history()

    assert history[0]["step"] == 1


def test_event_history_reset():
    graph = Graph()

    simulation = EVChargingSimulation(graph)

    station = ChargingStation(
        "S1",
        "A",
        2
    )

    simulation.add_station(station)

    ev = EV(
        "EV001",
        80,
        100,
        True,
        location="A"
    )

    simulation.add_ev(ev, "normal")

    assert len(simulation.get_event_history()) > 0

    simulation.reset()

    assert simulation.get_event_history() == []
    assert simulation.evs == []
    assert simulation.processed_evs == []

    # Stations remain after reset
    assert simulation.station_count() == 1

# =========================================================
# SIMULATION SNAPSHOT TESTS
# =========================================================

def test_snapshot_initial_state():
    graph = Graph()

    simulation = EVChargingSimulation(graph)

    snapshot = simulation.get_snapshot()

    assert "queues" in snapshot
    assert "charging" in snapshot
    assert "completed" in snapshot
    assert "stations" in snapshot
    assert "events" in snapshot

    assert snapshot["queues"]["normal"] == []
    assert snapshot["queues"]["priority"] == []
    assert snapshot["queues"]["special"] == []

    assert snapshot["charging"] == []
    assert snapshot["completed"] == []
    assert snapshot["stations"] == []
    assert snapshot["events"] == []


def test_snapshot_normal_queue():
    graph = Graph()

    simulation = EVChargingSimulation(graph)

    ev = EV(
        "EV001",
        80,
        100,
        True,
        location="A"
    )

    simulation.add_ev(ev, "normal")

    snapshot = simulation.get_snapshot()

    assert len(snapshot["queues"]["normal"]) == 1

    assert snapshot["queues"]["normal"][0]["ev_id"] == "EV001"
    assert snapshot["queues"]["normal"][0]["battery_level"] == 80
    assert snapshot["queues"]["normal"][0]["battery_capacity"] == 100
    assert snapshot["queues"]["normal"][0]["location"] == "A"


def test_snapshot_priority_queue():
    graph = Graph()

    simulation = EVChargingSimulation(graph)

    ev = EV(
        "EV001",
        10,
        100,
        True,
        priority=1,
        location="A"
    )

    simulation.add_ev(ev, "priority")

    snapshot = simulation.get_snapshot()

    assert len(snapshot["queues"]["priority"]) == 1

    assert snapshot["queues"]["priority"][0]["ev_id"] == "EV001"
    assert snapshot["queues"]["priority"][0]["priority"] == 1


def test_snapshot_special_deque():
    graph = Graph()

    simulation = EVChargingSimulation(graph)

    ev = EV(
        "EV001",
        80,
        100,
        True,
        location="A"
    )

    simulation.add_ev(ev, "special")

    snapshot = simulation.get_snapshot()

    assert len(snapshot["queues"]["special"]) == 1

    assert snapshot["queues"]["special"][0]["ev_id"] == "EV001"


def test_snapshot_station():
    graph = Graph()

    simulation = EVChargingSimulation(graph)

    station = ChargingStation(
        "S1",
        "A",
        2
    )

    simulation.add_station(station)

    snapshot = simulation.get_snapshot()

    assert len(snapshot["stations"]) == 1

    station_data = snapshot["stations"][0]

    assert station_data["station_id"] == "S1"
    assert station_data["location"] == "A"
    assert station_data["charging_slots"] == 2
    assert station_data["active_evs"] == []
    assert station_data["available_slots"] == 2


def test_snapshot_contains_events():
    graph = Graph()

    simulation = EVChargingSimulation(graph)

    ev = EV(
        "EV001",
        80,
        100,
        True,
        location="A"
    )

    simulation.add_ev(ev, "normal")

    snapshot = simulation.get_snapshot()

    assert len(snapshot["events"]) == 2

    assert snapshot["events"][0]["type"] == "ev_arrived"
    assert snapshot["events"][1]["type"] == "queue_insert"


def test_snapshot_after_processing():
    graph = Graph()

    graph.add_vertex("A")
    graph.add_vertex("B")

    graph.add_edge("A", "B", 5)

    simulation = EVChargingSimulation(graph)

    station = ChargingStation(
        "S1",
        "B",
        2
    )

    simulation.add_station(station)

    ev = EV(
        "EV001",
        80,
        100,
        True,
        location="A"
    )

    simulation.add_ev(ev, "normal")

    result = simulation.process_next_ev()

    assert result["success"] is True

    snapshot = simulation.get_snapshot()

    assert len(snapshot["charging"]) == 1

    assert snapshot["charging"][0]["ev_id"] == "EV001"
    assert snapshot["charging"][0]["station_id"] == "S1"

    assert len(snapshot["stations"]) == 1

    assert snapshot["stations"][0]["active_evs"] == ["EV001"]

    assert snapshot["stations"][0]["available_slots"] == 1