# Flashcards QCM Droit

Version web statique de l'application de révision. Elle fonctionne sans serveur Python et peut être publiée directement avec GitHub Pages.

## Fonctions ajoutées

Le site inclut maintenant 50 améliorations d'entraînement :

1. Filtrage par chapitre.
2. Sélection multi-chapitres.
3. Bouton pour sélectionner tous les chapitres.
4. Bouton pour désélectionner tous les chapitres.
5. Groupe "Sans chapitre fiable".
6. Filtrage par source.
7. Recherche dans les questions.
8. Recherche dans les options.
9. Recherche dans les rappels de cours.
10. Filtrage par cartes jamais tentées.
11. Filtrage par erreurs.
12. Filtrage par cartes à revoir.
13. Filtrage par cartes acquises.
14. Filtrage par favoris.
15. Filtrage par cartes sans rappel fiable.
16. Filtrage par difficulté.
17. Limite de session à 10 questions.
18. Limite de session à 20 questions.
19. Limite de session à 30 questions.
20. Limite de session à 50 questions.
21. Mode QCM avec réponses cochables.
22. Gestion des réponses multiples.
23. Validation explicite des réponses.
24. Correction immédiate optionnelle.
25. Mise en évidence des bonnes réponses.
26. Mise en évidence des mauvaises réponses choisies.
27. Score de session.
28. Pourcentage de réussite de session.
29. Score global.
30. Nombre total de tentatives.
31. Compteur d'erreurs.
32. Série actuelle de bonnes réponses.
33. Meilleure série.
34. Marquage automatique "acquise" en cas de bonne réponse.
35. Marquage automatique "à revoir" en cas d'erreur.
36. Bouton manuel "Acquise".
37. Bouton manuel "A revoir".
38. Favoris.
39. Tableau de bord.
40. Progression par chapitre.
41. Compteur de temps de session.
42. Nouvelle session avec remise à zéro du score de session.
43. Mélange des questions.
44. Mélange optionnel des options.
45. Retour à l'ordre normal.
46. Liste cliquable des questions filtrées.
47. Export de progression.
48. Import de progression.
49. Mode sombre.
50. Mode compact.

Optimisation mobile :

- Les filtres sont regroupés dans un tiroir replié par défaut sur téléphone.
- Les boutons `Précédente`, `Valider` et `Suivante` restent collés en bas de l'écran.
- Les options ont de grandes zones tactiles pour répondre vite.
- Le haut de question revient automatiquement quand on change de carte.
- La progression reste visible sans afficher toutes les statistiques par chapitre.

## Audit des corrections

Un audit complet des cartes peut être régénéré avec :

```bash
python audit_questions.py
```

Le rapport est écrit dans `audit_questions.csv`. Il indique pour chaque carte le nombre de réponses attendues, le type de contrôle affiché par le site, la source de cours utilisée et les éventuelles anomalies à vérifier.

## Lancer en local

Ouvrir `index.html` dans un navigateur.

## Déployer sur GitHub Pages

1. Créer un dépôt GitHub.
2. Ajouter ces fichiers à la racine du dépôt :
   - `index.html`
   - `styles.css`
   - `app.js`
   - `flashcards-data.js`
   - `.nojekyll`
3. Aller dans `Settings` > `Pages`.
4. Choisir `Deploy from a branch`, puis la branche `main` et le dossier `/root`.
5. Valider avec `Save`.

La progression est sauvegardée dans le navigateur avec `localStorage`.

## Mettre à jour les questions

Après modification de `pdf.py` ou des réponses dans `flashcards_droit.py`, lancer :

```bash
python export_flashcards_data.py
```

Cela régénère `flashcards-data.js`.

L'export supprime automatiquement les doublons stricts : même énoncé, mêmes options et mêmes réponses.
Il ajoute aussi une justification rédigée pour chaque carte. Elle est cachée par défaut sous le bouton `Voir la justification`, détaille les options correctes et les options écartées, et la source PDF est conservée quand le rapprochement avec le cours est fiable.

Si Python indique que `pypdf` ou `cryptography` manque, installer les dépendances avec :

```bash
python -m pip install pypdf cryptography
```
