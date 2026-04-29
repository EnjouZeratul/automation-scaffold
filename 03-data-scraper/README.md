# 03-data-scraper 数据抓取服务

FastAPI 统一数据抓取服务，支持 API / CSV / 数据库 / 网页 4 种数据源。

## 路由一览

| 路由前缀 | 说明 |
|----------|------|
| `/scrape/api` | API 数据源（支持分页） |
| `/scrape/csv` | CSV 导入 |
| `/scrape/db` | 数据库直连查询（只读 + 参数化） |
| `/scrape/web` | 网页抓取（static / Playwright 两种模式） |

## 启动与关闭

```bash
# 启动
cd D:/TA/automation-scaffold/03-data-scraper
uvicorn app:app --host 0.0.0.0 --port 8200 --reload

# 后台启动（Windows）
Start-Process python -ArgumentList "-m","uvicorn","app:app","--host","0.0.0.0","--port","8200" -WindowStyle Hidden

# 关闭（Ctrl+C 或 kill 进程）
Stop-Process -Name python -Force  # 仅当确认无其他 Python 进程时
```

## 测试

```bash
cd D:/TA/automation-scaffold
python -m pytest 03-data-scraper/tests/ -v
```

## 使用示例

```bash
# Health check
curl http://localhost:8200/health

# API 数据源抓取
curl http://localhost:8200/scrape/api/fetch?url=https://api.example.com/data

# 网页抓取
curl http://localhost:8200/scrape/web/scraper?url=https://example.com

# 数据库查询
curl http://localhost:8200/scrape/db/query?dsn=sqlite:///data.db&sql=SELECT+*+FROM+users
```

## 环境变量

| 变量 | 说明 |
|------|------|
| `SCRAPER_API_KEY` | API Key 认证（为空则跳过验证） |
