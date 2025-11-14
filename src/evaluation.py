from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, Optional

import matplotlib
matplotlib.use("Agg")  # backend sans interface graphique, adapté au serveur web
import matplotlib.pyplot as plt
import networkx as nx

from .graph_generation import Graph


@dataclass
class ExperimentResult:
    index: int
    greedy_sum: int
    tabu_sum: int
    greedy_time: float
    tabu_time: float
    # Nombre de couleurs utilisées (max des labels de couleur)
    greedy_colors: int | None = None
    tabu_colors: int | None = None


def _get_default_output_dir() -> Path:
    """Default directory for artifacts: `web/static` at project root."""

    # src/ -> project root -> web/static
    src_dir = Path(__file__).resolve().parent
    project_root = src_dir.parent
    web_static = project_root / "web" / "static"
    web_static.mkdir(parents=True, exist_ok=True)
    return web_static


def _plot_example_graph(graph: Graph, coloring: dict[int, int], output_path: Path) -> None:
    """Draw a colored graph using NetworkX + Matplotlib.

    Pour améliorer la lisibilité, on ne dessine qu'un sous-graphe avec
    au plus 40 sommets et on utilise des arêtes plus visibles.
    """

    max_nodes = min(graph.n, 40)
    nodes = list(range(max_nodes))

    G = nx.Graph()
    G.add_nodes_from(nodes)

    for u in nodes:
        for v in graph.neighbors(u):
            if v in nodes and u < v:
                G.add_edge(u, v)

    # Layout: spring layout pour une disposition lisible.
    pos = nx.spring_layout(G, seed=0)

    # Colors: map integer colors to a colormap.
    node_colors = [coloring.get(v, 0) for v in G.nodes]

    plt.figure(figsize=(6, 6))
    nx.draw_networkx(
        G,
        pos=pos,
        node_color=node_colors,
        cmap=plt.cm.get_cmap("tab20"),
        with_labels=False,
        node_size=60,
        edge_color="black",
        width=0.7,
        alpha=0.8,
    )
    plt.title("Exemple de graphe coloré (sous-graphe de 40 sommets)")
    plt.axis("off")
    plt.tight_layout()
    plt.savefig(output_path)
    plt.close()


def _plot_metrics(results: Iterable[ExperimentResult], output_path: Path) -> None:
    """Plot greedy vs tabu sums over all graphs."""

    res_list = list(results)
    if not res_list:
        return

    indices = [r.index for r in res_list]
    greedy_sums = [r.greedy_sum for r in res_list]
    tabu_sums = [r.tabu_sum for r in res_list]

    plt.figure(figsize=(8, 4))
    plt.plot(indices, greedy_sums, marker="o", label="Greedy")
    plt.plot(indices, tabu_sums, marker="o", label="Tabu Search")
    plt.xlabel("Indice du graphe")
    plt.ylabel("Somme des couleurs")
    plt.title("Comparaison Greedy vs Tabu Search (par graphe)")
    plt.legend()
    plt.grid(True, linestyle=":", linewidth=0.5)
    plt.tight_layout()
    plt.savefig(output_path)
    plt.close()


def save_experiment_artifacts(
    *,
    results: Iterable[ExperimentResult],
    example_graph: Optional[Graph],
    example_coloring: Optional[dict[int, int]],
    output_dir: Optional[Path] = None,
) -> None:
    """Save CSV and plots for later inspection and for the web UI.

    - metrics.csv : une ligne par graphe avec les métriques principales.
    - graph_example.png : dessin d'un graphe coloré (si dispo).
    - metrics.png : graphe des résultats Greedy vs Tabu.
    """

    if output_dir is None:
        output_dir = _get_default_output_dir()
    else:
        output_dir.mkdir(parents=True, exist_ok=True)

    res_list = list(results)
    if not res_list:
        return

    # 1) CSV des métriques
    csv_path = output_dir / "metrics.csv"
    try:
        with csv_path.open("w", encoding="utf-8") as f:
            f.write(
                "index,greedy_sum,tabu_sum,greedy_colors,tabu_colors,greedy_time,tabu_time\\n"
            )
            for r in res_list:
                f.write(
                    f"{r.index},{r.greedy_sum},{r.tabu_sum},{(r.greedy_colors or 0)},{(r.tabu_colors or 0)},{r.greedy_time:.6f},{r.tabu_time:.6f}\\n"
                )
    except PermissionError:
        # Si le fichier est ouvert dans un autre programme (Excel, etc.),
        # on ignore l'erreur pour ne pas faire planter le site.
        pass

    # 2) Graphique des métriques
    try:
        metrics_png = output_dir / "metrics.png"
        _plot_metrics(res_list, metrics_png)
    except PermissionError:
        pass

    # 3) Exemple de graphe coloré
    if example_graph is not None and example_coloring is not None:
        try:
            graph_png = output_dir / "graph_example.png"
            _plot_example_graph(example_graph, example_coloring, graph_png)
        except PermissionError:
            pass
