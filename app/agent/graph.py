from langgraph.graph import StateGraph, END

from app.agent.state import AgentState
from app.agent.nodes import extract_country, fetch_data, synthesize_answer


def _should_continue(state: AgentState) -> str:
    if state.get("error"):
        return "synthesize"
    return "fetch"


def build_graph() -> StateGraph:
    graph = StateGraph(AgentState)

    graph.add_node("extract", extract_country)
    graph.add_node("fetch", fetch_data)
    graph.add_node("synthesize", synthesize_answer)

    graph.set_entry_point("extract")
    graph.add_conditional_edges(
        "extract",
        _should_continue,
        {"fetch": "fetch", "synthesize": "synthesize"},
    )
    graph.add_edge("fetch", "synthesize")
    graph.add_edge("synthesize", END)

    return graph.compile()