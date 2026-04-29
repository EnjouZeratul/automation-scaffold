# shared 公共包

各子系统共享的基础组件。

## 模块一览

| 模块 | 说明 |
|------|------|
| `config/settings.py` | pydantic-settings 统一配置（钉钉/飞书/百炼） |
| `utils/dingtalk.py` | 钉钉 API 客户端（Token 自动刷新，提前 300s） |
| `utils/feishu.py` | 飞书 API 客户端（tenant_access_token） |
| `utils/bailian.py` | 百炼 AI 客户端（文本分类/情感分析） |
| `utils/logger.py` | 统一日志 setup_logger(name, level, log_file) |

## 使用示例

```python
from shared.config.settings import Settings
from shared.utils.dingtalk import DingTalkClient

settings = Settings()
client = DingTalkClient(settings.dingtalk)
token = await client.get_access_token()
```

## 测试

```bash
cd D:/TA/automation-scaffold
python -m pytest shared/tests/ -v
```

## 环境变量

| 变量 | 说明 |
|------|------|
| `DINGTALK_APP_KEY` | 钉钉应用 Key |
| `DINGTALK_APP_SECRET` | 钉钉应用 Secret |
| `DINGTALK_WEBHOOK_URL` | 钉钉群机器人 Webhook |
| `FEISHU_APP_ID` | 飞书应用 ID |
| `FEISHU_APP_SECRET` | 飞书应用 Secret |
| `FEISHU_WEBHOOK_URL` | 飞书群机器人 Webhook |
| `DASHSCOPE_API_KEY` | 百炼 API Key |
| `DASHSCOPE_BASE_URL` | 百炼 API 地址 |
| `DASHSCOPE_MODEL` | 百炼模型名 |
