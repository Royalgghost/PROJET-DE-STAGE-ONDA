# Rapport ONDA Risk Intelligence + CyberRange

Ce dossier contient la source LaTeX du rapport fusionné :

> Conception d'un modèle d'analyse des risques et d'alertes prédictives basé sur les données de maintenance des actifs informatiques

Le fichier `main.tex` référence uniquement des chemins relatifs. Les captures ONDA, les figures CyberRange et les diagrammes de conception sont donc inclus dans le dossier `images/` et resteront attachés au rapport lors d'une compilation locale ou d'un dépôt sur Overleaf.

## Compilation locale

Installer une distribution LaTeX, par exemple MiKTeX sous Windows ou TeX Live sous Linux/macOS, puis exécuter depuis ce dossier :

```text
pdflatex -interaction=nonstopmode main.tex
pdflatex -interaction=nonstopmode main.tex
```

La deuxième compilation met à jour la table des matières ainsi que les listes des figures et des tableaux. Avec `latexmk`, une seule commande suffit :

```text
latexmk -pdf -interaction=nonstopmode main.tex
```

## Import dans Overleaf

1. Créer un nouveau projet Overleaf.
2. Choisir `Upload Project` et importer l'archive ZIP complète.
3. Définir `main.tex` comme fichier principal si Overleaf ne le détecte pas automatiquement.
4. Compiler avec pdfLaTeX.

Le rapport conserve ses 4 chapitres numérotés, ses 35 sections et ses 28 figures numérotées individuellement, ainsi que les listes générées automatiquement par `\listoffigures` et `\listoftables`. Le contenu et l'organisation du rapport de référence sont conservés ; seule la mise en forme est portée en LaTeX.

## Structure

```text
main.tex
README.md
images/
  diagrams/       # schémas d'architecture et de conception
  onda/           # logo et captures de la plateforme ONDA
  cyberrange/     # logo EMSI et preuves de simulation CyberRange
```

Le CyberRange est décrit comme un laboratoire pédagogique isolé et ne doit pas être exécuté contre une infrastructure de production.
