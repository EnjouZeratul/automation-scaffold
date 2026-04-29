# 01-ai-table AI 表格搭建

钉钉 + 飞书双平台电子表格 CRUD + AI 处理 + 变更监听。

## 模块一览

| 文件 | 说明 |
|------|------|
| `table_ops.py` | 双平台表格操作（建表/增/查/改） |
| `ai_processor.py` | 百炼 AI 批量处理（文本分类/情感分析） |
| `watcher.py` | 表格变更监听（轮询 + MD5 比对 + Webhook 通知） |
| `main.py` | CLI 入口 |

## 启动方式

```bash
# 建表
cd D:/TA/automation-scaffold/01-ai-table
python main.py create --title "测试表"

# AI 批量处理（情感分析）
python main.py process --spreadsheet-token <token> --sheet-id 0 \
  --task sentiment

# AI 批量处理（文本分类）
python main.py process --spreadsheet-token <token> --sheet-id 0 \
  --task classification --categories "正面" "负面" "中性"

# 监听表格变更（30 秒轮询，Ctrl+C 停止）
python main.py watch --spreadsheet-token <token> --sheet-id 0 --interval 30
```

## 测试

```bash
cd D:/TA/automation-scaffold
python -m pytest 01-ai-table/tests/ -v
```

## 环境变量

需要在 `.env` 中配置 `shared/` 的所有环境变量。
