from __future__ import annotations

from pathlib import Path
import sys

from flask import Flask, render_template_string, request

# Ensure the project root (parent of this file's directory) is on sys.path so that
# "import src" works even if the app is launched from the "web" directory.
BASE_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = BASE_DIR.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.main import run_experiment
from src.evaluation import ExperimentResult

STATIC_DIR = BASE_DIR / "static"
STATIC_DIR.mkdir(parents=True, exist_ok=True)

app = Flask(__name__, static_folder=str(STATIC_DIR), static_url_path="/static")


def ensure_artifacts() -> None:
    """Ensure metrics/images exist, otherwise run an experiment once."""

    graph_img = STATIC_DIR / "graph_example.png"
    metrics_img = STATIC_DIR / "metrics.png"

    if not graph_img.exists() or not metrics_img.exists():
        # This will generate artifacts into web/static via evaluation.py
        run_experiment()


def load_metrics() -> list[ExperimentResult]:
    """Load metrics.csv into a list of ExperimentResult (for display in a table)."""

    csv_path = STATIC_DIR / "metrics.csv"
    results: list[ExperimentResult] = []
    if not csv_path.exists():
        return results

    with csv_path.open("r", encoding="utf-8") as f:
        # Skip header
        header = f.readline()
        for line in f:
            line = line.strip()
            if not line:
                continue
            parts = line.split(",")
            # Ancien format (5 colonnes) ou nouveau (7 colonnes)
            if len(parts) == 5:
                index_s, greedy_s, tabu_s, greedy_t, tabu_t = parts
                greedy_colors_s = tabu_colors_s = "0"
            else:
                (
                    index_s,
                    greedy_s,
                    tabu_s,
                    greedy_colors_s,
                    tabu_colors_s,
                    greedy_t,
                    tabu_t,
                ) = parts
            results.append(
                ExperimentResult(
                    index=int(index_s),
                    greedy_sum=int(greedy_s),
                    tabu_sum=int(tabu_s),
                    greedy_time=float(greedy_t),
                    tabu_time=float(tabu_t),
                    greedy_colors=int(greedy_colors_s),
                    tabu_colors=int(tabu_colors_s),
                )
            )
    return results


@app.route("/")
def index():
    """Page d'accueil simple avec un bouton pour aller vers l'expérience."""

    html = """<!doctype html>
<html lang=\"fr\">
  <head>
    <meta charset=\"utf-8\" />
    <title>Minimum Sum Coloring - Accueil</title>
    <style>
      body { font-family: system-ui, -apple-system, sans-serif; margin: 2rem; }
      h1, h2 { color: #222; }
      .btn { display: inline-block; padding: 0.5rem 1rem; background: #007bff; color: white; text-decoration: none; border-radius: 4px; }
      .btn:hover { background: #0056b3; }
    </style>
  </head>
  <body>
    <h1>Bienvenue sur le projet Minimum Sum Coloring</h1>
    <p>
      Ce petit site te permet de jouer avec un problème de coloriage de graphes.
      Tu peux générer plusieurs graphes aléatoires, lancer les algorithmes Greedy
      et Tabu Search, et voir combien de couleurs sont utilisées et quelle est la
      somme totale des couleurs.
    </p>
    <p>
      Quand tu es prêt, clique sur le bouton ci-dessous pour continuer vers la
      page d'expérience.
    </p>
    <p>
      <a href=\"/experiment\" class=\"btn\">Continuer</a>
    </p>
  </body>
</html>
"""
    return render_template_string(html)


@app.route("/experiment", methods=["GET", "POST"])
def experiment():
    """Page principale pour lancer les tests et lire les résultats."""

    # Si l'utilisateur envoie le formulaire, on relance une expérience
    if request.method == "POST":
        try:
            num_graphs = int(request.form.get("num_graphs", "20"))
            n = int(request.form.get("n", "100"))
            p = float(request.form.get("p", "0.2"))
            base_seed = int(request.form.get("base_seed", "42"))
        except ValueError:
            # En cas de mauvaise saisie, on retombe sur les valeurs par défaut
            num_graphs, n, p, base_seed = 20, 100, 0.2, 42

        run_experiment(num_graphs=num_graphs, n=n, p=p, base_seed=base_seed)

    # Make sure artifacts are present for this request.
    ensure_artifacts()
    metrics = load_metrics()
    print("[DEBUG] metrics loaded:", len(metrics))

    # Prépare les lignes HTML du tableau ici (plus simple que d'utiliser une boucle Jinja)
    table_rows = ""
    for r in metrics:
        diff = r.greedy_sum - r.tabu_sum
        table_rows += (
            f"<tr>"
            f"<td>{r.index}</td>"
            f"<td>{r.greedy_sum}</td>"
            f"<td>{r.tabu_sum}</td>"
            f"<td>{diff}</td>"
            f"<td>{r.greedy_colors or 0}</td>"
            f"<td>{r.tabu_colors or 0}</td>"
            f"<td>{r.greedy_time:.4f}</td>"
            f"<td>{r.tabu_time:.4f}</td>"
            f"</tr>"
        )

    html = """<!doctype html>
<html lang="fr">
  <head>
    <meta charset="utf-8" />
    <title>Minimum Sum Coloring - Résultats</title>
    <style>
      body { font-family: system-ui, -apple-system, sans-serif; margin: 2rem; }
      h1, h2 { color: #222; }
      .section { margin-bottom: 2rem; }
      img { max-width: 100%; height: auto; border: 1px solid #ccc; padding: 4px; background: #fafafa; }
      code { background: #f4f4f4; padding: 2px 4px; border-radius: 3px; }
    </style>
  </head>
  <body>
    <h1>Minimum Sum Coloring (MSC) - Visualisation</h1>
    <p>
      Cette page t'aide à comprendre un problème de coloriage de graphes.
      Tu peux imaginer un graphe comme un ensemble de points (sommets)
      reliés par des traits (arêtes). On doit colorier chaque point avec un numéro
      (1, 2, 3, ...) de manière à ce que deux points reliés n'aient jamais le même numéro.
      Ensuite, on additionne tous les numéros&nbsp;: plus la somme est petite, mieux c'est.
    </p>

    <div class="section">
      <h2>0. Paramètres de l'expérience</h2>
      <p>Tu peux modifier ici les paramètres de génération des graphes et relancer l'expérience.</p>
      <form method="post">
        <label>Nombre de graphes (num_graphs):
          <input type="number" name="num_graphs" value="20" min="1" max="100" />
        </label><br />
        <label>Nombre de sommets par graphe (n):
          <input type="number" name="n" value="100" min="5" max="500" />
        </label><br />
        <label>Probabilité d'arête (p):
          <input type="number" step="0.01" name="p" value="0.2" min="0" max="1" />
        </label><br />
        <label>Base seed (pour la reproductibilité):
          <input type="number" name="base_seed" value="42" />
        </label><br />
        <button type="submit">Relancer l'expérience</button>
      </form>
    </div>

    <div class="section">
      <h2>1. Exemple de graphe coloré</h2>
      <p>
        Ici tu vois un <strong>graphe</strong> :
      </p>
      <ul>
        <li>Chaque <strong>point</strong> (petit cercle) est un sommet.</li>
        <li>Chaque <strong>trait</strong> entre deux points est une arête (une connexion).</li>
        <li>Chaque point a une <strong>couleur</strong> (un numéro 1, 2, 3, ...).</li>
      </ul>
      <p>
        L'algorithme essaie de choisir ces numéros pour que&nbsp;:
      </p>
      <ul>
        <li>Deux voisins ne partagent jamais le même numéro.</li>
        <li>La somme de tous les numéros soit la plus petite possible.</li>
      </ul>
      <p>
        On ne montre qu'un sous-graphe (par exemple 40 sommets) pour que ce soit
        plus facile à regarder. Quand tu changes les paramètres en haut et que
        tu relances l'expérience, cette image est reconstruite avec le nouveau graphe.
      </p>
      <img src="/static/graph_example.png" alt="Graphe coloré" />
    </div>

    <div class="section">
      <h2>2. Comparaison des résultats Greedy vs Tabu Search</h2>
      <p>
        Ce graphique montre, pour chaque graphe, deux courbes&nbsp;:
      </p>
      <ul>
        <li><strong>Greedy</strong> : une méthode simple, rapide, qui choisit une couleur "correcte" mais pas toujours optimale.</li>
        <li><strong>Tabu Search</strong> : une méthode plus intelligente qui part de la solution Greedy et essaie de l'améliorer petit à petit.</li>
      </ul>
      <p>
        Sur l'axe horizontal (x), on a le numéro du graphe (1, 2, ...). Sur l'axe vertical (y),
        on a la <strong>somme des couleurs</strong>. Plus la courbe est <strong>basse</strong>, meilleure est la solution.
      </p>
      <img src="/static/metrics.png" alt="Graphique des résultats" />
      <p>
        En dessous, tu as un tableau qui donne les nombres exacts pour chaque graphe&nbsp;:
      </p>

      <h3>Détails numériques (par graphe)</h3>
      <p>
        Chaque ligne du tableau compare Greedy et Tabu pour un graphe.
        La colonne <strong>Diff (Greedy - Tabu)</strong> indique combien Tabu améliore la somme :
        si la valeur est positive, Tabu est meilleur ; si elle vaut 0, les deux donnent la même somme.
      </p>
      <table border="1" cellspacing="0" cellpadding="4">
        <tr>
          <th># Graphe</th>
          <th>Greedy sum</th>
          <th>Tabu sum</th>
          <th>Diff (Greedy - Tabu)</th>
          <th># couleurs Greedy</th>
          <th># couleurs Tabu</th>
          <th>Greedy time (s)</th>
          <th>Tabu time (s)</th>
        </tr>
        {{ table_rows|safe }}
      </table>
    </div>

    <div class="section">
      <h2>3. Où sont les données ?</h2>
      <p>
        Si tu veux garder une trace des résultats ou les réutiliser ailleurs, le programme les enregistre
        aussi dans des fichiers&nbsp;:
      </p>
      <ul>
        <li><code>web/static/metrics.csv</code> : tableau des résultats (une ligne par graphe).</li>
        <li><code>web/static/graph_example.png</code> : image d'un graphe coloré.</li>
        <li><code>web/static/metrics.png</code> : image du graphique Greedy vs Tabu.</li>
      </ul>
      <p>
        Tu peux ouvrir ces fichiers avec un tableur (pour le CSV) ou un lecteur d'images, mais ce n'est pas
        obligatoire pour comprendre les résultats : tout est déjà visible et expliqué sur cette page.
      </p>
    </div>
  </body>
</html>
"""
    return render_template_string(html, table_rows=table_rows)


if __name__ == "__main__":
    # Lancement du serveur de développement Flask
    app.run(debug=True)
