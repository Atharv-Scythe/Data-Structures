# Smart EV Charging Queue & Route Optimizer
## Start-to-End Implementation Plan Used in the Project

**Project type:** Data Structures Course Project  
**Backend:** Python + Flask  
**Frontend:** HTML + CSS + JavaScript  
**Core Data Structures:** Simple Queue, Min-Heap Priority Queue, Deque  
**Algorithm:** Graph + Dijkstra  
**Current test checkpoint:** 202 tests passing  
**Current application state:** Backend/API working + connected frontend dashboard

---

## 1. Project Objective

Build a full-stack educational EV charging simulation that demonstrates core Data Structures and Algorithms through a realistic use case.

The project models:

- EV arrivals
- Normal FIFO charging requests
- Critical/urgent EV scheduling using a Priority Queue implemented with a Min-Heap
- Special/VIP EV handling using a Deque
- Charging station availability
- Graph-based road networks
- Shortest-path routing using Dijkstra's algorithm
- Event/history tracking
- A frontend dashboard for visualization
- REST API communication between frontend and backend
- Dockerized deployment as the final stage

The project is simulation-only. No real EV charging hardware is controlled.

---

# 2. Final Architecture

```text
                    ┌────────────────────────────┐
                    │        FRONTEND             │
                    │      HTML/CSS/JS            │
                    │                            │
                    │ Dashboard                   │
                    │ Queue Visualizers           │
                    │ Graph / Route Visualizer    │
                    │ Controls / Event Timeline   │
                    └─────────────┬──────────────┘
                                  │ HTTP / JSON
                                  ▼
                    ┌────────────────────────────┐
                    │        FLASK API            │
                    │      REST Endpoints         │
                    └─────────────┬──────────────┘
                                  │
                                  ▼
                    ┌────────────────────────────┐
                    │    EVChargingSimulation     │
                    │       Coordinator           │
                    └─────────────┬──────────────┘
                                  │
             ┌────────────────────┼────────────────────┐
             ▼                    ▼                    ▼
      ChargingManager       RouteManager         Event/Snapshot
             │                    │                    │
       ┌─────┼─────┐              │                    │
       ▼     ▼     ▼              ▼                    ▼
     Queue  Heap  Deque       Graph + Dijkstra       JSON State
```

---

# 3. Implementation Philosophy

The project was intentionally developed from the Data Structures layer upward.

The important architectural decision was:

```text
Data Structures
      ↓
Algorithms
      ↓
Models
      ↓
Services
      ↓
Simulation
      ↓
API
      ↓
Frontend
      ↓
Docker
```

The Flask layer does not reimplement the Data Structures. It exposes the existing simulation.

The core structures remain manually implemented rather than replacing them with Python's built-in queue/deque/heap implementations.

---

# 4. Actual Project Structure

```text
D:\Data Structure cp│
├── backend│   ├── app.py
│   ├── requirements.txt
│   │
│   ├── src│   │   ├── __init__.py
│   │   │
│   │   ├── api│   │   │   ├── __init__.py
│   │   │   └── routes.py
│   │   │
│   │   ├── algorithms│   │   │   ├── __init__.py
│   │   │   ├── graph.py
│   │   │   └── dijkstra.py
│   │   │
│   │   ├── data_structures│   │   │   ├── __init__.py
│   │   │   ├── queue.py
│   │   │   ├── min_heap.py
│   │   │   └── deque.py
│   │   │
│   │   ├── models│   │   │   ├── __init__.py
│   │   │   ├── ev.py
│   │   │   └── station.py
│   │   │
│   │   └── services│   │       ├── __init__.py
│   │       ├── charging_manager.py
│   │       ├── route_manager.py
│   │       └── simulation.py
│   │
│   └── tests│       ├── test_queue.py
│       ├── test_min_heap.py
│       ├── test_deque.py
│       ├── test_graph.py
│       ├── test_dijkstra.py
│       ├── test_ev.py
│       ├── test_station.py
│       ├── test_charging_manager.py
│       ├── test_route_manager.py
│       ├── test_simulation.py
│       └── test_api.py
│
├── frontend│   ├── index.html
│   ├── css│   │   └── style.css
│   └── js│       ├── api.js
│       └── main.js
│
└── [final-stage files]
    ├── docker-compose.yml
    ├── backend/Dockerfile
    ├── frontend/Dockerfile
    ├── frontend/nginx.conf
    ├── README.md
    └── docs```

---

# 5. Phase 1 — Core Data Structures

## 5.1 Simple Queue

### File

```text
backend/src/data_structures/queue.py
```

### Purpose

Models normal EVs waiting in arrival order.

### Main implementation

A circular-array-style queue was implemented manually.

### Operations

```text
enqueue()
dequeue()
peek()
is_empty()
is_full()
size()
display()
clear()
__len__()
__str__()
```

### Concept demonstrated

FIFO:

```text
First EV In → First EV Out
```

### Complexity

```text
enqueue   O(1)
dequeue   O(1)
peek      O(1)
size      O(1)
```

---

## 5.2 Min-Heap / Priority Queue

### File

```text
backend/src/data_structures/min_heap.py
```

### Purpose

Models urgent EV scheduling.

Lower priority value is handled first.

The Min-Heap is also reused by Dijkstra.

### Operations

```text
insert()
extract_min()
peek_min()
heapify_up
heapify_down
size()
display()
clear()
```

### Structure

Each heap item is represented using:

```text
(priority, item)
```

### Concept demonstrated

Priority scheduling using a binary Min-Heap.

### Complexity

```text
insert       O(log n)
extract_min  O(log n)
peek_min     O(1)
```

---

## 5.3 Deque

### File

```text
backend/src/data_structures/deque.py
```

### Purpose

Models special/VIP EV handling where insertion/removal may happen at either end.

### Operations

```text
add_front()
add_rear()
remove_front()
remove_rear()
peek_front()
peek_rear()
is_empty()
is_full()
size()
display()
clear()
```

### Concept demonstrated

Double-ended access.

### Complexity

```text
add_front     O(1)
add_rear      O(1)
remove_front  O(1)
remove_rear   O(1)
```

---

# 6. Phase 2 — Graph and Algorithm

## 6.1 Graph

### File

```text
backend/src/algorithms/graph.py
```

### Purpose

Models the road network.

Vertices represent:

```text
locations / intersections
```

Edges represent:

```text
roads with weights
```

### Implementation

Adjacency list:

```text
A -> [(B, 4), (C, 2)]
B -> [...]
```

### Features

```text
add_vertex()
add_edge()
remove_vertex()
remove_edge()
get_neighbors()
has_vertex()
has_edge()
vertex_count()
edge_count()
get_vertices()
display()
clear()
get_edges()
```

The `get_edges()` method was later added to make the graph easy to expose to the frontend without duplicating undirected edges.

---

## 6.2 Dijkstra

### File

```text
backend/src/algorithms/dijkstra.py
```

### Purpose

Find shortest routes through the charging network.

### Important design choice

Dijkstra uses the project's own:

```text
MinHeap
```

instead of Python's built-in `heapq`.

This keeps the algorithm connected to the Data Structures portion of the project.

### Output

The algorithm returns:

```text
distances
previous
```

and route reconstruction produces:

```text
[path]
```

Example:

```text
A → C → D → E
```

with total distance:

```text
5
```

for the current demo graph.

---

# 7. Phase 3 — Models

## 7.1 EV Model

### File

```text
backend/src/models/ev.py
```

### Main fields

```text
ev_id
battery_level
battery_capacity
charging_required
priority
location
```

### Main behavior

```text
is_critical()
battery_needed()
```

Critical battery levels can automatically enter the priority queue.

---

## 7.2 Charging Station

### File

```text
backend/src/models/station.py
```

### Main fields

```text
station_id
location
charging_slots
active_evs
```

### Main behavior

```text
has_available_slot()
start_charging()
stop_charging()
active_count()
```

---

# 8. Phase 4 — Services

## 8.1 Charging Manager

### File

```text
backend/src/services/charging_manager.py
```

### Responsibility

Coordinates the three Data Structures:

```text
normal_queue
priority_queue
special_deque
```

It also tracks:

```text
charging_evs
completed_evs
```

### Main operations

```text
add_normal_ev()
add_priority_ev()
add_special_ev()

get_next_normal_ev()
get_next_priority_ev()
get_next_special_ev()

start_charging()
complete_charging()

waiting_count()
charging_count()
completed_count()
total_ev_count()

get_status()
clear()
```

---

## 8.2 Route Manager

### File

```text
backend/src/services/route_manager.py
```

### Responsibility

Connects:

```text
Graph
+
Dijkstra
+
Charging Stations
```

### Main behavior

```text
add_station()
remove_station()
get_stations()
station_count()

calculate_route()
get_station_routes()
get_available_stations()
find_nearest_station()

clear()
```

This service finds the nearest available charging station using shortest-path distances.

---

# 9. Phase 5 — Simulation Coordinator

## File

```text
backend/src/services/simulation.py
```

Created to coordinate all parts of the project.

### Main responsibilities

```text
EV management
Station management
Queue selection
Route selection
Charging processing
Completion
Status reporting
Reset
Clear
```

### Main methods

```text
add_station()
remove_station()

add_ev()
add_ev_automatically()

get_next_ev()
process_next_ev()

complete_charging()

get_status()
reset()
clear()
```

---

# 10. Phase 6 — Event History

The simulation was extended with an event/history mechanism.

### Main fields

```text
event_history
event_counter
```

### Main methods

```text
_record_event()
get_event_history()
clear_event_history()
```

### Example trace

```text
Step 1  EV001 arrived at charging network
Step 2  EV001 added to normal queue
Step 3  EV002 arrived at charging network
Step 4  EV002 automatically classified as priority
Step 5  EV002 selected from priority queue
Step 6  Route calculated for EV002
Step 7  Station S1 assigned to EV002
Step 8  Charging started for EV002
Step 9  Charging completed for EV002
```

The event records use JSON-friendly dictionaries so they can later be returned directly by Flask.

---

# 11. Phase 7 — Simulation Snapshot

A complete state snapshot was added.

### Main method

```text
simulation.get_snapshot()
```

### Snapshot structure

```text
queues
├── normal
├── priority
└── special

charging
completed
stations
events
```

This creates the bridge between backend state and frontend visualization.

---

# 12. Phase 8 — Testing Strategy

Testing was performed continuously instead of waiting until the end.

## Test layers

```text
Data Structure tests
        ↓
Algorithm tests
        ↓
Model tests
        ↓
Service tests
        ↓
Simulation tests
        ↓
API tests
        ↓
Full regression suite
```

## Testing command

```powershell
python -m pytest -v
```

## Major checkpoints

```text
128 passed  → core DS/algorithm/model/service layer
158 passed  → simulation coordinator
165 passed  → event history
172 passed  → simulation snapshot
196 passed  → Flask API
202 passed  → graph API / graph serialization
```

The final current checkpoint is:

```text
202 passed
```

---

# 13. Phase 9 — Flask API

## Files

```text
backend/app.py
backend/requirements.txt
backend/src/api/__init__.py
backend/src/api/routes.py
backend/tests/test_api.py
```

## Architecture

The API receives the already-created simulation instance.

```text
Flask
  ↓
create_api_blueprint(simulation)
  ↓
EVChargingSimulation
```

The API does not create a second copy of the Data Structures.

---

# 14. Main API Endpoints

## Health

```text
GET /api/health
```

## Status

```text
GET /api/status
```

## Full snapshot

```text
GET /api/snapshot
```

## Event history

```text
GET /api/events
GET /api/events?limit=10
```

## Graph

```text
GET /api/graph
POST /api/graph/vertices
POST /api/graph/edges
```

## Stations

```text
GET  /api/stations
POST /api/stations
GET  /api/stations/nearest?start=A
```

## EVs

```text
GET  /api/evs
POST /api/evs
POST /api/evs/automatic
```

## Processing

```text
POST /api/process
POST /api/charging/complete
```

## Routing

```text
GET /api/routes?start=A&destination=E
```

## Simulation control

```text
POST /api/reset
POST /api/clear
```

---

# 15. Phase 10 — Frontend Foundation

## Current files

```text
frontend/index.html
frontend/css/style.css
frontend/js/api.js
frontend/js/main.js
```

## Current dashboard already supports

```text
API connection badge
Status cards
EV count
Waiting count
Charging count
Completed count
Station count
Event count

Add EV control
Process Next control
Reset control

Normal Queue panel
Priority Queue panel
Deque panel
Charging panel

Charging Station panel
Simulation Event Timeline
```

The frontend uses:

```text
HTTP fetch
+
REST API
+
JSON snapshots
```

The dashboard was verified to connect to:

```text
http://127.0.0.1:5000
```

using the frontend server:

```text
http://127.0.0.1:5500
```

---

# 16. Current Demo Graph

The default Flask application builds:

```text
Vertices:
A
B
C
D
E
```

Weighted roads:

```text
A --4-- B
A --2-- C
B --5-- D
B --9-- E
C --1-- D
C --7-- E
D --2-- E
```

This graph provides the demonstration network for Dijkstra and nearest-station routing.

---

# 17. Current End-to-End Flow

A normal EV:

```text
Frontend
   ↓
POST /api/evs
   ↓
EV object
   ↓
Simulation
   ↓
ChargingManager
   ↓
SimpleQueue
```

A critical EV:

```text
Frontend
   ↓
POST /api/evs/automatic
   ↓
EV.is_critical()
   ↓
MinHeap Priority Queue
```

Processing:

```text
POST /api/process
   ↓
Simulation.get_next_ev()
   ↓
Priority Queue / Deque / Simple Queue
   ↓
RouteManager
   ↓
Dijkstra
   ↓
Nearest available Station
   ↓
ChargingManager.start_charging()
   ↓
Event History
   ↓
Snapshot
   ↓
JSON
   ↓
Frontend
```

---

# 18. Why This Implementation Order Was Used

The order reduced integration risk.

Instead of starting with Flask or frontend, the project first established:

```text
correct Data Structures
```

Then:

```text
correct algorithms
```

Then:

```text
correct business models
```

Then:

```text
services that combine the structures
```

Then:

```text
simulation orchestration
```

Then:

```text
observable history + snapshot
```

Then:

```text
REST API
```

Then:

```text
frontend
```

Finally:

```text
Docker + documentation
```

This ensures the frontend is visualizing tested logic rather than hiding unfinished backend behavior.

---

# 19. Final Planned Product

The finished project should demonstrate all of the following visually:

```text
┌───────────────────────────────────────────────────────┐
│        SMART EV CHARGING CONTROL CENTER              │
├───────────────────────────────────────────────────────┤
│ EVs │ Waiting │ Charging │ Completed │ Stations      │
├───────────────┬───────────────┬───────────────────────┤
│ SIMPLE QUEUE  │ MIN HEAP      │ DEQUE                 │
│ FIFO          │ Priority Tree │ Double End            │
│ EV → EV → EV  │       EV      │ VIP ↔ EV ↔ EV         │
├───────────────┴───────────────┴───────────────────────┤
│                    CITY GRAPH                         │
│                                                       │
│     A ───── B                                         │
│      \       \                                       │
│       C ───── D ───── E                               │
│                                                       │
│       Dijkstra: A → C → D → E                        │
├───────────────────────────────┬───────────────────────┤
│ Charging Stations             │ Event / DS Trace      │
│ S1     S2     S3              │ #1 EV arrived         │
│                               │ #2 → Priority Queue   │
│                               │ #3 EV selected        │
└───────────────────────────────┴───────────────────────┘
```

---

# 20. Final Delivery Stages

The remaining stages are:

```text
1. Queue visualizer
2. Min-Heap tree visualizer
3. Deque visualizer
4. Graph/city-map visualization
5. Dijkstra route highlighting
6. EV movement animation
7. Charging-slot visualization
8. Auto-simulation mode
9. DS complexity/operation trace
10. Export/report feature
11. Docker backend
12. Docker frontend + Nginx
13. docker-compose
14. README
15. Architecture documentation
16. Complexity documentation
17. Screenshots
18. Final regression testing
19. Final demo walkthrough
```

---

# 21. Completion Criteria

The project is considered complete when:

```text
[ ] All backend tests pass
[ ] API tests pass
[ ] Frontend connects to API
[ ] Queue visualization works
[ ] Min-Heap visualization works
[ ] Deque visualization works
[ ] Graph is rendered from API data
[ ] Dijkstra route is highlighted
[ ] EV processing is animated
[ ] Charging stations show availability
[ ] Event timeline updates live
[ ] Auto-simulation runs without errors
[ ] Docker build succeeds
[ ] docker-compose starts the full application
[ ] README is complete
[ ] Complexity analysis is documented
[ ] Final demo workflow is reproducible
```

---

## Current Milestone

```text
Core DS                         COMPLETE
Algorithms                      COMPLETE
Models                          COMPLETE
Services                        COMPLETE
Simulation                      COMPLETE
Event History                   COMPLETE
Snapshot                        COMPLETE
Flask REST API                  COMPLETE
API Testing                     COMPLETE
Frontend Foundation             COMPLETE
Frontend Visualizations         REMAINING
Docker                          REMAINING
Documentation                   REMAINING
Final Demo                      REMAINING

Current automated tests:
202 PASSED
```
