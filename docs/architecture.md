# Smart EV Charging Control Center — System Architecture

## Architecture Overview

The system follows a modular 6-tier architecture designed around strict separation of concerns, ensuring core Data Structures and Algorithms remain decoupled from HTTP transportation layers.

```text
┌─────────────────────────────────────────────────────────────┐
│                    FRONTEND DASHBOARD                       │
│     HTML5 • Modern CSS Glassmorphism • Modular JS ES6       │
│  (GraphVisualizer, HeapVisualizer, QueueVisualizer, Deque)  │
└──────────────────────────────┬──────────────────────────────┘
                               │ REST HTTP / JSON
                               ▼
┌─────────────────────────────────────────────────────────────┐
│                      FLASK REST API                         │
│           Blueprint Routes & JSON Serializers               │
└──────────────────────────────┬──────────────────────────────┘
                               │ Method Calls
                               ▼
┌─────────────────────────────────────────────────────────────┐
│                 SIMULATION COORDINATOR                      │
│                (EVChargingSimulation)                       │
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

## Data Structure & Component Mapping

### 1. Simple Queue (`SimpleQueue`)
- **File:** `backend/src/data_structures/queue.py`
- **Role:** First-In, First-Out (FIFO) queue for normal EV charging requests.
- **Operations:** `enqueue()`, `dequeue()`, `peek()`, `size()`, `is_empty()`.

### 2. Priority Queue / Min-Heap (`MinHeap`)
- **File:** `backend/src/data_structures/min_heap.py`
- **Role:** Array-based binary Min-Heap for critical/urgent EVs (battery < 20% or high priority) and priority optimization inside Dijkstra.
- **Operations:** `insert()`, `extract_min()`, `peek_min()`, `heapify_up()`, `heapify_down()`.

### 3. Deque (`EVDeque`)
- **File:** `backend/src/data_structures/deque.py`
- **Role:** Double-ended queue for special/VIP EVs or fast-track bypass.
- **Operations:** `add_front()`, `add_rear()`, `remove_front()`, `remove_rear()`, `peek_front()`, `peek_rear()`.

### 4. Graph Network & Dijkstra (`Graph`, `Dijkstra`)
- **Files:** `backend/src/algorithms/graph.py`, `backend/src/algorithms/dijkstra.py`
- **Role:** Models the city road network as an adjacency-list weighted graph. Dijkstra finds the shortest path to available charging stations using the system's own `MinHeap`.

---

## Event History & Snapshot Engine

The system maintains a full event log (`event_history`) tracking every step executed by the simulation, along with state snapshots containing JSON-serialized states of all three queues, active charging sessions, station capacity, and event streams.
