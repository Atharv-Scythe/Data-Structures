from src.models.ev import EV
from src.models.station import ChargingStation
from src.services.charging_manager import ChargingManager
from src.services.route_manager import RouteManager


class EVChargingSimulation:

    def __init__(self, graph):
        self.graph = graph

        self.charging_manager = ChargingManager()
        self.route_manager = RouteManager(graph)

        self.evs = []
        self.stations = []
        self.processed_evs = []

        # Simulation event history
        self.event_history = []
        self.event_counter = 0

    # =========================================================
    # EVENT HISTORY
    # =========================================================

    def _record_event(
        self,
        event_type,
        message,
        ev=None,
        station=None,
        details=None
    ):
        """
        Record a simulation event.

        Events are stored as dictionaries so they can later
        be directly converted into JSON by the Flask API.
        """

        self.event_counter += 1

        event = {
            "step": self.event_counter,
            "type": event_type,
            "message": message,
            "ev_id": ev.ev_id if ev is not None else None,
            "station_id": (
                station.station_id
                if station is not None
                else None
            ),
            "details": details if details is not None else {}
        }

        self.event_history.append(event)

    def get_event_history(self):
        """
        Return a copy of the complete event history.
        """

        return list(self.event_history)

    def clear_event_history(self):
        """
        Clear all recorded events and reset event numbering.
        """

        self.event_history.clear()
        self.event_counter = 0

    # =========================================================
    # STATION MANAGEMENT
    # =========================================================

    def add_station(self, station):

        if station not in self.stations:

            self.stations.append(station)
            self.route_manager.add_station(station)

            self._record_event(
                "station_added",
                f"Charging station {station.station_id} added",
                station=station,
                details={
                    "location": station.location,
                    "charging_slots": station.charging_slots
                }
            )

    def remove_station(self, station):

        if station not in self.stations:
            return False

        self.stations.remove(station)
        self.route_manager.remove_station(station)

        self._record_event(
            "station_removed",
            f"Charging station {station.station_id} removed",
            station=station
        )

        return True

    def station_count(self):
        return len(self.stations)

    # =========================================================
    # EV MANAGEMENT
    # =========================================================

    def add_ev(self, ev, ev_type="normal"):

        if not isinstance(ev, EV):
            raise TypeError("ev must be an EV object")

        if ev in self.evs:
            return False

        if ev_type not in ("normal", "priority", "special"):
            raise ValueError(
                "ev_type must be normal, priority, or special"
            )

        self.evs.append(ev)

        self._record_event(
            "ev_arrived",
            f"{ev.ev_id} arrived at charging network",
            ev=ev,
            details={
                "battery_level": ev.battery_level,
                "battery_capacity": ev.battery_capacity
            }
        )

        if ev_type == "normal":

            self.charging_manager.add_normal_ev(ev)

            self._record_event(
                "queue_insert",
                f"{ev.ev_id} added to normal queue",
                ev=ev,
                details={
                    "queue": "normal"
                }
            )

        elif ev_type == "priority":

            self.charging_manager.add_priority_ev(ev)

            self._record_event(
                "queue_insert",
                f"{ev.ev_id} added to priority queue",
                ev=ev,
                details={
                    "queue": "priority",
                    "priority": ev.priority
                }
            )

        else:

            self.charging_manager.add_special_ev(ev)

            self._record_event(
                "queue_insert",
                f"{ev.ev_id} added to special deque",
                ev=ev,
                details={
                    "queue": "special"
                }
            )

        return True

    def add_ev_automatically(self, ev):

        if not isinstance(ev, EV):
            raise TypeError("ev must be an EV object")

        if ev in self.evs:
            return None

        self.evs.append(ev)

        self._record_event(
            "ev_arrived",
            f"{ev.ev_id} arrived at charging network",
            ev=ev,
            details={
                "battery_level": ev.battery_level,
                "battery_capacity": ev.battery_capacity
            }
        )

        if ev.is_critical():

            self.charging_manager.add_priority_ev(ev)

            self._record_event(
                "queue_insert",
                f"{ev.ev_id} automatically classified as priority",
                ev=ev,
                details={
                    "queue": "priority",
                    "reason": "critical battery",
                    "battery_level": ev.battery_level
                }
            )

            return "priority"

        self.charging_manager.add_normal_ev(ev)

        self._record_event(
            "queue_insert",
            f"{ev.ev_id} automatically classified as normal",
            ev=ev,
            details={
                "queue": "normal",
                "reason": "battery above critical threshold",
                "battery_level": ev.battery_level
            }
        )

        return "normal"

    # =========================================================
    # EV SELECTION
    # =========================================================

    def get_next_ev(self):

        ev = self.charging_manager.get_next_priority_ev()

        if ev is not None:

            self._record_event(
                "ev_selected",
                f"{ev.ev_id} selected from priority queue",
                ev=ev,
                details={
                    "queue": "priority"
                }
            )

            return ev

        ev = self.charging_manager.get_next_special_ev()

        if ev is not None:

            self._record_event(
                "ev_selected",
                f"{ev.ev_id} selected from special deque",
                ev=ev,
                details={
                    "queue": "special"
                }
            )

            return ev

        ev = self.charging_manager.get_next_normal_ev()

        if ev is not None:

            self._record_event(
                "ev_selected",
                f"{ev.ev_id} selected from normal queue",
                ev=ev,
                details={
                    "queue": "normal"
                }
            )

            return ev

        return None

    # =========================================================
    # PROCESS NEXT EV
    # =========================================================

    def process_next_ev(self):

        ev = self.get_next_ev()

        if ev is None:
            return None

        self._record_event(
            "route_search_started",
            f"Finding nearest available station for {ev.ev_id}",
            ev=ev
        )

        route = self.route_manager.find_nearest_station(
            ev.location
        )

        if route is None:

            self._record_event(
                "processing_failed",
                f"No available charging station for {ev.ev_id}",
                ev=ev,
                details={
                    "reason": "No available charging station"
                }
            )

            return {
                "success": False,
                "ev": ev,
                "station": None,
                "distance": None,
                "path": [],
                "reason": "No available charging station"
            }

        station = route["station"]

        self._record_event(
            "route_calculated",
            f"Route calculated for {ev.ev_id}",
            ev=ev,
            station=station,
            details={
                "distance": route["distance"],
                "path": route["path"]
            }
        )

        self._record_event(
            "station_assigned",
            f"Station {station.station_id} assigned to {ev.ev_id}",
            ev=ev,
            station=station,
            details={
                "distance": route["distance"]
            }
        )

        started = self.charging_manager.start_charging(
            ev,
            station
        )

        if not started:

            self._record_event(
                "processing_failed",
                f"Unable to start charging for {ev.ev_id}",
                ev=ev,
                station=station,
                details={
                    "reason": "Unable to start charging"
                }
            )

            return {
                "success": False,
                "ev": ev,
                "station": station,
                "distance": route["distance"],
                "path": route["path"],
                "reason": "Unable to start charging"
            }

        self._record_event(
            "charging_started",
            f"Charging started for {ev.ev_id}",
            ev=ev,
            station=station,
            details={
                "distance": route["distance"],
                "path": route["path"]
            }
        )

        result = {
            "success": True,
            "ev": ev,
            "station": station,
            "distance": route["distance"],
            "path": route["path"],
            "status": "charging"
        }

        self.processed_evs.append(result)

        return result

    # =========================================================
    # COMPLETE CHARGING
    # =========================================================

    def complete_charging(self, ev, station):

        result = self.charging_manager.complete_charging(
            ev,
            station
        )

        if result:

            self._record_event(
                "charging_completed",
                f"Charging completed for {ev.ev_id}",
                ev=ev,
                station=station
            )

        return result

    # =========================================================
    # STATUS
    # =========================================================

    def get_status(self):

        manager_status = self.charging_manager.get_status()

        return {
            "ev_count": len(self.evs),
            "station_count": len(self.stations),

            "waiting_normal":
                manager_status["waiting_normal"],

            "waiting_priority":
                manager_status["waiting_priority"],

            "waiting_special":
                manager_status["waiting_special"],

            "charging":
                manager_status["charging"],

            "completed":
                manager_status["completed"],

            "processed":
                len(self.processed_evs),

            "event_count":
                len(self.event_history)
        }

    # =========================================================
    # SIMULATION SNAPSHOT / DS TRACE
    # =========================================================

    def get_snapshot(self):
        """
        Return the complete current state of the simulation.

        This snapshot is designed to be used later by the
        Flask API and frontend visualization.
        """

        return {
            "queues": {
                "normal": self._get_normal_queue_snapshot(),
                "priority": self._get_priority_queue_snapshot(),
                "special": self._get_special_deque_snapshot()
            },

            "charging": self._get_charging_snapshot(),

            "completed": self._get_completed_snapshot(),

            "stations": self._get_station_snapshot(),

            "events": self.get_event_history()
        }

    def _get_normal_queue_snapshot(self):
        """
        Return the EVs currently waiting in the normal FIFO queue.
        """

        return [
            self._ev_to_dict(ev)
            for ev in self.charging_manager.normal_queue.display()
        ]

    def _get_priority_queue_snapshot(self):
        """
        Return the EVs currently waiting in the priority min-heap.
        """

        return [
            {
                "ev_id": item[1].ev_id,
                "priority": item[0]
            }
            for item in self.charging_manager.priority_queue.display()
        ]

    def _get_special_deque_snapshot(self):
        """
        Return the EVs currently inside the special deque.
        """

        return [
            self._ev_to_dict(ev)
            for ev in self.charging_manager.special_deque.display()
        ]

    def _get_charging_snapshot(self):
        """
        Return EVs that are currently charging.

        ChargingManager stores EV objects in charging_evs.
        The station is found by checking which station currently
        contains the EV in its active_evs list.
        """

        charging_snapshot = []

        for ev in self.charging_manager.charging_evs:

            station_id = None

            for station in self.stations:

                if ev in station.active_evs:
                    station_id = station.station_id
                    break

            charging_snapshot.append({
                "ev_id": ev.ev_id,
                "battery_level": ev.battery_level,
                "battery_capacity": ev.battery_capacity,
                "station_id": station_id
            })

        return charging_snapshot

    def _get_completed_snapshot(self):
        """
        Return EVs that have completed charging.
        """

        return [
            self._ev_to_dict(ev)
            for ev in self.charging_manager.completed_evs
        ]

    def _get_station_snapshot(self):
        """
        Return the current state of all charging stations.
        """

        return [
            {
                "station_id": station.station_id,
                "location": station.location,
                "charging_slots": station.charging_slots,
                "active_evs": [
                    ev.ev_id
                    for ev in station.active_evs
                ],
                "available_slots": (
                    station.charging_slots
                    - len(station.active_evs)
                )
            }
            for station in self.stations
        ]

    def _ev_to_dict(self, ev):
        """
        Convert an EV object into a JSON-friendly dictionary.
        """

        return {
            "ev_id": ev.ev_id,
            "battery_level": ev.battery_level,
            "battery_capacity": ev.battery_capacity,
            "charging_required": ev.charging_required,
            "priority": ev.priority,
            "location": ev.location
        }
    
    # =========================================================
    # RESET
    # =========================================================

    def reset(self):

        self.charging_manager.clear()

        self.evs.clear()
        self.processed_evs.clear()

        for station in self.stations:
            station.active_evs.clear()

        self.clear_event_history()

    # =========================================================
    # COMPLETE CLEAR
    # =========================================================

    def clear(self):

        self.charging_manager.clear()

        self.evs.clear()
        self.stations.clear()
        self.processed_evs.clear()

        self.route_manager.clear()

        self.clear_event_history()