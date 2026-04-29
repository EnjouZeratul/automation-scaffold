from shared.utils.logger import setup_logger


def test_setup_logger(capsys):
    logger = setup_logger("test-logger", level="DEBUG")
    logger.info("hello")
    captured = capsys.readouterr()
    assert "hello" in captured.out
