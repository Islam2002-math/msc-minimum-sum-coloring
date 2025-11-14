from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Set
import random


Vertex = int


@dataclass
class Graph:
    """Simple undirected graph based on an adjacency list.

    Vertices are represented by consecutive integers in ``range(n)``.
    The adjacency structure is symmetric: if ``u`` is in ``adj[v]``, then
    ``v`` is in ``adj[u]``.
    """

    n: int
    adj: Dict[Vertex, Set[Vertex]]

    def neighbors(self, v: Vertex) -> Set[Vertex]:
        return self.adj.get(v, set())


def generate_erdos_renyi_graph(
    n: int,
    p: float,
    seed: int | None = None,
) -> Graph:
    """Generate an undirected Erdős–Rényi G(n, p) graph.

    Parameters
    ----------
    n:
        Number of vertices.
    p:
        Probability that each potential edge is present.
    seed:
        Optional random seed for reproducibility.
    """

    if not (0.0 <= p <= 1.0):
        raise ValueError("p must be in [0, 1]")

    rng = random.Random(seed)
    adj: Dict[Vertex, Set[Vertex]] = {v: set() for v in range(n)}

    for u in range(n):
        for v in range(u + 1, n):
            if rng.random() < p:
                adj[u].add(v)
                adj[v].add(u)

    return Graph(n=n, adj=adj)


def generate_random_graphs(
    count: int,
    n: int,
    p: float,
    base_seed: int | None = None,
) -> List[Graph]:
    """Generate a list of independent Erdős–Rényi graphs.

    ``base_seed`` (if provided) is used to derive deterministic seeds
    for each graph, so that the whole batch is reproducible.
    """

    seeds: List[int | None]
    if base_seed is None:
        seeds = [None] * count
    else:
        seeds = [base_seed + i for i in range(count)]

    return [generate_erdos_renyi_graph(n=n, p=p, seed=s) for s in seeds]