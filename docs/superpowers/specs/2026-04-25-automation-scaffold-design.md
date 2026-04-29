# Automation Scaffold 项目设计文档

> 日期: 2026-04-25
> 状态: Review 通过，待实现

## 概述

统一 Monorepo 项目脚手架，包含 4 个子系统：AI 表格搭建（钉钉+飞书）、影刀 RPA 数据处理、高级数据抓取服务、LangGraph Agent。各系统通过 `shared/` 公共包复用配置和工具。

---

## 整体架构

```
automation-scaffold/
├── shared/                        # 公共包
│   ├── config/
│   │   ├── settings.py            # 统一配置（pydantic-settings）
│   │   └── env.example            # 环境变量模板
│   ├── utils/
│   │   ├── logger.py              # 统一日志
│   │   ├── dingtalk.py            # 钉钉 API 客户端
│   │   ├── feishu.py              # 飞书 API 客户端
│   │   └── bailian.py             # 百炼 API 客户端
│   └── pyproject.toml
├── 01-ai-table/                   # AI 表格搭建
│   ├── main.py                    # 入口
│   ├── table_ops.py               # 建表 / 增删改查
│   ├── ai_processor.py            # 百炼 AI 处理
│   ├── watcher.py                 # 数据变更监听 + 群机器人通知
│   ├── pyproject.toml
│   └── tests/
├── 02-rpa/                        # 影刀 RPA
│   ├── processors/
│   │   ├── base.py                # 数据处理基类
│   │   ├── web_scraper.py         # 网页采集数据处理
│   │   └── report_export.py       # 报表导出处理
│   ├── utils/
│   │   └── encrypt.py             # 加密参数解析
│   ├── scripts/                   # 可独立运行的脚本
│   ├── README.md                  # 影刀调用说明
│   └── pyproject.toml
├── 03-data-scraper/               # 数据抓取服务
│   ├── app.py                     # FastAPI 入口
│   ├── config.py                  # pydantic-settings
│   ├── routers/
│   │   ├── api_source.py          # API 数据源路由
│   │   ├── csv_source.py          # CSV 导入路由
│   │   ├── db_source.py           # 数据库直连路由
│   │   └── web_scraper.py         # 高级网页抓取路由
│   ├── cleaners/
│   │   └── normalizer.py          # Pandas 统一清洗
│   ├── writers/
│   │   ├── db_writer.py           # 写数据库
│   │   └── table_writer.py        # 写钉钉/飞书表格
│   ├── logs/                      # 抓取日志
│   ├── pyproject.toml
│   └── tests/
├── 04-agent/                      # Agent 搭建
│   ├── app.py                     # LangGraph 入口
│   ├── config.py                  # pydantic-settings
│   ├── graph/
│   │   ├── router.py              # 路由节点
│   │   └── workflow.py            # 工具调用闭环
│   ├── tools/
│   │   ├── bailian_tool.py        # 百炼 API 工具
│   │   ├── table_tool.py          # 表格查询/推送工具
│   │   ├── web_search_tool.py     # 联网搜索工具
│   │   ├── scrape_tool.py         # 抓取工具（预留接口）
│   │   └── rpa_tool.py            # RPA 工具（预留接口）
│   ├── openclaw/
│   │   ├── bot.py                 # 钉钉/飞书双向适配
│   │   ├── callback.py            # 群机器人回调处理
│   │   ├── router.py              # 消息路由
│   │   └── skills.py              # 表格查询/数据推送 skill
│   ├── pyproject.toml
│   └── tests/
├── pyproject.toml                 # 根配置（uv workspace）
└── README.md                      # 项目总览
```

**Monorepo 管理：**
- 使用 `uv` 作为包管理和 workspace 工具（`uv workspace`）
- 根 `pyproject.toml` 定义 workspace members
- 各子项目独立 `pyproject.toml`，统一版本策略

**运行方式：**
- `03-data-scraper`: 常驻服务（`uvicorn app:app --reload`）
- `01-ai-table`: 可单次执行或常驻 watcher 模式
- `04-agent`: 常驻 Bot 服务
- `02-rpa`: 被影刀调用的脚本集，不常驻

---

## 01-ai-table: AI 表格搭建

### 功能
- 支持钉钉电子表格 API 和飞书电子表格 API
- 通过环境变量 `SPREADSHEET_PLATFORM=dingtalk|feishu` 选择平台
- 建表（自定义字段模板：文本、数字、日期、单选）
- 行 CRUD（增删改查，支持条件过滤）
- AI 文本处理：调百炼 API 做文本分类/情感分析，结果回写字段
- 数据变更监听（轮询），通过钉钉/飞书群机器人 Webhook 推送通知

### 配置（pydantic-settings）
```python
class DingTalkSettings(BaseSettings):
    app_key: str
    app_secret: str
    webhook_url: str
    webhook_sign_key: str | None = None  # 签名密钥

class FeishuSettings(BaseSettings):
    app_id: str
    app_secret: str
    webhook_url: str

class BaiLianSettings(BaseSettings):
    api_key: str
    model: str = "qwen-plus"

class Settings(BaseSettings):
    platform: str = "dingtalk"
    dingtalk: DingTalkSettings = Field(default_factory=DingTalkSettings)
    feishu: FeishuSettings = Field(default_factory=FeishuSettings)
    bailian: BaiLianSettings = Field(default_factory=BaiLianSettings)
    spreadsheet_token: str
    watcher_poll_interval: int = 30
    notify_columns: list[str] = []
```

### 依赖
`httpx`、`pydantic-settings`、`pyyaml`（仅用于表格模板）

---

## 02-rpa: 影刀 RPA

### 设计思路
- **Python 层**（`processors/`） — 纯 Python 脚本，可独立运行
  - `base.py` — 数据处理基类，定义 `process(input) -> output` 接口
  - `web_scraper.py` — 清洗网页采集数据（去重、字段标准化、空值处理）
  - `report_export.py` — 解析报表数据（日期格式化、金额计算、汇总统计）
  - `utils/encrypt.py` — 加密参数解析（AES/Base64，密钥从环境变量读取）
- **影刀端** — 只负责浏览器操作（登录、点击、导出）
  - 通过"执行 Python 代码块"节点调用 `processors/` 中的脚本

### 调用流程
```
影刀: 登录 → 导出CSV → 执行 Python 脚本 → 清洗数据 → 写回 DB/表格
```

### 加密参数处理
- 密钥不硬编码，从环境变量 `RPA_ENCRYPT_KEY` 读取
- 使用 AES-GCM 模式，IV 随机生成并附加在密文头部
- Base64 编码传输

### 依赖
`pandas`、`openpyxl`、`cryptography`

---

## 03-data-scraper: 数据抓取服务

### 认证
- API Key 认证：请求头 `X-API-Key: <key>`，从环境变量 `SCRAPER_API_KEY` 读取
- 无认证返回 401
- 所有写操作（POST/DELETE）必须认证，读操作（GET）可配置是否认证

### API 路由
```
GET  /health                     → 健康检查
POST /scrape/api                 → API 数据源采集
POST /scrape/csv                 → CSV 导入清洗
POST /scrape/db                  → 数据库查询采集（只读，参数化查询）
POST /scrape/web                 → 高级网页抓取
GET  /scrape/jobs/{id}           → 查询任务状态
GET  /scrape/logs                → 查看日志
GET  /scrape/sources             → 查看已配置数据源
POST /scrape/sources             → 新增/更新数据源
DELETE /scrape/sources/{id}      → 删除数据源
```

### 数据源策略
- **API Source**: REST API 调用，支持分页、请求头/参数配置
- **CSV Source**: 上传影刀导出的 CSV，Pandas 清洗
- **DB Source**: 直连 MySQL/PostgreSQL/SQLite
  - **只读访问**：使用只读数据库用户连接
  - **参数化查询**：仅支持预定义查询模板，禁止任意 SQL
  - 禁止 DROP/DELETE/UPDATE/TRUNCATE 等写操作
- **Web Scraper**: 高级网页抓取
  - 简单页面：`httpx + BeautifulSoup4`（轻量快速）
  - JS 渲染页面：`playwright`（处理 SPA）
  - User-Agent 池、请求间隔随机化、代理 IP 支持
  - 深度抓取（链接发现、分页递归）
  - 预留验证码处理接口

### 统一清洗（Pandas）
- 列名 snake_case 标准化
- 空值处理（填充/删除）
- 日期格式统一 YYYY-MM-DD
- 类型转换

### 日志
- 每次抓取记录：时间、数据源、数据量、耗时、成功/失败、错误信息
- 文件日志：`logs/scrape_YYYY-MM-DD.log`

### 健康检查
- `GET /health` 返回 `{"status": "ok"}`
- 可检查数据库连接等依赖服务状态

### 依赖
`fastapi`、`uvicorn`、`httpx`、`pandas`、`sqlalchemy`、`playwright`、`beautifulsoup4`、`fake-useragent`、`python-multipart`、`pydantic-settings`

---

## 04-agent: Agent 搭建

### 核心架构（LangGraph — ReAct 模式）
```
用户消息 → [Router(意图识别)] → [Tool Call(工具执行)] → [Result(结果汇总)] → 回复
              ↑                    ↓                         ↑
              └────────────────────┴─────────────────────────┘
                        (工具调用闭环)
```

### 图状态
```python
class AgentState(TypedDict):
    messages: list[dict]          # 对话历史
    user_intent: str              # 识别的意图
    tool_name: str                # 当前调用的工具
    tool_result: Any              # 工具返回结果
    error: str | None             # 错误信息
```

### 工具层

| 工具 | 状态 | 功能 |
|------|------|------|
| `bailian_analyze` | 实现 | 百炼文本分类/情感分析 |
| `table_query` | 实现 | 查询钉钉/飞书表格 |
| `table_push` | 实现 | 推送数据到表格 |
| `web_search` | 实现 | 联网搜索 |
| `scrape_data` | 预留 | 触发抓取 — 接口定义：`POST 03-data-scraper/scrape/{type}` |
| `rpa_trigger` | 预留 | 触发 RPA — 接口定义：通过影刀 MCP Server HTTP API |

### 预留接口设计

**scrape_data → 03-data-scraper:**
```
Agent 调用: POST http://scraper:8000/scrape/{type}
  → 类型: api/csv/db/web
  → 参数: 数据源配置或任务参数
  → 返回: task_id
Agent 轮询: GET http://scraper:8000/scrape/jobs/{task_id}
  → 返回: 任务状态和结果
```

**rpa_trigger → 02-rpa:**
```
Agent 调用: POST http://localhost:port/rpa/trigger (影刀 MCP Server)
  → 参数: 脚本名称 + 输入数据
  → 返回: 执行结果
```

### OpenClaw 层（钉钉/飞书双向适配）
- `bot.py` — 统一消息接口，屏蔽平台差异（消息收发格式适配）
- `callback.py` — 群机器人回调处理（签名验证、消息解析）
- `router.py` — 消息路由（@机器人检测、指令解析）
- `skills.py` — 预定义技能（表格查询、数据推送、AI 问答）

### 交互示例
```
@机器人 分析一下最近的销售数据情感倾向
→ table_query(销售表) → bailian_analyze → 回复

@机器人 查询表格"客户管理"中状态为"待跟进"的数据
→ table_query(条件过滤) → 回复

@机器人 搜索"人工智能最新进展"
→ web_search → 回复摘要
```

### 依赖
`langgraph`、`langchain`、`httpx`、`pydantic`

---

## shared/ 公共包

### config/settings.py
统一配置加载，基于 `pydantic-settings`，支持：
- 环境变量读取
- `.env` 文件加载
- 启动时验证（缺失必填配置立即报错）

### utils/logger.py
结构化日志：
- Console handler（开发环境，可读格式）
- File handler（生产环境，JSON 格式）
- 日志级别可配置
- 自动附加 context（服务名、请求 ID）

### utils/dingtalk.py
钉钉 API 客户端：
- Access token 自动获取和刷新（提前 5 分钟刷新）
- 电子表格 CRUD 操作封装
- 群机器人 Webhook 推送（支持 HMAC-SHA256 签名）

### utils/feishu.py
飞书 API 客户端：
- Tenant access token 自动获取和刷新
- 电子表格 CRUD 操作封装
- 群机器人 Webhook 推送

### utils/bailian.py
百炼 API 客户端：
- 文本分类调用
- 情感分析调用
- 超时和重试处理（最多 3 次）

---

## 安全设计

1. **密钥管理**：所有密钥通过环境变量注入，禁止硬编码
2. **Webhook 签名**：群机器人 Webhook 使用 HMAC-SHA256 签名验证
3. **Scraper 认证**：03-data-scraper 所有写操作需要 API Key
4. **DB 只读**：03-data-scraper 数据库连接使用只读用户，仅支持参数化查询
5. **加密处理**：02-rpa 加密密钥从环境变量读取，使用 AES-GCM

---

## 测试策略

- **单元测试**：每个子项目独立 `tests/` 目录
- **API 客户端 mock**：钉钉/飞书/百炼 API 使用 httpx mock 或 unittest mock
- **Pandas 清洗逻辑**：用 sample DataFrame 验证清洗规则
- **LangGraph 测试**：模拟用户消息验证路由和工具调用链
- **测试运行**：`pytest`，覆盖率目标 > 70%

---

## 后续阶段（未实现，预留）
- 04-agent `scrape_data` 工具对接 03-data-scraper HTTP API
- 04-agent `rpa_trigger` 工具对接影刀 MCP Server
- 影刀 MCP Server 生产环境配置
- Docker 容器化部署
