from flask import Blueprint, jsonify, request

from src.models.ev import EV
from src.models.station import ChargingStation


def create_api_blueprint(simulation):
    """
    Create and configure the REST API blueprint.

    The blueprint receives the existing simulation object instead
    of creating another simulation. This keeps the API thin and
    ensures all Data Structure logic remains inside the services.
    """

    api = Blueprint("api", __name__)

    # =========================================================
    # RESPONSE HELPERS
    # =========================================================

    def success(data=None, status_code=200):
        """
        Return a standard successful API response.
        """

        response = {
            "success": True,
            "data": data
        }

        return jsonify(response), status_code

    def error(message, status_code=400, details=None):
        """
        Return a standard error API response.
        """

        response = {
            "success": False,
            "error": {
                "message": message
            }
        }

        if details is not None:
            response["error"]["details"] = details

        return jsonify(response), status_code

    def get_json_body():
        """
        Safely retrieve a JSON request body.
        """

        data = request.get_json(silent=True)

        if not isinstance(data, dict):
            return None

        return data

    # =========================================================
    # SERIALIZATION HELPERS
    # =========================================================

    def serialize_ev(ev):
        """
        Convert an EV object into JSON-safe data.
        """

        return {
            "ev_id": ev.ev_id,
            "battery_level": ev.battery_level,
            "battery_capacity": ev.battery_capacity,
            "charging_required": ev.charging_required,
            "priority": ev.priority,
            "location": ev.location
        }

    def serialize_station(station):
        """
        Convert a ChargingStation object into JSON-safe data.
        """

        return {
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

    def find_ev(ev_id):
        """
        Find an EV by ID.
        """

        for ev in simulation.evs:
            if ev.ev_id == ev_id:
                return ev

        return None

    def find_station(station_id):
        """
        Find a charging station by ID.
        """

        for station in simulation.stations:
            if station.station_id == station_id:
                return station

        return None

    def graph_location_exists(location):
        """
        Check whether a location exists as a graph vertex.

        The project's Graph implementation exposes
        get_neighbors(), not neighbors().
        """

        try:
            simulation.graph.get_neighbors(location)
            return True
        except (KeyError, ValueError):
            return False
    # =========================================================
    # HEALTH
    # =========================================================

    @api.get("/health")
    def health():
        """
        Basic API health check.
        """

        return success({
            "service": "Smart EV Charging Queue & Route Optimizer",
            "status": "online",
            "api_version": "1.0"
        })

    # =========================================================
    # STATUS
    # =========================================================

    @api.get("/status")
    def status():
        """
        Return the current simulation status.
        """

        return success(
            simulation.get_status()
        )

    # =========================================================
    # SNAPSHOT
    # =========================================================

    @api.get("/snapshot")
    def snapshot():
        """
        Return the complete simulation snapshot.
        """

        return success(
            simulation.get_snapshot()
        )

    # =========================================================
    # EVENTS
    # =========================================================

    @api.get("/events")
    def events():
        """
        Return simulation event history.

        Optional query parameter:
            ?limit=10

        returns the most recent 10 events.
        """

        event_history = simulation.get_event_history()

        limit_text = request.args.get("limit")

        if limit_text is None:
            return success({
                "count": len(event_history),
                "events": event_history
            })

        try:
            limit = int(limit_text)
        except ValueError:
            return error(
                "limit must be an integer",
                400
            )

        if limit <= 0:
            return error(
                "limit must be greater than zero",
                400
            )

        selected_events = event_history[-limit:]

        return success({
            "count": len(selected_events),
            "events": selected_events
        })

    # =========================================================
    # GRAPH
    # =========================================================

    @api.get("/graph")
    def get_graph():
        """
        Return the complete graph in a frontend-friendly format.

        The data comes directly from the Graph object used by
        RouteManager and Dijkstra.
        """

        graph = simulation.graph

        return success({
            "directed": graph.directed,
            "vertices": graph.get_vertices(),
            "edges": graph.get_edges(),
            "vertex_count": graph.vertex_count(),
            "edge_count": graph.edge_count()
        })
    
    @api.post("/graph/vertices")
    def add_vertex():
        """
        Add a vertex to the charging network graph.

        Expected JSON:
        {
            "vertex": "F"
        }
        """

        data = get_json_body()

        if data is None:
            return error(
                "Request body must be a JSON object",
                400
            )

        vertex = data.get("vertex")

        if vertex is None:
            return error(
                "Missing required field: vertex",
                400
            )

        try:
            simulation.graph.add_vertex(vertex)
        except (ValueError, TypeError, KeyError) as exc:
            return error(
                str(exc),
                400
            )

        return success({
            "vertex": vertex,
            "message": f"Vertex {vertex} added"
        }, 201)

    # =========================================================
    # GRAPH EDGE
    # =========================================================

    @api.post("/graph/edges")
    def add_edge():
        """
        Add a weighted edge to the graph.

        Expected JSON:
        {
            "source": "A",
            "destination": "B",
            "weight": 4
        }
        """

        data = get_json_body()

        if data is None:
            return error(
                "Request body must be a JSON object",
                400
            )

        source = data.get("source")
        destination = data.get("destination")
        weight = data.get("weight")

        if source is None:
            return error(
                "Missing required field: source",
                400
            )

        if destination is None:
            return error(
                "Missing required field: destination",
                400
            )

        if weight is None:
            return error(
                "Missing required field: weight",
                400
            )

        if isinstance(weight, bool) or not isinstance(
            weight,
            (int, float)
        ):
            return error(
                "weight must be numeric",
                400
            )

        if weight < 0:
            return error(
                "weight cannot be negative",
                400
            )

        try:
            simulation.graph.add_edge(
                source,
                destination,
                weight
            )
        except (ValueError, TypeError, KeyError) as exc:
            return error(
                str(exc),
                400
            )

        return success({
            "source": source,
            "destination": destination,
            "weight": weight,
            "message": (
                f"Edge {source} -> {destination} added"
            )
        }, 201)

    # =========================================================
    # ADD STATION
    # =========================================================

    @api.post("/stations")
    def add_station():
        """
        Add a charging station.

        Expected JSON:
        {
            "station_id": "S1",
            "location": "A",
            "charging_slots": 2
        }
        """

        data = get_json_body()

        if data is None:
            return error(
                "Request body must be a JSON object",
                400
            )

        station_id = data.get("station_id")
        location = data.get("location")
        charging_slots = data.get("charging_slots", 1)

        if station_id is None:
            return error(
                "Missing required field: station_id",
                400
            )

        if location is None:
            return error(
                "Missing required field: location",
                400
            )

        if (
            isinstance(charging_slots, bool)
            or not isinstance(charging_slots, int)
            or charging_slots <= 0
        ):
            return error(
                "charging_slots must be a positive integer",
                400
            )

        if find_station(station_id) is not None:
            return error(
                f"Station {station_id} already exists",
                409
            )

        if not graph_location_exists(location):
            return error(
                f"Location {location} does not exist in the graph",
                400
            )

        station = ChargingStation(
            station_id,
            location,
            charging_slots
        )

        try:
            simulation.add_station(station)
        except (ValueError, TypeError, KeyError) as exc:
            return error(
                str(exc),
                400
            )

        return success(
            serialize_station(station),
            201
        )

    # =========================================================
    # GET STATIONS
    # =========================================================

    @api.get("/stations")
    def get_stations():
        """
        Return all charging stations.
        """

        stations = [
            serialize_station(station)
            for station in simulation.stations
        ]

        return success({
            "count": len(stations),
            "stations": stations
        })

    # =========================================================
    # NEAREST STATION
    # =========================================================

    @api.get("/stations/nearest")
    def nearest_station():
        """
        Find the nearest available charging station.

        Example:
            /api/stations/nearest?start=A
        """

        start = request.args.get("start")

        if start is None:
            return error(
                "Missing required query parameter: start",
                400
            )

        if not graph_location_exists(start):
            return error(
                f"Location {start} does not exist in the graph",
                400
            )

        try:
            result = simulation.route_manager.find_nearest_station(
                start
            )
        except (ValueError, KeyError, TypeError) as exc:
            return error(
                str(exc),
                400
            )

        if result is None:
            return error(
                "No available charging station found",
                404
            )

        station = result["station"]

        return success({
            "station": serialize_station(station),
            "distance": result["distance"],
            "path": result["path"]
        })

    # =========================================================
    # ADD EV
    # =========================================================

    @api.post("/evs")
    def add_ev():
        """
        Add an EV to a specific queue type.

        Expected JSON:
        {
            "ev_id": "EV001",
            "battery_level": 80,
            "battery_capacity": 100,
            "charging_required": true,
            "priority": 5,
            "location": "A",
            "type": "normal"
        }
        """

        data = get_json_body()

        if data is None:
            return error(
                "Request body must be a JSON object",
                400
            )

        ev_id = data.get("ev_id")
        battery_level = data.get("battery_level")
        battery_capacity = data.get("battery_capacity")
        charging_required = data.get(
            "charging_required",
            True
        )
        priority = data.get("priority", 0)
        location = data.get("location")
        ev_type = data.get("type", "normal")

        if ev_id is None:
            return error(
                "Missing required field: ev_id",
                400
            )

        if battery_level is None:
            return error(
                "Missing required field: battery_level",
                400
            )

        if battery_capacity is None:
            return error(
                "Missing required field: battery_capacity",
                400
            )

        if location is None:
            return error(
                "Missing required field: location",
                400
            )

        if ev_type not in (
            "normal",
            "priority",
            "special"
        ):
            return error(
                "type must be normal, priority, or special",
                400
            )

        if (
            isinstance(battery_level, bool)
            or not isinstance(battery_level, (int, float))
        ):
            return error(
                "battery_level must be numeric",
                400
            )

        if (
            isinstance(battery_capacity, bool)
            or not isinstance(battery_capacity, (int, float))
        ):
            return error(
                "battery_capacity must be numeric",
                400
            )

        if battery_capacity <= 0:
            return error(
                "battery_capacity must be greater than zero",
                400
            )

        if battery_level < 0:
            return error(
                "battery_level cannot be negative",
                400
            )

        if battery_level > battery_capacity:
            return error(
                "battery_level cannot exceed battery_capacity",
                400
            )

        if not isinstance(charging_required, bool):
            return error(
                "charging_required must be boolean",
                400
            )

        if (
            isinstance(priority, bool)
            or not isinstance(priority, int)
        ):
            return error(
                "priority must be an integer",
                400
            )

        if find_ev(ev_id) is not None:
            return error(
                f"EV {ev_id} already exists",
                409
            )

        if not graph_location_exists(location):
            return error(
                f"Location {location} does not exist in the graph",
                400
            )

        ev = EV(
            ev_id,
            battery_level,
            battery_capacity,
            charging_required,
            priority,
            location
        )

        try:
            added = simulation.add_ev(
                ev,
                ev_type
            )
        except (ValueError, TypeError, KeyError) as exc:
            return error(
                str(exc),
                400
            )

        if not added:
            return error(
                f"EV {ev_id} could not be added",
                409
            )

        return success({
            "ev": serialize_ev(ev),
            "queue": ev_type
        }, 201)

    # =========================================================
    # AUTOMATIC EV CLASSIFICATION
    # =========================================================

    @api.post("/evs/automatic")
    def add_ev_automatic():
        """
        Add an EV and let the simulation classify it.

        Critical EVs go to the priority queue.
        Other EVs go to the normal queue.
        """

        data = get_json_body()

        if data is None:
            return error(
                "Request body must be a JSON object",
                400
            )

        required_fields = [
            "ev_id",
            "battery_level",
            "battery_capacity",
            "location"
        ]

        for field in required_fields:
            if field not in data:
                return error(
                    f"Missing required field: {field}",
                    400
                )

        ev_id = data["ev_id"]
        battery_level = data["battery_level"]
        battery_capacity = data["battery_capacity"]
        location = data["location"]

        charging_required = data.get(
            "charging_required",
            True
        )

        priority = data.get(
            "priority",
            0
        )

        if find_ev(ev_id) is not None:
            return error(
                f"EV {ev_id} already exists",
                409
            )

        if not graph_location_exists(location):
            return error(
                f"Location {location} does not exist in the graph",
                400
            )

        if (
            isinstance(battery_level, bool)
            or not isinstance(battery_level, (int, float))
            or battery_level < 0
        ):
            return error(
                "battery_level must be a non-negative number",
                400
            )

        if (
            isinstance(battery_capacity, bool)
            or not isinstance(battery_capacity, (int, float))
            or battery_capacity <= 0
        ):
            return error(
                "battery_capacity must be a positive number",
                400
            )

        if battery_level > battery_capacity:
            return error(
                "battery_level cannot exceed battery_capacity",
                400
            )

        if not isinstance(charging_required, bool):
            return error(
                "charging_required must be boolean",
                400
            )

        if (
            isinstance(priority, bool)
            or not isinstance(priority, int)
        ):
            return error(
                "priority must be an integer",
                400
            )

        ev = EV(
            ev_id,
            battery_level,
            battery_capacity,
            charging_required,
            priority,
            location
        )

        try:
            queue_type = simulation.add_ev_automatically(ev)
        except (ValueError, TypeError, KeyError) as exc:
            return error(
                str(exc),
                400
            )

        if queue_type is None:
            return error(
                f"EV {ev_id} could not be added",
                409
            )

        return success({
            "ev": serialize_ev(ev),
            "queue": queue_type
        }, 201)

    # =========================================================
    # GET EVS
    # =========================================================

    @api.get("/evs")
    def get_evs():
        """
        Return all EVs registered in the simulation.
        """

        evs = [
            serialize_ev(ev)
            for ev in simulation.evs
        ]

        return success({
            "count": len(evs),
            "evs": evs
        })

    # =========================================================
    # PROCESS NEXT EV
    # =========================================================

    @api.post("/process")
    def process_next_ev():
        """
        Select the next EV, find its nearest available station,
        calculate the route, assign the station and start charging.
        """

        try:
            result = simulation.process_next_ev()
        except (ValueError, KeyError, TypeError) as exc:
            return error(
                str(exc),
                400
            )

        if result is None:
            return error(
                "No EV is waiting to be processed",
                409
            )

        response_data = {
            "ev": serialize_ev(result["ev"]),
            "station": (
                serialize_station(result["station"])
                if result["station"] is not None
                else None
            ),
            "distance": result["distance"],
            "path": result["path"],
            "status": result.get("status"),
            "reason": result.get("reason")
        }

        if result["success"]:
            return success(
                response_data,
                200
            )

        return error(
            result["reason"],
            409,
            response_data
        )

    # =========================================================
    # COMPLETE CHARGING
    # =========================================================

    @api.post("/charging/complete")
    def complete_charging():
        """
        Complete charging for an EV.

        Expected JSON:
        {
            "ev_id": "EV001",
            "station_id": "S1"
        }
        """

        data = get_json_body()

        if data is None:
            return error(
                "Request body must be a JSON object",
                400
            )

        ev_id = data.get("ev_id")
        station_id = data.get("station_id")

        if ev_id is None:
            return error(
                "Missing required field: ev_id",
                400
            )

        if station_id is None:
            return error(
                "Missing required field: station_id",
                400
            )

        ev = find_ev(ev_id)

        if ev is None:
            return error(
                f"EV {ev_id} not found",
                404
            )

        station = find_station(station_id)

        if station is None:
            return error(
                f"Station {station_id} not found",
                404
            )

        try:
            completed = simulation.complete_charging(
                ev,
                station
            )
        except (ValueError, KeyError, TypeError) as exc:
            return error(
                str(exc),
                400
            )

        if not completed:
            return error(
                (
                    f"EV {ev_id} is not currently charging "
                    f"at station {station_id}"
                ),
                409
            )

        return success({
            "ev": serialize_ev(ev),
            "station": serialize_station(station),
            "status": "completed"
        })

    # =========================================================
    # CALCULATE ROUTE
    # =========================================================

    @api.get("/routes")
    def calculate_route():
        """
        Calculate the shortest route between two graph vertices.

        Example:
            /api/routes?start=A&destination=E
        """

        start = request.args.get("start")
        destination = request.args.get("destination")

        if start is None:
            return error(
                "Missing required query parameter: start",
                400
            )

        if destination is None:
            return error(
                "Missing required query parameter: destination",
                400
            )

        if not graph_location_exists(start):
            return error(
                f"Start location {start} does not exist",
                400
            )

        if not graph_location_exists(destination):
            return error(
                f"Destination {destination} does not exist",
                400
            )

        try:
            result = simulation.route_manager.calculate_route(
                start,
                destination
            )
        except (ValueError, KeyError, TypeError) as exc:
            return error(
                str(exc),
                400
            )

        if result is None:
            return error(
                f"No route found from {start} to {destination}",
                404
            )

        return success({
            "start": start,
            "destination": destination,
            "distance": result["distance"],
            "path": result["path"]
        })

    # =========================================================
    # RESET
    # =========================================================

    @api.post("/reset")
    def reset():
        """
        Reset runtime simulation state while keeping stations.
        """

        simulation.reset()

        return success({
            "message": "Simulation reset",
            "status": simulation.get_status()
        })

    # =========================================================
    # CLEAR
    # =========================================================

    @api.post("/clear")
    def clear():
        """
        Completely clear simulation state.
        """

        simulation.clear()

        return success({
            "message": "Simulation cleared",
            "status": simulation.get_status()
        })

    return api