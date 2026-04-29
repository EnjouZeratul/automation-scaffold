# 02-rpa 影刀 RPA

## 影刀 Python 代码块调用方式

1. 在影刀流程中添加"执行 Python 代码块"节点
2. 配置 Python 环境路径指向本项目的 `.venv`
3. 代码示例：

```python
import sys
sys.path.append(r"D:\TA\automation-scaffold\02-rpa")
from processors.web_scraper import WebScrapeProcessor

proc = WebScrapeProcessor()
df = proc.load_csv(r"C:\temp\export.csv")
result = proc.process(df)
proc.save(result, r"C:\temp\output.csv")
```

## 可用处理器

- **WebScrapeProcessor** — 网页采集数据清洗（去重、列名标准化、空值处理）
- **ReportExportProcessor** — 报表数据解析（金额列/日期列格式化）

## MCP Server 配置

在影刀中配置 MCP Server：
1. 打开影刀设置 → MCP Server
2. 添加 Server: `http://localhost:<port>`
3. 通过 HTTP API 触发 Python 脚本
