class EVDeque:
    """
    Circular Array Based Double-Ended Queue (Deque).

    Supports insertion and deletion from both ends.

    EV use case:
    - VIP EVs can enter from the front.
    - Normal EVs can enter from the rear.
    - EVs can be removed from either end.
    """

    def __init__(self, capacity=10):
        if capacity <= 0:
            raise ValueError("Deque capacity must be greater than 0")

        self.capacity = capacity
        self._data = [None] * capacity

        self.front = 0
        self.rear = -1
        self._size = 0

    def add_front(self, ev):
        """
        Add an EV to the front.

        Time Complexity: O(1)
        """

        if self.is_full():
            raise OverflowError("Deque is full")

        # First element
        if self.is_empty():
            self.front = 0
            self.rear = 0
            self._data[self.front] = ev

        else:
            # Move front one position backwards circularly
            self.front = (self.front - 1) % self.capacity
            self._data[self.front] = ev

        self._size += 1

    def add_rear(self, ev):
        """
        Add an EV to the rear.

        Time Complexity: O(1)
        """

        if self.is_full():
            raise OverflowError("Deque is full")

        # First element
        if self.is_empty():
            self.front = 0
            self.rear = 0
            self._data[self.rear] = ev

        else:
            # Move rear one position forward circularly
            self.rear = (self.rear + 1) % self.capacity
            self._data[self.rear] = ev

        self._size += 1

    def remove_front(self):
        """
        Remove and return the EV from the front.

        Time Complexity: O(1)
        """

        if self.is_empty():
            raise IndexError("Deque is empty")

        ev = self._data[self.front]
        self._data[self.front] = None

        # Removing the last element
        if self._size == 1:
            self.front = 0
            self.rear = -1

        else:
            self.front = (self.front + 1) % self.capacity

        self._size -= 1

        return ev

    def remove_rear(self):
        """
        Remove and return the EV from the rear.

        Time Complexity: O(1)
        """

        if self.is_empty():
            raise IndexError("Deque is empty")

        ev = self._data[self.rear]
        self._data[self.rear] = None

        # Removing the last element
        if self._size == 1:
            self.front = 0
            self.rear = -1

        else:
            self.rear = (self.rear - 1) % self.capacity

        self._size -= 1

        return ev

    def peek_front(self):
        """
        Return the front EV without removing it.

        Time Complexity: O(1)
        """

        if self.is_empty():
            raise IndexError("Deque is empty")

        return self._data[self.front]

    def peek_rear(self):
        """
        Return the rear EV without removing it.

        Time Complexity: O(1)
        """

        if self.is_empty():
            raise IndexError("Deque is empty")

        return self._data[self.rear]

    def is_empty(self):
        """
        Check whether deque is empty.

        Time Complexity: O(1)
        """

        return self._size == 0

    def is_full(self):
        """
        Check whether deque is full.

        Time Complexity: O(1)
        """

        return self._size == self.capacity

    def size(self):
        """
        Return number of elements.

        Time Complexity: O(1)
        """

        return self._size

    def display(self):
        """
        Return elements from front to rear.

        Time Complexity: O(n)
        """

        elements = []

        for i in range(self._size):
            index = (self.front + i) % self.capacity
            elements.append(self._data[index])

        return elements

    def clear(self):
        """
        Remove all elements.

        Time Complexity: O(1)
        """

        self._data = [None] * self.capacity
        self.front = 0
        self.rear = -1
        self._size = 0

    def __len__(self):
        """Allows len(deque)."""

        return self._size

    def __str__(self):
        """Human-readable representation."""

        return " <-> ".join(str(ev) for ev in self.display())