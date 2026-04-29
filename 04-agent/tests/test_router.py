from graph.router import identify_intent


def test_intent_classification():
    assert identify_intent("分析一下销售数据") == "bailian_analyze"
    assert identify_intent("查询客户管理表格") == "table_query"
    assert identify_intent("搜索人工智能进展") == "web_search"
    assert identify_intent("情感分析") == "bailian_analyze"


def test_intent_fallback():
    assert identify_intent("随便说点什么") == "bailian_analyze"
