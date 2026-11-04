import json
import re
from pathlib import Path
from typing import Any

from agent.model import llm
from agent.state import AgentState
from agent.tool_executor import execute_tool
from backend.logger import logger
from tools.search_tools import search_python_docs
from tools.rag_tools import rag_code_knowledge
from tools.file_tools import write_file
from tools.execution_tools import execute_python
from tools.testing_tools import run_tests
from tools.meta_tools import critique_test_failure
from tools.safety_tools import (
    detect_prompt_injection,
    detect_high_risk_operation,
    detect_missing_information,
    reconcile_conflicting_sources
)


def extract_json(content: str) -> dict:
    """Robustly extract and parse JSON from LLM response."""
    content = content.strip()

    # Match fenced code blocks (```json ... ``` or ``` ... ```)
    match = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", content, re.DOTALL)
    if match:
        return json.loads(match.group(1))

    # Match outermost JSON object { ... }
    match = re.search(r"(\{.*\})", content, re.DOTALL)
    if match:
        return json.loads(match.group(1))

    return json.loads(content)


def router_node(state: AgentState) -> dict[str, Any]:
    """Safety Assessment, Prompt Injection Check, and Intent Routing."""
    task = state["task"].strip()
    step_count = state.get("step_count", 0) + 1
    max_steps = state.get("max_steps", 12)

    # 1. Stop Condition Check: Prompt Injection
    has_injection, injection_msg = detect_prompt_injection(task)
    if has_injection:
        logger.warning(f"[RISK_TOO_HIGH] Prompt injection attempt blocked: {injection_msg}")
        logger.info(f"[STATE_UPDATE] stop_reason='risk_too_high', status='stopped_risk_too_high', step_count={step_count}")
        return {
            "intent": "chat",
            "stop_reason": "risk_too_high",
            "status": "stopped_risk_too_high",
            "final_response": f"⚠️ **Security Warning**: Request halted because a potential prompt injection or unauthorized instruction override was detected ({injection_msg}). Execution stopped to ensure system integrity.",
            "step_count": step_count,
            "max_steps": max_steps
        }

    # 2. Stop Condition Check: High Risk Operations
    has_risk, risk_msg = detect_high_risk_operation(task)
    if has_risk:
        logger.warning(f"[RISK_TOO_HIGH] High risk operation blocked: {risk_msg}")
        logger.info(f"[STATE_UPDATE] stop_reason='risk_too_high', status='stopped_risk_too_high', step_count={step_count}")
        return {
            "intent": "chat",
            "stop_reason": "risk_too_high",
            "status": "stopped_risk_too_high",
            "final_response": f"⚠️ **Safety Refusal**: Request halted because high-risk or destructive system operations were detected ({risk_msg}). Direct system file tampering and dangerous shell executions are prohibited.",
            "step_count": step_count,
            "max_steps": max_steps
        }

    # 3. Stop Condition Check: Missing Information
    is_missing, missing_msg = detect_missing_information(task)
    if is_missing:
        logger.warning(f"[INFORMATION_MISSING] Essential task specification missing: {missing_msg}")
        logger.info(f"[STATE_UPDATE] stop_reason='information_missing', status='stopped_information_missing', step_count={step_count}")
        return {
            "intent": "chat",
            "stop_reason": "information_missing",
            "status": "stopped_information_missing",
            "final_response": f"ℹ️ **Information Missing**: {missing_msg}\n\nPlease specify what algorithm, function, inputs, or expected outputs you would like to design, and I will be happy to assist!",
            "step_count": step_count,
            "max_steps": max_steps
        }

    prompt = f"""You are an intent classification assistant for an autonomous AI software engineer.
Analyze the user's message and determine whether it requires writing/modifying code files, or if it is general conversational interaction.

User message:
"{task}"

Categories:
- "chat": Greetings (hi, hello, hey, good morning), pleasantries, asking what you can do, asking questions about code or general topics, thanking.
- "code": Explicit requests to build, code, create, modify, add features, refactor, test, or debug Python software.

Respond with ONLY ONE word: either "chat" or "code".
"""
    response = llm.invoke(prompt)
    content = response.content

    if isinstance(content, list):
        content = "\n".join(
            block["text"]
            for block in content
            if isinstance(block, dict) and block.get("type") == "text"
        )

    decision = content.strip().lower()
    intent = "chat" if "chat" in decision else "code"
    logger.info(f"[TOOL_CHOICE] Selected LLM intent classifier to route between interactive conversation and autonomous code building.")
    logger.info(f"[RouterNode] Classified intent as '{intent}' for task: '{task[:80]}'")
    logger.info(f"[STATE_UPDATE] intent='{intent}', step_count={step_count}, max_steps={max_steps}")

    return {
        "intent": intent,
        "status": "routed",
        "step_count": step_count,
        "max_steps": max_steps
    }


def chat_node(state: AgentState) -> dict[str, Any]:
    """Respond conversationally to non-coding chat messages with full conversational memory."""
    task = state["task"]
    existing_code = state.get("generated_code", {})
    chat_history = list(state.get("chat_history", []))

    # Format previous turns (excluding current task message)
    past_turns = [m for m in chat_history[:-1] if m.get("content")]
    history_context = ""
    if past_turns:
        history_context = "\nConversation History (Previous Turns in this Thread):\n" + "\n".join(
            f"- {'User' if m.get('role') == 'user' else 'Ola'}: {m.get('content')}"
            for m in past_turns[-8:]
        ) + "\n"

    files_summary = ""
    if existing_code:
        files_summary = f"\nFiles currently in workspace: {', '.join(existing_code.keys())}"

    prompt = f"""You are Ola, a helpful, friendly, and expert AI coding assistant.
You maintain persistent memory of your conversation history with the developer.
{history_context}
User message:
{task}
{files_summary}

Instructions:
- Maintain full context of prior conversation turns: remember what the user told you, your previous replies, decisions, and any code discussed.
- If the user is greeting you (e.g. 'hi', 'hello'), greet them warmly and let them know you're ready to plan, research, code, and test Python applications for them.
- If the user is asking a question about previous messages, your identity, or the code, answer clearly, concisely, and accurately based on the conversation history.
- Keep your tone friendly, professional, and helpful.
"""
    response = llm.invoke(prompt)
    content = response.content

    if isinstance(content, list):
        content = "\n".join(
            block["text"]
            for block in content
            if isinstance(block, dict) and block.get("type") == "text"
        )

    reply = content.strip()
    step_count = state.get("step_count", 0) + 1
    updated_history = chat_history + [{"role": "assistant", "content": reply}]
    logger.info(f"[TOOL_CHOICE] Selected conversational chat synthesis to respond to user inquiry with {len(chat_history)} memory turn(s).")
    logger.info(f"[ChatNode] Formulated conversational response ({len(reply)} chars): '{reply[:80]}...'")
    logger.info(f"[STATE_UPDATE] status='completed', stop_reason='goal_complete', chat_history_len={len(updated_history)}, step_count={step_count}")

    return {
        "chat_response": reply,
        "final_response": reply,
        "chat_history": updated_history,
        "stop_reason": "goal_complete",
        "step_count": step_count,
        "status": "completed"
    }


def planning_node(state: AgentState) -> dict[str, Any]:
    """Meta-Tool: Create structured task plan and initialize progress state."""
    task = state["task"]
    step_count = state.get("step_count", 1) + 1
    chat_history = list(state.get("chat_history", []))

    past_turns = [m for m in chat_history[:-1] if m.get("content")]
    history_context = ""
    if past_turns:
        history_context = "\nPrior Conversation Context in this Thread:\n" + "\n".join(
            f"- {'User' if m.get('role') == 'user' else 'Ola'}: {m.get('content')[:150]}"
            for m in past_turns[-6:]
        ) + "\n"

    prompt = f"""You are an expert AI software architect.
{history_context}
The developer wants you to complete this task:
{task}

Create a clear step-by-step implementation plan.
Rules:
- Return between 3 and 6 steps.
- Include research, implementation, and pytest testing.
- Return only the numbered steps, one per line.
- Do not write any code yet.
"""
    response = llm.invoke(prompt)
    content = response.content

    if isinstance(content, list):
        content = "\n".join(
            block["text"]
            for block in content
            if isinstance(block, dict) and block.get("type") == "text"
        )

    plan = []
    for line in content.splitlines():
        line = line.strip()
        if line:
            step = line.lstrip("0123456789. )-")
            if step:
                plan.append(step.strip())

    if not plan:
        logger.warning(f"[INFORMATION_MISSING] Unable to generate coherent plan for task: {task[:80]}")
        return {
            "stop_reason": "information_missing",
            "status": "stopped_information_missing",
            "final_response": "ℹ️ **Information Missing**: The task is too ambiguous to create a reliable plan. Please specify requirements and target behavior.",
            "step_count": step_count
        }

    decision_exp = f"Created a {len(plan)}-step architectural roadmap to fulfill user requirements."
    logger.info("[TOOL_CHOICE] Selected 'manage_plan' meta-tool to decompose user requirements into a structured milestone roadmap.")
    logger.info(f"[PLAN_MADE] Formulated initial {len(plan)}-step plan: {plan}")
    logger.info(f"[STATE_UPDATE] plan: {len(plan)} steps, current_step: 0, step_count: {step_count}")

    plan_history = [{
        "version": 1,
        "action": "initial_plan",
        "plan": plan
    }]

    return {
        "plan": plan,
        "plan_history": plan_history,
        "current_step": 0,
        "retry_count": 0,
        "step_count": step_count,
        "evidence": [],
        "tool_validations": [
            {
                "tool": "manage_plan",
                "success": True,
                "validated": True,
                "summary": f"Initial plan established with {len(plan)} milestones."
            }
        ],
        "decision_explanations": [decision_exp],
        "status": "planned"
    }


def research_node(state: AgentState) -> dict[str, Any]:
    """Search & RAG Execution Tools: Retrieve official documentation and best practices.

    Validates every tool output, cites evidence with source metadata, and records decision.
    """
    task = state["task"]
    plan = state.get("plan", [])

    # Ask LLM for the optimal technical search queries
    prompt = f"""You are an AI research specialist preparing to build Python software.
Developer task:
{task}

Proposed plan:
{plan}

Determine:
1. One Python standard library module or package to search documentation for (e.g. 'math', 're', 'pytest', 'collections').
2. One technical keyword for RAG best practice retrieval (e.g. 'parametrize', 'algorithms', 'clean code', 'testing').

Return ONLY valid JSON in this exact structure:
{{
    "doc_query": "module_or_function_name",
    "rag_query": "technical_concept_keyword"
}}
"""
    response = llm.invoke(prompt)
    content = response.content

    if isinstance(content, list):
        content = "\n".join(
            block["text"]
            for block in content
            if isinstance(block, dict) and block.get("type") == "text"
        )

    doc_query = "pytest"
    rag_query = "parametrize"

    try:
        queries = extract_json(content)
        doc_query = queries.get("doc_query", "pytest")
        rag_query = queries.get("rag_query", "parametrize")
    except Exception:
        # Fallback query extraction from task text
        if "prime" in task.lower():
            doc_query, rag_query = "math.isqrt", "prime"
        elif "search" in task.lower():
            doc_query, rag_query = "bisect", "binary search"

    step_count = state.get("step_count", 0) + 1
    logger.info(f"[TOOL_CHOICE] Selected 'search_python_docs' (query: '{doc_query}') and 'rag_code_knowledge' (query: '{rag_query}') to ground code generation in verified reference citations.")

    # 1. Execute Search Tool
    search_res = search_python_docs(doc_query)

    # 2. Execute RAG Tool
    rag_res = rag_code_knowledge(rag_query)

    # Collect citations and validation results
    evidence = list(state.get("evidence", []))
    validations = list(state.get("tool_validations", []))

    validations.append({
        "tool": "search_documentation",
        "query": doc_query,
        "success": search_res.get("success", False),
        "validated": search_res.get("validated", False),
        "summary": search_res.get("validation_summary", "")
    })

    validations.append({
        "tool": "rag_code_knowledge",
        "query": rag_query,
        "success": rag_res.get("success", False),
        "validated": rag_res.get("validated", False),
        "summary": rag_res.get("validation_summary", "")
    })

    if search_res.get("evidence"):
        evidence.extend(search_res["evidence"])
    if rag_res.get("evidence"):
        evidence.extend(rag_res["evidence"])

    # 3. Unreliable Sources Guard: Reconcile Conflicting Sources
    has_conflict, conflict_msg, reconciled_evidence = reconcile_conflicting_sources(evidence)
    conflicting_sources_list = []
    if has_conflict:
        conflicting_sources_list.append(conflict_msg)
        logger.warning(f"[CONFLICTING_SOURCES] {conflict_msg}")
        evidence = reconciled_evidence

    explanation = (
        f"Queried official Python docs for '{doc_query}' and RAG knowledge for '{rag_query}'. "
        f"Gathered {len(evidence)} verified reference citations before coding."
    )
    decision_exps = list(state.get("decision_explanations", []))
    decision_exps.append(explanation)
    logger.info(f"[ResearchNode] Searched docs for '{doc_query}', queried RAG for '{rag_query}', gathered {len(evidence)} citations (conflicts: {has_conflict})")
    logger.info(f"[STATE_UPDATE] evidence: {len(evidence)} items, step_count: {step_count}")

    return {
        "evidence": evidence,
        "conflicting_sources": conflicting_sources_list,
        "tool_validations": validations,
        "decision_explanations": decision_exps,
        "step_count": step_count,
        "status": "researched"
    }


def code_generation_node(state: AgentState) -> dict[str, Any]:
    """Generate Python implementation and matching pytest tests citing retrieved evidence."""
    task = state["task"]
    plan = state.get("plan", [])
    evidence = state.get("evidence", [])
    step_count = state.get("step_count", 0) + 1
    alt_approach = state.get("alternative_approach", "")
    chat_history = list(state.get("chat_history", []))

    past_turns = [m for m in chat_history[:-1] if m.get("content")]
    history_context = ""
    if past_turns:
        history_context = "\nPrior Conversation Context in this Thread:\n" + "\n".join(
            f"- {'User' if m.get('role') == 'user' else 'Ola'}: {m.get('content')[:150]}"
            for m in past_turns[-4:]
        ) + "\n"

    evidence_summary = ""
    if evidence:
        evidence_summary = "\nRetrieved Technical Evidence & Citations:\n" + "\n".join(
            f"- Source [{e.get('source')}]: {e.get('title')} -> {e.get('snippet', '')[:180]}"
            for e in evidence[:4]
        )

    alt_approach_section = f"\nSpecific Alternative Strategy to Apply:\n{alt_approach}\n" if alt_approach else ""

    prompt = f"""You are an expert Python developer.
{history_context}
Developer's request:
{task}

Implementation plan:
{plan}
{evidence_summary}
{alt_approach_section}
Generate all Python files needed to complete this task.
Rules:
- Decide appropriate filenames based on the task (e.g. module.py and test_module.py).
- Generate complete, runnable Python code with explicit type annotations.
- Include thorough pytest unit tests with edge cases (zero, negative, boundary, invalid inputs).
- Cite evidence from the retrieved patterns in docstrings where appropriate.
- Make code non-interactive (no input() calls). Include an automatic demonstration under `if __name__ == '__main__':`.
- Return ONLY valid JSON in this exact structure:

{{
    "filename.py": "Python code here",
    "test_filename.py": "Python test code here"
}}
"""
    response = llm.invoke(prompt)
    content = response.content

    if isinstance(content, list):
        content = "\n".join(
            block["text"]
            for block in content
            if isinstance(block, dict) and block.get("type") == "text"
        )

    try:
        generated_files = extract_json(content)
    except Exception as e:
        return {
            "errors": [f"Failed to parse generated files as JSON: {e}"],
            "step_count": step_count,
            "status": "generation_failed"
        }

    explanation = f"Generated {len(generated_files)} file(s) ({', '.join(generated_files.keys())}) adhering to technical evidence and PEP 8."
    decision_exps = list(state.get("decision_explanations", []))
    decision_exps.append(explanation)
    logger.info("[TOOL_CHOICE] Selected LLM code synthesis with strict AST verification schema, incorporating retrieved evidence patterns and type contracts.")
    logger.info(f"[CodeGenerationNode] Generated {len(generated_files)} file(s): {list(generated_files.keys())}")
    logger.info(f"[STATE_UPDATE] generated_code: {list(generated_files.keys())}, step_count: {step_count}")

    return {
        "generated_code": generated_files,
        "step_count": step_count,
        "decision_explanations": decision_exps,
        "status": "code_generated"
    }


def save_code_node(state: AgentState) -> dict[str, Any]:
    """System & Environment Tool: Write files to workspace with AST syntax validation."""
    generated_files = state.get("generated_code", {})
    step_count = state.get("step_count", 0) + 1

    if not generated_files:
        return {
            "files": [],
            "errors": state.get("errors", []) + ["No generated code to save."],
            "step_count": step_count,
            "status": "save_failed"
        }

    saved_files = []
    errors = []
    validations = list(state.get("tool_validations", []))

    for file_name, content in generated_files.items():
        result = write_file(file_name, content)
        validations.append({
            "tool": "write_workspace_file",
            "file": file_name,
            "success": result.get("success", False),
            "validated": result.get("validated", False),
            "summary": result.get("validation_summary", result.get("error", ""))
        })

        if not result.get("success"):
            errors.append(f"{file_name}: {result.get('error', 'Write failed')}")
        else:
            saved_files.append(file_name)

    explanation = f"Validated AST syntax and saved {len(saved_files)} file(s) into workspace."
    decision_exps = list(state.get("decision_explanations", []))
    decision_exps.append(explanation)
    logger.info("[TOOL_CHOICE] Selected 'write_file' filesystem tool with AST syntax pre-validation to enforce valid Python grammar before disk write.")

    if errors:
        logger.warning(f"[SaveCodeNode] Save failed for some files: {errors}")
        return {
            "files": saved_files,
            "errors": errors,
            "tool_validations": validations,
            "decision_explanations": decision_exps,
            "step_count": step_count,
            "status": "save_failed"
        }

    logger.info(f"[SaveCodeNode] AST validation passed. Saved {len(saved_files)} file(s): {saved_files}")
    logger.info(f"[STATE_UPDATE] files: {saved_files}, step_count: {step_count}")
    return {
        "files": saved_files,
        "tool_validations": validations,
        "decision_explanations": decision_exps,
        "step_count": step_count,
        "status": "code_saved"
    }


def execution_node(state: AgentState) -> dict[str, Any]:
    """Code & Compute Tool: Execute Python application code and validate returncode."""
    files = state.get("files", [])
    step_count = state.get("step_count", 0) + 1

    python_files = [
        file for file in files
        if file.endswith(".py") and not Path(file).name.startswith("test_")
    ]

    if not python_files:
        error = "No application Python files found."
        return {
            "execution_output": error,
            "execution_success": False,
            "errors": [error],
            "step_count": step_count,
            "status": "execution_failed"
        }

    outputs = []
    errors = []
    validations = list(state.get("tool_validations", []))
    evidence = list(state.get("evidence", []))

    logger.info("[TOOL_CHOICE] Selected 'execute_python' in subprocess environment with 10s timeout to safely test script execution and capture runtime output.")

    for file in python_files:
        result = execute_python(file)
        validations.append({
            "tool": "execute_python_file",
            "file": file,
            "success": result.get("success", False),
            "validated": result.get("validated", False),
            "summary": result.get("validation_summary", "")
        })

        if result.get("evidence"):
            evidence.append(result["evidence"])

        if not result.get("success"):
            errors.append(f"{file} execution failed (exit code {result.get('returncode')}): {result.get('error', result.get('stderr'))}")

        outputs.append(
            f"--- {file} ---\n{result.get('stdout', '')}\n{result.get('stderr', '')}"
        )

    explanation = f"Executed {len(python_files)} script(s) in subprocess environment."
    decision_exps = list(state.get("decision_explanations", []))
    decision_exps.append(explanation)
    logger.info(f"[ExecutionNode] Subprocess execution finished. Script count: {len(python_files)}, Errors: {len(errors)}")
    logger.info(f"[STATE_UPDATE] execution_success: {len(errors) == 0}, step_count: {step_count}")

    return {
        "execution_output": "\n".join(outputs),
        "execution_success": len(errors) == 0,
        "errors": errors,
        "evidence": evidence,
        "tool_validations": validations,
        "decision_explanations": decision_exps,
        "step_count": step_count,
        "status": "executed" if not errors else "execution_failed"
    }


def testing_node(state: AgentState) -> dict[str, Any]:
    """Code & Compute Tool: Run pytest suite and validate test assertions."""
    files = state.get("files", [])
    step_count = state.get("step_count", 0) + 1

    test_files = [
        file for file in files
        if file.endswith(".py") and Path(file).name.startswith("test_")
    ]

    if not test_files:
        error = "No test files were generated."
        return {
            "test_output": error,
            "tests_passed": False,
            "errors": [error],
            "step_count": step_count,
            "status": "testing_failed"
        }

    outputs = []
    errors = []
    validations = list(state.get("tool_validations", []))
    evidence = list(state.get("evidence", []))

    logger.info("[TOOL_CHOICE] Selected 'run_tests' with pytest and 30s timeout guard to empirically verify test assertions and edge cases.")

    for test_file in test_files:
        result = run_tests(test_file)
        validations.append({
            "tool": "test_project",
            "file": test_file,
            "success": result.get("success", False),
            "validated": result.get("validated", False),
            "summary": result.get("validation_summary", "")
        })

        if result.get("evidence"):
            evidence.append(result["evidence"])

        outputs.append(
            f"--- {test_file} ---\n{result.get('stdout', '')}\n{result.get('stderr', '')}"
        )

        if not result.get("success"):
            errors.append(f"Pytest assertion failure in {test_file}")

    passed = len(errors) == 0
    explanation = f"Ran pytest test suite: {'All tests PASSED' if passed else 'Tests FAILED, triggering critique'}"
    decision_exps = list(state.get("decision_explanations", []))
    decision_exps.append(explanation)
    logger.info(f"[TestingNode] Pytest completed. Tests passed: {passed}. Test files: {test_files}. Errors: {errors}")

    stop_reason = "goal_complete" if passed else None
    if passed:
        logger.info("[GOAL_COMPLETE] All unit tests passed! Target goal successfully fulfilled.")

    logger.info(f"[STATE_UPDATE] tests_passed: {passed}, stop_reason: {stop_reason}, step_count: {step_count}")

    return {
        "test_output": "\n".join(outputs),
        "tests_passed": passed,
        "stop_reason": stop_reason,
        "errors": errors,
        "evidence": evidence,
        "tool_validations": validations,
        "decision_explanations": decision_exps,
        "step_count": step_count,
        "status": "completed" if passed else "testing_failed"
    }


def critique_node(state: AgentState) -> dict[str, Any]:
    """Meta-Tool: Perform deep critique of execution errors and test failures."""
    code_files = state.get("generated_code", {})
    exec_out = state.get("execution_output", "")
    test_out = state.get("test_output", "")
    step_count = state.get("step_count", 0) + 1

    critique_result = critique_test_failure(code_files, exec_out, test_out)

    validations = list(state.get("tool_validations", []))
    validations.append({
        "tool": "critique_code",
        "success": True,
        "validated": True,
        "summary": critique_result.get("validation_summary", "")
    })

    explanation = f"Critiqued test failure: {', '.join(critique_result.get('findings', []))}. Formulated fix strategy."
    decision_exps = list(state.get("decision_explanations", []))
    decision_exps.append(explanation)

    logger.info("[TOOL_CHOICE] Selected 'critique_test_failure' meta-tool to conduct root-cause reflection and diagnostic analysis on test failures.")
    logger.info(f"[FAILURE_REFLECTION] Reflection on failure: {critique_result.get('findings')} | Recommended corrective fixes: {critique_result.get('recommended_fixes')}")
    logger.info(f"[STATE_UPDATE] critique: {len(critique_result.get('findings', []))} findings, step_count: {step_count}")

    return {
        "critique": critique_result,
        "tool_validations": validations,
        "decision_explanations": decision_exps,
        "step_count": step_count,
        "status": "critiqued"
    }


def retry_node(state: AgentState) -> dict[str, Any]:
    """Increment retry counter, revise plan, and formulate alternative approach and corrected query."""
    new_count = state.get("retry_count", 0) + 1
    step_count = state.get("step_count", 0) + 1

    # Formulate a different valid approach and corrected query based on critique reflection
    findings_str = " ".join(state.get("critique", {}).get("findings", [])).lower()
    test_out = state.get("test_output", "").lower()

    if "recursion" in findings_str or "recursion" in test_out:
        alt_approach = "Switch from recursive algorithm to iterative algorithm using an explicit loop and state accumulator to avoid stack overflow."
        corrected_query = "python iterative algorithms accumulator"
    elif "assertion" in findings_str or "assertion" in test_out:
        alt_approach = "Adopt an alternative mathematical formula / algorithmic structure with strict edge-case handling for boundary conditions (zero, negative, empty)."
        corrected_query = "pytest edge cases boundary guards"
    elif "indexerror" in findings_str or "index" in test_out:
        alt_approach = "Replace direct index lookups with defensive slice operations and length checks."
        corrected_query = "python slice bounds safety"
    elif "zerodivision" in findings_str or "zerodivision" in test_out:
        alt_approach = "Implement upfront input validation guard clause returning defined default or raising explicit ValueError."
        corrected_query = "python zero division guard clause"
    else:
        alt_approach = "Refactor logic using alternative Python standard library pattern with robust type conversion."
        corrected_query = "clean python standard library algorithms"

    current_plan = list(state.get("plan", []))
    revised_step = f"Retry #{new_count}: Apply alternative approach ({alt_approach}) with corrected query '{corrected_query}'"
    revised_plan = current_plan + [revised_step]
    logger.info(f"[PLAN_REVISED] Plan revised for retry #{new_count}: {revised_step}")

    plan_history = list(state.get("plan_history", []))
    plan_history.append({
        "version": len(plan_history) + 1,
        "retry": new_count,
        "action": "plan_revision",
        "alternative_approach": alt_approach,
        "corrected_query": corrected_query,
        "revised_plan": revised_plan
    })

    explanation = f"Entered self-correction iteration #{new_count}/2 with alternative approach: {alt_approach}"
    decision_exps = list(state.get("decision_explanations", []))
    decision_exps.append(explanation)

    logger.info(f"[TOOL_CHOICE] Selected 'retry_node' to trigger retry #{new_count}/2 with alternative approach and corrected search query.")
    logger.info(f"[STATE_UPDATE] retry_count: {new_count}/2, alternative_approach: '{alt_approach}', corrected_query: '{corrected_query}', step_count: {step_count}")

    stop_reason = "max_retries_reached" if new_count >= 2 else None

    return {
        "retry_count": new_count,
        "plan": revised_plan,
        "plan_history": plan_history,
        "alternative_approach": alt_approach,
        "corrected_query": corrected_query,
        "stop_reason": stop_reason,
        "decision_explanations": decision_exps,
        "step_count": step_count,
        "status": "retrying"
    }


def fix_code_node(state: AgentState) -> dict[str, Any]:
    """Analyze error critique and apply targeted fixes using the alternative approach."""
    task = state["task"]
    existing_code = state.get("generated_code", {})
    execution_output = state.get("execution_output", "")
    test_output = state.get("test_output", "")
    critique = state.get("critique", {})
    errors = state.get("errors", [])
    step_count = state.get("step_count", 0) + 1
    alt_approach = state.get("alternative_approach", "")
    corrected_query = state.get("corrected_query", "")

    prompt = f"""You are an expert Python debugging assistant.
Original developer request:
{task}

Existing generated files:
{json.dumps(existing_code, indent=2)}

Execution output:
{execution_output}

Test failure output:
{test_output}

Meta-Tool Critique Findings:
{critique.get('findings', [])}

Critique Recommended Fixes:
{critique.get('recommended_fixes', [])}

Mandatory Alternative Approach to Implement:
{alt_approach} (Corrected query reference: {corrected_query})

Your job is to FIX the code using this ALTERNATIVE VALID APPROACH.
Rules:
- Directly implement the alternative approach described above rather than blindly repeating the failed pattern.
- Apply the critique recommendations directly.
- Preserve existing filenames.
- Return ALL files (implementation and test files).
- Return ONLY valid JSON in this exact structure:

{{
    "filename.py": "Updated Python code",
    "test_filename.py": "Updated test code"
}}
"""
    response = llm.invoke(prompt)
    content = response.content

    if isinstance(content, list):
        content = "\n".join(
            block["text"]
            for block in content
            if isinstance(block, dict) and block.get("type") == "text"
        )

    try:
        fixed_files = extract_json(content)
    except Exception as e:
        return {
            "errors": [f"Failed to parse fixed files as JSON: {e}"],
            "step_count": step_count,
            "status": "fix_failed"
        }

    # Ensure test files aren't dropped
    for fname, code in existing_code.items():
        if fname not in fixed_files and (fname.startswith("test_") or fname.endswith("_test.py")):
            fixed_files[fname] = code

    explanation = f"Applied alternative approach fix ({alt_approach}) to {', '.join(fixed_files.keys())}."
    decision_exps = list(state.get("decision_explanations", []))
    decision_exps.append(explanation)
    logger.info(f"[TOOL_CHOICE] Selected code refactoring tool with alternative approach: '{alt_approach}'")
    logger.info(f"[FixCodeNode] Applied targeted fixes to {list(fixed_files.keys())}")
    logger.info(f"[STATE_UPDATE] generated_code: {list(fixed_files.keys())}, step_count: {step_count}")

    return {
        "generated_code": fixed_files,
        "decision_explanations": decision_exps,
        "step_count": step_count,
        "status": "code_fixed"
    }


def conclusion_node(state: AgentState) -> dict[str, Any]:
    """Generate final comprehensive task summary citing evidence, explaining decisions, and detailing stop reason."""
    task = state["task"]
    files = state.get("files", [])
    execution_success = state.get("execution_success", False)
    tests_passed = state.get("tests_passed", False)
    retry_count = state.get("retry_count", 0)
    step_count = state.get("step_count", 0) + 1
    max_steps = state.get("max_steps", 12)
    evidence = state.get("evidence", [])
    validations = state.get("tool_validations", [])
    decisions = state.get("decision_explanations", [])
    stop_reason = state.get("stop_reason")

    # If stop_reason is already a terminal safety or missing info, return immediately
    if stop_reason in ("risk_too_high", "information_missing"):
        final_msg = state.get("final_response", "")
        logger.info(f"[CONCLUSION] Safety/Guard Stop reached. Reason: '{stop_reason}'. Step count: {step_count}")
        logger.info(f"[STATE_UPDATE] status='completed', stop_reason='{stop_reason}'")
        return {
            "final_response": final_msg,
            "chat_response": final_msg,
            "stop_reason": stop_reason,
            "step_count": step_count,
            "status": "completed"
        }

    # Determine stop condition
    if tests_passed and execution_success:
        stop_reason = "goal_complete"
    elif step_count >= max_steps:
        stop_reason = "max_steps_reached"
    elif retry_count >= 2:
        stop_reason = "max_retries_reached"
    else:
        stop_reason = stop_reason or "goal_complete"

    citations_text = ""
    if evidence:
        citations_text = "\n\nCited Evidence & Documentation Sources:\n" + "\n".join(
            f"* **[{e.get('source', 'Unknown')}]**: {e.get('title', 'Reference')} — _{e.get('snippet', '')[:120]}..._"
            for e in evidence[:4]
        )

    decisions_text = ""
    if decisions:
        decisions_text = "\n\nKey Decisions Made Across Execution:\n" + "\n".join(
            f"1. {d}" for d in decisions[:6]
        )

    prompt = f"""You are Ola, an expert and friendly AI software engineer.
You have completed the workflow for the developer's coding task.

Developer's original request:
{task}

Workflow Stop Condition:
{stop_reason.upper()} (Goal Complete: {tests_passed}, Steps: {step_count}/{max_steps}, Retries: {retry_count}/2)

Files created in workspace:
{', '.join(files) if files else 'None'}

Execution successful: {execution_success}
All unit tests passed: {tests_passed}
Self-correction retries: {retry_count}
Validated Tool Calls: {len(validations)}
{citations_text}
{decisions_text}

Write a natural, friendly, and complete concluding response to the developer.
Guidelines:
- If stop condition is 'GOAL_COMPLETE', announce success enthusiastically!
- If stop condition is 'MAX_RETRIES_REACHED' or 'MAX_STEPS_REACHED', explain transparently what succeeded and where tests failed.
- Mention the files created and what they implement.
- Confirm that every tool output was validated.
- Explicitly cite the evidence / documentation references used.
- Briefly summarize the key decisions taken during the workflow.
- Invite the developer to inspect the code in the editor tab or run additional tests.
"""
    response = llm.invoke(prompt)
    content = response.content

    if isinstance(content, list):
        content = "\n".join(
            block["text"]
            for block in content
            if isinstance(block, dict) and block.get("type") == "text"
        )

    conclusion = content.strip()
    chat_history = list(state.get("chat_history", []))
    updated_history = chat_history + [{"role": "assistant", "content": conclusion}]
    logger.info(f"[CONCLUSION] Workflow finished. Stop reason: '{stop_reason}', Step count: {step_count}, Retries: {retry_count}/2, Tests passed: {tests_passed}")
    logger.info(f"[STATE_UPDATE] status='completed', stop_reason='{stop_reason}', chat_history_len={len(updated_history)}")

    return {
        "final_response": conclusion,
        "chat_response": conclusion,
        "chat_history": updated_history,
        "stop_reason": stop_reason,
        "step_count": step_count,
        "status": "completed"
    }
