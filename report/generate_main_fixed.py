from __future__ import annotations

import ast
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parent
BUILDER = ROOT / "build_report_docx.py"
OUTPUT = ROOT / "main_fixed.tex"


def value(node: ast.AST):
    return ast.literal_eval(node)


def call_name(node: ast.Call) -> str:
    if isinstance(node.func, ast.Name):
        return node.func.id
    return ""


def path_value(node: ast.AST) -> str:
    if isinstance(node, ast.BinOp) and isinstance(node.op, ast.Div):
        if isinstance(node.left, ast.Name) and isinstance(node.right, ast.Constant):
            base = {"DIAG": "diagrams", "ONDA": "onda", "CR": "cyberrange"}[node.left.id]
            return f"images/{base}/{node.right.value}"
    raise ValueError(f"Unsupported figure path: {ast.dump(node)}")


def latex_text(text: str) -> str:
    replacements = {
        "&": r"\&",
        "%": r"\%",
        "$": r"\$",
        "#": r"\#",
        "_": r"\_",
        "{": r"\{",
        "}": r"\}",
    }
    return "".join(replacements.get(char, char) for char in text)


def heading_latex(text: str, level: int) -> str:
    if text == "Introduction générale":
        return r"\frontchapter{Introduction générale}"
    match = re.match(r"Chapitre \d+ : (.*)", text)
    if level == 1 and match:
        return f"\\chapter{{{latex_text(match.group(1))}}}"
    if level == 1:
        return f"\\chapter{{{latex_text(text)}}}"
    if level == 2:
        clean_text = re.sub(r"^\d+(?:\.\d+)+\s+", "", text)
        return f"\\section{{{latex_text(clean_text)}}}"
    clean_text = re.sub(r"^\d+(?:\.\d+)+\s+", "", text)
    return f"\\subsection{{{latex_text(clean_text)}}}"


def table_latex(headers: list[str], rows: list[list[str]], caption: str) -> str:
    columns = len(headers)
    caption = re.sub(r"^Tableau\s+\d+\.\s*", "", caption)
    widths = [4.0, 5.0, 5.0, 4.0][: max(columns - 1, 1)]
    spec = "B{%.1fcm}" % widths[0]
    for width in widths[1:columns - 1]:
        spec += " P{%.1fcm}" % width
    spec += " X" if columns > 1 else ""
    lines = [
        r"\begin{table}[H]",
        r"\centering",
        r"\small",
        f"\\caption{{{latex_text(caption)}}}",
        f"\\begin{{tabularx}}{{\\textwidth}}{{{spec}}}",
        r"\toprule",
        " & ".join(latex_text(x) for x in headers) + r"\\",
        r"\midrule",
    ]
    for row in rows:
        lines.append(" & ".join(latex_text(str(x)) for x in row) + r"\\")
    lines += [r"\bottomrule", r"\end{tabularx}", r"\end{table}"]
    return "\n".join(lines)


def figure_latex(path: str, caption: str, width: float) -> str:
    caption = re.sub(r"^Figure\s+\d+\.\s*", "", caption)
    short_caption = caption.split(":", 1)[0].strip()
    width_ratio = min(max(width / 15.8, 0.70), 0.97)
    return (
        r"\begin{figure}[H]" + "\n" +
        r"\centering" + "\n" +
        f"\\includegraphics[width={width_ratio:.2f}\\textwidth,keepaspectratio]{{{path}}}\n" +
        f"\\caption[{latex_text(short_caption)}]{{{latex_text(caption)}}}\n" +
        r"\end{figure}"
    )


def translate_nodes(nodes: list[ast.stmt]) -> list[str]:
    output: list[str] = []
    for node in nodes:
        if not isinstance(node, ast.Expr) or not isinstance(node.value, ast.Call):
            continue
        call = node.value
        name = call_name(call)
        if name == "add_heading":
            text = value(call.args[1])
            level = value(call.args[2])
            page_break = False
            for keyword in call.keywords:
                if keyword.arg == "page_break":
                    page_break = bool(value(keyword.value))
            heading = heading_latex(text, level)
            output.append((r"\clearpage" + "\n" if page_break else "") + heading)
        elif name == "add_text":
            output.append(latex_text(value(call.args[1])))
        elif name == "add_bullets":
            items = value(call.args[1])
            output.append("\\begin{itemize}\n" + "\n".join(
                f"  \\item {latex_text(item)}" for item in items
            ) + "\n\\end{itemize}")
        elif name == "add_table":
            headers = value(call.args[1])
            rows = value(call.args[2])
            caption = "Tableau"
            for keyword in call.keywords:
                if keyword.arg == "caption":
                    caption = value(keyword.value)
            output.append(table_latex(headers, rows, caption))
        elif name == "add_figure":
            path = path_value(call.args[1])
            caption = value(call.args[2])
            width = 15.0
            for keyword in call.keywords:
                if keyword.arg == "width":
                    width = value(keyword.value)
            output.append(figure_latex(path, caption, width))
    return output


def find_build_function(tree: ast.Module) -> ast.FunctionDef:
    for node in tree.body:
        if isinstance(node, ast.FunctionDef) and node.name == "build":
            return node
    raise RuntimeError("build() function not found")


def heading_text(node: ast.stmt) -> str | None:
    if not isinstance(node, ast.Expr) or not isinstance(node.value, ast.Call):
        return None
    if call_name(node.value) != "add_heading" or len(node.value.args) < 2:
        return None
    if isinstance(node.value.args[1], ast.Constant):
        return node.value.args[1].value
    return None


def build_source() -> str:
    tree = ast.parse(BUILDER.read_text(encoding="utf-8"))
    function = find_build_function(tree)
    headings = [heading_text(node) for node in function.body]
    start = headings.index("Introduction générale")
    end = headings.index("Conclusion générale")
    body = translate_nodes(function.body[start:end])

    front = r"""\documentclass[12pt,a4paper,oneside]{report}

\usepackage[T1]{fontenc}
\usepackage[utf8]{inputenc}
\usepackage[french]{babel}
\usepackage{lmodern}
\usepackage{geometry}
\geometry{a4paper,top=2.5cm,bottom=2.5cm,left=2.5cm,right=2.5cm,headheight=15pt}
\usepackage{graphicx}
\usepackage{booktabs}
\usepackage{tabularx}
\usepackage{array}
\usepackage{chngcntr}
\usepackage{enumitem}
\usepackage{xcolor}
\usepackage{fancyhdr}
\usepackage{caption}
\usepackage{float}
\usepackage{hyperref}
\usepackage{microtype}
\usepackage{tikz}
\usepackage{eso-pic}

\definecolor{ondaBlue}{HTML}{1F4E79}
\definecolor{ondaCyan}{HTML}{0EA5E9}
\definecolor{lightBlue}{HTML}{EFF6FF}
\hypersetup{colorlinks=true,linkcolor=ondaBlue,urlcolor=ondaCyan,citecolor=ondaBlue}
\setlist{itemsep=3pt,topsep=5pt}
\setlength{\parindent}{0.7cm}
\setlength{\parskip}{4pt}
\setlength{\emergencystretch}{3em}
\renewcommand{\arraystretch}{1.20}
\newcolumntype{P}[1]{>{\raggedright\arraybackslash}p{#1}}
\newcolumntype{B}[1]{>{\bfseries\raggedright\arraybackslash}p{#1}}

\pagestyle{fancy}
\fancyhf{}
\lfoot{\footnotesize\textcolor{ondaBlue}{ONDA -- Risk Intelligence et CyberRange}}
\cfoot{\footnotesize\textcolor{gray}{Page \thepage}}
\rfoot{\footnotesize\textcolor{gray}{EMSI -- 4IIR}}
\renewcommand{\headrulewidth}{0pt}
\renewcommand{\footrulewidth}{0pt}
\captionsetup{font=small,labelfont=bf,justification=centering}

% Fine decorative page border, applied to every page of the report.
\newcommand{\ReportPageBorder}{%
  \begin{tikzpicture}[remember picture,overlay]
    \draw[ondaBlue!55,line width=0.45pt]
      ([xshift=1.05cm,yshift=-1.05cm]current page.north west)
      rectangle
      ([xshift=-1.05cm,yshift=1.05cm]current page.south east);
    \draw[ondaBlue!25,line width=0.25pt]
      ([xshift=1.18cm,yshift=-1.18cm]current page.north west)
      rectangle
      ([xshift=-1.18cm,yshift=1.18cm]current page.south east);
    % Small corner flourishes inspired by the Word page-border style.
    \draw[ondaBlue!55,line width=0.35pt]
      ([xshift=1.05cm,yshift=-1.05cm]current page.north west) -- ++(0.32cm,0);
    \draw[ondaBlue!55,line width=0.35pt]
      ([xshift=1.05cm,yshift=-1.05cm]current page.north west) -- ++(0,-0.32cm);
    \draw[ondaBlue!55,line width=0.35pt]
      ([xshift=-1.05cm,yshift=-1.05cm]current page.north east) -- ++(-0.32cm,0);
    \draw[ondaBlue!55,line width=0.35pt]
      ([xshift=-1.05cm,yshift=-1.05cm]current page.north east) -- ++(0,-0.32cm);
    \draw[ondaBlue!55,line width=0.35pt]
      ([xshift=1.05cm,yshift=1.05cm]current page.south west) -- ++(0.32cm,0);
    \draw[ondaBlue!55,line width=0.35pt]
      ([xshift=1.05cm,yshift=1.05cm]current page.south west) -- ++(0,0.32cm);
    \draw[ondaBlue!55,line width=0.35pt]
      ([xshift=-1.05cm,yshift=1.05cm]current page.south east) -- ++(-0.32cm,0);
    \draw[ondaBlue!55,line width=0.35pt]
      ([xshift=-1.05cm,yshift=1.05cm]current page.south east) -- ++(0,0.32cm);
  \end{tikzpicture}%
}
\AddToShipoutPictureBG{\ReportPageBorder}

\newcommand{\frontchapter}[1]{%
  \chapter*{#1}%
  \addcontentsline{toc}{chapter}{#1}%
}

\begin{document}

\begin{titlepage}
\thispagestyle{empty}
\centering
\vspace*{0.4cm}
\includegraphics[width=3.0cm]{images/onda/onda_logo.png}

\vspace{0.35cm}
{\Large\bfseries\color{ondaBlue} OFFICE NATIONAL DES AÉROPORTS}\par
\vspace{1.2cm}
{\Large\bfseries\color{ondaBlue} PROJET DE FIN D'ANNEE}\par
\vspace{0.35cm}
{\large\bfseries 4ème Année en Ingénierie Informatique et Réseaux}\par
\vspace{1.3cm}
{\Large\bfseries\color{ondaBlue}
Conception d'un modèle d'analyse des risques et d'alertes prédictives\\
basé sur les données de maintenance des actifs informatiques}\par
\vspace{0.45cm}
{\large\itshape Rapport de projet -- version technique intégrée}\par
\vspace{1.0cm}
\begin{tabular}{p{0.42\textwidth} p{0.47\textwidth}}
\textbf{Réalisé par} & \textbf{Encadrement}\\[0.15cm]
Azzat Nouamane\\ Hnid Aimane &
Encadrement professionnel : Mme Jaouhari Ouafaa -- ONDA\\
Encadrement pédagogique : Mme Khadija Bousmar -- EMSI
\end{tabular}

\vfill
\textbf{Organisme d'accueil : Office National des Aéroports (ONDA)}\\[0.3cm]
Année universitaire : 2025--2026
\end{titlepage}

\pagenumbering{roman}

\frontchapter{Dédicace}
\begin{center}
Nous dédions ce travail à nos familles, pour leur soutien constant, leur patience et la confiance qu’elles nous accordent tout au long de notre formation. Leur encouragement nous a accompagnés pendant les phases de recherche, de développement, de tests et de rédaction, parfois lorsque les difficultés techniques exigeaient davantage de temps et de persévérance.

Nous dédions également ce projet à toutes les personnes qui nous ont transmis le goût de l’apprentissage et de l’innovation dans les domaines des réseaux, de la cybersécurité et de l’intelligence artificielle. À travers ce rapport, nous souhaitons valoriser le travail collectif, la responsabilité professionnelle et la volonté de construire des solutions utiles aux organisations qui dépendent de leurs systèmes d’information.
\end{center}

\frontchapter{Remerciements}
Nous remercions vivement Mme Jaouhari Ouafaa, notre encadrante au sein de l’ONDA, pour son accompagnement professionnel, sa disponibilité et les orientations qui nous ont permis de mieux comprendre les contraintes d’un réseau aéroportuaire. Ses remarques nous ont aidés à rapprocher les fonctionnalités développées des besoins concrets d’une équipe chargée de la continuité de service.

Nous remercions également Mme Khadija Bousmar, notre encadrante pédagogique à l’EMSI, pour ses conseils méthodologiques, son suivi régulier et son attention portée à la qualité de la présentation. Nous lui sommes reconnaissants de nous avoir encouragés à structurer le travail selon une démarche claire, à justifier nos choix techniques et à exposer les limites de la solution avec honnêteté.

Enfin, nous remercions les équipes de l’ONDA, nos enseignants et toutes les personnes qui ont contribué, directement ou indirectement, à rendre cette expérience formatrice. Les échanges, les lectures, les essais et les corrections successives ont enrichi notre compréhension de la maintenance informatique et de la cybersécurité. Ce projet est le résultat d’un effort de collaboration et de transmission.

\frontchapter{Résumé}
Ce projet porte sur la conception d’un modèle d’analyse des risques et d’alertes prédictives basé sur les données de maintenance des actifs informatiques de l’Office National des Aéroports. La solution exploite l’historique des incidents WAN de 27 sites pour estimer un score de risque sur un horizon de 30 jours, hiérarchiser les alertes et proposer des actions de prévention. L’objectif n’est pas de remplacer l’expertise des équipes, mais de leur fournir une information préparée, comparable et exploitable au moment de décider d’une intervention.

La plateforme associe un portail exécutif, un module de diagnostic du modèle, une gestion du facteur humain et un plan d’intervention préventive. Elle permet de passer d’une lecture dispersée des tickets à une vision structurée : les incidents sont agrégés, les tendances sont rendues visibles, les sites sont classés et les recommandations sont rattachées à des causes ou à des situations observées. Les résultats peuvent ainsi être discutés avec les responsables réseau et adaptés aux contraintes opérationnelles.

Un CyberRange isolé complète la validation en reproduisant un scénario d’incident de sécurité autorisé, depuis l’observation jusqu’à la détection et la remédiation. Cet environnement ne représente pas le réseau de production ; il sert à vérifier la capacité à collecter des preuves, à écrire des contrôles défensifs et à transformer les enseignements techniques en retour d’expérience. Cette intégration relie la continuité de service, la gouvernance de la maintenance et la préparation à la réponse aux incidents.

\textbf{Mots-clés :} analyse de risques, maintenance informatique, réseau WAN, apprentissage automatique, alertes prédictives, CyberRange, détection, REX.

\frontchapter{Abstract}
This project addresses the design of a risk analysis and predictive alerting model based on IT asset maintenance data for Morocco’s National Airports Authority. The solution uses the incident history of 27 WAN sites to estimate a 30-day risk score, prioritize alerts and recommend preventive actions. It is designed as a decision-support system: the prediction highlights where attention should be focused, while operational teams retain responsibility for confirming the context and selecting the appropriate intervention.

The platform combines an executive portal, model diagnostics, human-factor controls and a preventive intervention plan. It organizes incident records into comparable indicators, makes the main risk drivers visible and links the result to concrete maintenance actions. An isolated CyberRange complements the validation by reproducing an authorized security-incident scenario, from observation to detection and remediation. The integrated approach connects service continuity, maintenance governance and incident-response readiness while keeping the production network outside the simulation perimeter.

\textbf{Keywords:} risk analysis, IT maintenance, WAN, machine learning, predictive alerts, CyberRange, detection, lessons learned.

\tableofcontents
\clearpage
\renewcommand{\listfigurename}{Table des figures}
\listoffigures
\clearpage
\listoftables

\clearpage
\pagenumbering{arabic}
\setcounter{page}{1}

"""

    closing = r"""
\frontchapter{Conclusion générale}
Ce projet a permis de concevoir une approche intégrée de l’analyse des risques et des alertes prédictives à partir des données de maintenance des actifs informatiques de l’ONDA. En exploitant les historiques de 27 sites WAN, la plateforme calcule un score à 30 jours, classe les priorités et propose des actions de prévention compréhensibles par les équipes. Le portail exécutif facilite la décision, le module de risque rend les indicateurs et les performances du modèle visibles, le module facteur humain réduit les oublis avant intervention et le REX organise la capitalisation. Chaque composant répond ainsi à une étape du même problème : éviter qu’un signal connu ne soit ignoré jusqu’à devenir une interruption coûteuse.

La simulation menée dans un CyberRange Host-Only complète cette vision en donnant un cadre contrôlé pour observer des traces, tester des détections et formaliser des mesures de remédiation. Elle rappelle que la disponibilité d’un service ne dépend pas uniquement d’un équipement ou d’un opérateur ; elle dépend aussi de la capacité à surveiller, à réagir et à apprendre. Les preuves techniques obtenues dans le laboratoire peuvent donc servir de support pédagogique pour discuter la segmentation, le filtrage, la supervision et la documentation des incidents.

Les résultats doivent toutefois être interprétés avec prudence. Le modèle décrit principalement un risque au niveau site, dépend de la qualité des tickets et reste une aide à la décision. La performance mesurée doit être suivie dans le temps, les faux positifs doivent être analysés et toute alerte doit être confrontée au contexte opérationnel. De la même manière, les règles de détection issues du CyberRange ne peuvent pas être appliquées directement à la production sans validation, adaptation et accord des responsables compétents.

Les perspectives sont l’enrichissement du référentiel d’actifs, l’ajout de données de topologie et de supervision temps réel, le suivi du drift du modèle, l’intégration d’une authentification et d’un journal d’audit, ainsi que la validation progressive des règles de détection dans un environnement conforme aux procédures de sécurité de l’ONDA. À terme, cette évolution pourrait fournir un historique complet reliant l’état d’un site, son risque estimé, les interventions réalisées, les preuves observées et l’efficacité des mesures prises.

\clearpage
\frontchapter{Bibliographie et Nétographie}
\begin{enumerate}[label={[\arabic*]},leftmargin=1.0cm]
\item Documentation Python, Python Software Foundation, \url{https://docs.python.org/3/}.
\item Scikit-learn, \emph{User Guide -- Logistic Regression and model evaluation}, \url{https://scikit-learn.org/stable/user_guide.html}.
\item Pandas Documentation, User Guide, \url{https://pandas.pydata.org/docs/}.
\item VirtualBox User Manual, Oracle, \url{https://www.virtualbox.org/manual/}.
\item Wireshark Documentation, User's Guide, \url{https://www.wireshark.org/docs/}.
\item Ghidra Documentation, National Security Agency, \url{https://ghidra-sre.org/}.
\item YARA Documentation, \url{https://yara.readthedocs.io/}.
\item Snort Documentation, Cisco Talos, \url{https://www.snort.org/documents}.
\item MITRE ATT\&CK, Enterprise Matrix, \url{https://attack.mitre.org/}.
\item OWASP, Secure Coding Practices and Application Security Verification resources, \url{https://owasp.org/}.
\item Documentation interne du projet ONDA : historiques d’incidents, écrans de la plateforme et résultats d’évaluation, 2024.
\item Rapport technique CyberRange du binôme, éléments de laboratoire et captures intégrées au présent rapport.
\end{enumerate}

\clearpage
\frontchapter{Annexes}
\section*{Annexe A -- Principaux indicateurs du projet}
\begin{table}[H]
\centering
\small
\caption{Récapitulatif des indicateurs.}
\begin{tabularx}{\textwidth}{B{8.5cm} X}
\toprule
Indicateur & Valeur\\
\midrule
Incidents historiques analysés & 864\\
Sites aéroportuaires & 27\\
Horizon de prédiction & 30 jours\\
Accuracy & 62,39\%\\
Précision & 54,70\%\\
Rappel & 88,44\%\\
F1-score & 67,59\%\\
PR-AUC & 0,705\\
\bottomrule
\end{tabularx}
\end{table}

\section*{Annexe B -- Périmètre de la simulation}
La simulation est limitée à un réseau Host-Only contrôlé, à des machines prévues pour la formation et à des objectifs de détection/remédiation. Elle ne fournit aucune autorisation d’essai sur le réseau ONDA ou sur un tiers. Toute reprise opérationnelle doit faire l’objet d’une validation formelle, d’un périmètre défini et d’une supervision compétente.

\end{document}
"""

    return front + "\n\n".join(body) + "\n\n" + closing


if __name__ == "__main__":
    OUTPUT.write_text(build_source(), encoding="utf-8")
    print(OUTPUT)
