"""Meta-Tools for Planning, Self-Correction Critique, and Delegation.
Category: Meta-Tools
"""

from typing import Any


def update_plan(plan: list[str], current_step: int, status: str = "in_progress") -> dict[str, Any]:
    """Meta-Tool: Create or update task implementation plan and active step tracking."""
    return {
        "success": True,
        "validated": True,
        "validation_summary": f"Plan updated: Step {current_step + 1}/{len(plan)} active",
        "plan": plan,
        "current_step": current_step,
        "status": status,
        "source": "meta:plan"
    }


def critique_test_failure(
    code_files: dict[str, str],
    error_output: str,
    test_output: str
) -> dict[str, Any]:
    """Meta-Tool: Perform deep critique of execution errors and test failure tracebacks.

    Diagnoses root causes and prescribes concrete corrective actions for the next loop.
    """
    findings = []
    recommended_fixes = []

    combined_text = (error_output + "\n" + test_output).lower()

    if "syntaxerror" in combined_text:
        findings.append("Syntax error detected in generated Python file.")
        recommended_fixes.append("Re-parse AST and verify indentation, missing colons, or unclosed brackets.")

    if "assertionerror" in combined_text:
        findings.append("Assertion failure: Output value does not match expected test outcome.")
        recommended_fixes.append("Review mathematical or algorithmic logic against edge cases and update implementation.")

    if "indexerror" in combined_text:
        findings.append("IndexError: Attempted to access an out-of-bounds index.")
        recommended_fixes.append("Add boundary guards (e.g., if not sequence: return default) before indexing.")

    if "zerodivisionerror" in combined_text:
        findings.append("ZeroDivisionError: Division or modulo by zero.")
        recommended_fixes.append("Guard against zero values before division.")

    if "modulenotfounderror" in combined_text or "importerror" in combined_text:
        findings.append("Import error: Function or module name mismatch between code and test file.")
        recommended_fixes.append("Ensure module names match exact filenames and exports are named identically.")

    if not findings:
        findings.append("Runtime exception or test assertion failure encountered.")
        recommended_fixes.append("Inspect traceback stack, correct failed statements, and re-execute.")

    return {
        "success": True,
        "validated": True,
        "validation_summary": f"Critique complete: {len(findings)} issue(s) diagnosed",
        "findings": findings,
        "recommended_fixes": recommended_fixes,
        "source": "meta:critique"
    }
