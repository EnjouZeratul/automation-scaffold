import pandas as pd

from processors.web_scraper import WebScrapeProcessor
from processors.report_export import ReportExportProcessor


def test_web_scrape_processor():
    df = pd.DataFrame({
        "Name - Title": ["Alice", "Bob", "Alice"],
        "Value": ["100", "200", "100"],
    })
    proc = WebScrapeProcessor()
    result = proc.process(df)
    assert len(result) == 2  # 去重后
    assert "name_title" in result.columns


def test_report_export_processor():
    df = pd.DataFrame({
        "date": ["2024/01/01", "2024-02-02"],
        "amount": ["1,000", "2,500"],
    })
    proc = ReportExportProcessor(amount_columns=["amount"], date_columns=["date"])
    result = proc.process(df)
    assert result["amount"].iloc[0] == 1000.0
    assert result["date"].iloc[0] == "2024-01-01"
