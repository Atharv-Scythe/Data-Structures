import pytest

from src.algorithms.graph import Graph
from src.algorithms.dijkstra import dijkstra, get_shortest_path


def create_sample_graph():
    graph = Graph()

    graph.add_edge("A", "B", 4)
    graph.add_edge("A", "C", 2)
    graph.add_edge("B", "C", 1)
    graph.add_edge("B", "D", 5)
    graph.add_edge("C", "D", 8)
    graph.add_edge("C", "E", 10)
    graph.add_edge("D", "E", 2)

    return graph


def test_dijkstra_basic():
    graph = create_sample_graph()

    distances, previous = dijkstra(graph, "A")

    assert distances["A"] == 0
    assert distances["B"] == 3
    assert distances["C"] == 2
    assert distances["D"] == 8
    assert distances["E"] == 10


def test_dijkstra_previous_vertices():
    graph = create_sample_graph()

    distances, previous = dijkstra(graph, "A")

    assert previous["C"] == "A"
    assert previous["B"] == "C"
    assert previous["D"] == "B"
    assert previous["E"] == "D"


def test_shortest_path():
    graph = create_sample_graph()

    distances, previous = dijkstra(graph, "A")

    path = get_shortest_path(
        previous,
        "A",
        "E"
    )

    assert path == ["A", "C", "B", "D", "E"]


def test_shortest_distance():
    graph = create_sample_graph()

    distances, previous = dijkstra(graph, "A")

    path = get_shortest_path(
        previous,
        "A",
        "D"
    )

    assert path == ["A", "C", "B", "D"]
    assert distances["D"] == 8


def test_source_to_source():
    graph = create_sample_graph()

    distances, previous = dijkstra(graph, "A")

    path = get_shortest_path(
        previous,
        "A",
        "A"
    )

    assert path == ["A"]
    assert distances["A"] == 0


def test_unreachable_vertex():
    graph = Graph()

    graph.add_edge("A", "B", 5)
    graph.add_vertex("C")

    distances, previous = dijkstra(graph, "A")

    assert distances["C"] == float("inf")

    path = get_shortest_path(
        previous,
        "A",
        "C"
    )

    assert path == []


def test_invalid_start_vertex():
    graph = create_sample_graph()

    with pytest.raises(KeyError):
        dijkstra(graph, "X")


def test_invalid_graph_type():
    with pytest.raises(TypeError):
        dijkstra("not a graph", "A")


def test_invalid_destination():
    graph = create_sample_graph()

    distances, previous = dijkstra(graph, "A")

    with pytest.raises(KeyError):
        get_shortest_path(
            previous,
            "A",
            "X"
        )


def test_alternative_shorter_route():
    graph = Graph()

    graph.add_edge("A", "B", 10)
    graph.add_edge("A", "C", 3)
    graph.add_edge("C", "B", 2)

    distances, previous = dijkstra(graph, "A")

    assert distances["B"] == 5

    path = get_shortest_path(
        previous,
        "A",
        "B"
    )

    assert path == ["A", "C", "B"]


def test_multiple_routes():
    graph = Graph()

    graph.add_edge("A", "B", 2)
    graph.add_edge("A", "C", 5)
    graph.add_edge("B", "C", 1)
    graph.add_edge("B", "D", 4)
    graph.add_edge("C", "D", 1)

    distances, previous = dijkstra(graph, "A")

    assert distances["A"] == 0
    assert distances["B"] == 2
    assert distances["C"] == 3
    assert distances["D"] == 4

    path = get_shortest_path(
        previous,
        "A",
        "D"
    )

    assert path == ["A", "B", "C", "D"]