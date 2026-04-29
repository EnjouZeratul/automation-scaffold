from __future__ import annotations

from typing import TypedDict

from graph.router import AgentState, identify_intent
from tools.bailian_tool import BailianAnalyzeTool
from tools.table_tool import TableQueryTool
from tools.web_search_tool import WebSearchTool

try:
    from langgraph.graph import StateGraph, END
    LANGGRAPH_AVAILABLE = True
except ImportError:
    LANGGRAPH_AVAILABLE = False


class AgentWorkflow:
    def __init__(
        self, bailian: BailianAnalyzeTool, table: TableQueryTool, search: WebSearchTool
    ):
        self.bailian = bailian
        self.table = table
        self.search = search
        self.graph = self._build_graph() if LANGGRAPH_AVAILABLE else None

    def _build_graph(self):
        graph = StateGraph(AgentState)
        graph.add_node("route", self._route)
        graph.add_node("tool_call", self._tool_call)
        graph.add_node("result", self._summarize)
        graph.set_entry_point("route")
        graph.add_conditional_edges(
            "route",
            self._choose_tool,
            {
                "bailian_analyze": "tool_call",
                "table_query": "tool_call",
                "web_search": "tool_call",
            },
        )
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
            result = f"查询结果: {text}"
        elif intent == "web_search":
            data = await self.search.execute(text)
            result = str(data)
        else:
            result = f"未知意图: {intent}"

        return {**state, "tool_name": intent, "tool_result": result}

    async def _summarize(self, state: AgentState) -> AgentState:
        return {
            **state,
            "messages": state["messages"]
            + [{"role": "assistant", "content": state["tool_result"]}],
        }

    async def invoke(self, user_message: str) -> str:
        initial_state = AgentState(
            messages=[{"role": "user", "content": user_message}],
            user_intent="",
            tool_name="",
            tool_result="",
            error=None,
        )
        if self.graph:
            result = await self.graph.ainvoke(initial_state)
            return result["messages"][-1]["content"]
        # 降级：直接调用 bailian
        result = await self.bailian.execute(task="general", text=user_message)
        return result
