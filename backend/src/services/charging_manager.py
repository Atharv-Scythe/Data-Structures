from src.data_structures.queue import SimpleQueue
from src.data_structures.min_heap import MinHeap
from src.data_structures.deque import EVDeque


class ChargingManager:
    """
    Manages EVs waiting for and receiving charging.

    Data Structures used:

        SimpleQueue
            -> Normal EVs
            -> FIFO scheduling

        MinHeap
            -> Critical EVs
            -> Lower priority value = higher priority

        EVDeque
            -> Special/VIP EVs
            -> Can be processed from either end
    """

    def __init__(self):
        # Normal EVs waiting in FIFO order
        self.normal_queue = SimpleQueue()

        # Critical EVs waiting according to priority
        self.priority_queue = MinHeap()

        # Special/VIP EVs
        self.special_deque = EVDeque()

        # EVs currently being charged
        self.charging_evs = []

        # Completed EVs
        self.completed_evs = []

    # ---------------------------------------------------------
    # EV ARRIVAL
    # ---------------------------------------------------------

    def add_normal_ev(self, ev):
        """
        Add a normal EV to the Simple Queue.
        """
        self.normal_queue.enqueue(ev)

    def add_priority_ev(self, ev):
        """
        Add a critical EV to the Min Heap.

        Lower priority number means higher priority.
        """
        self.priority_queue.insert(
            ev,
            ev.priority
        )

    def add_special_ev(self, ev, front=False):
        """
        Add a special/VIP EV to the Deque.

        front=True  -> add to front
        front=False -> add to rear
        """
        if front:
            self.special_deque.add_front(ev)
        else:
            self.special_deque.add_rear(ev)

    # ---------------------------------------------------------
    # GET NEXT EV
    # ---------------------------------------------------------

    def get_next_priority_ev(self):
        """
        Get the highest-priority EV.

        Returns:
            EV object or None
        """
        if self.priority_queue.is_empty():
            return None

        _, ev = self.priority_queue.extract_min()
        return ev

    def get_next_normal_ev(self):
        """
        Get the next normal EV using FIFO order.

        Returns:
            EV object or None
        """
        if self.normal_queue.is_empty():
            return None

        return self.normal_queue.dequeue()

    def get_next_special_ev(self):
        """
        Get the next special/VIP EV.

        Removes from the front of the deque.
        """
        if self.special_deque.is_empty():
            return None

        return self.special_deque.remove_front()

    # ---------------------------------------------------------
    # CHARGING
    # ---------------------------------------------------------

    def start_charging(self, ev, station):
        """
        Start charging an EV at a station.

        Returns:
            True if charging started
            False if station has no available slot
        """

        if not station.has_available_slot():
            return False

        if station.start_charging(ev):
            self.charging_evs.append(ev)
            return True

        return False

    def complete_charging(self, ev, station):
        """
        Complete charging for an EV.

        The EV is removed from the station and
        added to the completed EV list.
        """

        if station.stop_charging(ev):

            if ev in self.charging_evs:
                self.charging_evs.remove(ev)

            self.completed_evs.append(ev)

            return True

        return False

    # ---------------------------------------------------------
    # STATUS
    # ---------------------------------------------------------

    def waiting_count(self):
        """
        Return total number of waiting EVs.
        """

        return (
            self.normal_queue.size()
            + self.priority_queue.size()
            + self.special_deque.size()
        )

    def charging_count(self):
        """
        Return number of EVs currently charging.
        """
        return len(self.charging_evs)

    def completed_count(self):
        """
        Return number of completed EVs.
        """
        return len(self.completed_evs)

    def total_ev_count(self):
        """
        Return total EVs managed by the system.
        """

        return (
            self.waiting_count()
            + self.charging_count()
            + self.completed_count()
        )

    # ---------------------------------------------------------
    # DISPLAY
    # ---------------------------------------------------------

    def get_status(self):
        """
        Return current charging system status.
        """

        return {
            "waiting_normal": self.normal_queue.size(),
            "waiting_priority": self.priority_queue.size(),
            "waiting_special": self.special_deque.size(),
            "charging": self.charging_count(),
            "completed": self.completed_count(),
            "total": self.total_ev_count()
        }

    def clear(self):
        """
        Clear the entire charging manager.
        """

        self.normal_queue.clear()
        self.priority_queue.clear()
        self.special_deque.clear()

        self.charging_evs.clear()
        self.completed_evs.clear()