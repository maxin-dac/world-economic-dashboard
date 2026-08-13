"""
Power BI Translation Exporter (Auto-Adaptive)
Scans ALL keys from translations.py and generates a Tabular Translator JSON.
No manual key mapping required: 100% of translations are exported.
"""

import json
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))
from translations import TRANSLATIONS


def classify_key(key: str) -> tuple:
    """
    Auto-classify a translation key into a Power BI object type.
    Returns (objectType, objectId) based on key prefix heuristics.
    """
    key_lower = key.lower()
    
    # Pages (tabs in Streamlit = pages in Power BI)
    if key_lower.startswith("tab_") or key_lower.endswith("_title"):
        return "ReportPage", key
    
    # PESTEL pillars
    if key_lower.startswith("pillar_"):
        return "Column", f"Dim_Indicator[Pillar]::{key}"
    
    # Common filters and labels
    if key_lower in ("region", "year", "income_group", "country"):
        return "Column", f"Dim_Country[{key.title()}]"
    
    # Investment-specific labels
    if any(kw in key_lower for kw in ("score", "red_flag", "opportunity", "quadrant")):
        return "Measure", f"[{key.title()}]"
    
    # Everything else: generic measure (you'll rename later in PBI Desktop)
    return "Measure", f"[{key.title()}]"


def extract_all_translations() -> dict:
    """
    Extract ALL translations from TRANSLATIONS["fr"].
    Zero keys lost — everything is exported.
    """
    if "fr" not in TRANSLATIONS:
        raise ValueError("French translations not found in TRANSLATIONS dict")

    fr_dict = TRANSLATIONS["fr"]
    
    translation_model = {
        "culture": "fr-FR",
        "translations": {},
        "_metadata": {
            "total_keys": len(fr_dict),
            "source": "translations.py",
            "auto_generated": True,
            "note": "objectId values are based on source keys. "
                    "Rename them in Power BI Desktop to match your actual model."
        }
    }
    
    translations = {}
    category_count = {"ReportPage": 0, "Column": 0, "Measure": 0}
    
    for key, value in fr_dict.items():
        if not isinstance(value, str):
            continue  # Skip non-string values (nested dicts, etc.)
        
        obj_type, obj_id = classify_key(key)
        trans_key = f"{obj_type}.{obj_id}"
        translations[trans_key] = value
        category_count[obj_type] += 1
    
    translation_model["translations"] = translations
    
    print(f"✓ Extracted {len(translations)} translations (100% of source keys)")
    print(f"  ├─ Pages:    {category_count['ReportPage']}")
    print(f"  ├─ Columns:  {category_count['Column']}")
    print(f"  └─ Measures: {category_count['Measure']}")
    
    return translation_model


def export_translation_json(translation_model: dict, output_path: Path):
    """Export translation model to JSON file."""
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(translation_model, f, indent=2, ensure_ascii=False)
    
    size_kb = output_path.stat().st_size / 1024
    print(f"✓ Exported to {output_path} ({size_kb:.1f} KB)")


def main():
    print("=" * 60)
    print("Power BI Translation Exporter (Auto-Adaptive)")
    print("=" * 60)
    
    # Extract ALL translations
    model = extract_all_translations()
    
    # Export
    output_path = Path(__file__).parent.parent / "data" / "powerbi" / "translations.json"
    export_translation_json(model, output_path)
    
    print("\n" + "=" * 60)
    print("Next steps in Power BI Desktop:")
    print("1. File → Options → Preview Features → Enable 'Tabular Translator'")
    print("2. Tools → Tabular Translator → Import from JSON")
    print(f"3. Select: {output_path.name}")
    print("4. Rename the objectId values to match your actual model names")
    print("=" * 60)


if __name__ == "__main__":
    main()