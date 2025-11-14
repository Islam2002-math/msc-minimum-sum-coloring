from __future__ import annotations

from typing import Dict, Tuple

from .graph_generation import Graph, Vertex


Color = int
Coloring = Dict[Vertex, Color]


def greedy_msc(graph: Graph) -> Tuple[Coloring, int]:
    """Greedy heuristic for Minimum Sum Coloring.

    The algorithm processes vertices in non-increasing degree order and
    assigns to each vertex the smallest positive color that does not
    conflict with already-colored neighbors. This is a standard greedy
    coloring strategy adapted to the minimum-sum objective.

    Returns
    -------
    coloring:
        Mapping from vertex to assigned color (1, 2, 3, ...).
    total_sum:
        Sum of colors over all vertices.
    """

    # Order vertices by decreasing degree (ties broken by vertex id).
    vertices = list(range(graph.n))
    vertices.sort(key=lambda v: (-len(graph.neighbors(v)), v))

    coloring: Coloring = {}

    for v in vertices:
        forbidden_colors = {coloring[u] for u in graph.neighbors(v) if u in coloring}
        color = 1
        while color in forbidden_colors:
            color += 1
        coloring[v] = color

    total_sum = sum(coloring.values())
    return coloring, total_sum