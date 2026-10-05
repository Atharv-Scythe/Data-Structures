from src.models.ev import EV
from src.models.station import ChargingStation
from src.services.charging_manager import ChargingManager


def create_ev(
    ev_id,
    battery_level=50,
    priority=5
):
    return EV(
        ev_id=ev_id,
        battery_level=battery_level,
        battery_capacity=60,
        charging_required=50,
        priority=priority
    )


# ---------------------------------------------------------
# NORMAL QUEUE TESTS
# ---------------------------------------------------------

def test_add_normal_ev():
    manager = ChargingManager()

    ev = create_ev("EV001")

    manager.add_normal_ev(ev)

    assert manager.normal_queue.size() == 1
    assert manager.waiting_count() == 1


def test_normal_ev_fifo_order():
    manager = ChargingManager()

    ev1 = create_ev("EV001")
    ev2 = create_ev("EV002")
    ev3 = create_ev("EV003")

    manager.add_normal_ev(ev1)
    manager.add_normal_ev(ev2)
    manager.add_normal_ev(ev3)

    assert manager.get_next_normal_ev() == ev1
    assert manager.get_next_normal_ev() == ev2
    assert manager.get_next_normal_ev() == ev3


def test_empty_normal_queue():
    manager = ChargingManager()

    assert manager.get_next_normal_ev() is None


# ---------------------------------------------------------
# PRIORITY QUEUE TESTS
# ---------------------------------------------------------

def test_add_priority_ev():
    manager = ChargingManager()

    ev = create_ev(
        "EV001",
        battery_level=10,
        priority=1
    )

    manager.add_priority_ev(ev)

    assert manager.priority_queue.size() == 1
    assert manager.waiting_count() == 1


def test_priority_order():
    manager = ChargingManager()

    ev1 = create_ev("EV001", priority=5)
    ev2 = create_ev("EV002", priority=1)
    ev3 = create_ev("EV003", priority=3)

    manager.add_priority_ev(ev1)
    manager.add_priority_ev(ev2)
    manager.add_priority_ev(ev3)

    assert manager.get_next_priority_ev() == ev2
    assert manager.get_next_priority_ev() == ev3
    assert manager.get_next_priority_ev() == ev1


def test_empty_priority_queue():
    manager = ChargingManager()

    assert manager.get_next_priority_ev() is None


# ---------------------------------------------------------
# DEQUE TESTS
# ---------------------------------------------------------

def test_add_special_ev_rear():
    manager = ChargingManager()

    ev = create_ev("EV001")

    manager.add_special_ev(ev)

    assert manager.special_deque.size() == 1
    assert manager.waiting_count() == 1


def test_add_special_ev_front():
    manager = ChargingManager()

    ev1 = create_ev("EV001")
    ev2 = create_ev("EV002")

    manager.add_special_ev(ev1)
    manager.add_special_ev(ev2, front=True)

    assert manager.get_next_special_ev() == ev2
    assert manager.get_next_special_ev() == ev1


def test_special_ev_rear_order():
    manager = ChargingManager()

    ev1 = create_ev("EV001")
    ev2 = create_ev("EV002")
    ev3 = create_ev("EV003")

    manager.add_special_ev(ev1)
    manager.add_special_ev(ev2)
    manager.add_special_ev(ev3)

    assert manager.get_next_special_ev() == ev1
    assert manager.get_next_special_ev() == ev2
    assert manager.get_next_special_ev() == ev3


def test_empty_special_deque():
    manager = ChargingManager()

    assert manager.get_next_special_ev() is None


# ---------------------------------------------------------
# CHARGING TESTS
# ---------------------------------------------------------

def test_start_charging():
    manager = ChargingManager()

    station = ChargingStation(
        station_id="S001",
        location="Pune",
        charging_slots=1
    )

    ev = create_ev("EV001")

    result = manager.start_charging(ev, station)

    assert result is True
    assert ev in station.active_evs
    assert ev in manager.charging_evs
    assert manager.charging_count() == 1


def test_station_full():
    manager = ChargingManager()

    station = ChargingStation(
        station_id="S001",
        location="Pune",
        charging_slots=1
    )

    ev1 = create_ev("EV001")
    ev2 = create_ev("EV002")

    assert manager.start_charging(ev1, station) is True
    assert manager.start_charging(ev2, station) is False

    assert manager.charging_count() == 1
    assert ev2 not in manager.charging_evs


def test_complete_charging():
    manager = ChargingManager()

    station = ChargingStation(
        station_id="S001",
        location="Pune",
        charging_slots=1
    )

    ev = create_ev("EV001")

    manager.start_charging(ev, station)

    result = manager.complete_charging(ev, station)

    assert result is True
    assert ev not in manager.charging_evs
    assert ev in manager.completed_evs
    assert manager.charging_count() == 0
    assert manager.completed_count() == 1


def test_complete_non_charging_ev():
    manager = ChargingManager()

    station = ChargingStation(
        station_id="S001",
        location="Pune",
        charging_slots=1
    )

    ev = create_ev("EV001")

    result = manager.complete_charging(ev, station)

    assert result is False
    assert manager.completed_count() == 0


# ---------------------------------------------------------
# COUNT TESTS
# ---------------------------------------------------------

def test_waiting_count():
    manager = ChargingManager()

    normal_ev = create_ev("EV001")
    priority_ev = create_ev("EV002", priority=1)
    special_ev = create_ev("EV003")

    manager.add_normal_ev(normal_ev)
    manager.add_priority_ev(priority_ev)
    manager.add_special_ev(special_ev)

    assert manager.waiting_count() == 3


def test_charging_count():
    manager = ChargingManager()

    station = ChargingStation(
        station_id="S001",
        location="Pune",
        charging_slots=2
    )

    ev1 = create_ev("EV001")
    ev2 = create_ev("EV002")

    manager.start_charging(ev1, station)
    manager.start_charging(ev2, station)

    assert manager.charging_count() == 2


def test_completed_count():
    manager = ChargingManager()

    station = ChargingStation(
        station_id="S001",
        location="Pune",
        charging_slots=1
    )

    ev = create_ev("EV001")

    manager.start_charging(ev, station)
    manager.complete_charging(ev, station)

    assert manager.completed_count() == 1


def test_total_ev_count():
    manager = ChargingManager()

    station = ChargingStation(
        station_id="S001",
        location="Pune",
        charging_slots=1
    )

    ev1 = create_ev("EV001")
    ev2 = create_ev("EV002")
    ev3 = create_ev("EV003")

    manager.add_normal_ev(ev1)
    manager.add_priority_ev(ev2)

    manager.start_charging(ev3, station)

    assert manager.total_ev_count() == 3


# ---------------------------------------------------------
# STATUS TESTS
# ---------------------------------------------------------

def test_get_status():
    manager = ChargingManager()

    station = ChargingStation(
        station_id="S001",
        location="Pune",
        charging_slots=1
    )

    ev1 = create_ev("EV001")
    ev2 = create_ev("EV002", priority=1)
    ev3 = create_ev("EV003")
    ev4 = create_ev("EV004")

    manager.add_normal_ev(ev1)
    manager.add_priority_ev(ev2)
    manager.add_special_ev(ev3)

    manager.start_charging(ev4, station)

    status = manager.get_status()

    assert status["waiting_normal"] == 1
    assert status["waiting_priority"] == 1
    assert status["waiting_special"] == 1
    assert status["charging"] == 1
    assert status["completed"] == 0
    assert status["total"] == 4


# ---------------------------------------------------------
# CLEAR TEST
# ---------------------------------------------------------

def test_clear():
    manager = ChargingManager()

    station = ChargingStation(
        station_id="S001",
        location="Pune",
        charging_slots=1
    )

    ev1 = create_ev("EV001")
    ev2 = create_ev("EV002", priority=1)
    ev3 = create_ev("EV003")
    ev4 = create_ev("EV004")

    manager.add_normal_ev(ev1)
    manager.add_priority_ev(ev2)
    manager.add_special_ev(ev3)

    manager.start_charging(ev4, station)
    manager.complete_charging(ev4, station)

    manager.clear()

    assert manager.waiting_count() == 0
    assert manager.charging_count() == 0
    assert manager.completed_count() == 0
    assert manager.total_ev_count() == 0