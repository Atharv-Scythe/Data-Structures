# Smart EV Charging Queue & Route Optimizer

[![Python](https://img.shields.io/badge/Python-3.11%2B-blue.svg)](https://www.python.org/)
[![Flask](https://img.shields.io/badge/Flask-3.0%2B-green.svg)](https://flask.palletsprojects.com/)
[![Tests](https://img.shields.io/badge/Tests-202%20Passed-brightgreen.svg)]()
[![Docker](https://img.shields.io/badge/Docker-Ready-blue.svg)](https://www.docker.com/)

A full-stack, educational EV Charging Simulation and Control Center demonstrating core Data Structures and Algorithms through real-time queue scheduling, priority management, and shortest-path road network routing.

---

## 📌 Project Overview

The **Smart EV Charging Queue & Route Optimizer** models an urban EV charging network handling incoming electric vehicles, queue scheduling based on battery urgency, and shortest-path routing to available charging stations.

### Core Data Structures & Algorithms Applied:
1. **Simple Queue (FIFO):** Handles normal EV charging requests in arrival order ($O(1)$ enqueue/dequeue).
2. **Min-Heap (Priority Queue):** Handles urgent/critical EVs (low battery levels) with binary tree priority scheduling ($O(\log n)$ insertion/extract-min).
3. **Deque (Double-Ended Queue):** Manages special/VIP EVs allowing instant front or rear access ($O(1)$ operations).
4. **Weighted Graph Network:** Represents intersections as vertices and roads with distance weights as adjacency lists.
5. **Dijkstra's Shortest Path Algorithm:** Finds the shortest route from an EV's location to the nearest available charging station using the system's own custom `MinHeap`.

---

## 🏗 System Architecture

```text
┌─────────────────────────────────────────────────────────────┐
│                    FRONTEND DASHBOARD                       │
│     HTML5 • Modern CSS Glassmorphism • Modular JS ES6       │
│   SVG Graph Visualizer • Min-Heap Tree Viz • FIFO & Deque   │
└──────────────────────────────┬──────────────────────────────┘
                               │ REST HTTP / JSON
                               ▼
┌─────────────────────────────────────────────────────────────┐
│                      FLASK REST API                         │
│             Blueprint API Routes & Controller               │
└──────────────────────────────┬──────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────┐
│                 EVChargingSimulation Coordinator            │
└──────────────┬───────────────┼───────────────┬──────────────┘
               │               │               │
               ▼               ▼               ▼
┌──────────────────────┐ ┌───────────┐ ┌───────────────┐
│   ChargingManager    │ │RouteManag.│ │Event/Snapshot │
└──────┬───────┬───────┘ └─────┬─────┘ └───────────────┘
       │       │       │       │
       ▼       ▼       ▼       ▼
┌────────┐ ┌───────┐ ┌─────┐ ┌─────────────────────────┐
│ Simple │ │ Min-  │ │Deque│ │ Graph + Dijkstra        │
│ Queue  │ │ Heap  │ │     │ │ (Adjacency List + Heap) │
└────────┘ └───────┘ └─────┘ └─────────────────────────┘
```

---

## 🚀 Quick Start & Installation

### Option 1: Run Locally

1. **Clone the Repository:**
   ```bash
   git clone 
   cd smart-ev-charging
   ```

2. **Backend Setup (Python):**
   ```bash
   # Set PYTHONPATH to backend directory
   export PYTHONPATH=backend
   
   # Install dependencies
   pip install -r backend/requirements.txt

   # Start Flask API server
   python backend/app.py
   ```
   The backend API runs on `http://127.0.0.1:5000/api`.

3. **Frontend Setup:**
   Open `frontend/index.html` in any web browser, or serve using any static web server (e.g. Live Server or Python http.server):
   ```bash
   cd frontend
   python -m http.server 5500
   ```
   Navigate to `http://127.0.0.1:5500` in your browser.

---

### Option 2: Run with Docker Compose

Run the complete stack (Flask backend + Nginx frontend) in isolated containers:

```bash
docker-compose up --build
```

- **Frontend Application:** `http://localhost` or `http://localhost:5500`
- **Backend REST API:** `http://localhost:5000/api`

---

## 🧪 Running Automated Tests

The backend includes a comprehensive test suite of 202 unit & integration tests covering all Data Structures, Algorithms, Services, Simulation logic, and REST endpoints.

```bash
# Set PYTHONPATH and run pytest
$env:PYTHONPATH="backend"
python -m pytest -v
```

---

## 📊 Theoretical Complexity Summary

| Operation / Component | Data Structure | Time Complexity | Space Complexity |
| :--- | :--- | :--- | :--- |
| **Normal Queue Ingestion** | Simple Queue (FIFO) | $O(1)$ | $O(n)$ |
| **Priority Queue Ingestion** | Binary Min-Heap | $O(\log n)$ | $O(n)$ |
| **Priority Selection** | Binary Min-Heap | $O(\log n)$ | $O(1)$ |
| **Deque Front / Rear Ingestion**| Deque | $O(1)$ | $O(n)$ |
| **Route Path Calculation** | Graph + Dijkstra | $O((V + E) \log V)$ | $O(V + E)$ |

---

## 📁 Repository Structure

```text
.
├── backend/
│   ├── app.py                      # Flask Application Entry Point
│   ├── requirements.txt            # Python Dependencies
│   ├── Dockerfile                  # Backend Container Config
│   ├── src/
│   │   ├── algorithms/             # Graph & Dijkstra Implementations
│   │   ├── api/                    # Flask Blueprint & REST Routes
│   │   ├── data_structures/        # Custom Queue, MinHeap, Deque
│   │   ├── models/                 # EV and ChargingStation Models
│   │   └── services/               # Simulation, Route & Charging Managers
│   └── tests/                      # 202 Automated Pytest Files
├── frontend/
│   ├── index.html                  # Dashboard Control Center Layout
│   ├── Dockerfile                  # Frontend Nginx Container Config
│   ├── nginx.conf                  # Nginx Proxy Configuration
│   ├── css/
│   │   └── style.css               # Modern Glassmorphism Styling
│   └── js/
│       ├── api.js                  # HTTP REST API Client
│       ├── graph.js                # SVG Graph & Dijkstra Path Visualizer
│       ├── heap.js                 # Binary Heap Tree & Array Visualizer
│       ├── queue.js                # Simple FIFO Queue Visualizer
│       ├── deque.js                # Double-Ended Queue Visualizer
│       ├── simulation.js           # Live Auto Simulation & DS Trace Logger
│       └── main.js                 # Application Main Orchestrator
├── docs/
│   ├── architecture.md             # System Architecture Specifications
│   ├── algorithms.md               # Algorithm & Data Structure Guide
│   └── complexity.md               # Complexity Matrix & Tradeoffs
├── docker-compose.yml              # Multi-container Deployment Setup
└── README.md                       # Project Documentation
```

---

## ⚡ API Endpoint Reference

| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `GET` | `/api/health` | Service health status |
| `GET` | `/api/status` | Current metrics & queue counts |
| `GET` | `/api/snapshot` | Complete JSON simulation snapshot |
| `GET` | `/api/events` | Simulation event log trace |
| `GET` | `/api/graph` | City road network graph structure |
| `GET` | `/api/routes?start=A&destination=E` | Calculate Dijkstra shortest path |
| `GET` | `/api/stations/nearest?start=A` | Find nearest station & route |
| `POST` | `/api/evs/automatic` | Ingest EV with auto classification |
| `POST` | `/api/process` | Process next vehicle & route to station |
| `POST` | `/api/charging/complete` | Complete active charging session |
| `POST` | `/api/reset` | Reset simulation runtime state |
| `POST` | `/api/clear` | Clear all data structures |
