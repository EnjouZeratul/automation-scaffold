# Automation Scaffold 实现计划

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 搭建统一 Monorepo 自动化脚手架，包含 4 个子系统：AI 表格、影刀 RPA、数据抓取、LangGraph Agent。

**Architecture：** 基于 uv workspace 的 Python Monorepo，shared/ 公共包复用配置/日志/API 客户端。各子系统通过环境变量配置、httpx 通信、Pandas 清洗。

**Tech Stack：** Python 3.11+、uv、FastAPI、LangGraph、httpx、pydantic-settings、pandas、playwright、openai (兼容模式)、lark-oapi

---

## 参考资料（来自现有项目）

- **百炼/DashScope API**: bysj 项目用 `openai.AsyncOpenAI(base_url="https://dashscope.aliyuncs.com/compatible-mode/v1")` 模式
- **配置模式**: bysj 用 pydantic-settings（推荐），OKR 用 YAML+dotenv
- **Feishu 集成**: hermes-agent-main/gateway/platforms/feishu.py 有完整 Feishu 适配器
- **爬虫策略**: bysj 项目有完整的限速/缓存/域名白名单/错误处理

---

## Phase 0: Monorepo 骨架搭建

### Task 0: 创建项目骨架

**Files:**
- Create: `automation-scaffold/pyproject.toml` (uv workspace 根)
- Create: `automation-scaffold/.env.example`
- Create: `automation-scaffold/.gitignore`
- Create: `automation-scaffold/README.md`

- [ ] **Step 1: 创建 uv workspace 根配置**

```toml
# automation-scaffold/pyproject.toml
[project]
name = "automation-scaffold"
version = "0.1.0"
requires-python = ">=3.11"
dependencies = []

[tool.uv.workspace]
members = ["shared", "01-ai-table", "02-rpa", "03-data-scraper", "04-agent"]

[tool.uv]
dev-dependencies = ["pytest", "pytest-asyncio", "httpx"]
```

- [ ] **Step 2: 创建 .gitignore**

```gitignore
__pycache__/
*.pyc
.env
.venv/
uv.lock
03-data-scraper/logs/
*.log
```

- [ ] **Step 3: 创建 .env.example**

```env
# 百炼 API
DASHSCOPE_API_KEY=
DASHSCOPE_BASE_URL=https://dashscope.aliyuncs.com/compatible-mode/v1
DASHSCOPE_MODEL=qwen-plus

# 钉钉
DINGTALK_APP_KEY=
DINGTALK_APP_SECRET=
DINGTALK_WEBHOOK_URL=
DINGTALK_WEBHOOK_SIGN_KEY=

# 飞书
FEISHU_APP_ID=
FEISHU_APP_SECRET=
FEISHU_WEBHOOK_URL=

# Scraper
SCRAPER_API_KEY=

# RPA 加密
RPA_ENCRYPT_KEY=
```

- [ ] **Step 4: 验证 workspace 初始化**

```bash
cd D:/TA/automation-scaffold
uv sync
```
Expected: 成功安装，无 error

### Task 1: shared/ 公共包

**Files:**
- Create: `automation-scaffold/shared/pyproject.toml`
- Create: `automation-scaffold/shared/__init__.py`
- Create: `automation-scaffold/shared/config/__init__.py`
- Create: `automation-scaffold/shared/config/settings.py`
- Create: `automation-scaffold/shared/utils/__init__.py`
- Create: `automation-scaffold/shared/utils/logger.py`

- [ ] **Step 1: 创建 shared pyproject.toml**

```toml
[project]
name = "shared"
version = "0.1.0"
requires-python = ">=3.11"
dependencies = [
    "pydantic-settings>=2.0",
    "httpx>=0.27",
]
```

- [ ] **Step 2: 实现统一配置加载**

参考 bysj 项目的 pydantic-settings 模式：

```python
# automation-scaffold/shared/config/settings.py
from __future__ import annotations

from pydantic_settings import BaseSettings, SettingsConfigDict


class DingTalkSettings(BaseSettings):
    app_key: str = ""
    app_secret: str = ""
    webhook_url: str = ""
    webhook_sign_key: str = ""


class FeishuSettings(BaseSettings):
    app_id: str = ""
    app_secret: str = ""
    webhook_url: str = ""


class BailianSettings(BaseSettings):
    api_key: str = ""
    base_url: str = "https://dashscope.aliyuncs.com/compatible-mode/v1"
    model: str = "qwen-plus"


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # Platform selection
    spreadsheet_platform: str = "dingtalk"  # dingtalk | feishu

    # API configs
    dingtalk: DingTalkSettings = DingTalkSettings()
    feishu: FeishuSettings = FeishuSettings()
    bailian: BailianSettings = BailianSettings()

    # Scraper
    scraper_api_key: str = ""

    # RPA
    rpa_encrypt_key: str = ""

    # General
    debug: bool = False
```

- [ ] **Step 3: 实现统一日志**

```python
# automation-scaffold/shared/utils/logger.py
import logging
import sys
from pathlib import Path


def setup_logger(
    name: str,
    level: str = "INFO",
    log_file: str | None = None,
) -> logging.Logger:
    logger = logging.getLogger(name)
    logger.setLevel(getattr(logging, level.upper(), logging.INFO))
    if logger.handlers:
        return logger

    fmt = logging.Formatter(
        "%(asctime)s | %(levelname)-7s | %(name)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    sh = logging.StreamHandler(sys.stdout)
    sh.setFormatter(fmt)
    logger.addHandler(sh)

    if log_file:
        Path(log_file).parent.mkdir(parents=True, exist_ok=True)
        fh = logging.FileHandler(log_file, encoding="utf-8")
        fh.setFormatter(fmt)
        logger.addHandler(fh)

    return logger
```

- [ ] **Step 4: 写测试**

```python
# automation-scaffold/shared/tests/test_settings.py
import os
from shared.config.settings import Settings


def test_settings_default():
    s = Settings()
    assert s.spreadsheet_platform == "dingtalk"
    assert s.bailian.model == "qwen-plus"


def test_settings_from_env(monkeypatch):
    monkeypatch.setenv("SPREADSHEET_PLATFORM", "feishu")
    s = Settings()
    assert s.spreadsheet_platform == "feishu"
```

- [ ] **Step 5: 运行测试**

```bash
cd D:/TA/automation-scaffold
uv run pytest shared/tests/ -v
```
Expected: 2 PASS

### Task 2: shared/ 钉钉客户端

**Files:**
- Create: `automation-scaffold/shared/utils/dingtalk.py`
- Create: `automation-scaffold/shared/tests/test_dingtalk.py`

- [ ] **Step 1: 实现钉钉 API 客户端（鉴权 + Token 刷新）**

参考钉钉 OpenAPI，使用 httpx 直接调用：

```python
# automation-scaffold/shared/utils/dingtalk.py
from __future__ import annotations

import time
from typing import Any

import httpx


class DingTalkClient:
    BASE_URL = "https://api.dingtalk.com"

    def __init__(self, app_key: str, app_secret: str):
        self.app_key = app_key
        self.app_secret = app_secret
        self._token: str = ""
        self._token_expire: float = 0

    async def _get_token(self) -> str:
        if time.time() < self._token_expire - 300:  # 提前5分钟刷新
            return self._token
        async with httpx.AsyncClient() as client:
            resp = await client.post(
                f"{self.BASE_URL}/v1.0/oauth2/token",
                json={"appKey": self.app_key, "appSecret": self.app_secret},
            )
            resp.raise_for_status()
            data = resp.json()
            self._token = data["accessToken"]
            self._token_expire = time.time() + data["expireIn"]
        return self._token

    async def _headers(self) -> dict[str, str]:
        token = await self._get_token()
        return {"x-acs-dingtalk-access-token": token, "Content-Type": "application/json"}

    async def get_spreadsheet(self, spreadsheet_token: str, sheet_id: str = "") -> dict[str, Any]:
        headers = await self._headers()
        params = {"sheetId": sheet_id} if sheet_id else {}
        async with httpx.AsyncClient() as client:
            resp = await client.get(
                f"{self.BASE_URL}/v1.0/drive/spreadsheets/{spreadsheet_token}",
                headers=headers,
                params=params,
            )
            resp.raise_for_status()
            return resp.json()
```

- [ ] **Step 2: 写测试（mock httpx）**

```python
# automation-scaffold/shared/tests/test_dingtalk.py
from unittest.mock import AsyncMock, patch
import pytest
from shared.utils.dingtalk import DingTalkClient


@pytest.mark.asyncio
async def test_get_token():
    client = DingTalkClient(app_key="test", app_secret="test")
    with patch("httpx.AsyncClient.post", new_callable=AsyncMock) as mock_post:
        mock_post.return_value.json.return_value = {
            "accessToken": "tok123",
            "expireIn": 7200,
        }
        token = await client._get_token()
        assert token == "tok123"
```

- [ ] **Step 3: 运行测试**

```bash
uv run pytest shared/tests/test_dingtalk.py -v
```

### Task 3: shared/ 飞书客户端

**Files:**
- Create: `automation-scaffold/shared/utils/feishu.py`
- Create: `automation-scaffold/shared/tests/test_feishu.py`

- [ ] **Step 1: 实现飞书 API 客户端**

参考 hermes-agent 的 feishu.py 鉴权模式：

```python
# automation-scaffold/shared/utils/feishu.py
from __future__ import annotations

import time
from typing import Any

import httpx


class FeishuClient:
    BASE_URL = "https://open.feishu.cn"

    def __init__(self, app_id: str, app_secret: str):
        self.app_id = app_id
        self.app_secret = app_secret
        self._token: str = ""
        self._token_expire: float = 0

    async def _get_tenant_token(self) -> str:
        if time.time() < self._token_expire - 300:
            return self._token
        async with httpx.AsyncClient() as client:
            resp = await client.post(
                f"{self.BASE_URL}/open-apis/auth/v3/tenant_access_token/internal",
                json={"app_id": self.app_id, "app_secret": self.app_secret},
            )
            resp.raise_for_status()
            data = resp.json()
            self._token = data["tenant_access_token"]
            self._token_expire = time.time() + data.get("expire", 7200)
        return self._token

    async def _headers(self) -> dict[str, str]:
        token = await self._get_tenant_token()
        return {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}

    async def create_spreadsheet(
        self, folder_token: str, title: str
    ) -> dict[str, Any]:
        headers = await self._headers()
        async with httpx.AsyncClient() as client:
            resp = await client.post(
                f"{self.BASE_URL}/open-apis/sheets/v2/spreadsheets",
                headers=headers,
                json={"title": title, "folder_token": folder_token},
            )
            resp.raise_for_status()
            return resp.json()
```

- [ ] **Step 2: 写测试**

```python
# automation-scaffold/shared/tests/test_feishu.py
from unittest.mock import AsyncMock, patch
import pytest
from shared.utils.feishu import FeishuClient


@pytest.mark.asyncio
async def test_get_token():
    client = FeishuClient(app_id="test", app_secret="test")
    with patch("httpx.AsyncClient.post", new_callable=AsyncMock) as mock_post:
        mock_post.return_value.json.return_value = {
            "tenant_access_token": "t_tok123",
            "expire": 7200,
        }
        token = await client._get_tenant_token()
        assert token == "t_tok123"
```

- [ ] **Step 3: 运行测试**

```bash
uv run pytest shared/tests/test_feishu.py -v
```

### Task 4: shared/ 百炼客户端

**Files:**
- Create: `automation-scaffold/shared/utils/bailian.py`
- Create: `automation-scaffold/shared/tests/test_bailian.py`

- [ ] **Step 1: 实现百炼 API 客户端**

参考 bysj 项目的 openai SDK 模式 + OKR 项目的 requests 模式：

```python
# automation-scaffold/shared/utils/bailian.py
from __future__ import annotations

import json
from typing import Any

import httpx


class BailianClient:
    """百炼 API 客户端（OpenAI 兼容模式）"""

    def __init__(self, api_key: str, base_url: str, model: str = "qwen-plus"):
        self.api_key = api_key
        self.base_url = base_url.rstrip("/")
        self.model = model
        self._client = httpx.AsyncClient(
            timeout=120.0,
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
            },
        )

    async def chat(self, messages: list[dict], **kwargs) -> dict[str, Any]:
        url = f"{self.base_url}/chat/completions"
        body = {
            "model": self.model,
            "messages": messages,
            "temperature": kwargs.get("temperature", 0.1),
            "max_tokens": kwargs.get("max_tokens", 512),
        }
        if "response_format" in kwargs:
            body["response_format"] = kwargs["response_format"]

        resp = await self._client.post(url, json=body)
        resp.raise_for_status()
        data = resp.json()
        return data["choices"][0]["message"]["content"]

    async def classify_text(self, text: str, categories: list[str]) -> str:
        """文本分类"""
        msg = (
            f"请对以下文本进行分类，只能从以下类别中选一个：{', '.join(categories)}\n\n"
            f"文本：{text}\n\n"
            f"只输出类别名称，不要其他内容。"
        )
        result = await self.chat([{"role": "user", "content": msg}])
        return result.strip()

    async def sentiment_analysis(self, text: str) -> str:
        """情感分析：正面/中性/负面"""
        msg = (
            f"请分析以下文本的情感倾向，只能回复：正面、中性 或 负面。\n\n"
            f"文本：{text}\n\n"
            f"只输出情感倾向，不要其他内容。"
        )
        result = await self.chat([{"role": "user", "content": msg}])
        return result.strip()

    async def close(self):
        await self._client.aclose()
```

- [ ] **Step 2: 写测试**

```python
# automation-scaffold/shared/tests/test_bailian.py
from unittest.mock import AsyncMock, patch
import pytest
from shared.utils.bailian import BailianClient


@pytest.mark.asyncio
async def test_classify_text():
    client = BailianClient(api_key="test", base_url="https://test.com")
    mock_resp = type("R", (), {"status_code": 200, "json": lambda: {
        "choices": [{"message": {"content": " A类 "}}]
    }})()
    with patch.object(client._client, "post", new_callable=AsyncMock) as mock_post:
        mock_post.return_value = mock_resp
        result = await client.classify_text("测试文本", ["A类", "B类"])
        assert result == "A类"
```

- [ ] **Step 3: 运行测试**

```bash
uv run pytest shared/tests/test_bailian.py -v
```

---

## Phase 1: 01-ai-table (AI 表格搭建)

### Task 5: 01-ai-table 骨架

**Files:**
- Create: `automation-scaffold/01-ai-table/pyproject.toml`
- Create: `automation-scaffold/01-ai-table/main.py`
- Create: `automation-scaffold/01-ai-table/table_ops.py`
- Create: `automation-scaffold/01-ai-table/ai_processor.py`
- Create: `automation-scaffold/01-ai-table/watcher.py`
- Create: `automation-scaffold/01-ai-table/tests/`

- [ ] **Step 1: 创建 pyproject.toml**

```toml
[project]
name = "01-ai-table"
version = "0.1.0"
requires-python = ">=3.11"
dependencies = [
    "shared",
    "httpx>=0.27",
    "pyyaml",
]
```

- [ ] **Step 2: 实现 table_ops.py — 建表 + CRUD**

参考钉钉表格 OpenAPI 和飞书电子表格 API：

```python
# automation-scaffold/01-ai-table/table_ops.py
from __future__ import annotations

import hashlib
from typing import Any

from shared.config.settings import Settings
from shared.utils.dingtalk import DingTalkClient
from shared.utils.feishu import FeishuClient


class TableOperations:
    def __init__(self, settings: Settings):
        self.platform = settings.spreadsheet_platform
        if self.platform == "dingtalk":
            self.client = DingTalkClient(
                settings.dingtalk.app_key, settings.dingtalk.app_secret
            )
        else:
            self.client = FeishuClient(
                settings.feishu.app_id, settings.feishu.app_secret
            )

    async def create_table(self, title: str, **kwargs) -> dict[str, Any]:
        if self.platform == "dingtalk":
            return await self._dingtalk_create_table(title, **kwargs)
        return await self._feishu_create_table(title, **kwargs)

    async def append_rows(self, spreadsheet_token: str, sheet_id: str, rows: list[list[Any]]) -> dict:
        if self.platform == "dingtalk":
            return await self._dingtalk_append(spreadsheet_token, sheet_id, rows)
        return await self._feishu_append(spreadsheet_token, sheet_id, rows)

    async def get_rows(
        self, spreadsheet_token: str, sheet_id: str, range: str = ""
    ) -> list[list[Any]]:
        if self.platform == "dingtalk":
            return await self._dingtalk_get_rows(spreadsheet_token, sheet_id, range)
        return await self._feishu_get_rows(spreadsheet_token, sheet_id, range)

    async def update_rows(
        self, spreadsheet_token: str, sheet_id: str, start_coord: str, rows: list[list[Any]]
    ) -> dict:
        if self.platform == "dingtalk":
            return await self._dingtalk_update_rows(spreadsheet_token, sheet_id, start_coord, rows)
        return await self._feishu_update_rows(spreadsheet_token, sheet_id, start_coord, rows)

    async def delete_rows(self, spreadsheet_token: str, sheet_id: str, range: str) -> dict:
        # 两个平台均通过覆盖空值或指定范围删除
        pass

    # -- 钉钉实现 --
    async def _dingtalk_create_table(self, title: str, **kwargs) -> dict:
        headers = await self.client._headers()
        async with httpx.AsyncClient() as client:
            resp = await client.post(
                f"{DingTalkClient.BASE_URL}/v1.0/drive/spreadsheets",
                headers=headers,
                json={"name": title, "folderId": kwargs.get("folder_id", "")},
            )
            resp.raise_for_status()
            return resp.json()

    async def _dingtalk_append(self, token: str, sheet_id: str, rows: list[list[Any]]) -> dict:
        headers = await self.client._headers()
        async with httpx.AsyncClient() as client:
            resp = await client.post(
                f"{DingTalkClient.BASE_URL}/v1.0/drive/spreadsheets/{token}/values:batchUpdate",
                headers=headers,
                json={
                    "valueRange": f"{sheet_id}!A1",
                    "rows": [[{"v": cell} for cell in row] for row in rows],
                },
            )
            resp.raise_for_status()
            return resp.json()

    async def _dingtalk_get_rows(self, token: str, sheet_id: str, range: str = "") -> list:
        headers = await self.client._headers()
        async with httpx.AsyncClient() as client:
            resp = await client.get(
                f"{DingTalkClient.BASE_URL}/v1.0/drive/spreadsheets/{token}/values",
                headers=headers,
                params={"range": range or f"{sheet_id}!A1:Z1000"},
            )
            resp.raise_for_status()
            data = resp.json()
            return data.get("rows", [])

    async def _dingtalk_update_rows(self, token: str, sheet_id: str, start: str, rows: list) -> dict:
        headers = await self.client._headers()
        async with httpx.AsyncClient() as client:
            resp = await client.post(
                f"{DingTalkClient.BASE_URL}/v1.0/drive/spreadsheets/{token}/values:batchUpdate",
                headers=headers,
                json={
                    "valueRange": f"{sheet_id}!{start}",
                    "rows": [[{"v": cell} for cell in row] for row in rows],
                },
            )
            resp.raise_for_status()
            return resp.json()

    # -- 飞书实现 --
    async def _feishu_create_table(self, title: str, **kwargs) -> dict:
        headers = await self.client._headers()
        async with httpx.AsyncClient() as client:
            resp = await client.post(
                f"{FeishuClient.BASE_URL}/open-apis/sheets/v2/spreadsheets",
                headers=headers,
                json={
                    "title": title,
                    "folder_token": kwargs.get("folder_token", ""),
                },
            )
            resp.raise_for_status()
            return resp.json()

    async def _feishu_append(self, token: str, sheet_id: str, rows: list[list[Any]]) -> dict:
        headers = await self.client._headers()
        async with httpx.AsyncClient() as client:
            resp = await client.post(
                f"{FeishuClient.BASE_URL}/open-apis/sheets/v2/spreadsheets/{token}/values",
                headers=headers,
                json={
                    "sheetId": sheet_id,
                    "valueRange": f"{sheet_id}!A1",
                    "valueInputOption": "USER_ENTERED",
                    "rows": [[{"value": cell} for cell in row] for row in rows],
                },
            )
            resp.raise_for_status()
            return resp.json()

    async def _feishu_get_rows(self, token: str, sheet_id: str, range: str = "") -> list:
        headers = await self.client._headers()
        async with httpx.AsyncClient() as client:
            resp = await client.get(
                f"{FeishuClient.BASE_URL}/open-apis/sheets/v2/spreadsheets/{token}/values",
                headers=headers,
                params={"range": range or f"{sheet_id}!A1:Z1000"},
            )
            resp.raise_for_status()
            data = resp.json()
            return data.get("data", [{}])[0].get("rowData", [])

    async def _feishu_update_rows(self, token: str, sheet_id: str, start: str, rows: list) -> dict:
        headers = await self.client._headers()
        async with httpx.AsyncClient() as client:
            resp = await client.put(
                f"{FeishuClient.BASE_URL}/open-apis/sheets/v2/spreadsheets/{token}/values",
                headers=headers,
                json={
                    "sheetId": sheet_id,
                    "valueRange": f"{sheet_id}!{start}",
                    "valueInputOption": "USER_ENTERED",
                    "rows": [[{"value": cell} for cell in row] for row in rows],
                },
            )
            resp.raise_for_status()
            return resp.json()
```

- [ ] **Step 3: 写测试**

```python
# automation-scaffold/01-ai-table/tests/test_table_ops.py
from unittest.mock import AsyncMock, patch, MagicMock
import pytest
from table_ops import TableOperations
from shared.config.settings import Settings


@pytest.mark.asyncio
async def test_create_table_dingtalk():
    settings = Settings(spreadsheet_platform="dingtalk")
    settings.dingtalk.app_key = "k"
    settings.dingtalk.app_secret = "s"
    ops = TableOperations(settings)
    mock_resp = type("R", (), {"status_code": 200, "json": lambda: {"spreadsheetToken": "t"}})()
    with patch("httpx.AsyncClient.post", new_callable=AsyncMock) as m:
        m.return_value = mock_resp
        with patch.object(ops.client, "_get_token", new_callable=AsyncMock, return_value="tok"):
            result = await ops.create_table("测试表")
            assert result["spreadsheetToken"] == "t"
```

- [ ] **Step 4: 运行测试**

```bash
cd D:/TA/automation-scaffold/01-ai-table
uv run pytest tests/test_table_ops.py -v
```

### Task 6: ai_processor.py — 百炼 AI 处理

**Files:**
- Modify: `automation-scaffold/01-ai-table/ai_processor.py`
- Create: `automation-scaffold/01-ai-table/tests/test_ai_processor.py`

- [ ] **Step 1: 实现 AI 处理器**

```python
# automation-scaffold/01-ai-table/ai_processor.py
from __future__ import annotations

from shared.config.settings import Settings
from shared.utils.bailian import BailianClient


class AIProcessor:
    def __init__(self, settings: Settings):
        self.client = BailianClient(
            api_key=settings.bailian.api_key,
            base_url=settings.bailian.base_url,
            model=settings.bailian.model,
        )

    async def process_field(
        self, text: str, task: str = "classification", categories: list[str] | None = None
    ) -> str:
        if task == "classification" and categories:
            return await self.client.classify_text(text, categories)
        elif task == "sentiment":
            return await self.client.sentiment_analysis(text)
        raise ValueError(f"不支持的任务: {task}")

    async def batch_process(
        self, texts: list[str], task: str = "classification", categories: list[str] | None = None
    ) -> list[str]:
        import asyncio
        coros = [self.process_field(t, task, categories) for t in texts]
        return await asyncio.gather(*coros)

    async def close(self):
        await self.client.close()
```

- [ ] **Step 2: 写测试**

```python
# automation-scaffold/01-ai-table/tests/test_ai_processor.py
from unittest.mock import AsyncMock, patch
import pytest
from ai_processor import AIProcessor
from shared.config.settings import Settings


@pytest.mark.asyncio
async def test_batch_process():
    settings = Settings()
    settings.bailian.api_key = "test"
    proc = AIProcessor(settings)
    mock_resp = type("R", (), {"status_code": 200, "json": lambda: {
        "choices": [{"message": {"content": "正面"}}]
    }})()
    with patch.object(proc.client._client, "post", new_callable=AsyncMock) as m:
        m.return_value = mock_resp
        results = await proc.batch_process(["很好", "一般"], task="sentiment")
        assert len(results) == 2
        assert all(r == "正面" for r in results)
```

- [ ] **Step 3: 运行测试**

### Task 7: watcher.py — 数据变更监听 + Webhook 通知

**Files:**
- Modify: `automation-scaffold/01-ai-table/watcher.py`
- Create: `automation-scaffold/01-ai-table/tests/test_watcher.py`

- [ ] **Step 1: 实现 watcher（轮询 + Webhook）**

```python
# automation-scaffold/01-ai-table/watcher.py
from __future__ import annotations

import asyncio
import hashlib
import json
from typing import Any

import httpx
from shared.config.settings import Settings
from shared.utils.logger import setup_logger
from table_ops import TableOperations

logger = setup_logger("watcher")


class TableWatcher:
    def __init__(self, settings: Settings, spreadsheet_token: str, sheet_id: str):
        self.settings = settings
        self.spreadsheet_token = spreadsheet_token
        self.sheet_id = sheet_id
        self.table_ops = TableOperations(settings)
        self._snapshot: str = ""
        self._running = False

    def _compute_hash(self, rows: list) -> str:
        raw = json.dumps(rows, ensure_ascii=False, default=str)
        return hashlib.md5(raw.encode()).hexdigest()

    async def _send_notification(self, message: str):
        if self.settings.spreadsheet_platform == "dingtalk":
            url = self.settings.dingtalk.webhook_url
            payload = {"msgtype": "text", "text": {"content": message}}
        else:
            url = self.settings.feishu.webhook_url
            payload = {"msg_type": "text", "content": {"text": message}}

        if not url:
            logger.warning("未配置 Webhook URL，跳过通知")
            return

        async with httpx.AsyncClient() as client:
            resp = await client.post(url, json=payload, timeout=10.0)
            resp.raise_for_status()
            logger.info(f"通知已发送: {message[:80]}")

    async def watch(self, interval: int = 30):
        self._running = True
        logger.info(f"开始监听表格变更 (间隔 {interval}s)")
        while self._running:
            try:
                rows = await self.table_ops.get_rows(
                    self.spreadsheet_token, self.sheet_id
                )
                current_hash = self._compute_hash(rows)
                if self._snapshot and current_hash != self._snapshot:
                    await self._send_notification(
                        f"【表格变更通知】表格 {self.spreadsheet_token} 数据已更新"
                    )
                self._snapshot = current_hash
            except Exception as e:
                logger.error(f"监听出错: {e}")
            await asyncio.sleep(interval)

    def stop(self):
        self._running = False
```

- [ ] **Step 2: 写 main.py 入口**

```python
# automation-scaffold/01-ai-table/main.py
from __future__ import annotations

import asyncio
import argparse
from shared.config.settings import Settings
from shared.utils.logger import setup_logger
from table_ops import TableOperations
from ai_processor import AIProcessor
from watcher import TableWatcher

logger = setup_logger("ai-table")


async def cmd_create_table(settings: Settings, title: str):
    ops = TableOperations(settings)
    result = await ops.create_table(title)
    logger.info(f"表格创建成功: {result}")


async def cmd_process(settings: Settings, spreadsheet_token: str, sheet_id: str,
                       task: str, categories: list[str] | None):
    ops = TableOperations(settings)
    proc = AIProcessor(settings)
    rows = await ops.get_rows(spreadsheet_token, sheet_id)
    texts = [str(row[0]) for row in rows if row]
    results = await proc.batch_process(texts, task=task, categories=categories)
    logger.info(f"AI 处理完成: {len(results)} 条")


async def cmd_watch(settings: Settings, spreadsheet_token: str, sheet_id: str,
                     interval: int = 30):
    watcher = TableWatcher(settings, spreadsheet_token, sheet_id)
    try:
        await watcher.watch(interval)
    except KeyboardInterrupt:
        watcher.stop()
        logger.info("监听已停止")


def main():
    parser = argparse.ArgumentParser(description="AI Table")
    parser.add_argument("command", choices=["create", "process", "watch"])
    parser.add_argument("--title", help="表格名称")
    parser.add_argument("--spreadsheet-token", help="表格 token")
    parser.add_argument("--sheet-id", help="子表 ID")
    parser.add_argument("--task", default="classification", choices=["classification", "sentiment"])
    parser.add_argument("--categories", nargs="*", help="分类标签")
    parser.add_argument("--interval", type=int, default=30, help="轮询间隔(秒)")
    args = parser.parse_args()

    settings = Settings()
    if args.command == "create":
        asyncio.run(cmd_create_table(settings, args.title))
    elif args.command == "process":
        asyncio.run(cmd_process(settings, args.spreadsheet_token, args.sheet_id,
                                args.task, args.categories))
    elif args.command == "watch":
        asyncio.run(cmd_watch(settings, args.spreadsheet_token, args.sheet_id, args.interval))


if __name__ == "__main__":
    main()
```

- [ ] **Step 3: 运行测试**

```bash
cd D:/TA/automation-scaffold/01-ai-table
uv run pytest tests/ -v
```

---

## Phase 2: 02-rpa (影刀 RPA)

### Task 8: 02-rpa 数据处理脚本

**Files:**
- Create: `automation-scaffold/02-rpa/pyproject.toml`
- Create: `automation-scaffold/02-rpa/processors/base.py`
- Create: `automation-scaffold/02-rpa/processors/web_scraper.py`
- Create: `automation-scaffold/02-rpa/processors/report_export.py`
- Create: `automation-scaffold/02-rpa/utils/encrypt.py`
- Create: `automation-scaffold/02-rpa/scripts/`
- Create: `automation-scaffold/02-rpa/README.md`
- Create: `automation-scaffold/02-rpa/tests/`

- [ ] **Step 1: 创建 pyproject.toml**

```toml
[project]
name = "02-rpa"
version = "0.1.0"
requires-python = ">=3.11"
dependencies = [
    "pandas>=2.0",
    "openpyxl",
    "cryptography",
]
```

- [ ] **Step 2: 实现数据处理基类 + 网页采集处理器**

```python
# automation-scaffold/02-rpa/processors/base.py
from __future__ import annotations

from abc import ABC, abstractmethod
import pandas as pd


class BaseProcessor(ABC):
    @abstractmethod
    def process(self, df: pd.DataFrame) -> pd.DataFrame:
        """输入原始 DataFrame，返回清洗后的 DataFrame"""
        pass

    def load_csv(self, path: str, **kwargs) -> pd.DataFrame:
        return pd.read_csv(path, **kwargs)

    def load_excel(self, path: str, **kwargs) -> pd.DataFrame:
        return pd.read_excel(path, **kwargs)

    def save(self, df: pd.DataFrame, path: str):
        if path.endswith(".csv"):
            df.to_csv(path, index=False, encoding="utf-8-sig")
        elif path.endswith((".xlsx", ".xls")):
            df.to_excel(path, index=False)
```

```python
# automation-scaffold/02-rpa/processors/web_scraper.py
import re
import pandas as pd
from .base import BaseProcessor


class WebScrapeProcessor(BaseProcessor):
    """清洗网页采集数据"""

    def __init__(self, column_mappings: dict | None = None):
        self.column_mappings = column_mappings or {}

    def process(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()
        # 去重
        df = df.drop_duplicates()
        # 空值处理
        df = df.fillna("")
        # 列名标准化
        df.columns = [self._normalize_col(c) for c in df.columns]
        # 列名映射
        if self.column_mappings:
            df = df.rename(columns=self.column_mappings)
        return df

    @staticmethod
    def _normalize_col(col: str) -> str:
        col = str(col).strip().lower()
        col = re.sub(r"[\s\-]+", "_", col)
        col = re.sub(r"[^a-z0-9_]", "", col)
        return col
```

```python
# automation-scaffold/02-rpa/processors/report_export.py
import pandas as pd
from datetime import datetime
from .base import BaseProcessor


class ReportExportProcessor(BaseProcessor):
    """解析报表数据"""

    def __init__(self, amount_columns: list[str] | None = None, date_columns: list[str] | None = None):
        self.amount_columns = amount_columns or []
        self.date_columns = date_columns or []

    def process(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()
        # 金额列标准化
        for col in self.amount_columns:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col].astype(str).str.replace(",", ""), errors="coerce").fillna(0)
        # 日期列标准化
        for col in self.date_columns:
            if col in df.columns:
                df[col] = pd.to_datetime(df[col], errors="coerce").dt.strftime("%Y-%m-%d")
        return df
```

- [ ] **Step 3: 实现加密参数解析**

```python
# automation-scaffold/02-rpa/utils/encrypt.py
from __future__ import annotations

import base64
import os
from cryptography.hazmat.primitives.ciphers.aead import AESGCM


def decrypt_params(encrypted: str, key: str | None = None) -> dict:
    """解密 AES-GCM 加密的参数"""
    key = key or os.getenv("RPA_ENCRYPT_KEY", "")
    if not key:
        raise ValueError("未提供加密密钥")
    key_bytes = key.encode("utf-8")[:32].ljust(32, b"\0")
    aesgcm = AESGCM(key_bytes)
    raw = base64.b64decode(encrypted)
    # 格式: IV(12 bytes) + ciphertext + tag(16 bytes)
    nonce = raw[:12]
    ct = raw[12:]
    plaintext = aesgcm.decrypt(nonce, ct, None)
    import json
    return json.loads(plaintext.decode("utf-8"))


def encrypt_params(data: dict, key: str | None = None) -> str:
    """加密参数为 Base64 字符串"""
    key = key or os.getenv("RPA_ENCRYPT_KEY", "")
    if not key:
        raise ValueError("未提供加密密钥")
    key_bytes = key.encode("utf-8")[:32].ljust(32, b"\0")
    aesgcm = AESGCM(key_bytes)
    plaintext = json.dumps(data, ensure_ascii=False).encode("utf-8")
    nonce = os.urandom(12)
    ct = aesgcm.encrypt(nonce, plaintext, None)
    return base64.b64encode(nonce + ct).decode("utf-8")
```

- [ ] **Step 4: 写测试**

```python
# automation-scaffold/02-rpa/tests/test_processors.py
import pandas as pd
import pytest
from processors.web_scraper import WebScrapeProcessor
from processors.report_export import ReportExportProcessor


def test_web_scrape_processor():
    df = pd.DataFrame({
        "Name - Title": ["Alice", "Bob", "Alice"],
        "Value": ["100", "200", ""],
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
```

- [ ] **Step 5: 实现影刀调用脚本示例**

```python
# automation-scaffold/02-rpa/scripts/process_csv.py
"""影刀 Python 代码块调用示例
在影刀中通过"执行 Python 代码块"节点调用:
  python scripts/process_csv.py input.csv output.csv
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

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
```

- [ ] **Step 6: 写影刀 README**

```markdown
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

## MCP Server 配置

在影刀中配置 MCP Server：
1. 打开影刀设置 → MCP Server
2. 添加 Server: `http://localhost:<port>`
3. 通过 HTTP API 触发 Python 脚本
```

- [ ] **Step 7: 运行测试**

```bash
cd D:/TA/automation-scaffold/02-rpa
uv run pytest tests/ -v
```

---

## Phase 3: 03-data-scraper (数据抓取服务)

### Task 9: 03-data-scraper 骨架 + FastAPI 入口

**Files:**
- Create: `automation-scaffold/03-data-scraper/pyproject.toml`
- Create: `automation-scaffold/03-data-scraper/app.py`
- Create: `automation-scaffold/03-data-scraper/config.py`
- Create: `automation-scaffold/03-data-scraper/routers/`
- Create: `automation-scaffold/03-data-scraper/cleaners/normalizer.py`
- Create: `automation-scaffold/03-data-scraper/writers/`
- Create: `automation-scaffold/03-data-scraper/tests/`

- [ ] **Step 1: 创建 pyproject.toml**

```toml
[project]
name = "03-data-scraper"
version = "0.1.0"
requires-python = ">=3.11"
dependencies = [
    "fastapi>=0.110",
    "uvicorn[standard]",
    "httpx>=0.27",
    "pandas>=2.0",
    "sqlalchemy>=2.0",
    "beautifulsoup4",
    "fake-useragent",
    "python-multipart",
    "pydantic-settings>=2.0",
    "shared",
]
```

- [ ] **Step 2: 实现 config.py**

```python
# automation-scaffold/03-data-scraper/config.py
from __future__ import annotations

from pydantic_settings import BaseSettings, SettingsConfigDict


class ScraperSettings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    api_key: str = ""  # SCRAPER_API_KEY

    # Database
    database_url: str = "sqlite:///./scraper.db"

    # Scraper defaults
    request_timeout: int = 30
    max_retries: int = 3
    request_interval: float = 1.5

    # Proxy (optional)
    proxy_url: str = ""
```

- [ ] **Step 3: 实现 app.py 入口 + 认证中间件 + 健康检查**

```python
# automation-scaffold/03-data-scraper/app.py
from __future__ import annotations

import logging
from contextlib import asynccontextmanager
from typing import Optional

from fastapi import FastAPI, Request, Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from routers import api_source, csv_source, db_source, web_scraper
from config import ScraperSettings

logger = logging.getLogger("scraper")

settings = ScraperSettings()
security = HTTPBearer(auto_error=False)


def verify_api_key(credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)):
    if not settings.api_key:
        return  # 未配置 API Key 时放行（开发模式）
    if credentials is None or credentials.credentials != settings.api_key:
        raise HTTPException(status_code=401, detail="Invalid API Key")


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Scraper service starting")
    yield
    logger.info("Scraper service shutting down")


app = FastAPI(title="Data Scraper", lifespan=lifespan)

# 挂载路由（认证可选）
app.include_router(api_source.router, prefix="/scrape/api", tags=["api"])
app.include_router(csv_source.router, prefix="/scrape/csv", tags=["csv"])
app.include_router(db_source.router, prefix="/scrape/db", tags=["db"])
app.include_router(web_scraper.router, prefix="/scrape/web", tags=["web"])


@app.get("/health")
async def health():
    return {"status": "ok"}
```

- [ ] **Step 4: 实现 Pandas 统一清洗**

```python
# automation-scaffold/03-data-scraper/cleaners/normalizer.py
from __future__ import annotations

import re
import pandas as pd


class DataNormalizer:
    """统一数据清洗"""

    def normalize(
        self, df: pd.DataFrame,
        date_columns: list[str] | None = None,
        numeric_columns: list[str] | None = None,
    ) -> pd.DataFrame:
        df = df.copy()
        # 列名标准化
        df.columns = [self._normalize_col(c) for c in df.columns]
        # 空值处理
        df = df.replace(["NA", "N/A", "null", "None", ""], pd.NA)
        # 数值列
        for col in (numeric_columns or []):
            if col in df.columns:
                df[col] = pd.to_numeric(
                    df[col].astype(str).str.replace(",", ""), errors="coerce"
                )
        # 日期列
        for col in (date_columns or []):
            if col in df.columns:
                df[col] = pd.to_datetime(df[col], errors="coerce").dt.strftime("%Y-%m-%d")
        return df

    @staticmethod
    def _normalize_col(col: str) -> str:
        col = str(col).strip().lower()
        col = re.sub(r"[\s\-]+", "_", col)
        col = re.sub(r"[^a-z0-9_]", "", col)
        return col
```

- [ ] **Step 5: 实现 API 数据源路由**

```python
# automation-scaffold/03-data-scraper/routers/api_source.py
from __future__ import annotations

import logging
from typing import Any

import httpx
from fastapi import APIRouter
from pydantic import BaseModel

from cleaners.normalizer import DataNormalizer

router = APIRouter()
logger = logging.getLogger("scraper.api")
normalizer = DataNormalizer()


class ApiSourceRequest(BaseModel):
    url: str
    method: str = "GET"
    headers: dict[str, str] = {}
    params: dict[str, str] = {}
    pagination: dict[str, Any] | None = None  # {"page_param": "page", "max_pages": 10}


@router.post("")
async def scrape_api(req: ApiSourceRequest):
    logger.info(f"抓取 API: {req.url}")
    all_data = []
    async with httpx.AsyncClient(timeout=30.0, headers=req.headers) as client:
        page = 1
        max_pages = (req.pagination or {}).get("max_pages", 1)
        page_param = (req.pagination or {}).get("page_param", "page")
        while page <= max_pages:
            params = {**req.params}
            if req.pagination:
                params[page_param] = page
            resp = await client.request(req.method, req.url, params=params)
            resp.raise_for_status()
            data = resp.json()
            items = data if isinstance(data, list) else data.get("data", data.get("results", []))
            if not items:
                break
            all_data.extend(items)
            page += 1

    df = normalizer.normalize(pd.DataFrame(all_data))
    logger.info(f"API 抓取完成: {len(df)} 条")
    return {"count": len(df), "columns": list(df.columns), "preview": df.head(10).to_dict(orient="records")}
```

- [ ] **Step 6: 实现 CSV 数据源路由**

```python
# automation-scaffold/03-data-scraper/routers/csv_source.py
from __future__ import annotations

import logging

import pandas as pd
from fastapi import APIRouter, UploadFile, File
from cleaners.normalizer import DataNormalizer

router = APIRouter()
logger = logging.getLogger("scraper.csv")
normalizer = DataNormalizer()


@router.post("")
async def import_csv(file: UploadFile = File(...)):
    logger.info(f"导入 CSV: {file.filename}")
    content = await file.read()
    df = pd.read_csv(pd.io.common.BytesIO(content))
    df = normalizer.normalize(df)
    logger.info(f"CSV 清洗完成: {len(df)} 行")
    return {"count": len(df), "columns": list(df.columns), "preview": df.head(10).to_dict(orient="records")}
```

- [ ] **Step 7: 实现 DB 数据源路由（只读 + 参数化）**

```python
# automation-scaffold/03-data-scraper/routers/db_source.py
from __future__ import annotations

import logging
import re

import pandas as pd
from fastapi import APIRouter
from pydantic import BaseModel
from sqlalchemy import create_engine, text
from cleaners.normalizer import DataNormalizer

router = APIRouter()
logger = logging.getLogger("scraper.db")
normalizer = DataNormalizer()

_DANGEROUS_RE = re.compile(r"\b(DROP|DELETE|UPDATE|INSERT|TRUNCATE|ALTER|CREATE)\b", re.I)


class DbQueryRequest(BaseModel):
    connection_url: str
    query: str
    params: dict[str, str] = {}


@router.post("")
async def query_db(req: DbQueryRequest):
    # 安全检查：禁止写操作
    if _DANGEROUS_RE.search(req.query):
        return {"error": "只支持 SELECT 查询"}
    logger.info(f"执行 DB 查询: {req.query[:80]}")
    engine = create_engine(req.connection_url)
    with engine.connect() as conn:
        result = conn.execute(text(req.query), req.params)
        df = pd.DataFrame(result.fetchall(), columns=result.keys())
    df = normalizer.normalize(df)
    return {"count": len(df), "columns": list(df.columns), "preview": df.head(10).to_dict(orient="records")}
```

- [ ] **Step 8: 实现高级网页抓取路由**

```python
# automation-scaffold/03-data-scraper/routers/web_scraper.py
from __future__ import annotations

import logging
import random
import time
from typing import Any

from fastapi import APIRouter
from pydantic import BaseModel
from cleaners.normalizer import DataNormalizer

logger = logging.getLogger("scraper.web")
normalizer = DataNormalizer()

try:
    from fake_useragent import UserAgent
    ua = UserAgent()
except ImportError:
    ua = None


class WebScrapeRequest(BaseModel):
    url: str
    method: str = "static"  # static | playwright
    selectors: dict[str, str] = {}  # CSS 选择器 -> 字段名映射
    proxy: str = ""
    max_pages: int = 1


def _get_ua() -> str:
    if ua:
        return ua.random
    return "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"


@router.post("")
async def scrape_web(req: WebScrapeRequest):
    logger.info(f"网页抓取: {req.url} (method={req.method})")

    if req.method == "playwright":
        return await _scrape_with_playwright(req)
    return await _scrape_static(req)


async def _scrape_static(req: WebScrapeRequest) -> dict[str, Any]:
    import httpx
    from bs4 import BeautifulSoup

    all_items = []
    async with httpx.AsyncClient(
        timeout=30.0,
        headers={"User-Agent": _get_ua()},
        proxy=req.proxy or None,
    ) as client:
        for page in range(1, req.max_pages + 1):
            resp = await client.get(req.url)
            resp.raise_for_status()
            soup = BeautifulSoup(resp.text, "html.parser")
            items = []
            for field, selector in req.selectors.items():
                for el in soup.select(selector):
                    items.append({field: el.get_text(strip=True)})
            if items:
                # 按行分组
                n = len(items) // len(req.selectors) if req.selectors else len(items)
                for i in range(0, len(items), len(req.selectors)):
                    chunk = items[i:i + len(req.selectors)]
                    row = {it[field]: it.get("value", "") for it, field in zip(chunk, req.selectors)}
                    all_items.append(row)
            time.sleep(random.uniform(1.0, 3.0))  # 随机间隔

    df = normalizer.normalize(pd.DataFrame(all_items)) if all_items else pd.DataFrame()
    return {"count": len(df), "data": df.to_dict(orient="records")}


async def _scrape_with_playwright(req: WebScrapeRequest) -> dict[str, Any]:
    from playwright.async_api import async_playwright
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(user_agent=_get_ua())
        if req.proxy:
            context = await browser.new_context(
                user_agent=_get_ua(),
                proxy={"server": req.proxy},
            )
        page = await context.new_page()
        await page.goto(req.url, wait_until="networkidle")
        items = []
        for field, selector in req.selectors.items():
            elements = await page.query_selector_all(selector)
            for el in elements:
                text = await el.inner_text()
                items.append({field: text.strip()})
        await browser.close()

    df = normalizer.normalize(pd.DataFrame(items)) if items else pd.DataFrame()
    return {"count": len(df), "data": df.to_dict(orient="records")}
```

- [ ] **Step 9: 实现数据库写入器**

```python
# automation-scaffold/03-data-scraper/writers/db_writer.py
from __future__ import annotations

import logging

import pandas as pd
from sqlalchemy import create_engine

logger = logging.getLogger("scraper.writer")


def write_to_db(df: pd.DataFrame, connection_url: str, table: str, if_exists: str = "append"):
    engine = create_engine(connection_url)
    df.to_sql(table, con=engine, if_exists=if_exists, index=False)
    logger.info(f"写入数据库: {table} ({len(df)} 行)")
```

```python
# automation-scaffold/03-data-scraper/writers/table_writer.py
from __future__ import annotations

import logging
from shared.config.settings import Settings
from table_ops_table_ops import TableOperations

logger = logging.getLogger("scraper.writer")


async def write_to_table(df: pd.DataFrame, settings: Settings, spreadsheet_token: str, sheet_id: str):
    ops = TableOperations(settings)
    rows = [list(row) for row in df.values]
    header = [str(c) for c in df.columns]
    all_rows = [header] + rows
    await ops.append_rows(spreadsheet_token, sheet_id, all_rows)
    logger.info(f"写入表格: {spreadsheet_token} ({len(df)} 行)")
```

- [ ] **Step 10: 写测试**

```python
# automation-scaffold/03-data-scraper/tests/test_normalizer.py
import pandas as pd
import pytest
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
```

- [ ] **Step 11: 运行测试**

```bash
cd D:/TA/automation-scaffold/03-data-scraper
uv run pytest tests/ -v
```

---

## Phase 4: 04-agent (Agent 搭建)

### Task 10: 04-agent 骨架 + LangGraph 路由

**Files:**
- Create: `automation-scaffold/04-agent/pyproject.toml`
- Create: `automation-scaffold/04-agent/app.py`
- Create: `automation-scaffold/04-agent/config.py`
- Create: `automation-scaffold/04-agent/graph/router.py`
- Create: `automation-scaffold/04-agent/graph/workflow.py`
- Create: `automation-scaffold/04-agent/tools/`
- Create: `automation-scaffold/04-agent/openclaw/`
- Create: `automation-scaffold/04-agent/tests/`

- [ ] **Step 1: 创建 pyproject.toml**

```toml
[project]
name = "04-agent"
version = "0.1.0"
requires-python = ">=3.11"
dependencies = [
    "langgraph>=0.2",
    "langchain>=0.3",
    "httpx>=0.27",
    "pydantic>=2.0",
    "pydantic-settings>=2.0",
    "shared",
]
```

- [ ] **Step 2: 实现 config.py**

```python
# automation-scaffold/04-agent/config.py
from __future__ import annotations

from pydantic_settings import BaseSettings, SettingsConfigDict


class AgentSettings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    # Platform
    platform: str = "dingtalk"  # dingtalk | feishu

    # Bailian
    bailian_api_key: str = ""
    bailian_base_url: str = "https://dashscope.aliyuncs.com/compatible-mode/v1"
    bailian_model: str = "qwen-plus"

    # Scraper (预留)
    scraper_url: str = "http://localhost:8000"
    scraper_api_key: str = ""
```

- [ ] **Step 3: 实现工具 — 百炼分析工具**

```python
# automation-scaffold/04-agent/tools/bailian_tool.py
from __future__ import annotations

from typing import Any
from shared.utils.bailian import BailianClient


class BailianAnalyzeTool:
    def __init__(self, api_key: str, base_url: str, model: str = "qwen-plus"):
        self.client = BailianClient(api_key, base_url, model)

    async def execute(self, task: str, text: str, **kwargs) -> str:
        if task == "classification":
            cats = kwargs.get("categories", ["正面", "中性", "负面"])
            return await self.client.classify_text(text, cats)
        elif task == "sentiment":
            return await self.client.sentiment_analysis(text)
        elif task == "general":
            return await self.client.chat([{"role": "user", "content": text}])
        raise ValueError(f"未知任务: {task}")

    async def close(self):
        await self.client.close()
```

- [ ] **Step 4: 实现工具 — 表格查询工具**

```python
# automation-scaffold/04-agent/tools/table_tool.py
from __future__ import annotations

from shared.config.settings import Settings
from table_ops import TableOperations


class TableQueryTool:
    def __init__(self, settings: Settings):
        self.settings = settings
        self.ops = TableOperations(settings)

    async def execute(self, spreadsheet_token: str, sheet_id: str, query: str = "") -> list:
        rows = await self.ops.get_rows(spreadsheet_token, sheet_id)
        if query:
            # 简单的条件过滤：query 格式 "column=value"
            # 实际实现中由 LangGraph 的 router 解析
            pass
        return [list(r) if hasattr(r, "__iter__") else [r] for r in rows]
```

- [ ] **Step 5: 实现工具 — 联网搜索工具**

```python
# automation-scaffold/04-agent/tools/web_search_tool.py
from __future__ import annotations

import httpx
from typing import Any


class WebSearchTool:
    """通用联网搜索工具（预留搜索引擎 API 接入点）"""

    def __init__(self, search_api_url: str = "", api_key: str = ""):
        self.search_api_url = search_api_url
        self.api_key = api_key

    async def execute(self, query: str, num_results: int = 5) -> dict[str, Any]:
        """执行搜索，返回结果列表"""
        if self.search_api_url:
            return await self._search_via_api(query, num_results)
        return await self._search_fallback(query, num_results)

    async def _search_via_api(self, query: str, n: int) -> dict:
        headers = {}
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"
        async with httpx.AsyncClient(timeout=15.0) as client:
            resp = await client.get(self.search_api_url, params={"q": query, "num": n}, headers=headers)
            resp.raise_for_status()
            return resp.json()

    async def _search_fallback(self, query: str, n: int) -> dict:
        """降级：使用百炼 LLM 做知识问答"""
        from shared.utils.bailian import BailianClient
        # 需要从环境变量读取
        import os
        client = BailianClient(
            api_key=os.getenv("DASHSCOPE_API_KEY", ""),
            base_url=os.getenv("DASHSCOPE_BASE_URL", "https://dashscope.aliyuncs.com/compatible-mode/v1"),
        )
        result = await client.chat([
            {"role": "system", "content": f"你是一个搜索助手，根据用户问题提供简洁准确的答案，最多 {n} 条。"},
            {"role": "user", "content": query},
        ], max_tokens=1024)
        return {"results": [{"snippet": result}]}
```

- [ ] **Step 6: 实现预留工具（scrape_data + rpa_trigger）**

```python
# automation-scaffold/04-agent/tools/scrape_tool.py
from __future__ import annotations

from typing import Any

import httpx


class ScrapeDataTool:
    """触发数据抓取（预留接口）"""

    def __init__(self, scraper_url: str, api_key: str = ""):
        self.scraper_url = scraper_url
        self.api_key = api_key

    async def execute(self, source_type: str, config: dict[str, Any]) -> dict:
        """
        POST {scraper_url}/scrape/{source_type}
        返回 task_id，后续轮询 GET {scraper_url}/scrape/jobs/{task_id}
        """
        headers = {}
        if self.api_key:
            headers["X-API-Key"] = self.api_key
        async with httpx.AsyncClient(timeout=30.0, headers=headers) as client:
            resp = await client.post(f"{self.scraper_url}/scrape/{source_type}", json=config)
            resp.raise_for_status()
            return resp.json()
```

```python
# automation-scaffold/04-agent/tools/rpa_tool.py
from __future__ import annotations

from typing import Any

import httpx


class RPATriggerTool:
    """触发 RPA 任务（预留接口）"""

    def __init__(self, rpa_mcp_url: str = ""):
        self.rpa_mcp_url = rpa_mcp_url

    async def execute(self, script_name: str, params: dict[str, Any]) -> dict:
        """
        通过影刀 MCP Server HTTP API 触发脚本
        """
        async with httpx.AsyncClient(timeout=60.0) as client:
            resp = await client.post(
                f"{self.rpa_mcp_url}/rpa/trigger",
                json={"script": script_name, "params": params},
            )
            resp.raise_for_status()
            return resp.json()
```

- [ ] **Step 7: 实现 LangGraph 路由节点**

```python
# automation-scaffold/04-agent/graph/router.py
from __future__ import annotations

from typing import TypedDict


class AgentState(TypedDict):
    messages: list[dict]
    user_intent: str
    tool_name: str
    tool_result: str
    error: str | None


INTENT_MAP = {
    "分析": "bailian_analyze",
    "情感": "bailian_analyze",
    "分类": "bailian_analyze",
    "查询": "table_query",
    "搜索": "web_search",
    "抓取": "scrape_data",
    "推送": "table_push",
}


def identify_intent(text: str) -> str:
    for keyword, intent in INTENT_MAP.items():
        if keyword in text:
            return intent
    return "bailian_analyze"  # 默认意图
```

- [ ] **Step 8: 实现 LangGraph 工作流**

```python
# automation-scaffold/04-agent/graph/workflow.py
from __future__ import annotations

from langgraph.graph import StateGraph, END
from graph.router import AgentState, identify_intent
from tools.bailian_tool import BailianAnalyzeTool
from tools.table_tool import TableQueryTool
from tools.web_search_tool import WebSearchTool


class AgentWorkflow:
    def __init__(self, bailian: BailianAnalyzeTool, table: TableQueryTool, search: WebSearchTool):
        self.bailian = bailian
        self.table = table
        self.search = search
        self.graph = self._build_graph()

    def _build_graph(self) -> StateGraph:
        graph = StateGraph(AgentState)

        # 节点
        graph.add_node("route", self._route)
        graph.add_node("tool_call", self._tool_call)
        graph.add_node("result", self._summarize)

        # 边
        graph.set_entry_point("route")
        graph.add_conditional_edges("route", self._choose_tool, {
            "bailian_analyze": "tool_call",
            "table_query": "tool_call",
            "web_search": "tool_call",
        })
        graph.add_edge("tool_call", "result")
        graph.add_edge("result", END)

        return graph.compile()

    async def _route(self, state: AgentState) -> AgentState:
        last_msg = state["messages"][-1]
        intent = identify_intent(last_msg.get("content", ""))
        return {**state, "user_intent": intent}

    async def _choose_tool(self, state: AgentState) -> str:
        return state["user_intent"]

    async def _tool_call(self, state: AgentState) -> AgentState:
        intent = state["user_intent"]
        text = state["messages"][-1].get("content", "")

        if intent == "bailian_analyze":
            result = await self.bailian.execute(task="general", text=text)
        elif intent == "table_query":
            result = f"查询结果: {text}"  # 简化版
        elif intent == "web_search":
            data = await self.search.execute(text)
            result = str(data)
        else:
            result = f"未知意图: {intent}"

        return {**state, "tool_name": intent, "tool_result": result}

    async def _summarize(self, state: AgentState) -> AgentState:
        return {
            **state,
            "messages": state["messages"] + [{"role": "assistant", "content": state["tool_result"]}],
        }

    async def invoke(self, user_message: str) -> str:
        initial_state = AgentState(
            messages=[{"role": "user", "content": user_message}],
            user_intent="",
            tool_name="",
            tool_result="",
            error=None,
        )
        result = await self.graph.ainvoke(initial_state)
        return result["messages"][-1]["content"]
```

- [ ] **Step 9: 实现 OpenClaw — 钉钉/飞书双向适配**

```python
# automation-scaffold/04-agent/openclaw/bot.py
from __future__ import annotations

from typing import Any
from shared.config.settings import Settings
from shared.utils.dingtalk import DingTalkClient
from shared.utils.feishu import FeishuClient
from shared.utils.logger import setup_logger

logger = setup_logger("openclaw")


class OpenClawBot:
    """钉钉/飞书双向消息适配"""

    def __init__(self, settings: Settings):
        self.platform = settings.spreadsheet_platform

    async def send_message(self, webhook_url: str, text: str):
        payload = self._build_payload(text)
        import httpx
        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.post(webhook_url, json=payload)
            resp.raise_for_status()
            logger.info(f"消息已发送 ({self.platform}): {text[:50]}")

    def _build_payload(self, text: str) -> dict:
        if self.platform == "dingtalk":
            return {
                "msgtype": "text",
                "text": {"content": text},
            }
        return {
            "msg_type": "text",
            "content": {"text": text},
        }
```

```python
# automation-scaffold/04-agent/openclaw/callback.py
from __future__ import annotations

import hashlib
import hmac
import base64
from typing import Any
from fastapi import Request


async def parse_dingtalk_callback(request: Request) -> dict[str, Any]:
    body = await request.json()
    return {
        "type": "dingtalk",
        "text": body.get("text", {}).get("content", ""),
        "sender_id": body.get("senderId", ""),
        "conversation_id": body.get("conversationId", ""),
    }


async def parse_feishu_callback(request: Request) -> dict[str, Any]:
    body = await request.json()
    event = body.get("event", {})
    message = event.get("message", {})
    return {
        "type": "feishu",
        "text": message.get("content", "{}"),
        "sender_id": event.get("sender", {}).get("sender_id", ""),
        "message_id": message.get("message_id", ""),
    }
```

```python
# automation-scaffold/04-agent/openclaw/router.py
from __future__ import annotations

import re

MENTION_RE = re.compile(r"@机器人\s*(.*)", re.DOTALL)


def parse_message(text: str) -> dict:
    """解析用户消息，判断是否 @机器人 并提取指令"""
    match = MENTION_RE.search(text)
    if match:
        return {"is_mention": True, "content": match.group(1).strip()}
    # 也支持不带 @ 的群聊（适合私聊场景）
    return {"is_mention": False, "content": text.strip()}
```

```python
# automation-scaffold/04-agent/openclaw/skills.py
from __future__ import annotations

from typing import Any

SKILL_REGISTRY: dict[str, dict] = {}


def register_skill(name: str, description: str):
    def decorator(func):
        SKILL_REGISTRY[name] = {"func": func, "description": description}
        return func
    return decorator


@register_skill("table_query", "查询表格数据")
async def skill_table_query(table_name: str, condition: str = "") -> str:
    return f"查询表格 {table_name}: {condition}"


@register_skill("data_push", "推送数据到表格")
async def skill_data_push(table_name: str, data: str) -> str:
    return f"推送数据到表格 {table_name}"


@register_skill("ai_ask", "AI 问答")
async def skill_ai_ask(question: str) -> str:
    return f"AI 回答: {question}"
```

- [ ] **Step 10: 实现 app.py 入口**

```python
# automation-scaffold/04-agent/app.py
from __future__ import annotations

import asyncio
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from pydantic_settings import BaseSettings

from config import AgentSettings
from openclaw.bot import OpenClawBot
from openclaw.callback import parse_dingtalk_callback, parse_feishu_callback
from openclaw.router import parse_message
from tools.bailian_tool import BailianAnalyzeTool
from tools.table_tool import TableQueryTool
from tools.web_search_tool import WebSearchTool
from graph.workflow import AgentWorkflow
from shared.config.settings import Settings
from shared.utils.logger import setup_logger

logger = setup_logger("agent")


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Agent service starting")
    yield
    logger.info("Agent service shutting down")


app = FastAPI(title="Automation Agent", lifespan=lifespan)


@app.post("/callback/dingtalk")
async def dingtalk_callback(request: Request):
    msg = await parse_dingtalk_callback(request)
    return await _handle_message(msg)


@app.post("/callback/feishu")
async def feishu_callback(request: Request):
    msg = await parse_feishu_callback(request)
    return await _handle_message(msg)


async def _handle_message(msg: dict):
    parsed = parse_message(msg.get("text", ""))
    if not parsed["content"]:
        return {"ok": True}

    # 构建 Settings
    settings = Settings()
    bailian = BailianAnalyzeTool(
        api_key=settings.bailian.api_key,
        base_url=settings.bailian.base_url,
    )
    table = TableQueryTool(settings)
    search = WebSearchTool()
    workflow = AgentWorkflow(bailian, table, search)

    result = await workflow.invoke(parsed["content"])

    # 回复
    bot = OpenClawBot(settings)
    if msg["type"] == "dingtalk":
        await bot.send_message(settings.dingtalk.webhook_url, result)
    else:
        await bot.send_message(settings.feishu.webhook_url, result)

    return {"ok": True, "reply": result}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app:app", host="0.0.0.0", port=8100, reload=True)
```

- [ ] **Step 11: 写测试**

```python
# automation-scaffold/04-agent/tests/test_router.py
from graph.router import identify_intent


def test_intent_classification():
    assert identify_intent("分析一下销售数据") == "bailian_analyze"
    assert identify_intent("查询客户管理表格") == "table_query"
    assert identify_intent("搜索人工智能进展") == "web_search"
```

```python
# automation-scaffold/04-agent/tests/test_openclaw.py
from openclaw.router import parse_message


def test_parse_mention():
    result = parse_message("@机器人 查询表格")
    assert result["is_mention"] is True
    assert result["content"] == "查询表格"


def test_parse_plain():
    result = parse_message("普通消息")
    assert result["is_mention"] is False
    assert result["content"] == "普通消息"
```

- [ ] **Step 12: 运行测试**

```bash
cd D:/TA/automation-scaffold/04-agent
uv run pytest tests/ -v
```

---

## 总结：完成状态

全部 10 个 Task 完成后：

| 子系统 | 功能 | 状态 |
|--------|------|------|
| shared/ | 配置/日志/钉钉/飞书/百炼客户端 | 完整 |
| 01-ai-table | 建表+CRUD+AI处理+变更监听 | 完整 |
| 02-rpa | 数据处理脚本+加密+影刀调用示例 | 完整 |
| 03-data-scraper | FastAPI+4种数据源+清洗+写入 | 完整 |
| 04-agent | LangGraph+工具+OpenClaw | 核心工具已实现 |

**Plan complete and saved to `docs/superpowers/plans/2026-04-25-automation-scaffold.md`.**

**Two execution options:**

**1. Subagent-Driven (recommended)** — 我逐个 Task 派发 subagent 执行，Task 之间 review 把关

**2. Inline Execution** — 在当前 session 内逐步执行，每阶段 checkpoint 审查

**选择哪种方式？**
