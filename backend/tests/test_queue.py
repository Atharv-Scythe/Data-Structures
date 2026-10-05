import pytest

from src.data_structures.queue import SimpleQueue


def test_queue_creation():
    queue = SimpleQueue(5)

    assert queue.is_empty()
    assert not queue.is_full()
    assert queue.size() == 0


def test_enqueue():
    queue = SimpleQueue(5)

    queue.enqueue("EV1")
    queue.enqueue("EV2")
    queue.enqueue("EV3")

    assert queue.size() == 3
    assert queue.display() == ["EV1", "EV2", "EV3"]


def test_fifo_order():
    queue = SimpleQueue(5)

    queue.enqueue("EV1")
    queue.enqueue("EV2")
    queue.enqueue("EV3")

    assert queue.dequeue() == "EV1"
    assert queue.dequeue() == "EV2"
    assert queue.dequeue() == "EV3"


def test_peek():
    queue = SimpleQueue(5)

    queue.enqueue("EV1")
    queue.enqueue("EV2")

    assert queue.peek() == "EV1"
    assert queue.size() == 2


def test_empty_queue():
    queue = SimpleQueue(5)

    with pytest.raises(IndexError):
        queue.dequeue()

    with pytest.raises(IndexError):
        queue.peek()


def test_full_queue():
    queue = SimpleQueue(2)

    queue.enqueue("EV1")
    queue.enqueue("EV2")

    assert queue.is_full()

    with pytest.raises(OverflowError):
        queue.enqueue("EV3")


def test_circular_behavior():
    queue = SimpleQueue(3)

    queue.enqueue("EV1")
    queue.enqueue("EV2")
    queue.enqueue("EV3")

    assert queue.dequeue() == "EV1"
    assert queue.dequeue() == "EV2"

    queue.enqueue("EV4")
    queue.enqueue("EV5")

    assert queue.display() == ["EV3", "EV4", "EV5"]


def test_clear():
    queue = SimpleQueue(5)

    queue.enqueue("EV1")
    queue.enqueue("EV2")

    queue.clear()

    assert queue.is_empty()
    assert queue.size() == 0
    assert queue.display() == []


def test_len():
    queue = SimpleQueue(5)

    queue.enqueue("EV1")
    queue.enqueue("EV2")

    assert len(queue) == 2