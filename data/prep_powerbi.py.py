"""
Power BI Star Schema Generator
Transforms world_economic.csv into optimized Parquet tables for Power BI.
Tables: Dim_Country, Dim_Time, Dim_Indicator, Fact_EconomicIndicators
"""

import pandas as pd
import numpy as np
from pathlib import Path
import sys

# Add project root to path to import core modules
sys.path.insert(0, str(Path(__file__).parent.parent))
from core.constants import PESTEL_INDICATORS, INVERSE_INDICATORS


def load_source_data() -> pd.DataFrame:
    """Load the aggregated CSV dataset."""
    csv_path = Path(__file__).parent / "world_economic.csv"
    if not csv_path.exists():
        raise FileNotFoundError(f"Source file not found: {csv_path}")
    
    df = pd.read_csv(csv_path)
    print(f"✓ Loaded {len(df):,} rows from {csv_path.name}")
    return df


def build_dim_country(df: pd.DataFrame) -> pd.DataFrame:
    """Build country dimension table."""
    cols = ["iso3", "country", "region", "income_group", "latitude", "longitude"]
    available_cols = [c for c in cols if c in df.columns]
    
    dim = df[available_cols].drop_duplicates(subset=["iso3"]).sort_values("iso3")
    
    # Add bilingual names if translations available
    try:
        from translations import TRANSLATIONS
        fr_names = {v: k for k, v in TRANSLATIONS.get("fr", {}).items() 
                    if isinstance(v, str) and len(k) == 3}
        dim["country_fr"] = dim["iso3"].map(fr_names).fillna(dim["country"])
    except Exception:
        dim["country_fr"] = dim["country"]
    
    print(f"✓ Dim_Country: {len(dim)} countries")
    return dim.reset_index(drop=True)


def build_dim_time(df: pd.DataFrame) -> pd.DataFrame:
    """Build time dimension table."""
    years = sorted(df["year"].dropna().unique())
    dim = pd.DataFrame({
        "year": years,
        "decade": (np.array(years) // 10) * 10,
        "is_leap_year": [(y % 4 == 0 and y % 100 != 0) or (y % 400 == 0) for y in years]
    })
    print(f"✓ Dim_Time: {len(dim)} years ({years[0]}-{years[-1]})")
    return dim


def build_dim_indicator() -> pd.DataFrame:
    """Build indicator dimension table from PESTEL schema."""
    records = []
    for pillar, indicators in PESTEL_INDICATORS.items():
        for ind_code in indicators:
            records.append({
                "indicator_id": ind_code,
                "pillar": pillar,
                "is_inverse": ind_code in INVERSE_INDICATORS
            })
    
    dim = pd.DataFrame(records).sort_values(["pillar", "indicator_id"])
    print(f"✓ Dim_Indicator: {len(dim)} indicators across {len(PESTEL_INDICATORS)} pillars")
    return dim.reset_index(drop=True)


def build_fact_table(df: pd.DataFrame, dim_indicator: pd.DataFrame) -> pd.DataFrame:
    """Build fact table in long format (unpivoted)."""
    id_cols = ["iso3", "year"]
    indicator_cols = dim_indicator["indicator_id"].tolist()
    
    # Filter to only existing indicator columns
    available_indicators = [c for c in indicator_cols if c in df.columns]
    missing = set(indicator_cols) - set(available_indicators)
    if missing:
        print(f"⚠ {len(missing)} indicators not found in source: {list(missing)[:5]}...")
    
    # Unpivot to long format
    fact = df[id_cols + available_indicators].melt(
        id_vars=id_cols,
        var_name="indicator_id",
        value_name="value"
    )
    
    # Remove null values to save space
    fact = fact.dropna(subset=["value"]).reset_index(drop=True)
    
    # Optimize dtypes
    fact["year"] = fact["year"].astype("int16")
    fact["value"] = fact["value"].astype("float32")
    fact["indicator_id"] = fact["indicator_id"].astype("category")
    fact["iso3"] = fact["iso3"].astype("category")
    
    print(f"✓ Fact_EconomicIndicators: {len(fact):,} rows ({len(available_indicators)} indicators)")
    return fact


def validate_schema(dim_country, dim_time, dim_indicator, fact):
    """Validate referential integrity."""
    errors = []
    
    # Check fact keys exist in dimensions
    fact_countries = set(fact["iso3"].unique())
    dim_countries = set(dim_country["iso3"])
    orphan_countries = fact_countries - dim_countries
    if orphan_countries:
        errors.append(f"Fact references {len(orphan_countries)} unknown countries")
    
    fact_years = set(fact["year"].unique())
    dim_years = set(dim_time["year"])
    orphan_years = fact_years - dim_years
    if orphan_years:
        errors.append(f"Fact references {len(orphan_years)} unknown years")
    
    fact_indicators = set(fact["indicator_id"].unique())
    dim_indicators = set(dim_indicator["indicator_id"])
    orphan_indicators = fact_indicators - dim_indicators
    if orphan_indicators:
        errors.append(f"Fact references {len(orphan_indicators)} unknown indicators")
    
    if errors:
        for e in errors:
            print(f"✗ VALIDATION ERROR: {e}")
        raise ValueError("Schema validation failed")
    
    print("✓ Schema validation passed (referential integrity OK)")


def export_parquet(name: str, df: pd.DataFrame, output_dir: Path):
    """Export DataFrame to Parquet with compression."""
    path = output_dir / f"{name}.parquet"
    df.to_parquet(path, index=False, engine="pyarrow", compression="snappy")
    size_mb = path.stat().st_size / (1024 * 1024)
    print(f"  → {path.name}: {size_mb:.1f} MB")


def main():
    """Main ETL pipeline."""
    print("=" * 60)
    print("Power BI Star Schema Generator")
    print("=" * 60)
    
    # Load source
    df = load_source_data()
    
    # Build dimensions
    dim_country = build_dim_country(df)
    dim_time = build_dim_time(df)
    dim_indicator = build_dim_indicator()
    
    # Build fact table
    fact = build_fact_table(df, dim_indicator)
    
    # Validate
    validate_schema(dim_country, dim_time, dim_indicator, fact)
    
    # Export
    output_dir = Path(__file__).parent / "powerbi"
    output_dir.mkdir(exist_ok=True)
    
    print("\nExporting Parquet files:")
    export_parquet("Dim_Country", dim_country, output_dir)
    export_parquet("Dim_Time", dim_time, output_dir)
    export_parquet("Dim_Indicator", dim_indicator, output_dir)
    export_parquet("Fact_EconomicIndicators", fact, output_dir)
    
    print("\n" + "=" * 60)
    print("✓ Star Schema generation complete!")
    print(f"  Output directory: {output_dir.absolute()}")
    print("=" * 60)


if __name__ == "__main__":
    main()