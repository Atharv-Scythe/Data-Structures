from src.data_structures.min_heap import MinHeap
from src.algorithms.graph import Graph


def dijkstra(graph, start):
    """
    Find the shortest distance from start to every vertex.

    Uses:
        - Graph adjacency list
        - Custom MinHeap priority queue

    Returns:
        distances: shortest distance to every vertex
        previous: previous vertex on the shortest path

    Time Complexity:
        O((V + E) log V)
    """

    if not isinstance(graph, Graph):
        raise TypeError("graph must be a Graph object")

    if start not in graph.adjacency_list:
        raise KeyError(f"Vertex '{start}' does not exist")

    # Initially, every vertex is infinitely far away.
    distances = {}

    # Stores the previous vertex in the shortest path.
    previous = {}

    for vertex in graph.get_vertices():
        distances[vertex] = float("inf")
        previous[vertex] = None

    # Distance from start to itself is zero.
    distances[start] = 0

    # Create our custom MinHeap.
    priority_queue = MinHeap()

    # Insert starting vertex with priority 0.
    priority_queue.insert(start, 0)

    while not priority_queue.is_empty():

        # Get vertex with smallest current distance.
        current_distance, current_vertex = priority_queue.extract_min()

        # Ignore an outdated heap entry.
        if current_distance > distances[current_vertex]:
            continue

        # Explore all neighboring vertices.
        for neighbor, weight in graph.get_neighbors(current_vertex):

            new_distance = current_distance + weight

            # Found a shorter path.
            if new_distance < distances[neighbor]:

                distances[neighbor] = new_distance
                previous[neighbor] = current_vertex

                # Add updated distance to MinHeap.
                priority_queue.insert(
                    neighbor,
                    new_distance
                )

    return distances, previous


def get_shortest_path(previous, start, destination):
    """
    Reconstruct the shortest path from start to destination.

    Returns:
        List containing vertices in the shortest path.
    """

    if destination not in previous:
        raise KeyError(f"Vertex '{destination}' does not exist")

    path = []
    current = destination

    while current is not None:
        path.append(current)

        if current == start:
            break

        current = previous[current]

    # Destination cannot be reached from start.
    if path[-1] != start:
        return []

    path.reverse()

    return path