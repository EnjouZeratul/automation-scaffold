from __future__ import annotations

from pydantic_settings import BaseSettings, SettingsConfigDict


class DingTalkSettings(BaseSettings):
    app_key: str = ""
    app_secret: str = ""
    webhook_url: str = ""
    webhook_sign_key: str = ""

    model_config = SettingsConfigDict(
        env_prefix="DINGTALK_",
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


class FeishuSettings(BaseSettings):
    app_id: str = ""
    app_secret: str = ""
    webhook_url: str = ""

    model_config = SettingsConfigDict(
        env_prefix="FEISHU_",
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


class BailianSettings(BaseSettings):
    api_key: str = ""
    base_url: str = "https://dashscope.aliyuncs.com/compatible-mode/v1"
    model: str = "qwen-plus"

    model_config = SettingsConfigDict(
        env_prefix="DASHSCOPE_",
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # Platform selection
    spreadsheet_platform: str = "dingtalk"  # dingtalk | feishu

    # Nested API configs
    dingtalk: DingTalkSettings = DingTalkSettings()
    feishu: FeishuSettings = FeishuSettings()
    bailian: BailianSettings = BailianSettings()

    # Scraper
    scraper_api_key: str = ""

    # RPA
    rpa_encrypt_key: str = ""

    # General
    debug: bool = False
