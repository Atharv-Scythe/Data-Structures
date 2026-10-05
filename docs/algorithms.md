# Smart EV Charging Control Center — Algorithms & Data Structures

## Data Structures Implementation Details

### 1. Simple Queue (FIFO)
The `SimpleQueue` handles normal EVs. Vehicles are queued in arrival order. When a charging slot becomes available, the EV at the **front** of the queue is processed first.

```text
Enqueue -> [ EV003 | EV002 | EV001 ] -> Dequeue (Front)
```

- **Time Complexity:**
  - Enqueue: $O(1)$
  - Dequeue: $O(1)$
  - Peek: $O(1)$

---

### 2. Min-Heap (Priority Queue)
The `MinHeap` stores items formatted as `(priority, item)`. It guarantees that the EV or node with the **lowest numerical priority value** (e.g. priority 1 before priority 5) is always at the root index `0`.

```text
          (P:1, EV002) [Root Node]
          /          \
  (P:3, EV005)     (P:2, EV004)
```

- **Parent Index Formula:** `(i - 1) // 2`
- **Left Child Index Formula:** `2 * i + 1`
- **Right Child Index Formula:** `2 * i + 2`
- **Time Complexity:**
  - Insert: $O(\log n)$ (via `heapify_up`)
  - Extract-Min: $O(\log n)$ (via `heapify_down`)
  - Peek-Min: $O(1)$

---

### 3. Deque (Double-Ended Queue)
The `EVDeque` supports constant-time push and pop operations at both ends (`FRONT` and `REAR`). This is utilized for special/VIP vehicles requiring instant insertion at the front of the line or custom scheduling.

```text
Push Front -> [ FRONT | EV007 | EV008 | REAR ] <- Push Rear
```

- **Time Complexity:**
  - Add Front / Rear: $O(1)$
  - Remove Front / Rear: $O(1)$

---

## Routing Algorithm — Dijkstra Shortest Path

### Graph Representation
The city network is stored as an **Adjacency List**:
```text
Node A -> [(B, 4), (C, 2)]
Node B -> [(A, 4), (D, 5), (E, 9)]
Node C -> [(A, 2), (D, 1), (E, 7)]
Node D -> [(B, 5), (C, 1), (E, 2)]
Node E -> [(B, 9), (C, 7), (D, 2)]
```

### Dijkstra Step-by-Step Traversal
1. Initialize distances from `start` node to all vertices as $\infty$, with `start` distance = 0.
2. Insert `(0, start)` into the custom `MinHeap`.
3. Extract vertex $u$ with minimum distance from heap.
4. For each neighbor $v$ with weight $w$:
   - If `dist[u] + w < dist[v]`:
     - `dist[v] = dist[u] + w`
     - `previous[v] = u`
     - Insert `(dist[v], v)` into `MinHeap`.
5. Reconstruct shortest path by tracing `previous` backwards from destination to start.

- **Time Complexity:** $O((V + E) \log V)$ using binary Min-Heap.
- **Space Complexity:** $O(V + E)$ for adjacency list and distance tables.
