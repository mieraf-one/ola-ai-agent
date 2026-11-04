def update_plan(plan: list[str], current_step: int, status: str) -> dict:
    """Update the agent's implementation plan."""

    return {
        "plan": plan,
        "current_step": current_step,
        "status": status
    }