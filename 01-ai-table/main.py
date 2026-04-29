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
