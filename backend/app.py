# pyrefly: ignore [missing-import]

from pathlib import Path

from flask import Flask, jsonify, send_from_directory
from flask_cors import CORS

from src.algorithms.graph import Graph
from src.services.simulation import EVChargingSimulation
from src.api import create_api_blueprint


# ============================================================
# PROJECT PATHS
# ============================================================

BACKEND_DIR = Path(__file__).resolve().parent
PROJECT_DIR = BACKEND_DIR.parent
FRONTEND_DIR = PROJECT_DIR / "frontend"


# ============================================================
# DEMO GRAPH
# ============================================================

def build_demo_graph():
    """
    Build the default EV charging network.

    Vertices represent locations/intersections.
    Weighted edges represent roads/distances.
    """

    graph = Graph()

    vertices = [
        "A",
        "B",
        "C",
        "D",
        "E"
    ]

    for vertex in vertices:
        graph.add_vertex(vertex)

    graph.add_edge("A", "B", 4)
    graph.add_edge("A", "C", 2)

    graph.add_edge("B", "D", 5)
    graph.add_edge("B", "E", 9)

    graph.add_edge("C", "D", 1)
    graph.add_edge("C", "E", 7)

    graph.add_edge("D", "E", 2)

    return graph


# ============================================================
# APPLICATION FACTORY
# ============================================================

def create_app(testing=False, simulation=None):
    """
    Create and configure the Flask application.

    Flask serves both:

        1. REST API
        2. Frontend dashboard

    This allows the entire project to run with:

        python app.py
    """

    app = Flask(
        __name__,
        static_folder=None
    )

    app.config.update(
        TESTING=testing
    )

    # --------------------------------------------------------
    # Create simulation
    # --------------------------------------------------------

    if simulation is None:

        graph = build_demo_graph()

        simulation = EVChargingSimulation(graph)

    app.extensions["ev_simulation"] = simulation

    # --------------------------------------------------------
    # CORS
    # --------------------------------------------------------

    CORS(
        app,
        resources={
            r"/api/*": {
                "origins": "*"
            }
        }
    )

    # --------------------------------------------------------
    # REST API
    # --------------------------------------------------------

    app.register_blueprint(
        create_api_blueprint(simulation),
        url_prefix="/api"
    )

    # ========================================================
    # FRONTEND
    # ========================================================

    @app.get("/")
    def serve_frontend():
        """
        Serve the main frontend dashboard.
        """

        return send_from_directory(
            FRONTEND_DIR,
            "index.html"
        )

    @app.get("/<path:path>")
    def serve_frontend_file(path):
        """
        Serve frontend CSS, JavaScript and other static files.

        Examples:

            /css/style.css
            /js/main.js
            /js/graph.js
        """

        # Never treat API routes as frontend routes.
        if path.startswith("api/"):

            return jsonify({
                "success": False,
                "error": {
                    "message": "API endpoint not found"
                }
            }), 404

        file_path = FRONTEND_DIR / path

        if file_path.is_file():

            return send_from_directory(
                FRONTEND_DIR,
                path
            )

        # Fallback to index.html.
        return send_from_directory(
            FRONTEND_DIR,
            "index.html"
        )

    return app


# ============================================================
# APPLICATION INSTANCE
# ============================================================

app = create_app()


# ============================================================
# SERVER
# ============================================================

if __name__ == "__main__":

    print("\n" + "=" * 60)
    print("  SMART EV CHARGING CONTROL & ROUTE OPTIMIZER")
    print("=" * 60)
    print(f"  {'Application':<24}http://127.0.0.1:5000")
    print(f"  {'Frontend':<24}http://127.0.0.1:5000/")
    print(f"  {'API':<24}http://127.0.0.1:5000/api")
    print(f"  {'Health Check':<24}http://127.0.0.1:5000/api/health")
    print("=" * 60 + "\n")

    app.run(
        host="0.0.0.0",
        port=5000,
        debug=False
    )