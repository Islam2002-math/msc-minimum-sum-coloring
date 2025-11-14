from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Tuple

from .graph_generation import Graph, Vertex


Color = int
Coloring = Dict[Vertex, Color]


@dataclass
class TabuSearchConfig:
    """Configuration parameters for the Tabu Search.

    These defaults are chosen to be reasonable for n ≈ 100.
    """

    max_iterations: int = 500
    tabu_tenure: int = 7
    max_no_improve: int = 100


def _objective(coloring: Coloring) -> int:
    return sum(coloring.values())


def tabu_search_msc(
    graph: Graph,
    initial_coloring: Coloring,
    config: TabuSearchConfig | None = None,
) -> Tuple[Coloring, int]:
    """Improve a valid coloring with Tabu Search.

    The search explores neighbor solutions obtained by recoloring a single
    vertex with a different (still valid) color. A simple Tabu list forbids
    recently applied moves for a fixed tenure, unless they lead to a new
    global best solution (aspiration criterion).
    """

    if config is None:
        config = TabuSearchConfig()

    current_coloring: Coloring = dict(initial_coloring)
    current_value = _objective(current_coloring)
    best_coloring: Coloring = dict(current_coloring)
    best_value = current_value

    # Tabu list: (vertex, color) -> iteration until which the move is tabu.
    tabu: Dict[Tuple[Vertex, Color], int] = {}

    max_color = max(current_coloring.values()) if current_coloring else 0

    iterations_without_improve = 0
    iteration = 0

    while iteration < config.max_iterations and iterations_without_improve < config.max_no_improve:
        iteration += 1
        best_move: Tuple[Vertex, Color] | None = None
        best_move_value: int | None = None

        # Explore 1-vertex recolor moves.
        for v in range(graph.n):
            current_color = current_coloring[v]

            # Try colors from 1 to max_color + 1 to allow new colors if helpful.
            for new_color in range(1, max_color + 2):
                if new_color == current_color:
                    continue

                # Check if assigning new_color to v preserves a proper coloring.
                if any(current_coloring[u] == new_color for u in graph.neighbors(v)):
                    continue

                new_value = current_value - current_color + new_color
                move = (v, new_color)
                tabu_until = tabu.get(move, -1)
                is_tabu = iteration <= tabu_until

                # Aspiration: allow tabu move if it improves global best.
                if is_tabu and new_value >= best_value:
                    continue

                if best_move is None or new_value < best_move_value:  # type: ignore[operator]
                    best_move = move
                    best_move_value = new_value

        if best_move is None or best_move_value is None:
            # No admissible move found (should be rare if graph is not pathological).
            break

        v, new_color = best_move
        old_color = current_coloring[v]

        # Apply move.
        current_coloring[v] = new_color
        current_value = best_move_value
        max_color = max(max_color, new_color)

        # Update Tabu list: forbids assigning this new_color to v again for a while
        # (which in practice prevents immediate cycling among a few colorings).
        tabu[(v, old_color)] = iteration + config.tabu_tenure

        if current_value < best_value:
            best_value = current_value
            best_coloring = dict(current_coloring)
            iterations_without_improve = 0
        else:
            iterations_without_improve += 1

    return best_coloring, best_value