# Instructions d'exécution – Projet MSC (Minimum Sum Coloring)

Ce fichier explique comment installer les dépendances, exécuter l'expérience, et lancer l'interface web qui affiche les graphes colorés et les résultats.

---

## 1. Installer les dépendances Python

Depuis la racine du projet (`msc-minimum-sum-coloring`), installe les bibliothèques nécessaires :

```bash
python -m pip install -r requirements.txt
```

Cela installe :
- **flask** : serveur web léger pour l'interface de visualisation
- **matplotlib** : génération de graphiques et images
- **networkx** : manipulation et visualisation de graphes

---

## 2. Exécuter l'expérience (génération des résultats)

Lance la commande suivante pour :
- Générer 20 graphes aléatoires G(100, 0.2)
- Calculer une solution MSC avec l'heuristique gloutonne
- Améliorer chaque solution avec la recherche tabou
- Sauvegarder les métriques et images dans `web/static/`

**Commande :**

```bash
python -m src.main
```

**Résultat :** tu verras dans le terminal les résultats pour chaque graphe (somme des couleurs, temps de calcul), et à la fin un résumé des moyennes.

**Fichiers générés :**
- `web/static/metrics.csv` : une ligne par graphe avec les valeurs (index, greedy_sum, tabu_sum, greedy_colors, tabu_colors, greedy_time, tabu_time).
- `web/static/graph_example.png` : une image du premier graphe coloré par Tabu Search.
- `web/static/metrics.png` : un graphique comparant Greedy et Tabu Search pour tous les graphes.

---

## 3. Lancer le site web de visualisation

Une fois l'expérience exécutée (ou même si tu ne l'as pas encore exécutée — le site peut la lancer automatiquement au premier démarrage), démarre le serveur Flask :

**Commande :**

```bash
python web/app.py
```

**Ce qui se passe :**
- Flask démarre un serveur de développement local (généralement sur `http://127.0.0.1:5000`).
- Si `web/static/graph_example.png` et `web/static/metrics.png` n'existent pas, le site exécute automatiquement une expérience au premier accès.

**Pour voir le site :**

Ouvre ton navigateur et va sur :

```
http://127.0.0.1:5000
```

Tu verras :
1. **Exemple de graphe coloré** : un graphe aléatoire coloré par Tabu Search.
2. **Graphique de comparaison** : les résultats (somme des couleurs) pour chaque graphe, Greedy vs Tabu Search.
3. **Explication des fichiers** : où trouver les CSV et images générés.

---

## 4. Où sont les données ?

Toutes les données produites par l'expérience se trouvent dans :

```
web/static/
  ├─ metrics.csv           (tableau des résultats)
  ├─ graph_example.png     (graphe coloré)
  └─ metrics.png           (graphique comparatif)
```

Tu peux ouvrir ces fichiers directement depuis l'explorateur de fichiers :
- `metrics.csv` : ouvre-le dans Excel, LibreOffice, ou un éditeur de texte.
- `graph_example.png` et `metrics.png` : ouvre-les avec n'importe quel lecteur d'images.

---

## 5. Résumé des commandes

| Étape | Commande | Description |
|-------|----------|-------------|
| 1. Installer dépendances | `python -m pip install -r requirements.txt` | Installe flask, matplotlib, networkx |
| 2. Exécuter expérience | `python -m src.main` | Génère les graphes, calcule MSC avec Greedy + Tabu, enregistre les résultats |
| 3. Lancer le site web | `python web/app.py` | Démarre le serveur Flask sur http://127.0.0.1:5000 |

---

## 6. En cas de problème

- **Erreur "No module named 'flask'" (ou matplotlib, networkx)** : relance `python -m pip install -r requirements.txt`.
- **Erreur "port already in use" lors du lancement de Flask** : un autre processus utilise le port 5000. Ferme-le ou change le port dans `web/app.py` (dans `app.run(debug=True, port=5001)` par exemple).
- **Images non affichées sur le site** : assure-toi d'avoir exécuté `python -m src.main` au moins une fois pour générer `web/static/graph_example.png` et `web/static/metrics.png`.

---

Bon usage et bonnes visualisations !
