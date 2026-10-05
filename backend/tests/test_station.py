import pytest

from src.models.ev import EV
from src.models.station import ChargingStation


def create_ev(ev_id):
    return EV(
        ev_id=ev_id,
        battery_level=30,
        battery_capacity=60,
        charging_required=70
    )


def test_create_station():
    station = ChargingStation(
        station_id="S001",
        location="Pune",
        charging_slots=2
    )

    assert station.station_id == "S001"
    assert station.location == "Pune"
    assert station.charging_slots == 2
    assert station.active_count() == 0


def test_available_slot():
    station = ChargingStation(
        station_id="S001",
        location="Pune",
        charging_slots=2
    )

    assert station.has_available_slot()


def test_start_charging():
    station = ChargingStation(
        station_id="S001",
        location="Pune",
        charging_slots=2
    )

    ev = create_ev("EV001")

    result = station.start_charging(ev)

    assert result is True
    assert ev in station.active_evs
    assert station.active_count() == 1


def test_multiple_charging_evs():
    station = ChargingStation(
        station_id="S001",
        location="Pune",
        charging_slots=2
    )

    ev1 = create_ev("EV001")
    ev2 = create_ev("EV002")

    assert station.start_charging(ev1)
    assert station.start_charging(ev2)

    assert station.active_count() == 2


def test_station_full():
    station = ChargingStation(
        station_id="S001",
        location="Pune",
        charging_slots=1
    )

    ev1 = create_ev("EV001")
    ev2 = create_ev("EV002")

    assert station.start_charging(ev1)
    assert station.start_charging(ev2) is False

    assert station.active_count() == 1
    assert not station.has_available_slot()


def test_stop_charging():
    station = ChargingStation(
        station_id="S001",
        location="Pune",
        charging_slots=2
    )

    ev = create_ev("EV001")

    station.start_charging(ev)

    result = station.stop_charging(ev)

    assert result is True
    assert ev not in station.active_evs
    assert station.active_count() == 0


def test_stop_nonexistent_ev():
    station = ChargingStation(
        station_id="S001",
        location="Pune",
        charging_slots=2
    )

    ev = create_ev("EV001")

    assert station.stop_charging(ev) is False


def test_slot_available_after_stop():
    station = ChargingStation(
        station_id="S001",
        location="Pune",
        charging_slots=1
    )

    ev1 = create_ev("EV001")
    ev2 = create_ev("EV002")

    station.start_charging(ev1)

    assert not station.has_available_slot()

    station.stop_charging(ev1)

    assert station.has_available_slot()
    assert station.start_charging(ev2)


def test_station_string():
    station = ChargingStation(
        station_id="S001",
        location="Pune",
        charging_slots=2
    )

    ev = create_ev("EV001")
    station.start_charging(ev)

    output = str(station)

    assert "S001" in output
    assert "Pune" in output
    assert "Slots=2" in output
    assert "Active=1" in output