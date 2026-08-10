"""Country narrative generator.
Deterministic baseline + optional LLM enhancement (Groq free tier).
Always falls back to the deterministic template on any failure."""
import os
import json

try:
    import requests
except ImportError:
    requests = None

MODEL = "llama-3.1-8b-instant"
ENDPOINT = "https://api.groq.com/openai/v1/chat/completions"
_cache = {}

FLAG_LABELS = {
    "en": {"inflation": "high inflation", "debt": "elevated public debt", "unemployment": "high unemployment",
           "stability": "political instability", "corruption": "weak corruption control"},
    "fr": {"inflation": "inflation élevée", "debt": "dette publique élevée", "unemployment": "chômage élevé",
           "stability": "instabilité politique", "corruption": "contrôle de la corruption faible"},
}
PILLAR_LABELS = {
    "en": {"political": "political", "economic": "economic", "social": "social", "technological": "technological",
           "environmental": "environmental", "legal": "legal & governance"},
    "fr": {"political": "politique", "economic": "économique", "social": "social", "technological": "technologique",
           "environmental": "environnemental", "legal": "légal & gouvernance"},
}


def _api_key():
    try:
        import streamlit as st
        return st.secrets.get("GROQ_API_KEY", os.environ.get("GROQ_API_KEY", ""))
    except Exception:
        return os.environ.get("GROQ_API_KEY", "")


def _sanitize(text):
    return text.encode("latin-1", "replace").decode("latin-1")


def deterministic_narrative(facts, lang):
    P, F = PILLAR_LABELS[lang], FLAG_LABELS[lang]
    c, s, pc = facts["country"], facts["score"], facts["percentile"]
    pos = f"top {pc}%" if pc >= 50 else f"bottom {100 - pc}%"
    if lang == "fr":
        l1 = (f"{c} obtient un score d'attractivité de {s}/100, le situant dans le {pos} mondial. "
              f"Son principal atout est le pilier {P[facts['strongest']]} ({facts['strongest_score']}/100), "
              f"tandis que le pilier {P[facts['weakest']]} ({facts['weakest_score']}/100) constitue sa principale faiblesse.")
        l2 = ("Aucun signal de risque critique n'est détecté; le profil macroéconomique apparaît stable."
              if not facts["flags"] else
              f"{len(facts['flags'])} signal(s) de risque à surveiller : " + ", ".join(F[f] for f in facts["flags"]) + ".")
        l3 = ("Recommandation : candidat solide à considérer pour l'investissement." if s >= 70 and not facts["flags"]
              else "Recommandation : procéder avec prudence et surveiller les indicateurs de risque." if s >= 50 and len(facts["flags"]) <= 1
              else "Recommandation : profil à haut risque nécessitant une due diligence approfondie.")
    else:
        l1 = (f"{c} scores {s}/100 on the composite attractiveness index, placing it in the {pos} globally. "
              f"Its main strength is the {P[facts['strongest']]} pillar ({facts['strongest_score']}/100), "
              f"while the {P[facts['weakest']]} pillar ({facts['weakest_score']}/100) is its main weakness.")
        l2 = ("No critical risk signal is detected; the macroeconomic profile appears stable."
              if not facts["flags"] else
              f"{len(facts['flags'])} risk signal(s) to monitor: " + ", ".join(F[f] for f in facts["flags"]) + ".")
        l3 = ("Recommendation: strong candidate for investment consideration." if s >= 70 and not facts["flags"]
              else "Recommendation: proceed with caution and monitor key risk indicators." if s >= 50 and len(facts["flags"]) <= 1
              else "Recommendation: high-risk profile requiring extensive due diligence.")
    return _sanitize(f"{l1} {l2} {l3}")


def _llm_narrative(facts, lang):
    key = _api_key()
    if not key or requests is None:
        return None
    language = "French" if lang == "fr" else "English"
    prompt = (f"You are a senior macro-economic analyst. Write a concise executive summary (3 short paragraphs) "
              f"in {language} for the country report of {facts['country']} (year {facts['year']}). "
              f"Use ONLY the data provided; do not invent figures. "
              f"Paragraph 1: overall positioning (score, percentile, main strength/weakness). "
              f"Paragraph 2: risk/stability assessment. Paragraph 3: investment recommendation. "
              f"Tone: professional, factual. DATA: {json.dumps(facts)}")
    try:
        r = requests.post(ENDPOINT, headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json"},
                          json={"model": MODEL, "temperature": 0, "max_tokens": 600,
                                "messages": [{"role": "user", "content": prompt}]}, timeout=20)
        r.raise_for_status()
        return _sanitize(r.json()["choices"][0]["message"]["content"].strip())
    except Exception:
        return None


def generate_narrative(facts, lang):
    key = (facts["country"], facts["year"], lang)
    if key in _cache:
        return _cache[key]
    text = _llm_narrative(facts, lang) or deterministic_narrative(facts, lang)
    _cache[key] = text
    return text
