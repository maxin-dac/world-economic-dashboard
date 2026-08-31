from translations import t, TRANSLATIONS

def test_languages_present():
    assert "en" in TRANSLATIONS and "fr" in TRANSLATIONS

def test_missing_key_falls_back_to_key():
    assert t("__missing_key__", "en") == "__missing_key__"
    assert t("__missing_key__", "fr") == "__missing_key__"

def test_format_kwargs_applied():
    en = TRANSLATIONS["en"]
    key = ("median_by_region" if "median_by_region" in en
           else next((k for k, v in en.items() if "{ind}" in v and "{y}" in v), None))
    assert key is not None
    assert "2030" in t(key, "en", ind="X", y=2030)
