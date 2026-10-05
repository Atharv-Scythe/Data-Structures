# pyrefly: ignore [missing-import]
from flask import Flask, jsonify
from flask_cors import CORS

from src.algorithms.graph import Graph
from src.services.simulation import EVChargingSimulation
from src.api import create_api_blueprint


def build_demo_graph():
    """
    Build the default EV charging network used when the API starts.

    The graph gives us a ready-to-use network for API testing,
    frontend development and demonstrations.
    """

    graph = Graph()

    # ---------------------------------------------------------
    # Vertices
    # ---------------------------------------------------------

    vertices = [
        "A",
        "B",
        "C",
        "D",
        "E"
    ]

    for vertex in vertices:
        graph.add_vertex(vertex)

    # ---------------------------------------------------------
    # Weighted roads
    # ---------------------------------------------------------

    graph.add_edge("A", "B", 4)
    graph.add_edge("A", "C", 2)

    graph.add_edge("B", "D", 5)
    graph.add_edge("B", "E", 9)

    graph.add_edge("C", "D", 1)
    graph.add_edge("C", "E", 7)

    graph.add_edge("D", "E", 2)

    return graph


def create_app(testing=False, simulation=None):
    """
    Application factory.

    A simulation can be injected during testing, otherwise a
    fresh demo simulation is created.
    """

    app = Flask(__name__)

    app.config.update(
        TESTING=testing
    )

    # ---------------------------------------------------------
    # Create simulation
    # ---------------------------------------------------------

    if simulation is None:

        graph = build_demo_graph()

        simulation = EVChargingSimulation(graph)

    # Store simulation on Flask's extension registry.
    app.extensions["ev_simulation"] = simulation

    # ---------------------------------------------------------
    # CORS
    # ---------------------------------------------------------

    CORS(
        app,
        resources={
            r"/api/*": {
                "origins": "*"
            }
        }
    )

    # ---------------------------------------------------------
    # Register API
    # ---------------------------------------------------------

    app.register_blueprint(
        create_api_blueprint(simulation),
        url_prefix="/api"
    )

    # ---------------------------------------------------------
    # Root endpoint
    # ---------------------------------------------------------

    @app.get("/")
    def index():

        return jsonify({
            "name": "Smart EV Charging Queue & Route Optimizer",
            "status": "online",
            "api": "/api",
            "health": "/api/health"
        })

    return app


# Default application instance
app = create_app()


if __name__ == "__main__":
    import os

    # Display clear service endpoints banner in terminal
    if os.environ.get("WERKZEUG_RUN_MAIN") != "false":
        print("\n" + "=" * 54)
        print("  SMART EV CHARGING CONTROL & ROUTE OPTIMIZER")
        print("=" * 54)
        print(f"  {'Service':<24}{'URL'}")
        print("  " + "-" * 50)
        print(f"  {'Backend API':<24}http://127.0.0.1:5000")
        print(f"  {'Frontend Dashboard':<24}http://127.0.0.1:5500")
        print("=" * 54 + "\n")

    app.run(
        host="0.0.0.0",
        port=5000,
        debug=False
    )
