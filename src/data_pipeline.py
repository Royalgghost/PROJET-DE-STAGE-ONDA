
from __future__ import annotations

import re
import unicodedata
from pathlib import Path

import numpy as np
import pandas as pd


COLUMN_MAP = {
    "Ticket-Number": "ticket_number",
    "SITE": "site_raw",
    "DATE_INCIDENT": "date_incident",
    "DATE_TICKET": "date_ticket",
    "DATE_RECOVERY": "date_recovery",
    "DATE_CLOTURE_TICKET": "date_closure",
    "DUREE_INCIDENT\n(h)": "incident_duration_h",
    "DUREE_TICKET\n(h)": "ticket_duration_h",
    "Nature Incident": "incident_nature_raw",
}

SITE_NAME_FIXES = {
    "BOUAARFA": "BOUARFA",
    "MARRACKECH": "MARRAKECH",
    "ELHOUCEIMA": "ELHOCEIMA",
    "IFRAN": "IFRANE",
    "BENIMELLAL": "BENI-MELLAL",
    "BENSLIMANE": "BENS-SLIMANE",
    "TITMELLIL": "TIT-MELLIL",
    "TANTAN": "TAN-TAN",
}


def normalize_text(value: object) -> str:
    if pd.isna(value):
        return ""
    text = str(value).strip().lower().replace("’", "'")
    text = unicodedata.normalize("NFKD", text)
    text = "".join(ch for ch in text if not unicodedata.combining(ch))
    return re.sub(r"\s+", " ", text)


def normalize_site(value: object) -> tuple[str, str, str]:
    raw = "" if pd.isna(value) else str(value).strip()
    match = re.match(r"^\s*(\d{1,3})\s*[-–]\s*(.+?)\s*$", raw)
    if not match:
        name = re.sub(r"[^A-Z0-9]+", "-", normalize_text(raw).upper()).strip("-")
        return "", name, name

    code = match.group(1).zfill(3)
    name = re.sub(
        r"[^A-Z0-9]+",
        "-",
        normalize_text(match.group(2)).upper(),
    ).strip("-")
    name = SITE_NAME_FIXES.get(name, name)
    return code, name, f"{code}-{name}"


def classify_incident(value: object) -> tuple[str, str, str]:
    text = normalize_text(value)

    has_iam = bool(re.search(r"\biam\b|maroc telecom", text))
    has_orange = "orange" in text

    if has_iam and has_orange:
        operator = "IAM + ORANGE"
    elif has_iam:
        operator = "IAM"
    elif has_orange:
        operator = "ORANGE"
    else:
        operator = "NON_IDENTIFIE"

    if "electric" in text:
        category = "ELECTRICITE"
    elif "vpn" in text or "firewall" in text:
        category = "VPN_FIREWALL"
    elif "liaison" in text or has_iam or has_orange:
        category = "LIAISON_WAN"
    else:
        category = "AUTRE"

    if "coupure totale" in text:
        incident_type = "COUPURE_TOTALE"
    elif "coupures multiples" in text or "coupure multiple" in text:
        incident_type = "COUPURES_MULTIPLES"
    elif "perturbation" in text:
        incident_type = "PERTURBATION"
    elif "lenteur" in text:
        incident_type = "LENTEUR"
    elif "electric" in text:
        incident_type = "COUPURE_ELECTRIQUE"
    else:
        incident_type = "AUTRE"

    return category, operator, incident_type


def load_and_clean_incidents(excel_path: str | Path) -> pd.DataFrame:
    """Load every sheet from the ONDA workbook and produce one clean incident table."""
    excel_path = Path(excel_path)
    sheets = pd.read_excel(excel_path, sheet_name=None)

    frames: list[pd.DataFrame] = []
    for sheet_name, frame in sheets.items():
        frame = frame.copy()
        frame.columns = [str(col).strip() for col in frame.columns]
        frame = frame.rename(columns=COLUMN_MAP)
        missing = set(COLUMN_MAP.values()) - set(frame.columns)
        if missing:
            raise ValueError(
                f"Feuille {sheet_name}: colonnes manquantes après normalisation: {sorted(missing)}"
            )
        frame = frame[list(COLUMN_MAP.values())]
        frame["source_sheet"] = str(sheet_name)
        frames.append(frame)

    incidents = pd.concat(frames, ignore_index=True)

    for col in ["date_incident", "date_ticket", "date_recovery", "date_closure"]:
        incidents[col] = pd.to_datetime(incidents[col], errors="coerce")

    for col in ["incident_duration_h", "ticket_duration_h"]:
        incidents[col] = pd.to_numeric(incidents[col], errors="coerce")

    incidents["ticket_number"] = (
        incidents["ticket_number"]
        .astype("string")
        .str.replace(r"\.0$", "", regex=True)
        .str.strip()
    )

    site_parts = incidents["site_raw"].apply(normalize_site)
    incidents[["site_code", "site_name", "site"]] = pd.DataFrame(
        site_parts.tolist(), index=incidents.index
    )

    nature_parts = incidents["incident_nature_raw"].apply(classify_incident)
    incidents[["category", "operator", "incident_type"]] = pd.DataFrame(
        nature_parts.tolist(), index=incidents.index
    )

    incidents["year"] = incidents["date_incident"].dt.year
    incidents["month"] = incidents["date_incident"].dt.month
    incidents["week"] = incidents["date_incident"].dt.isocalendar().week.astype("Int64")
    incidents["duration_gap_h"] = (
        incidents["ticket_duration_h"] - incidents["incident_duration_h"]
    )

    incidents["is_long_incident"] = (
        incidents["incident_duration_h"].fillna(0) >= 24
    ).astype(int)
    incidents["is_very_long_incident"] = (
        incidents["incident_duration_h"].fillna(0) >= 168
    ).astype(int)

    incidents = incidents.dropna(subset=["date_incident", "site"]).copy()
    incidents = incidents.sort_values(["date_incident", "site", "ticket_number"])
    incidents = incidents.reset_index(drop=True)
    return incidents


def _window_features(
    site_incidents: pd.DataFrame,
    reference_date: pd.Timestamp,
    window_days: int,
) -> pd.DataFrame:
    start = reference_date - pd.Timedelta(days=window_days)
    return site_incidents[
        (site_incidents["date_incident"] >= start)
        & (site_incidents["date_incident"] < reference_date)
    ]


def create_site_week_dataset(
    incidents: pd.DataFrame,
    horizon_days: int = 30,
    include_latest_unlabelled: bool = False,
) -> pd.DataFrame:
    """
    Create one observation per site and per week.

    Features use only incidents before the reference date.
    Target = at least one incident in the following horizon.
    """
    if incidents.empty:
        raise ValueError("Le tableau d'incidents est vide.")

    first_date = incidents["date_incident"].min().normalize()
    last_date = incidents["date_incident"].max().normalize()
    start = first_date + pd.Timedelta(days=90)
    labelled_end = last_date - pd.Timedelta(days=horizon_days)

    reference_dates = list(pd.date_range(start=start, end=labelled_end, freq="W-MON"))
    if include_latest_unlabelled:
        latest_ref = last_date + pd.Timedelta(days=1)
        reference_dates.append(latest_ref)

    rows: list[dict[str, object]] = []
    sites = sorted(incidents["site"].dropna().unique())

    for site in sites:
        site_df = incidents[incidents["site"] == site].sort_values("date_incident")
        dates = site_df["date_incident"]

        for ref in reference_dates:
            past_7 = _window_features(site_df, ref, 7)
            past_30 = _window_features(site_df, ref, 30)
            past_90 = _window_features(site_df, ref, 90)
            past_180 = _window_features(site_df, ref, 180)

            previous = site_df[site_df["date_incident"] < ref]
            if previous.empty:
                days_since_last = 365.0
            else:
                days_since_last = float(
                    (ref - previous["date_incident"].max()).days
                )

            future = site_df[
                (dates >= ref)
                & (dates < ref + pd.Timedelta(days=horizon_days))
            ]

            label_available = ref <= labelled_end
            row = {
                "reference_date": ref,
                "site": site,
                "site_code": site.split("-", 1)[0],
                "month": ref.month,
                "quarter": ref.quarter,
                "incidents_7d": len(past_7),
                "incidents_30d": len(past_30),
                "incidents_90d": len(past_90),
                "incidents_180d": len(past_180),
                "downtime_30d_h": past_30["incident_duration_h"].fillna(0).sum(),
                "downtime_90d_h": past_90["incident_duration_h"].fillna(0).sum(),
                "mean_duration_90d_h": (
                    past_90["incident_duration_h"].mean()
                    if not past_90.empty
                    else 0.0
                ),
                "max_duration_90d_h": (
                    past_90["incident_duration_h"].max()
                    if not past_90.empty
                    else 0.0
                ),
                "days_since_last_incident": days_since_last,
                "iam_incidents_90d": int((past_90["operator"] == "IAM").sum()),
                "orange_incidents_90d": int((past_90["operator"] == "ORANGE").sum()),
                "electric_incidents_90d": int(
                    (past_90["category"] == "ELECTRICITE").sum()
                ),
                "total_incidents_before": len(previous),
                "historical_mean_duration_h": (
                    previous["incident_duration_h"].mean()
                    if not previous.empty
                    else 0.0
                ),
                "target_incident_next_30d": (
                    int(len(future) > 0) if label_available else np.nan
                ),
            }
            rows.append(row)

    dataset = pd.DataFrame(rows)
    dataset = dataset.sort_values(["reference_date", "site"]).reset_index(drop=True)
    return dataset


def build_latest_feature_snapshot(incidents: pd.DataFrame) -> pd.DataFrame:
    """
    Build the latest unlabelled feature row for every site, using the day after
    the last incident as the reference date.
    """
    all_rows = create_site_week_dataset(
        incidents,
        horizon_days=30,
        include_latest_unlabelled=True,
    )
    latest_date = all_rows["reference_date"].max()
    return all_rows[all_rows["reference_date"] == latest_date].copy()
