class SimpleQueue:
    """
    Circular Array Based Queue

    FIFO - First In, First Out

    Used in the Smart EV Charging System to represent
    normal EVs waiting for charging in arrival order.
    """

    def __init__(self, capacity=10):
        if capacity <= 0:
            raise ValueError("Queue capacity must be greater than 0")

        self.capacity = capacity
        self._data = [None] * capacity

        self.front = 0
        self.rear = -1
        self._size = 0

    def enqueue(self, ev):
        """
        Add an EV to the rear of the queue.

        Time Complexity: O(1)
        """

        if self.is_full():
            raise OverflowError("Queue is full")

        self.rear = (self.rear + 1) % self.capacity
        self._data[self.rear] = ev
        self._size += 1

    def dequeue(self):
        """
        Remove and return the EV at the front.

        Time Complexity: O(1)
        """

        if self.is_empty():
            raise IndexError("Queue is empty")

        ev = self._data[self.front]

        self._data[self.front] = None
        self.front = (self.front + 1) % self.capacity
        self._size -= 1

        return ev

    def peek(self):
        """
        Return the EV at the front without removing it.

        Time Complexity: O(1)
        """

        if self.is_empty():
            raise IndexError("Queue is empty")

        return self._data[self.front]

    def is_empty(self):
        """
        Check whether the queue is empty.

        Time Complexity: O(1)
        """

        return self._size == 0

    def is_full(self):
        """
        Check whether the queue is full.

        Time Complexity: O(1)
        """

        return self._size == self.capacity

    def size(self):
        """
        Return the number of EVs currently in the queue.

        Time Complexity: O(1)
        """

        return self._size

    def display(self):
        """
        Return all EVs from front to rear.

        Time Complexity: O(n)
        """

        elements = []

        for i in range(self._size):
            index = (self.front + i) % self.capacity
            elements.append(self._data[index])

        return elements

    def clear(self):
        """
        Remove all EVs from the queue.

        Time Complexity: O(n)
        """

        self._data = [None] * self.capacity
        self.front = 0
        self.rear = -1
        self._size = 0

    def __len__(self):
        """
        Allows len(queue).

        Time Complexity: O(1)
        """

        return self._size

    def __str__(self):
        """
        Human-readable representation of the queue.
        """

        return " <- ".join(str(ev) for ev in self.display())