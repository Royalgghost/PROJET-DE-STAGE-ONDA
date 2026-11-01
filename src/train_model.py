
from __future__ import annotations

import json
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    accuracy_score,
    average_precision_score,
    classification_report,
    confusion_matrix,
    f1_score,
    precision_score,
    recall_score,
    roc_auc_score,
)
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

from data_pipeline import (
    build_latest_feature_snapshot,
    create_site_week_dataset,
    load_and_clean_incidents,
)


NUMERIC_FEATURES = [
    "month",
    "quarter",
    "incidents_7d",
    "incidents_30d",
    "incidents_90d",
    "incidents_180d",
    "downtime_30d_h",
    "downtime_90d_h",
    "mean_duration_90d_h",
    "max_duration_90d_h",
    "days_since_last_incident",
    "iam_incidents_90d",
    "orange_incidents_90d",
    "electric_incidents_90d",
    "total_incidents_before",
    "historical_mean_duration_h",
]
CATEGORICAL_FEATURES = ["site"]
FEATURES = NUMERIC_FEATURES + CATEGORICAL_FEATURES
TARGET = "target_incident_next_30d"


def risk_level(probability: float) -> str:
    if probability >= 0.70:
        return "ÉLEVÉ"
    if probability >= 0.40:
        return "MOYEN"
    return "FAIBLE"


def risk_reasons(row: pd.Series) -> str:
    reasons: list[str] = []
    if row["incidents_30d"] >= 3:
        reasons.append(f"{int(row['incidents_30d'])} incidents sur 30 jours")
    elif row["incidents_90d"] >= 3:
        reasons.append(f"{int(row['incidents_90d'])} incidents sur 90 jours")

    if row["downtime_90d_h"] >= 24:
        reasons.append(f"{row['downtime_90d_h']:.1f} h d'indisponibilité sur 90 jours")
    if row["days_since_last_incident"] <= 14:
        reasons.append(
            f"dernier incident il y a {int(row['days_since_last_incident'])} jours"
        )
    if row["electric_incidents_90d"] >= 2:
        reasons.append(
            f"{int(row['electric_incidents_90d'])} incidents électriques récents"
        )
    if row["iam_incidents_90d"] >= 2:
        reasons.append(f"{int(row['iam_incidents_90d'])} incidents IAM récents")
    if row["orange_incidents_90d"] >= 2:
        reasons.append(f"{int(row['orange_incidents_90d'])} incidents Orange récents")

    if not reasons:
        if row["total_incidents_before"] >= 20:
            reasons.append(
                f"fréquence historique élevée : {int(row['total_incidents_before'])} incidents connus"
            )
        elif row["historical_mean_duration_h"] >= 12:
            reasons.append(
                f"durée historique moyenne élevée : {row['historical_mean_duration_h']:.1f} h"
            )
        else:
            reasons.append("profil historique du site pris en compte par le modèle")
    return " ; ".join(reasons[:3])


def train(
    excel_path: str | Path,
    artifacts_dir: str | Path,
    test_start: str = "2024-01-01",
) -> dict[str, object]:
    artifacts_dir = Path(artifacts_dir)
    artifacts_dir.mkdir(parents=True, exist_ok=True)

    incidents = load_and_clean_incidents(excel_path)
    weekly = create_site_week_dataset(incidents, horizon_days=30)

    labelled = weekly.dropna(subset=[TARGET]).copy()
    labelled[TARGET] = labelled[TARGET].astype(int)

    test_start_date = pd.Timestamp(test_start)
    train_df = labelled[labelled["reference_date"] < test_start_date].copy()
    test_df = labelled[labelled["reference_date"] >= test_start_date].copy()

    if train_df.empty or test_df.empty:
        raise ValueError("Le découpage temporel a produit un jeu vide.")

    preprocessor = ColumnTransformer(
        transformers=[
            (
                "num",
                Pipeline(
                    steps=[
                        ("imputer", SimpleImputer(strategy="median")),
                        ("scale", StandardScaler()),
                    ]
                ),
                NUMERIC_FEATURES,
            ),
            (
                "cat",
                OneHotEncoder(handle_unknown="ignore"),
                CATEGORICAL_FEATURES,
            ),
        ],
        remainder="drop",
    )

    model = LogisticRegression(
        max_iter=2500,
        class_weight="balanced",
        C=0.7,
        random_state=42,
    )

    pipeline = Pipeline(
        steps=[
            ("preprocessor", preprocessor),
            ("model", model),
        ]
    )
    pipeline.fit(train_df[FEATURES], train_df[TARGET])

    probabilities = pipeline.predict_proba(test_df[FEATURES])[:, 1]
    predictions = (probabilities >= 0.50).astype(int)

    metrics = {
        "model": "LogisticRegression",
        "prediction_horizon_days": 30,
        "train_start": str(train_df["reference_date"].min().date()),
        "train_end": str(train_df["reference_date"].max().date()),
        "test_start": str(test_df["reference_date"].min().date()),
        "test_end": str(test_df["reference_date"].max().date()),
        "train_rows": int(len(train_df)),
        "test_rows": int(len(test_df)),
        "positive_rate_train": float(train_df[TARGET].mean()),
        "positive_rate_test": float(test_df[TARGET].mean()),
        "accuracy": float(accuracy_score(test_df[TARGET], predictions)),
        "precision": float(
            precision_score(test_df[TARGET], predictions, zero_division=0)
        ),
        "recall": float(recall_score(test_df[TARGET], predictions, zero_division=0)),
        "f1": float(f1_score(test_df[TARGET], predictions, zero_division=0)),
        "roc_auc": float(roc_auc_score(test_df[TARGET], probabilities)),
        "pr_auc": float(average_precision_score(test_df[TARGET], probabilities)),
        "confusion_matrix": confusion_matrix(
            test_df[TARGET], predictions
        ).tolist(),
        "classification_report": classification_report(
            test_df[TARGET], predictions, zero_division=0, output_dict=True
        ),
        "note": (
            "POC académique basé sur l'historique des incidents par site. "
            "Le score estime le risque d'au moins un incident dans les 30 jours."
        ),
    }

    test_predictions = test_df[
        ["reference_date", "site", TARGET]
    ].copy()
    test_predictions["risk_probability"] = probabilities
    test_predictions["predicted_class"] = predictions
    test_predictions["risk_score"] = np.round(probabilities * 100, 1)
    test_predictions["risk_level"] = test_predictions["risk_probability"].apply(
        risk_level
    )

    latest = build_latest_feature_snapshot(incidents)
    latest_probabilities = pipeline.predict_proba(latest[FEATURES])[:, 1]
    latest["risk_probability"] = latest_probabilities
    latest["risk_score"] = np.round(latest_probabilities * 100, 1)
    latest["risk_level"] = latest["risk_probability"].apply(risk_level)
    latest["alert"] = latest["risk_probability"] >= 0.70
    latest["risk_reasons"] = latest.apply(risk_reasons, axis=1)
    latest = latest.sort_values(
        ["risk_probability", "incidents_90d"],
        ascending=[False, False],
    )

    # Extract interpretable coefficients.
    feature_names = pipeline.named_steps["preprocessor"].get_feature_names_out()
    coefficients = pipeline.named_steps["model"].coef_[0]
    feature_importance = pd.DataFrame(
        {
            "feature": feature_names,
            "coefficient": coefficients,
            "absolute_importance": np.abs(coefficients),
        }
    ).sort_values("absolute_importance", ascending=False)

    incidents.to_csv(artifacts_dir / "incidents_clean.csv", index=False)
    weekly.to_csv(artifacts_dir / "site_week_dataset.csv", index=False)
    test_predictions.to_csv(artifacts_dir / "test_predictions.csv", index=False)
    latest.to_csv(artifacts_dir / "latest_risk_scores.csv", index=False)
    feature_importance.to_csv(
        artifacts_dir / "feature_importance.csv", index=False
    )
    joblib.dump(pipeline, artifacts_dir / "risk_model.joblib")

    with open(artifacts_dir / "metrics.json", "w", encoding="utf-8") as file:
        json.dump(metrics, file, ensure_ascii=False, indent=2)

    return metrics


if __name__ == "__main__":
    root = Path(__file__).resolve().parents[1]
    metrics = train(
        excel_path=root / "data" / "ONDA-Projet-WAN-Liste-incident-202109-202410.xlsx",
        artifacts_dir=root / "artifacts",
    )
    print(json.dumps(metrics, ensure_ascii=False, indent=2))
