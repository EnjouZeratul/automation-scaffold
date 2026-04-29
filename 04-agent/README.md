# 04-agent Agent 搭建

LangGraph 路由 → 工具调用闭环，支持钉钉/飞书双向消息交互。

## 模块一览

| 模块 | 说明 |
|------|------|
| `graph/router.py` | Agent 状态图 + 意图识别 |
| `graph/workflow.py` | LangGraph 状态机（route → tool_call → result） |
| `tools/bailian_tool.py` | 百炼 AI 工具封装 |
| `tools/table_tool.py` | 表格查询工具封装 |
| `tools/web_search_tool.py` | 联网搜索工具 |
| `tools/scrape_tool.py` | 数据抓取工具（预留） |
| `tools/rpa_tool.py` | RPA 触发工具（预留） |
| `openclaw/bot.py` | OpenClaw 消息发送（钉钉/飞书格式适配） |
| `openclaw/callback.py` | 回调消息解析 |
| `openclaw/router.py` | @机器人消息检测 + 指令提取 |
| `openclaw/skills.py` | 预定义技能注册 |
| `app.py` | FastAPI 入口 |

## 启动与关闭

```bash
# 启动（端口 8100）
cd D:/TA/automation-scaffold/04-agent
python app.py

# 或用 uvicorn
uvicorn app:app --host 0.0.0.0 --port 8100 --reload

# 关闭（Ctrl+C 或 kill）
```

## 回调端点

| 端点 | 说明 |
|------|------|
| `POST /callback/dingtalk` | 钉钉机器人回调 |
| `POST /callback/feishu` | 飞书机器人回调 |

## 测试

```bash
cd D:/TA/automation-scaffold
python -m pytest 04-agent/tests/ -v
```

## 环境变量

需要在 `.env` 中配置 `shared/` 的所有环境变量。
