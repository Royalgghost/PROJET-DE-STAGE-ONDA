# Contrat de reproduction du modèle de rapport EMSI

## Référence

- Fichier de référence : `C:\Users\nouam\Downloads\template rapport de stage 4IIR (1).docx`
- Taille : 476806 octets
- SHA-256 : `E49789C4158522F0D49AA127EEC5B0A254940CA08AD2EF9B42FAE24B0BF3ADEA`
- Nature : guide de rédaction PFA 4IIR contenant des exemples, des consignes, des styles et des modèles de tableaux, et non un rapport vide prêt à remplir.
- Page count : non résolu dans l'environnement actuel. Le document contient 28 sections OOXML, 451 paragraphes, 8 tableaux et 2 images incorporées. Le rendu via `render_docx.py` a été tenté mais LibreOffice/soffice est absent ; le lancement COM Word en session isolée n'a pas abouti.
- Le fichier de référence demeure inchangé et est conservé à son chemin d'origine.

## Système de page et pagination

- Format : A4 portrait, largeur 8.271 in, hauteur 11.694 in.
- Guide explicite de l'annexe B : marges de 2.5 cm en haut, bas, gauche et droite.
- Corps du texte : Times New Roman, 12 pt, texte justifié, retrait de première ligne de 0.8 cm, interligne 1.5 ligne, espacement avant/après de 6 pt.
- La pagination commence à l'introduction générale, qui porte le numéro 1.
- Les pages liminaires peuvent être non paginées ; les annexes peuvent avoir une pagination distincte.
- En-tête recommandé : titre du chapitre courant et ligne séparatrice.
- Pied de page recommandé : numéro de page, titre du projet et ligne séparatrice. Le guide déconseille de mettre le nom de l'étudiant ou de la société dans l'en-tête/pied de page.
- Le guide autorise une page indépendante pour le titre d'un chapitre, non numérotée et sans en-tête/pied ; la page suivante ne répète pas le titre.

## Hiérarchie et composants

- Page de garde : « PROJET DE FIN D'ANNEE », année 4 en Ingénierie Informatique et Réseaux, titre, « Réalisé par », tuteurs, encadrant professionnel, encadrant pédagogique, organisme d'accueil et année universitaire.
- Front matter : Dédicace, Remerciements, Table des matières, Liste des figures, Liste des tableaux.
- Introduction générale : sujet/problématique puis annonce brève du plan ; employer « nous » et ne pas annoncer les résultats à cet endroit.
- Chapitre 1 : Présentation du cadre de projet ; introduction, organisme d'accueil, étude de l'existant, critique, solution proposée, modèle de développement, planning prévisionnel, conclusion.
- Chapitre 2 : Spécification des besoins ; introduction, besoins fonctionnels, besoins non fonctionnels, acteurs, cas d'utilisation, description des cas et diagramme global, conclusion.
- Chapitre 3 : Conception du système ; introduction, modélisation dynamique (séquences, collaboration, états, activités), modélisation statique (classes, modèle relationnel, dictionnaire), architecture logicielle et matérielle, conclusion.
- Chapitre 4 : Réalisation du système ; introduction, environnement matériel et logiciel, principales interfaces commentées, conclusion.
- Fin du rapport : conclusion générale d'environ une page sous forme de paragraphe, puis bibliographie et nétographie. Annexes facultatives.
- Chaque chapitre doit comporter une courte introduction et une courte conclusion.
- Les titres de figures sont sous les figures ; les titres de tableaux sont au-dessus des tableaux.
- Maximum recommandé pour la table des matières : trois niveaux de titres. Le guide indique généralement 50 à 60 pages de l'introduction à la conclusion pour un PFE ; ce point est une recommandation, pas une contrainte de contenu pour le PFA.

## Mapping de contenu retenu pour le rapport fusionné

- Le projet ONDA est la solution principale : analyse prédictive des risques de maintenance WAN, score par site, alertes et prévention.
- Le CyberRange est intégré dans le même fil technique comme laboratoire isolé de validation, pas comme projet commercial séparé.
- Chapitre 1 : ONDA, DSI/Réseaux WAN, fonctionnement réactif existant, limites et solution fusionnée.
- Chapitre 2 : acteurs (DSI, ingénieur réseau, responsable maintenance, opérateur télécom, analyste sécurité), besoins fonctionnels/non fonctionnels et cas d'utilisation.
- Chapitre 3 : pipeline de données, modèle prédictif, architecture applicative, architecture Host-Only, modèles de données et flux « prédire → simuler → détecter → remédier → REX ».
- Chapitre 4 : environnement, résultats chiffrés, interfaces ONDA, check-list/REX, prévention WAN, captures CyberRange, IOC, YARA/Snort et remédiation.
- La partie entrepreneuriat du rapport CyberRange est explicitement supprimée selon la demande de l'utilisateur.

## Faits et garde-fous à préserver

- Auteurs : Azzat Nouamane et Hnid Aimane.
- Encadrement entreprise : Mme Jaouhari Ouafaa, ONDA.
- Encadrement pédagogique : Mme Khadija Bousmar, EMSI.
- Titre officiel : « Conception d'un modèle d'analyse des risques et d'alertes prédictives basé sur les données de maintenance des actifs informatiques ».
- Modèle ONDA : 864 incidents, 27 sites, horizon de 30 jours, accuracy 62.39 %, precision 54.70 %, recall 88.44 %, F1 67.59 %, PR-AUC 0.705.
- Limite à dire explicitement : les données disponibles permettent un risque au niveau site ; la prédiction au niveau d'un actif individuel nécessitera un identifiant et des attributs d'équipement.
- CyberRange : Kali Linux 2024 et Metasploitable 2, réseau Host-Only sans Internet. Les captures fournies montrent 192.168.243.129 et 192.168.243.128 ; ces valeurs doivent être privilégiées aux adresses illustratives présentes dans certains passages du rapport source.
- Les scénarios CVE, les charges utiles et les signatures sont rapportés comme essais autorisés en laboratoire ; aucune commande offensive ne doit être présentée comme procédure utilisable sur un réseau réel.

## Inventaire des éléments de package à préserver

Le modèle original contient les styles, numbering, thème, settings, headers/footers, notes, custom XML, relations, dessins et médias ci-dessous. La référence n'est pas modifiée ; le nouveau rapport pourra réutiliser le système de styles et les médias institutionnels utiles, sans conserver les textes de consigne.

| Partie | Taille | SHA-256 |
|---|---:|---|
| `[Content_Types].xml` | 3488 | `e10b7a3057e18eea42439baa4180e361c16c17aa37e213e22a830371886ac47f` |
| `word/document.xml` | 667871 | `1967319e25c68797747f22787fe048dc0abfefda5d13c68506b1c2945cff6af8` |
| `word/styles.xml` | 42610 | `77270deb73c6b9898e660b9e9601e98a0e5f3dd06c7253d97c5a61fafc56d486` |
| `word/numbering.xml` | 77289 | `5817990ec74b013cc888ba03aade705cf47ab2587981b9a1ed0146a9558aae07` |
| `word/theme/theme1.xml` | 6800 | `e318f0fcefc3e19fc659f2b924e403c3f0daed9ec88f4d7ad5a0507e3780e9` |
| `word/header1.xml` | 2945 | `f836a4e385be69ca9aface1ad40dd8d92a11e5b2a084a3ad90844a4f2b048230` |
| `word/footer1.xml` | 22035 | `42f6d2c005b145b7e9d2788eda4c31043dde82aa4a96967ebe0fb315536416ab` |
| `word/footer3.xml` | 22063 | `aef5d753353b1e0f19441313a10386e65a83e6d8356188a43d9fd64a0a4cccf9` |
| `word/footer5.xml` | 21700 | `7470c388e08d6addcfc01da3aa85140410b1fb804b005a56cb9920501a07a9ca` |
| `word/footer7.xml` | 22069 | `9060f1e14c52621d2b30421182ac3eea1cdddef1d5ce5f998a329db468378669` |
| `word/media/image1.png` | 125210 | `267f9b64e6bdcafee6997500a2968c045ae2e471fbd489b2ea214c772c7d5b76` |
| `word/media/image5.jpeg` | 58642 | `c0f4e5ab53879d4ea151d3bea6496885e9aada6de36591b4c2063bed86929fc3` |

Other package parts are unchanged preservation candidates: root relationships, document relationships, footer2/4/6, footnotes, endnotes, media image2/3/4/10, font table, web settings, core/app/custom properties and all four customXml parts and relationships.

## Fidelity gates

- Use the four-chapter school structure rather than a custom multi-chapter structure.
- Keep Times New Roman 12 pt, justified paragraphs, 1.5 spacing, first-line indentation and 2.5 cm margins.
- Use real heading styles and automatic table of contents/list-of-figures/list-of-tables fields where possible.
- Keep figure captions below figures and table captions above tables.
- Avoid color except where the subject itself requires it, especially screenshots and technical interfaces.
- Include diagrams for actors/use cases, data/model architecture, deployment/Host-Only topology and the integrated operational flow.
- Verify the resulting DOCX with structural audits and visual rendering when a renderer is available. If only Word is available locally, the DOCX remains editable and the PDF must be visually checked separately.
