class EV:
    """
    Represents an electric vehicle in the charging system.
    """

    def __init__(
        self,
        ev_id,
        battery_level,
        battery_capacity,
        charging_required,
        priority=0,
        location=None
    ):
        self.ev_id = ev_id
        self.battery_level = battery_level
        self.battery_capacity = battery_capacity
        self.charging_required = charging_required
        self.priority = priority
        self.location = location
    def is_critical(self, threshold=20):
        """
        Check whether the EV has critically low battery.
        """
        return self.battery_level <= threshold

    def battery_needed(self):
        """
        Calculate how much battery percentage is needed.
        """
        return 100 - self.battery_level

    def __str__(self):
        return (
            f"EV({self.ev_id}, "
            f"Battery={self.battery_level}%, "
            f"Priority={self.priority})"
        )

    def __repr__(self):
        return self.__str__()