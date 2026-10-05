import pytest

from src.models.ev import EV


def test_create_ev():
    ev = EV(
        ev_id="EV001",
        battery_level=30,
        battery_capacity=60,
        charging_required=70,
        priority=1
    )

    assert ev.ev_id == "EV001"
    assert ev.battery_level == 30
    assert ev.battery_capacity == 60
    assert ev.charging_required == 70
    assert ev.priority == 1


def test_critical_ev():
    ev = EV(
        ev_id="EV001",
        battery_level=15,
        battery_capacity=60,
        charging_required=85
    )

    assert ev.is_critical()


def test_non_critical_ev():
    ev = EV(
        ev_id="EV002",
        battery_level=60,
        battery_capacity=60,
        charging_required=40
    )

    assert not ev.is_critical()


def test_critical_threshold():
    ev = EV(
        ev_id="EV003",
        battery_level=20,
        battery_capacity=60,
        charging_required=80
    )

    assert ev.is_critical()


def test_battery_needed():
    ev = EV(
        ev_id="EV004",
        battery_level=40,
        battery_capacity=60,
        charging_required=60
    )

    assert ev.battery_needed() == 60


def test_ev_string():
    ev = EV(
        ev_id="EV005",
        battery_level=25,
        battery_capacity=60,
        charging_required=75,
        priority=2
    )

    output = str(ev)

    assert "EV005" in output
    assert "25%" in output
    assert "Priority=2" in output


def test_default_priority():
    ev = EV(
        ev_id="EV006",
        battery_level=50,
        battery_capacity=60,
        charging_required=50
    )

    assert ev.priority == 0