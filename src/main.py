from __future__ import annotations

from dataclasses import asdict
from time import perf_counter
from typing import List

from .graph_generation import generate_random_graphs, Graph
from .greedy_msc import greedy_msc
from .tabu_search_msc import tabu_search_msc, TabuSearchConfig
from .evaluation import ExperimentResult, save_experiment_artifacts


def run_experiment(
    num_graphs: int = 20,
    n: int = 100,
    p: float = 0.2,
    base_seed: int | None = 42,
) -> None:
    """Run the full MSC experiment over a batch of random graphs.

    For each graph, the function:
    - Generates a random graph G(n, p).
    - Computes a greedy MSC solution.
    - Improves it using Tabu Search.
    - Prints summary statistics.
    """

    print(f"Generating {num_graphs} random graphs with n={n}, p={p}...")
    graphs: List[Graph] = generate_random_graphs(
        count=num_graphs,
        n=n,
        p=p,
        base_seed=base_seed,
    )

    tabu_config = TabuSearchConfig()
    print("Tabu Search configuration:", asdict(tabu_config))

    greedy_sums: List[int] = []
    tabu_sums: List[int] = []
    results: List[ExperimentResult] = []

    example_graph: Graph | None = None
    example_coloring: dict[int, int] | None = None

    for idx, g in enumerate(graphs):
        print("\n=== Graph", idx + 1, "===")

        t0 = perf_counter()
        greedy_coloring, greedy_sum = greedy_msc(g)
        t1 = perf_counter()
        greedy_time = t1 - t0
        greedy_colors = max(greedy_coloring.values()) if greedy_coloring else 0

        print(
            f"Greedy MSC: sum={greedy_sum}, colors={greedy_colors}, time={greedy_time:.4f}s"
        )

        t2 = perf_counter()
        best_coloring, best_sum = tabu_search_msc(g, greedy_coloring, tabu_config)
        t3 = perf_counter()
        tabu_time = t3 - t2
        tabu_colors = max(best_coloring.values()) if best_coloring else 0

        print(
            f"Tabu Search MSC: sum={best_sum}, colors={tabu_colors}, time={tabu_time:.4f}s"
        )
        print(
            f"Improvement: {greedy_sum - best_sum} (lower is better), "
            f"colors change: {greedy_colors} -> {tabu_colors}"
        )

        greedy_sums.append(greedy_sum)
        tabu_sums.append(best_sum)

        results.append(
            ExperimentResult(
                index=idx + 1,
                greedy_sum=greedy_sum,
                tabu_sum=best_sum,
                greedy_time=greedy_time,
                tabu_time=tabu_time,
                greedy_colors=greedy_colors,
                tabu_colors=tabu_colors,
            )
        )

        if example_graph is None:
            example_graph = g
            example_coloring = best_coloring

    if greedy_sums:
        avg_greedy = sum(greedy_sums) / len(greedy_sums)
        avg_tabu = sum(tabu_sums) / len(tabu_sums)
        print("\n=== Summary over all graphs ===")
        print(f"Average greedy sum: {avg_greedy:.2f}")
        print(f"Average tabu sum:   {avg_tabu:.2f}")
        print(f"Average improvement: {avg_greedy - avg_tabu:.2f}")

    # Save CSV and plots for later inspection or for the web UI.
    save_experiment_artifacts(
        results=results,
        example_graph=example_graph,
        example_coloring=example_coloring,
    )


if __name__ == "__main__":
    # Entry point when running: python -m src.main
    run_experiment()