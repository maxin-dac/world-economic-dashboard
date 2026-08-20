"""
Power BI Star Schema Generator
Transforme world_economic.csv en tables Parquet + CSV pour Power BI.
Tables : Dim_Country, Dim_Time, Dim_Indicator, Fact_EconomicIndicators
"""

import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).parent.parent))
from core.constants import PESTEL_INDICATORS, INVERSE_INDICATORS


def load_iso3_to_fr() -> dict:
    """Noms de pays FR extraits de app.py via AST (sans lancer Streamlit)."""
    import ast
    src = Path(__file__).parent.parent / "app.py"
    tree = ast.parse(src.read_text(encoding="utf-8"))
    for node in ast.walk(tree):
        if isinstance(node, ast.Assign):
            for t in node.targets:
                if isinstance(t, ast.Name) and t.id == "ISO3_TO_FR":
                    return ast.literal_eval(node.value)
    return {}


def load_source_data() -> pd.DataFrame:
    csv_path = Path(__file__).parent / "world_economic.csv"
    if not csv_path.exists():
        raise FileNotFoundError(f"Fichier source introuvable: {csv_path}")
    df = pd.read_csv(csv_path)
    print(f"✓ {len(df):,} lignes lues depuis {csv_path.name}")
    return df


def build_dim_country(df: pd.DataFrame) -> pd.DataFrame:
    cols = ["iso3", "country", "region", "income_group",
            "latitude", "longitude"]
    cols = [c for c in cols if c in df.columns]
    dim = df[cols].drop_duplicates(subset=["iso3"]).sort_values("iso3").copy()
    dim["country_fr"] = (dim["iso3"].map(load_iso3_to_fr())
                         .fillna(dim["country"]))
    n_fr = (dim["country_fr"] != dim["country"]).sum()
    print(f"✓ Dim_Country: {len(dim)} pays ({n_fr} traduits en FR)")
    return dim.reset_index(drop=True)


def build_dim_time(df: pd.DataFrame) -> pd.DataFrame:
    years = sorted(int(y) for y in df["year"].dropna().unique())
    dim = pd.DataFrame({
        "year": years,
        "decade": [(y // 10) * 10 for y in years],
        "is_leap_year": [(y % 4 == 0 and y % 100 != 0) or (y % 400 == 0)
                         for y in years],
    })
    print(f"✓ Dim_Time: {len(dim)} annees ({years[0]}-{years[-1]})")
    return dim



def load_labels_fr() -> dict:
    """Libellés FR des indicateurs (translations.py, extraction AST)."""
    import ast
    import pathlib
    src = pathlib.Path(__file__).parent.parent / "translations.py"
    tree = ast.parse(src.read_text(encoding="utf-8"))
    for node in ast.walk(tree):
        if isinstance(node, ast.Assign):
            for t in node.targets:
                if isinstance(t, ast.Name) and t.id == "TRANSLATIONS":
                    return ast.literal_eval(node.value).get("fr", {})
    return {}


def build_dim_indicator() -> pd.DataFrame:
    records = [
        {"indicator_id": code, "pillar": pillar,
         "is_inverse": code in INVERSE_INDICATORS}
        for pillar, codes in PESTEL_INDICATORS.items()
        for code in codes
    ]
    dim = pd.DataFrame(records).sort_values(["pillar", "indicator_id"])
    labels = load_labels_fr()
    pillar_fr = {"political": "Politique", "economic": "Économique",
                 "social": "Social", "technological": "Technologique",
                 "environmental": "Environnemental", "legal": "Légal"}
    naked = dim["indicator_id"].str.replace("_", " ")
    dim["label_fr"] = (dim["pillar"].str.lower().map(pillar_fr)
                       .fillna(dim["pillar"])
                       + " - " + naked.map(labels).fillna(naked))
    print(f"✓ Dim_Indicator: {len(dim)} indicateurs (libelles FR)")
    return dim.reset_index(drop=True)


def build_fact_table(df: pd.DataFrame,
                     dim_indicator: pd.DataFrame) -> pd.DataFrame:
    codes = [c for c in dim_indicator["indicator_id"] if c in df.columns]
    missing = set(dim_indicator["indicator_id"]) - set(codes)
    if missing:
        print(f"⚠ {len(missing)} indicateurs absents du CSV source")
    fact = df[["iso3", "year"] + codes].melt(
        id_vars=["iso3", "year"],
        var_name="indicator_id",
        value_name="value",
    )
    fact = (fact.replace([np.inf, -np.inf], np.nan)
            .dropna(subset=["value"]))
    fact["iso3"] = fact["iso3"].astype(str)
    fact["indicator_id"] = fact["indicator_id"].astype(str)
    fact["year"] = fact["year"].astype("int64")
    fact["value"] = fact["value"].astype("float64")
    print(f"✓ Fact_EconomicIndicators: {len(fact):,} lignes")
    return fact.reset_index(drop=True)


def validate_schema(dim_country, dim_time, dim_indicator, fact) -> None:
    errors = []
    if set(fact["iso3"]) - set(dim_country["iso3"]):
        errors.append("iso3 inconnus dans les faits")
    if set(fact["year"]) - set(dim_time["year"]):
        errors.append("annees inconnues dans les faits")
    if set(fact["indicator_id"]) - set(dim_indicator["indicator_id"]):
        errors.append("indicateurs inconnus dans les faits")
    if errors:
        raise ValueError("Validation echouee: " + "; ".join(errors))
    print("✓ Integrity referentielle OK")


def export(name: str, df: pd.DataFrame, out: Path) -> None:
    pq = out / f"{name}.parquet"
    df.to_parquet(pq, index=False, compression="snappy")
    csv = out / f"{name}.csv"
    df.to_csv(csv, index=False, encoding="utf-8-sig")
    print(f"  → {name}: parquet {pq.stat().st_size / 1e6:.1f} MB "
          f"/ csv {csv.stat().st_size / 1e6:.1f} MB")


def main() -> None:
    print("=" * 60)
    print("Power BI Star Schema Generator")
    print("=" * 60)
    df = load_source_data()
    dim_country = build_dim_country(df)
    dim_time = build_dim_time(df)
    dim_indicator = build_dim_indicator()
    fact = build_fact_table(df, dim_indicator)
    validate_schema(dim_country, dim_time, dim_indicator, fact)

    out = Path(__file__).parent / "powerbi"
    out.mkdir(exist_ok=True)
    print("\nExport (Parquet + CSV):")
    export("Dim_Country", dim_country, out)
    export("Dim_Time", dim_time, out)
    export("Dim_Indicator", dim_indicator, out)
    export("Fact_EconomicIndicators", fact, out)
    print("\n✓ Generation Star Schema terminee")


if __name__ == "__main__":
    main()