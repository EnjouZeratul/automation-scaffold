import pandas as pd

from cleaners.normalizer import DataNormalizer


def test_normalize_columns():
    n = DataNormalizer()
    df = pd.DataFrame({"User Name": ["Alice"], "Age-Value": ["25"]})
    result = n.normalize(df)
    assert "user_name" in result.columns
    assert "age_value" in result.columns


def test_normalize_dates():
    n = DataNormalizer()
    df = pd.DataFrame({"created_at": ["2024/01/15", "2024-02-20"]})
    result = n.normalize(df, date_columns=["created_at"])
    assert result["created_at"].iloc[0] == "2024-01-15"


def test_normalize_numeric():
    n = DataNormalizer()
    df = pd.DataFrame({"price": ["1,234", "5,678"]})
    result = n.normalize(df, numeric_columns=["price"])
    assert result["price"].iloc[0] == 1234.0
