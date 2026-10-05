class Graph:
    """
    Weighted graph using an adjacency list.

    Each vertex represents a location/intersection.
    Each edge represents a road between two locations.

    Example:

        A ---- B
        |      |
        |      |
        C ---- D

    Adjacency list:

        A -> [(B, weight), (C, weight)]
        B -> [(A, weight), (D, weight)]
        ...
    """

    def __init__(self, directed=False):
        """
        Create an empty graph.

        Args:
            directed: 
                False -> Undirected graph
                True  -> Directed graph
        """

        self.adjacency_list = {}
        self.directed = directed

    def add_vertex(self, vertex):
        """
        Add a vertex to the graph.

        Time Complexity: O(1)
        """

        if vertex not in self.adjacency_list:
            self.adjacency_list[vertex] = []

    def add_edge(self, source, destination, weight):
        """
        Add a weighted edge between two vertices.

        For an undirected graph:

            A -> B

        also creates:

            B -> A

        Time Complexity: O(1)
        """

        if weight < 0:
            raise ValueError("Edge weight cannot be negative")

        # Make sure both vertices exist
        self.add_vertex(source)
        self.add_vertex(destination)

        # Add source -> destination
        self.adjacency_list[source].append(
            (destination, weight)
        )

        # Add destination -> source for undirected graph
        if not self.directed:
            self.adjacency_list[destination].append(
                (source, weight)
            )

    def remove_vertex(self, vertex):
        """
        Remove a vertex and all edges connected to it.

        Time Complexity: O(V + E)
        """

        if vertex not in self.adjacency_list:
            raise KeyError(f"Vertex '{vertex}' does not exist")

        # Remove the vertex itself
        del self.adjacency_list[vertex]

        # Remove edges pointing to the vertex
        for current_vertex in self.adjacency_list:
            self.adjacency_list[current_vertex] = [
                (neighbor, weight)
                for neighbor, weight
                in self.adjacency_list[current_vertex]
                if neighbor != vertex
            ]

    def remove_edge(self, source, destination):
        """
        Remove edge between source and destination.

        Raises:
            KeyError: If either vertex does not exist
            KeyError: If the edge does not exist

        Time Complexity:
            O(E) in the source adjacency list.
        """

        if source not in self.adjacency_list:
            raise KeyError(f"Vertex '{source}' does not exist")

        if destination not in self.adjacency_list:
            raise KeyError(f"Vertex '{destination}' does not exist")

        # Check whether the edge actually exists
        edge_exists = False

        for neighbor, _ in self.adjacency_list[source]:
            if neighbor == destination:
                edge_exists = True
                break

        if not edge_exists:
            raise KeyError(
                f"Edge '{source}' -> '{destination}' does not exist"
            )

        # Remove source -> destination
        self.adjacency_list[source] = [
            (neighbor, weight)
            for neighbor, weight in self.adjacency_list[source]
            if neighbor != destination
        ]

        # Remove reverse edge for undirected graph
        if not self.directed:
            self.adjacency_list[destination] = [
                (neighbor, weight)
                for neighbor, weight in self.adjacency_list[destination]
                if neighbor != source
            ]

    def get_neighbors(self, vertex):
        """
        Return all neighboring vertices and their weights.

        Example:

            graph.get_neighbors("A")

            [
                ("B", 4),
                ("C", 2)
            ]

        Time Complexity: O(1)
        """

        if vertex not in self.adjacency_list:
            raise KeyError(f"Vertex '{vertex}' does not exist")

        return self.adjacency_list[vertex].copy()

    def has_vertex(self, vertex):
        """
        Check whether a vertex exists.

        Time Complexity: O(1)
        """

        return vertex in self.adjacency_list

    def has_edge(self, source, destination):
        """
        Check whether an edge exists.

        Time Complexity: O(E)
        """

        if source not in self.adjacency_list:
            return False

        for neighbor, _ in self.adjacency_list[source]:
            if neighbor == destination:
                return True

        return False

    def vertex_count(self):
        """
        Return number of vertices.

        Time Complexity: O(1)
        """

        return len(self.adjacency_list)

    def edge_count(self):
        """
        Return number of edges.

        Time Complexity: O(V + E)
        """

        total_edges = sum(
            len(neighbors)
            for neighbors in self.adjacency_list.values()
        )

        if self.directed:
            return total_edges

        return total_edges // 2

    def get_vertices(self):
        """
        Return all vertices.

        Time Complexity: O(V)
        """

        return list(self.adjacency_list.keys())
    def get_edges(self):
        """
        Return all graph edges in a JSON-friendly format.

        For an undirected graph, each edge is returned only once
        even though the adjacency list stores it in both directions.

        Example:

            [
                {
                    "source": "A",
                    "destination": "B",
                    "weight": 4
                }
            ]

        For a directed graph, every directed edge is returned.

        Time Complexity:
            O(V + E)
        """

        edges = []

        if self.directed:

            for source, neighbors in self.adjacency_list.items():

                for destination, weight in neighbors:

                    edges.append({
                        "source": source,
                        "destination": destination,
                        "weight": weight
                    })

            return edges

        # -----------------------------------------------------
        # Undirected graph
        # -----------------------------------------------------

        processed_edges = set()

        for source, neighbors in self.adjacency_list.items():

            for destination, weight in neighbors:

                # frozenset makes A-B and B-A equivalent
                edge_key = frozenset(
                    (source, destination)
                )

                if edge_key in processed_edges:
                    continue

                processed_edges.add(edge_key)

                edges.append({
                    "source": source,
                    "destination": destination,
                    "weight": weight
                })

        return edges
    
    def display(self):
        """
        Return the complete adjacency list.

        Example:

            {
                "A": [("B", 4), ("C", 2)],
                "B": [("A", 4)]
            }
        """

        return {
            vertex: neighbors.copy()
            for vertex, neighbors
            in self.adjacency_list.items()
        }

    def clear(self):
        """
        Remove all vertices and edges.

        Time Complexity: O(1)
        """

        self.adjacency_list.clear()

    def __len__(self):
        """
        Return number of vertices.
        """

        return self.vertex_count()

    def __str__(self):
        """
        Human-readable adjacency list.
        """

        lines = []

        for vertex, neighbors in self.adjacency_list.items():
            formatted_neighbors = " -> ".join(
                f"{neighbor}({weight})"
                for neighbor, weight in neighbors
            )

            if formatted_neighbors:
                lines.append(
                    f"{vertex} -> {formatted_neighbors}"
                )
            else:
                lines.append(
                    f"{vertex} ->"
                )

        return "\n".join(lines)