"""State definition for LangGraph Agentic System.
Maintains persistent task state, tool validation logs, cited evidence, and decision explanations.
"""

from typing import Any, Optional, TypedDict


class AgentState(TypedDict, total=False):
    # User's request
    task: str

    # Conversational memory across turns
    chat_history: list[dict[str, str]]

    # Intent routing ("chat" vs "code")
    intent: str
    chat_response: str

    # Planning information (Meta-tool)
    plan: list[str]
    current_step: int

    # Generated files & workspace state
    files: list[str]
    generated_code: dict[str, str]

    # Dynamic Tool Calling & Evidence State
    evidence: list[dict[str, Any]]
    tool_validations: list[dict[str, Any]]
    decision_explanations: list[str]
    tools_called: list[str]

    # Execution and testing results
    execution_output: str
    test_output: str
    execution_success: bool
    tests_passed: bool

    # Critique & Self-Correction
    critique: Optional[dict[str, Any]]
    errors: list[str]
    retry_count: int

    # Step budgeting & stop conditions
    step_count: int
    max_steps: int
    stop_reason: Optional[str]  # "goal_complete" | "information_missing" | "risk_too_high" | "max_steps_reached" | "max_retries_reached"
    risk_assessment: Optional[dict[str, Any]]

    # Plan evolution & agentic evidence
    plan_history: list[dict[str, Any]]
    alternative_approach: Optional[str]
    corrected_query: Optional[str]
    conflicting_sources: list[str]

    # Agent progress & final response
    status: str
    final_response: str
