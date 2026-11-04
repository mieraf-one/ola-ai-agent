from langgraph.graph import StateGraph, START, END

from agent.state import AgentState
from agent.nodes import (
    router_node,
    chat_node,
    planning_node,
    research_node,
    code_generation_node,
    save_code_node,
    execution_node,
    testing_node,
    critique_node,
    retry_node,
    fix_code_node,
    conclusion_node
)


def route_intent(state: AgentState) -> str:
    """Route user request based on classified intent and safety stop conditions."""
    stop_reason = state.get("stop_reason")
    if stop_reason in ("risk_too_high", "information_missing"):
        return "conclude"
    if state.get("intent") == "chat":
        return "chat"
    return "code"


def check_test_results(state: AgentState) -> str:
    """Evaluate pytest results and decide between conclusion or self-correction."""
    # 1. Stop when Goal complete
    if state.get("execution_success", False) and state.get("tests_passed", False):
        return "conclude"

    # 2. Stop when Max steps reached
    step_count = state.get("step_count", 0)
    max_steps = state.get("max_steps", 12)
    if step_count >= max_steps:
        return "conclude"

    # 3. Stop when Max 2 retries reached
    retry_count = state.get("retry_count", 0)
    if retry_count < 2:
        return "fix"

    return "conclude"


# Create the graph
builder = StateGraph(AgentState)

# Register nodes
builder.add_node("router", router_node)
builder.add_node("chat", chat_node)
builder.add_node("planning", planning_node)
builder.add_node("research", research_node)
builder.add_node("code_generation", code_generation_node)
builder.add_node("save_code", save_code_node)
builder.add_node("execute_code", execution_node)
builder.add_node("testing_code", testing_node)
builder.add_node("critique", critique_node)
builder.add_node("retry", retry_node)
builder.add_node("fix_code", fix_code_node)
builder.add_node("conclusion", conclusion_node)

# Connect nodes
builder.add_edge(START, "router")
builder.add_conditional_edges(
    "router",
    route_intent,
    {
        "chat": "chat",
        "code": "planning",
        "conclude": "conclusion"
    }
)
builder.add_edge("chat", END)

# Code Generation Pipeline with Research & HITL Approval
builder.add_edge("planning", "research")
builder.add_edge("research", "code_generation")
builder.add_edge("code_generation", "save_code")
builder.add_edge("save_code", "execute_code")
builder.add_edge("execute_code", "testing_code")

# Test validation branch
builder.add_conditional_edges(
    "testing_code",
    check_test_results,
    {
        "conclude": "conclusion",
        "fix": "critique"
    }
)

# Self-correction loop
builder.add_edge("critique", "retry")
builder.add_edge("retry", "fix_code")
builder.add_edge("fix_code", "save_code")

builder.add_edge("conclusion", END)

# Compile graph
graph = builder.compile()
