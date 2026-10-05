class ChargingStation:
    """
    Represents an EV charging station.
    """

    def __init__(
        self,
        station_id,
        location,
        charging_slots=1
    ):
        self.station_id = station_id
        self.location = location
        self.charging_slots = charging_slots

        # Currently charging EVs
        self.active_evs = []

    def has_available_slot(self):
        """
        Check whether a charging slot is available.
        """
        return len(self.active_evs) < self.charging_slots

    def start_charging(self, ev):
        """
        Add an EV to the active charging list.
        """
        if not self.has_available_slot():
            return False

        self.active_evs.append(ev)
        return True

    def stop_charging(self, ev):
        """
        Remove an EV from active charging.
        """
        if ev in self.active_evs:
            self.active_evs.remove(ev)
            return True

        return False

    def active_count(self):
        """
        Return the number of EVs currently charging.
        """
        return len(self.active_evs)

    def __str__(self):
        return (
            f"Station({self.station_id}, "
            f"Location={self.location}, "
            f"Slots={self.charging_slots}, "
            f"Active={self.active_count()})"
        )

    def __repr__(self):
        return self.__str__()