# Automation Scaffold

统一 Monorepo 自动化脚手架，包含 4 个子系统：

- `shared/` — 公共包（配置/日志/钉钉/飞书/百炼客户端）
- `01-ai-table/` — AI 表格搭建（钉钉+飞书）
- `02-rpa/` — 影刀 RPA 数据处理
- `03-data-scraper/` — 数据抓取服务
- `04-agent/` — LangGraph Agent

---

## 快速开始

### 1. 环境准备

```bash
cd automation-scaffold
# 安装依赖（各子项目独立安装）
pip install -e shared/
pip install -e 01-ai-table/
pip install -e 02-rpa/
pip install -e 03-data-scraper/
pip install -e 04-agent/
```

### 2. 配置 API Key

```bash
cp .env.example .env
# 编辑 .env 填入对应 API Key
```

### 3. 运行测试

```bash
cd D:/TA/automation-scaffold

# 运行全部测试
python -m pytest shared/tests/ -v
python -m pytest 01-ai-table/tests/ -v
python -m pytest 02-rpa/tests/ -v
python -m pytest 03-data-scraper/tests/ -v
python -m pytest 04-agent/tests/ -v
```

---

## 各子系统

| 子系统 | 启动命令 | 端口 | README |
|--------|----------|------|--------|
| shared | 无需启动 | - | [README](shared/README.md) |
| 01-ai-table | `python main.py <command>` | CLI | [README](01-ai-table/README.md) |
| 02-rpa | 影刀调用 / 独立脚本 | - | [README](02-rpa/README.md) |
| 03-data-scraper | `uvicorn app:app --host 0.0.0.0 --port 8200` | 8200 | [README](03-data-scraper/README.md) |
| 04-agent | `python app.py` | 8100 | [README](04-agent/README.md) |

### 服务启停

```bash
# 启动 03-data-scraper
cd 03-data-scraper
uvicorn app:app --host 0.0.0.0 --port 8200 --reload
# 关闭: Ctrl+C

# 启动 04-agent
cd 04-agent
python app.py
# 关闭: Ctrl+C

# 运行 01-ai-table CLI
cd 01-ai-table
python main.py create --title "我的表格"
python main.py watch --spreadsheet-token <tok> --sheet-id 0 --interval 30
# 停止: Ctrl+C
```

---

## 项目结构

```
automation-scaffold/
├── pyproject.toml              # uv workspace 根配置
├── .env.example                # API Key 模板
├── .gitignore
├── README.md
├── shared/                     # 公共包
│   ├── config/settings.py      # 统一配置
│   ├── utils/                  # 钉钉/飞书/百炼/日志
│   └── tests/
├── 01-ai-table/                # AI 表格
│   ├── table_ops.py            # 表格 CRUD
│   ├── ai_processor.py         # AI 处理
│   ├── watcher.py              # 变更监听
│   └── main.py                 # CLI 入口
├── 02-rpa/                     # 影刀 RPA
│   ├── processors/             # 数据处理器
│   ├── utils/encrypt.py        # AES-GCM 加密
│   └── scripts/                # 影刀调用脚本
├── 03-data-scraper/            # 数据抓取
│   ├── app.py                  # FastAPI 入口
│   ├── routers/                # 4 种数据源路由
│   └── cleaners/               # 数据标准化
├── 04-agent/                   # Agent
│   ├── app.py                  # FastAPI 回调服务
│   ├── graph/                  # LangGraph 状态机
│   ├── tools/                  # 工具封装
│   └── openclaw/               # 消息适配
└── docs/superpowers/
    ├── specs/                  # 设计文档
    └── plans/                  # 实现计划
```
