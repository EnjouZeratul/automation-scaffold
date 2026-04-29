from openclaw.router import parse_message


def test_parse_mention():
    result = parse_message("@机器人 查询表格")
    assert result["is_mention"] is True
    assert result["content"] == "查询表格"


def test_parse_plain():
    result = parse_message("普通消息")
    assert result["is_mention"] is False
    assert result["content"] == "普通消息"
