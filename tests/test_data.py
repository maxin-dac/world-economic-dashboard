from core.data import load_data

def test_load_data_columns_and_years():
    df = load_data()
    assert not df.empty
    for col in ["iso3", "country", "region", "income_group", "year"]:
        assert col in df.columns
    assert df["year"].min() >= 2000 and df["year"].max() <= 2024
