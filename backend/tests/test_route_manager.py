import pytest

from src.algorithms.graph import Graph
from src.models.station import ChargingStation
from src.services.route_manager import RouteManager


# ---------------------------------------------------------
# HELPER
# ---------------------------------------------------------

def create_graph():
    """
    Create a sample road network:

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


def create_station(station_id, location, slots=1):
    return ChargingStation(
        station_id=station_id,
        location=location,
        charging_slots=slots
    )


# ---------------------------------------------------------
# INITIALIZATION
# ---------------------------------------------------------

def test_create_route_manager():
    graph = create_graph()

    manager = RouteManager(graph)

    assert manager.graph == graph
    assert manager.station_count() == 0


# ---------------------------------------------------------
# STATION MANAGEMENT
# ---------------------------------------------------------

def test_add_station():
    graph = create_graph()
    manager = RouteManager(graph)

    station = create_station("S001", "D")

    manager.add_station(station)

    assert manager.station_count() == 1
    assert station in manager.get_stations()


def test_add_multiple_stations():
    graph = create_graph()
    manager = RouteManager(graph)

    station1 = create_station("S001", "C")
    station2 = create_station("S002", "D")
    station3 = create_station("S003", "E")

    manager.add_station(station1)
    manager.add_station(station2)
    manager.add_station(station3)

    assert manager.station_count() == 3


def test_duplicate_station_not_added():
    graph = create_graph()
    manager = RouteManager(graph)

    station = create_station("S001", "C")

    manager.add_station(station)
    manager.add_station(station)

    assert manager.station_count() == 1


def test_remove_station():
    graph = create_graph()
    manager = RouteManager(graph)

    station = create_station("S001", "C")

    manager.add_station(station)

    result = manager.remove_station(station)

    assert result is True
    assert manager.station_count() == 0
    assert station not in manager.get_stations()


def test_remove_nonexistent_station():
    graph = create_graph()
    manager = RouteManager(graph)

    station = create_station("S001", "C")

    assert manager.remove_station(station) is False


def test_get_stations_returns_copy():
    graph = create_graph()
    manager = RouteManager(graph)

    station = create_station("S001", "C")

    manager.add_station(station)

    stations = manager.get_stations()

    stations.clear()

    assert manager.station_count() == 1


# ---------------------------------------------------------
# ROUTE CALCULATION
# ---------------------------------------------------------

def test_calculate_route():
    graph = create_graph()
    manager = RouteManager(graph)

    result = manager.calculate_route("A", "D")

    assert result["distance"] == 3
    assert result["path"] == ["A", "C", "D"]


def test_calculate_direct_route():
    graph = create_graph()
    manager = RouteManager(graph)

    result = manager.calculate_route("A", "B")

    assert result["distance"] == 4
    assert result["path"] == ["A", "B"]


def test_calculate_route_to_same_location():
    graph = create_graph()
    manager = RouteManager(graph)

    result = manager.calculate_route("A", "A")

    assert result["distance"] == 0
    assert result["path"] == ["A"]


def test_invalid_start_location():
    graph = create_graph()
    manager = RouteManager(graph)

    with pytest.raises(KeyError):
        manager.calculate_route("X", "A")


def test_invalid_destination():
    graph = create_graph()
    manager = RouteManager(graph)

    with pytest.raises(KeyError):
        manager.calculate_route("A", "X")


# ---------------------------------------------------------
# STATION ROUTES
# ---------------------------------------------------------

def test_get_station_routes():
    graph = create_graph()
    manager = RouteManager(graph)

    station1 = create_station("S001", "C")
    station2 = create_station("S002", "D")

    manager.add_station(station1)
    manager.add_station(station2)

    routes = manager.get_station_routes("A")

    assert len(routes) == 2

    assert routes[0]["station"] == station1
    assert routes[0]["distance"] == 2
    assert routes[0]["path"] == ["A", "C"]

    assert routes[1]["station"] == station2
    assert routes[1]["distance"] == 3
    assert routes[1]["path"] == ["A", "C", "D"]


def test_station_route_availability():
    graph = create_graph()
    manager = RouteManager(graph)

    station = create_station(
        "S001",
        "C",
        slots=1
    )

    manager.add_station(station)

    routes = manager.get_station_routes("A")

    assert len(routes) == 1
    assert routes[0]["available"] is True


def test_station_route_unavailable():
    graph = create_graph()
    manager = RouteManager(graph)

    station = create_station(
        "S001",
        "C",
        slots=1
    )

    manager.add_station(station)

    # Fill the only charging slot
    station.start_charging("EV")

    routes = manager.get_station_routes("A")

    assert len(routes) == 1
    assert routes[0]["available"] is False


# ---------------------------------------------------------
# AVAILABLE STATIONS
# ---------------------------------------------------------

def test_get_available_stations():
    graph = create_graph()
    manager = RouteManager(graph)

    station1 = create_station("S001", "C", slots=1)
    station2 = create_station("S002", "D", slots=1)

    manager.add_station(station1)
    manager.add_station(station2)

    # Make station D unavailable
    station2.start_charging("EV")

    available = manager.get_available_stations("A")

    assert len(available) == 1
    assert available[0]["station"] == station1


def test_no_available_stations():
    graph = create_graph()
    manager = RouteManager(graph)

    station1 = create_station("S001", "C", slots=1)
    station2 = create_station("S002", "D", slots=1)

    station1.start_charging("EV1")
    station2.start_charging("EV2")

    manager.add_station(station1)
    manager.add_station(station2)

    available = manager.get_available_stations("A")

    assert available == []


# ---------------------------------------------------------
# NEAREST STATION
# ---------------------------------------------------------

def test_find_nearest_station():
    graph = create_graph()
    manager = RouteManager(graph)

    station1 = create_station("S001", "D")
    station2 = create_station("S002", "C")

    manager.add_station(station1)
    manager.add_station(station2)

    result = manager.find_nearest_station("A")

    assert result["station"] == station2
    assert result["distance"] == 2
    assert result["path"] == ["A", "C"]


def test_find_nearest_station_ignores_full_station():
    graph = create_graph()
    manager = RouteManager(graph)

    nearest_station = create_station(
        "S001",
        "C",
        slots=1
    )

    farther_station = create_station(
        "S002",
        "D",
        slots=1
    )

    # Nearest station is full
    nearest_station.start_charging("EV")

    manager.add_station(nearest_station)
    manager.add_station(farther_station)

    result = manager.find_nearest_station("A")

    assert result["station"] == farther_station
    assert result["distance"] == 3


def test_find_nearest_station_no_stations():
    graph = create_graph()
    manager = RouteManager(graph)

    result = manager.find_nearest_station("A")

    assert result is None


def test_find_nearest_station_all_full():
    graph = create_graph()
    manager = RouteManager(graph)

    station1 = create_station("S001", "C", slots=1)
    station2 = create_station("S002", "D", slots=1)

    station1.start_charging("EV1")
    station2.start_charging("EV2")

    manager.add_station(station1)
    manager.add_station(station2)

    result = manager.find_nearest_station("A")

    assert result is None


# ---------------------------------------------------------
# UNREACHABLE STATIONS
# ---------------------------------------------------------

def test_unreachable_station_is_ignored():
    graph = Graph()

    graph.add_edge("A", "B", 5)
    graph.add_vertex("C")

    manager = RouteManager(graph)

    station = create_station("S001", "C")

    manager.add_station(station)

    routes = manager.get_station_routes("A")

    assert routes == []


# ---------------------------------------------------------
# CLEAR
# ---------------------------------------------------------

def test_clear():
    graph = create_graph()
    manager = RouteManager(graph)

    station1 = create_station("S001", "C")
    station2 = create_station("S002", "D")

    manager.add_station(station1)
    manager.add_station(station2)

    assert manager.station_count() == 2

    manager.clear()

    assert manager.station_count() == 0
    assert manager.get_stations() == []