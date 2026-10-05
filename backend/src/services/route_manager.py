from src.algorithms.dijkstra import dijkstra, get_shortest_path


class RouteManager:
    """
    Manages route calculation between an EV location
    and available charging stations.

    Responsibilities:
        - Store charging stations
        - Calculate shortest routes using Dijkstra
        - Find reachable stations
        - Select a station based on shortest distance
    """

    def __init__(self, graph):
        """
        Create a RouteManager.

        Args:
            graph:
                Graph object representing the road network.
        """

        self.graph = graph
        self.stations = []

    # ---------------------------------------------------------
    # STATION MANAGEMENT
    # ---------------------------------------------------------

    def add_station(self, station):
        """
        Add a charging station to the manager.
        """

        if station not in self.stations:
            self.stations.append(station)

    def remove_station(self, station):
        """
        Remove a charging station.

        Returns:
            True if removed
            False if station was not present
        """

        if station in self.stations:
            self.stations.remove(station)
            return True

        return False

    def get_stations(self):
        """
        Return all registered charging stations.
        """

        return self.stations.copy()

    def station_count(self):
        """
        Return number of registered stations.
        """

        return len(self.stations)

    # ---------------------------------------------------------
    # ROUTE CALCULATION
    # ---------------------------------------------------------

    def calculate_route(self, start, destination):
        """
        Calculate shortest route between two locations.

        Returns:
            Dictionary containing:
                distance
                path
        """

        distances, previous = dijkstra(
            self.graph,
            start
        )

        path = get_shortest_path(
            previous,
            start,
            destination
        )

        return {
            "distance": distances[destination],
            "path": path
        }

    # ---------------------------------------------------------
    # STATION ROUTES
    # ---------------------------------------------------------

    def get_station_routes(self, start):
        """
        Calculate routes from a starting location
        to every registered charging station.

        Returns:
            List of dictionaries containing:
                station
                distance
                path
                available
        """

        distances, previous = dijkstra(
            self.graph,
            start
        )

        routes = []

        for station in self.stations:

            destination = station.location

            # Skip stations whose location is not
            # present in the graph.
            if destination not in distances:
                continue

            distance = distances[destination]

            # Ignore unreachable stations.
            if distance == float("inf"):
                continue

            path = get_shortest_path(
                previous,
                start,
                destination
            )

            routes.append({
                "station": station,
                "distance": distance,
                "path": path,
                "available": station.has_available_slot()
            })

        return routes

    # ---------------------------------------------------------
    # AVAILABLE STATIONS
    # ---------------------------------------------------------

    def get_available_stations(self, start):
        """
        Return reachable stations that have
        at least one available charging slot.
        """

        routes = self.get_station_routes(start)

        return [
            route
            for route in routes
            if route["available"]
        ]

    # ---------------------------------------------------------
    # SELECT STATION
    # ---------------------------------------------------------

    def find_nearest_station(self, start):
        """
        Find the nearest reachable charging station.

        Only stations with an available charging slot
        are considered.

        Returns:
            Route information dictionary.

            None if no station is available.
        """

        available_stations = self.get_available_stations(
            start
        )

        if not available_stations:
            return None

        nearest = available_stations[0]

        for route in available_stations[1:]:
            if route["distance"] < nearest["distance"]:
                nearest = route

        return nearest

    # ---------------------------------------------------------
    # CLEAR
    # ---------------------------------------------------------

    def clear(self):
        """
        Remove all registered stations.
        """

        self.stations.clear()