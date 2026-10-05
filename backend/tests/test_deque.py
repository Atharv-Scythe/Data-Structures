import pytest

from src.data_structures.deque import EVDeque


def test_deque_creation():
    deque = EVDeque(5)

    assert deque.is_empty()
    assert not deque.is_full()
    assert deque.size() == 0


def test_add_rear():
    deque = EVDeque(5)

    deque.add_rear("EV1")
    deque.add_rear("EV2")
    deque.add_rear("EV3")

    assert deque.display() == ["EV1", "EV2", "EV3"]
    assert deque.size() == 3


def test_add_front():
    deque = EVDeque(5)

    deque.add_front("EV1")
    deque.add_front("EV2")
    deque.add_front("EV3")

    assert deque.display() == ["EV3", "EV2", "EV1"]
    assert deque.size() == 3


def test_add_both_ends():
    deque = EVDeque(5)

    deque.add_rear("EV2")
    deque.add_rear("EV3")
    deque.add_front("EV1")
    deque.add_rear("EV4")
    deque.add_front("VIP")

    assert deque.display() == [
        "VIP",
        "EV1",
        "EV2",
        "EV3",
        "EV4"
    ]


def test_remove_front():
    deque = EVDeque(5)

    deque.add_rear("EV1")
    deque.add_rear("EV2")
    deque.add_rear("EV3")

    assert deque.remove_front() == "EV1"
    assert deque.display() == ["EV2", "EV3"]


def test_remove_rear():
    deque = EVDeque(5)

    deque.add_rear("EV1")
    deque.add_rear("EV2")
    deque.add_rear("EV3")

    assert deque.remove_rear() == "EV3"
    assert deque.display() == ["EV1", "EV2"]


def test_remove_from_both_ends():
    deque = EVDeque(5)

    deque.add_rear("EV2")
    deque.add_rear("EV3")
    deque.add_front("EV1")

    assert deque.remove_front() == "EV1"
    assert deque.remove_rear() == "EV3"

    assert deque.display() == ["EV2"]


def test_peek_front():
    deque = EVDeque(5)

    deque.add_rear("EV1")
    deque.add_rear("EV2")

    assert deque.peek_front() == "EV1"
    assert deque.size() == 2


def test_peek_rear():
    deque = EVDeque(5)

    deque.add_rear("EV1")
    deque.add_rear("EV2")

    assert deque.peek_rear() == "EV2"
    assert deque.size() == 2


def test_empty_deque():
    deque = EVDeque(5)

    with pytest.raises(IndexError):
        deque.remove_front()

    with pytest.raises(IndexError):
        deque.remove_rear()

    with pytest.raises(IndexError):
        deque.peek_front()

    with pytest.raises(IndexError):
        deque.peek_rear()


def test_full_deque():
    deque = EVDeque(2)

    deque.add_rear("EV1")
    deque.add_rear("EV2")

    assert deque.is_full()

    with pytest.raises(OverflowError):
        deque.add_rear("EV3")

    with pytest.raises(OverflowError):
        deque.add_front("EV3")


def test_circular_behavior():
    deque = EVDeque(3)

    deque.add_rear("EV1")
    deque.add_rear("EV2")
    deque.add_rear("EV3")

    assert deque.remove_front() == "EV1"

    deque.add_front("EV4")

    assert deque.display() == ["EV4", "EV2", "EV3"]


def test_clear():
    deque = EVDeque(5)

    deque.add_rear("EV1")
    deque.add_front("EV2")

    deque.clear()

    assert deque.is_empty()
    assert deque.size() == 0
    assert deque.display() == []


def test_len():
    deque = EVDeque(5)

    deque.add_rear("EV1")
    deque.add_rear("EV2")

    assert len(deque) == 2