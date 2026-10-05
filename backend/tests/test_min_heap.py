import pytest

from src.data_structures.min_heap import MinHeap


def test_heap_creation():
    heap = MinHeap()

    assert heap.is_empty()
    assert heap.size() == 0


def test_insert():
    heap = MinHeap()

    heap.insert("EV1", 40)
    heap.insert("EV2", 20)
    heap.insert("EV3", 50)
    heap.insert("EV4", 10)
    heap.insert("EV5", 30)

    assert heap.size() == 5
    assert heap.peek_min() == (10, "EV4")


def test_heapify_up():
    heap = MinHeap()

    heap.insert("EV1", 50)
    heap.insert("EV2", 40)
    heap.insert("EV3", 30)
    heap.insert("EV4", 20)
    heap.insert("EV5", 10)

    assert heap.peek_min() == (10, "EV5")


def test_extract_min():
    heap = MinHeap()

    heap.insert("EV1", 40)
    heap.insert("EV2", 20)
    heap.insert("EV3", 50)
    heap.insert("EV4", 10)
    heap.insert("EV5", 30)

    assert heap.extract_min() == (10, "EV4")

    assert heap.size() == 4

    assert heap.peek_min() == (20, "EV2")


def test_priority_order():
    heap = MinHeap()

    heap.insert("EV1", 40)
    heap.insert("EV2", 20)
    heap.insert("EV3", 50)
    heap.insert("EV4", 10)
    heap.insert("EV5", 30)

    priorities = []

    while not heap.is_empty():
        priority, item = heap.extract_min()
        priorities.append(priority)

    assert priorities == [10, 20, 30, 40, 50]


def test_peek_does_not_remove():
    heap = MinHeap()

    heap.insert("EV1", 30)
    heap.insert("EV2", 10)

    result = heap.peek_min()

    assert result == (10, "EV2")
    assert heap.size() == 2


def test_extract_empty_heap():
    heap = MinHeap()

    with pytest.raises(IndexError):
        heap.extract_min()


def test_peek_empty_heap():
    heap = MinHeap()

    with pytest.raises(IndexError):
        heap.peek_min()


def test_clear():
    heap = MinHeap()

    heap.insert("EV1", 40)
    heap.insert("EV2", 10)
    heap.insert("EV3", 20)

    heap.clear()

    assert heap.is_empty()
    assert heap.size() == 0


def test_len():
    heap = MinHeap()

    heap.insert("EV1", 30)
    heap.insert("EV2", 20)
    heap.insert("EV3", 10)

    assert len(heap) == 3


def test_duplicate_priorities():
    heap = MinHeap()

    heap.insert("EV1", 10)
    heap.insert("EV2", 10)
    heap.insert("EV3", 20)

    assert heap.extract_min()[0] == 10
    assert heap.extract_min()[0] == 10
    assert heap.extract_min()[0] == 20


def test_heap_property():
    heap = MinHeap()

    heap.insert("EV1", 70)
    heap.insert("EV2", 40)
    heap.insert("EV3", 60)
    heap.insert("EV4", 10)
    heap.insert("EV5", 30)
    heap.insert("EV6", 20)
    heap.insert("EV7", 50)

    data = heap.display()

    for i in range(len(data)):
        left = 2 * i + 1
        right = 2 * i + 2

        if left < len(data):
            assert data[i][0] <= data[left][0]

        if right < len(data):
            assert data[i][0] <= data[right][0]