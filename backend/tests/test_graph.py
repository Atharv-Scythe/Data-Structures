import pytest

from src.algorithms.graph import Graph


def test_empty_graph():
    graph = Graph()

    assert graph.vertex_count() == 0
    assert graph.edge_count() == 0
    assert graph.get_vertices() == []


def test_add_vertex():
    graph = Graph()

    graph.add_vertex("A")
    graph.add_vertex("B")

    assert graph.has_vertex("A")
    assert graph.has_vertex("B")
    assert graph.vertex_count() == 2


def test_duplicate_vertex():
    graph = Graph()

    graph.add_vertex("A")
    graph.add_vertex("A")

    assert graph.vertex_count() == 1


def test_add_undirected_edge():
    graph = Graph()

    graph.add_edge("A", "B", 4)

    assert graph.has_edge("A", "B")
    assert graph.has_edge("B", "A")
    assert graph.edge_count() == 1


def test_edge_creates_vertices():
    graph = Graph()

    graph.add_edge("A", "B", 5)

    assert graph.has_vertex("A")
    assert graph.has_vertex("B")
    assert graph.vertex_count() == 2


def test_neighbors():
    graph = Graph()

    graph.add_edge("A", "B", 4)
    graph.add_edge("A", "C", 2)

    neighbors = graph.get_neighbors("A")

    assert ("B", 4) in neighbors
    assert ("C", 2) in neighbors
    assert len(neighbors) == 2


def test_edge_weights():
    graph = Graph()

    graph.add_edge("A", "B", 10)
    graph.add_edge("A", "C", 3)

    neighbors = graph.get_neighbors("A")

    assert ("B", 10) in neighbors
    assert ("C", 3) in neighbors


def test_negative_weight_rejected():
    graph = Graph()

    with pytest.raises(ValueError):
        graph.add_edge("A", "B", -5)


def test_remove_edge():
    graph = Graph()

    graph.add_edge("A", "B", 4)
    graph.add_edge("A", "C", 2)

    graph.remove_edge("A", "B")

    assert not graph.has_edge("A", "B")
    assert not graph.has_edge("B", "A")
    assert graph.has_edge("A", "C")
    assert graph.edge_count() == 1


def test_remove_vertex():
    graph = Graph()

    graph.add_edge("A", "B", 4)
    graph.add_edge("A", "C", 2)
    graph.add_edge("B", "C", 3)

    graph.remove_vertex("B")

    assert not graph.has_vertex("B")
    assert not graph.has_edge("A", "B")
    assert not graph.has_edge("B", "C")

    assert graph.has_vertex("A")
    assert graph.has_vertex("C")
    assert graph.has_edge("A", "C")


def test_vertex_count():
    graph = Graph()

    graph.add_vertex("A")
    graph.add_vertex("B")
    graph.add_vertex("C")

    assert graph.vertex_count() == 3


def test_edge_count_undirected():
    graph = Graph()

    graph.add_edge("A", "B", 1)
    graph.add_edge("B", "C", 2)
    graph.add_edge("C", "D", 3)

    assert graph.edge_count() == 3


def test_directed_graph():
    graph = Graph(directed=True)

    graph.add_edge("A", "B", 4)

    assert graph.has_edge("A", "B")
    assert not graph.has_edge("B", "A")
    assert graph.edge_count() == 1


def test_directed_neighbors():
    graph = Graph(directed=True)

    graph.add_edge("A", "B", 4)
    graph.add_edge("A", "C", 2)

    assert graph.get_neighbors("A") == [
        ("B", 4),
        ("C", 2)
    ]

    assert graph.get_neighbors("B") == []


def test_directed_remove_edge():
    graph = Graph(directed=True)

    graph.add_edge("A", "B", 4)

    graph.remove_edge("A", "B")

    assert not graph.has_edge("A", "B")


def test_missing_vertex():
    graph = Graph()

    with pytest.raises(KeyError):
        graph.get_neighbors("A")


def test_remove_missing_vertex():
    graph = Graph()

    with pytest.raises(KeyError):
        graph.remove_vertex("A")


def test_remove_missing_edge():
    graph = Graph()

    graph.add_vertex("A")
    graph.add_vertex("B")

    with pytest.raises(KeyError):
        graph.remove_edge("A", "B")


def test_get_vertices():
    graph = Graph()

    graph.add_vertex("A")
    graph.add_vertex("B")
    graph.add_vertex("C")

    vertices = graph.get_vertices()

    assert set(vertices) == {"A", "B", "C"}


def test_display():
    graph = Graph()

    graph.add_edge("A", "B", 4)
    graph.add_edge("A", "C", 2)

    display = graph.display()

    assert display["A"] == [
        ("B", 4),
        ("C", 2)
    ]

    assert display["B"] == [
        ("A", 4)
    ]


def test_clear():
    graph = Graph()

    graph.add_edge("A", "B", 4)
    graph.add_edge("B", "C", 3)

    graph.clear()

    assert graph.vertex_count() == 0
    assert graph.edge_count() == 0
    assert graph.get_vertices() == []


def test_len():
    graph = Graph()

    graph.add_vertex("A")
    graph.add_vertex("B")

    assert len(graph) == 2


def test_string_representation():
    graph = Graph()

    graph.add_edge("A", "B", 4)
    graph.add_edge("A", "C", 2)

    output = str(graph)

    assert "A ->" in output
    assert "B(4)" in output
    assert "C(2)" in output

# =========================================================
# GET EDGES TESTS
# =========================================================

def test_get_edges_undirected():

    graph = Graph()

    graph.add_edge("A", "B", 4)
    graph.add_edge("A", "C", 2)
    graph.add_edge("B", "D", 5)

    edges = graph.get_edges()

    assert len(edges) == 3

    assert {
        "source": "A",
        "destination": "B",
        "weight": 4
    } in edges

    assert {
        "source": "A",
        "destination": "C",
        "weight": 2
    } in edges

    assert {
        "source": "B",
        "destination": "D",
        "weight": 5
    } in edges


def test_get_edges_does_not_duplicate_undirected_edges():

    graph = Graph()

    graph.add_edge("A", "B", 10)

    edges = graph.get_edges()

    assert len(edges) == 1

    assert (
        edges[0]["source"] == "A"
        and edges[0]["destination"] == "B"
    ) or (
        edges[0]["source"] == "B"
        and edges[0]["destination"] == "A"
    )


def test_get_edges_directed():

    graph = Graph(directed=True)

    graph.add_edge("A", "B", 4)
    graph.add_edge("B", "A", 7)

    edges = graph.get_edges()

    assert len(edges) == 2

    assert {
        "source": "A",
        "destination": "B",
        "weight": 4
    } in edges

    assert {
        "source": "B",
        "destination": "A",
        "weight": 7
    } in edges


def test_get_edges_empty_graph():

    graph = Graph()

    assert graph.get_edges() == []