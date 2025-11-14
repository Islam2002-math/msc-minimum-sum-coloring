# WARP.md

This file provides guidance to WARP (warp.dev) when working with code in this repository.

## Project overview

This is a Python project to experiment with **Minimum Sum Coloring (MSC)** on random graphs using a greedy heuristic followed by Tabu Search improvements.

Planned workflow (from `README.md`):
- Generate 20 random graphs (n = 100, p = 0.2).
- Compute an initial MSC solution with a greedy heuristic.
- Use Tabu Search to improve the greedy solution.
- Compare results (sum of colors, runtime, etc.).

The implementation is currently a skeleton: source files exist but are mostly empty stubs intended to host the logic described above.

## Commands and development workflow

All commands below assume the repo root as the working directory and a Python environment already activated.

### Run the main program

From `README.md`, the canonical way to run the project is:

```bash
python -m src.main
```

This executes the `src` package as a module, using `main.py` as the entrypoint once it is implemented.

### Dependencies

- `requirements.txt` exists but is currently empty, so there are no pinned third-party dependencies.
- The project is expected to work with standard Python tooling; when you start adding external libraries, keep `requirements.txt` up to date and prefer importing them from within the `src` package.

### Tests and linting

There is currently no tests directory or test configuration in the repo, and no linter configuration files.

If you introduce tests with `pytest`, common commands will be:
- Run all tests:
  ```bash
  pytest
  ```
- Run a single test file or test:
  ```bash
  pytest path/to/test_file.py::TestClass::test_name
  ```

If you add a linter (e.g. `ruff`, `flake8`), define a clear entry command (e.g. via `make`, `tox`, or simple shell commands) so future tools can call it consistently.

## High-level architecture and structure

### Packages and layout

- `src/`
  - Python package for all project code. It is meant to contain:
    - `main.py`: Orchestrates the full experiment (graph generation, greedy MSC, Tabu Search, result comparison). This is the module invoked via `python -m src.main`.
    - `graph_generation.py`: Responsible for generating random graphs (e.g., 20 graphs with n = 100, p = 0.2). Keep graph representation and generation logic here so heuristic and search modules can stay focused on optimization logic.
    - `greedy_msc.py`: Hosts the greedy heuristic for Minimum Sum Coloring.
    - `tabu_search_msc.py`: Hosts the Tabu Search procedure that refines the greedy solution.
    - `__init__.py`: Marks `src` as a package; can expose high-level APIs (e.g. `run_experiment`) once the code matures.

As of now, these modules are empty; they define the intended modular structure rather than completed implementations.

### Intended responsibilities and interactions

- **Graph generation (`graph_generation.py`)**
  - Provide functions to generate one or more random graphs with configurable parameters (number of vertices `n`, edge probability `p`, random seed, etc.).
  - Output a graph representation that is stable across the project (e.g., adjacency lists or adjacency matrices) so the greedy and Tabu Search modules can work against a common interface.

- **Greedy heuristic (`greedy_msc.py`)**
  - Implement the initial MSC solution using a greedy algorithm.
  - Accept graphs from `graph_generation` and return:
    - A coloring assignment (vertex → color).
    - The total sum of colors used.

- **Tabu Search (`tabu_search_msc.py`)**
  - Start from the greedy solution and iteratively explore neighboring colorings to reduce the sum of colors.
  - Maintain Tabu structures (e.g., Tabu list, tenure) and stopping criteria (iterations, time budget, no-improvement threshold).
  - Return an improved coloring and associated metrics.

- **Experiment orchestration (`main.py`)**
  - Glue module that:
    - Configures experiment parameters (number of graphs, `n`, `p`, random seeds, Tabu parameters).
    - Calls `graph_generation` to build graphs.
    - Runs `greedy_msc` to obtain baseline solutions.
    - Runs `tabu_search_msc` on those solutions.
    - Aggregates and prints or logs comparison data: sum of colors, runtime, possibly distributions across the 20 graphs.

When extending the project, prefer creating new modules under `src/` (e.g., `evaluation.py`, `visualization.py`) rather than crowding `main.py`, and keep inter-module dependencies flowing from `main.py` into more specialized modules, not the other way around.
