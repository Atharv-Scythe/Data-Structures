class MinHeap:
    """
    Array-based Min Heap implementation.

    The smallest-priority element always remains at the root.

    This data structure will later be used for:
    1. EV priority scheduling
    2. Dijkstra's shortest-path algorithm
    """

    def __init__(self):
        self._heap = []

    def _parent(self, index):
        """Return parent index."""
        return (index - 1) // 2

    def _left_child(self, index):
        """Return left child index."""
        return 2 * index + 1

    def _right_child(self, index):
        """Return right child index."""
        return 2 * index + 2

    def _swap(self, i, j):
        """Swap two heap elements."""
        self._heap[i], self._heap[j] = self._heap[j], self._heap[i]

    def insert(self, item, priority):
        """
        Insert an item with the given priority.

        Time Complexity: O(log n)
        """

        self._heap.append((priority, item))

        current_index = len(self._heap) - 1

        self._heapify_up(current_index)

    def _heapify_up(self, index):
        """
        Restore Min Heap property from bottom to top.

        Time Complexity: O(log n)
        """

        while index > 0:
            parent_index = self._parent(index)

            current_priority = self._heap[index][0]
            parent_priority = self._heap[parent_index][0]

            if current_priority >= parent_priority:
                break

            self._swap(index, parent_index)

            index = parent_index

    def extract_min(self):
        """
        Remove and return the item with the smallest priority.

        Returns:
            (priority, item)

        Time Complexity: O(log n)
        """

        if self.is_empty():
            raise IndexError("Heap is empty")

        # Root contains minimum element
        minimum = self._heap[0]

        # Remove last element
        last_element = self._heap.pop()

        # If heap is not empty, move last element to root
        if not self.is_empty():
            self._heap[0] = last_element

            self._heapify_down(0)

        return minimum

    def _heapify_down(self, index):
        """
        Restore Min Heap property from top to bottom.

        Time Complexity: O(log n)
        """

        size = len(self._heap)

        while True:
            smallest = index

            left = self._left_child(index)
            right = self._right_child(index)

            # Compare left child
            if (
                left < size
                and self._heap[left][0] < self._heap[smallest][0]
            ):
                smallest = left

            # Compare right child
            if (
                right < size
                and self._heap[right][0] < self._heap[smallest][0]
            ):
                smallest = right

            # Heap property is satisfied
            if smallest == index:
                break

            self._swap(index, smallest)

            index = smallest

    def peek_min(self):
        """
        Return minimum element without removing it.

        Time Complexity: O(1)
        """

        if self.is_empty():
            raise IndexError("Heap is empty")

        return self._heap[0]

    def is_empty(self):
        """
        Check whether heap is empty.

        Time Complexity: O(1)
        """

        return len(self._heap) == 0

    def size(self):
        """
        Return number of elements.

        Time Complexity: O(1)
        """

        return len(self._heap)

    def display(self):
        """
        Return heap contents in array representation.

        Time Complexity: O(n)
        """

        return self._heap.copy()

    def clear(self):
        """
        Remove all elements from heap.

        Time Complexity: O(1)
        """

        self._heap.clear()

    def __len__(self):
        """Allows len(heap)."""

        return len(self._heap)

    def __str__(self):
        """Human-readable heap representation."""

        return str(self._heap)