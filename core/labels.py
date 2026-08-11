"""Label helpers: indicator display names with optional PESTEL pillar prefix."""
from translations import t, TRANSLATIONS
from core.constants import INDICATOR_TO_PILLAR, PESTEL_LABEL_KEYS


def en_label(key: str) -> str:
    """English fallback label for an indicator key."""
    return TRANSLATIONS.get("en", {}).get(key, key.replace("_", " ").title())


def ind_label(key: str, current_lang: str, with_pillar: bool = False) -> str:
    """Localized label for an indicator, optionally prefixed with its PESTEL pillar."""
    label = t(key, current_lang)
    if label == key:
        label = key.replace("_", " ").title()
    if with_pillar:
        pillar = INDICATOR_TO_PILLAR.get(key)
        if pillar:
            return f"{t(PESTEL_LABEL_KEYS[pillar], current_lang)} - {label}"
    return label
