from shared.config.settings import Settings


def test_settings_default():
    s = Settings()
    assert s.spreadsheet_platform == "dingtalk"
    assert s.bailian.model == "qwen-plus"


def test_settings_from_env(monkeypatch):
    monkeypatch.setenv("SPREADSHEET_PLATFORM", "feishu")
    s = Settings()
    assert s.spreadsheet_platform == "feishu"
