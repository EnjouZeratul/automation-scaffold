"""影刀 Python 代码块调用示例

在影刀中通过"执行 Python 代码块"节点调用:
  python scripts/process_csv.py input.csv output.csv
"""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT))

from processors.web_scraper import WebScrapeProcessor
from processors.report_export import ReportExportProcessor


def main(input_path: str, output_path: str, processor: str = "web"):
    if processor == "web":
        proc = WebScrapeProcessor()
    else:
        proc = ReportExportProcessor()
    df = proc.load_csv(input_path)
    result = proc.process(df)
    proc.save(result, output_path)
    print(f"处理完成: {len(result)} 行 -> {output_path}")


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2], sys.argv[3] if len(sys.argv) > 3 else "web")
