# Smart EV Charging Control Center — Complexity Analysis & Tradeoffs

## Theoretical & Empirical Complexity Matrix

| Component / Operation | Data Structure Used | Time Complexity (Best) | Time Complexity (Worst) | Space Complexity |
| :--- | :--- | :--- | :--- | :--- |
| **Normal EV Ingestion** | Simple Queue (FIFO) | $O(1)$ | $O(1)$ | $O(n)$ |
| **Normal EV Processing** | Simple Queue (FIFO) | $O(1)$ | $O(1)$ | $O(1)$ |
| **Critical EV Ingestion** | Binary Min-Heap | $O(1)$ | $O(\log n)$ | $O(n)$ |
| **Critical EV Selection** | Binary Min-Heap | $O(1)$ | $O(\log n)$ | $O(1)$ |
| **VIP EV Ingestion** | Double-Ended Queue (Deque) | $O(1)$ | $O(1)$ | $O(n)$ |
| **VIP EV Selection** | Double-Ended Queue (Deque) | $O(1)$ | $O(1)$ | $O(1)$ |
| **Graph Construction** | Adjacency List | $O(1)$ per edge | $O(V + E)$ | $O(V + E)$ |
| **Shortest Route Search** | Dijkstra + MinHeap | $O((V + E) \log V)$ | $O((V + E) \log V)$ | $O(V)$ |
| **Nearest Station Search** | Dijkstra Loop across stations | $O(S \cdot (V + E) \log V)$ | $O(S \cdot (V + E) \log V)$ | $O(V)$ |

---

## Architectural Tradeoffs

### 1. Custom Min-Heap vs Built-in `heapq` / `queue.PriorityQueue`
- **Tradeoff:** Writing a custom `MinHeap` class requires explicit index tracking and manual `heapify_up` / `heapify_down` loops.
- **Benefit:** Allows complete transparency into binary tree step-by-step swaps, array representations, custom priorities, and full integration into the educational visualizer.

### 2. Adjacency List vs Adjacency Matrix for City Graph
- **Tradeoff:** Matrix enables $O(1)$ edge existence checks, but requires $O(V^2)$ memory.
- **Benefit:** Adjacency List uses $O(V + E)$ memory, which is optimal for sparse road networks where degree per intersection is low.

### 3. Deque for VIP Bypass
- **Tradeoff:** Allows vehicles to jump straight to the head of the queue (`add_front`).
- **Benefit:** Ensures $O(1)$ urgency handling without restructuring an entire priority tree.
