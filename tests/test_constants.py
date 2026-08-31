from core.constants import (PESTEL_PILLAR_ORDER, PESTEL_INDICATORS,
                            INDICATOR_TO_PILLAR, get_expressive_colorscale)

def test_pestel_pillar_order():
    assert PESTEL_PILLAR_ORDER == ["political", "economic", "social",
                                   "technological", "environmental", "legal"]

def test_indicator_mapping_consistent():
    for pillar, inds in PESTEL_INDICATORS.items():
        for ind in inds:
            assert INDICATOR_TO_PILLAR[ind] == pillar

def test_no_indicator_in_two_pillars():
    all_inds = [i for inds in PESTEL_INDICATORS.values() for i in inds]
    assert len(all_inds) == len(set(all_inds))

def test_colorscale_fallback():
    assert get_expressive_colorscale("gdp_per_capita") == "Viridis"
    assert isinstance(get_expressive_colorscale("unknown_xyz"), str)
