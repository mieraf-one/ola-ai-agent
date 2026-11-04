"""Safety, Prompt Injection, Risk Assessment, and Ambiguity Detection Tools.
Category: Security & Robustness
"""

import re
from typing import Any

# Known prompt injection signatures
PROMPT_INJECTION_PATTERNS = [
    r"ignore\s+(all\s+)?(previous|prior|above)\s+instructions?",
    r"disregard\s+(all\s+)?(previous|prior|above)\s+instructions?",
    r"you\s+are\s+now\s+(an\s+unrestricted|in\s+developer\s+mode|dan)",
    r"system\s*:\s*override",
    r"bypass\s+all\s+(filters|rules|safety)",
    r"leak\s+(the\s+)?(system\s+prompt|api\s*key|env|credentials)",
    r"output\s+the\s+entire\s+system\s+prompt",
    r"reveal\s+your\s+hidden\s+instructions",
    r"do\s+anything\s+now",
]

# High risk operations and destructive code signatures
HIGH_RISK_PATTERNS = [
    r"rm\s+-rf\s+[/~]",
    r"shutil\.rmtree\s*\(\s*['\"](?:\/|~|\.\.)",
    r"os\.system\s*\(\s*['\"](?:rm|format|mkfs|dd|chmod\s+777)",
    r"eval\s*\(\s*compile\(",
    r"subprocess\.call\s*\(\s*['\"](?:curl|wget).*?\|\s*(?:bash|sh)",
    r"\/etc\/(?:passwd|shadow)",
    r"\b(?:base64\s+-d.*?\|\s*bash)\b",
]

# Missing information heuristics: tasks that are too short, empty, or ungrounded
MISSING_INFO_PATTERNS = [
    r"^(?:code|build|do\s+it|fix\s+it|run|test|create|start|implement|help\s+me)\.?$",
    r"^(?:please\s+)?(?:do|fix|code)\s+the\s+(?:function|thing|bug)\.?$",
    r"^(?:write\s+code|make\s+app)\.?$",
]


def detect_prompt_injection(text: str) -> tuple[bool, str]:
    """Scan input text for adversarial prompt injection attempts."""
    text_lower = text.lower()
    for pattern in PROMPT_INJECTION_PATTERNS:
        match = re.search(pattern, text_lower, re.IGNORECASE)
        if match:
            return True, f"Prompt injection pattern detected: '{match.group(0)}'"
    return False, ""


def detect_high_risk_operation(text: str) -> tuple[bool, str]:
    """Scan task or code for destructive commands or high-risk system calls."""
    text_lower = text.lower()
    for pattern in HIGH_RISK_PATTERNS:
        match = re.search(pattern, text_lower, re.IGNORECASE)
        if match:
            return True, f"High-risk operation pattern detected: '{match.group(0)}'"
    return False, ""


def detect_missing_information(task: str) -> tuple[bool, str]:
    """Identify if the task lacks required operational specifications."""
    stripped = task.strip().lower()
    if len(stripped.split()) < 3:
        for pattern in MISSING_INFO_PATTERNS:
            if re.match(pattern, stripped):
                return True, "Task is ambiguous and lacks essential specifications (e.g. required logic, inputs, outputs, or problem definition)."
    return False, ""


def reconcile_conflicting_sources(sources: list[dict[str, Any]]) -> tuple[bool, str, list[dict[str, Any]]]:
    """Detect and reconcile conflicting documentation or pattern sources.
    
    Prefers official standard library references over third-party snippets.
    """
    conflicts = []
    has_conflict = False

    # Check for Python 2 vs Python 3 idioms or conflicting data structures
    source_texts = " ".join(s.get("snippet", "") + " " + s.get("content", "") for s in sources).lower()
    if "print " in source_texts and "print(" in source_texts:
        has_conflict = True
        conflicts.append("Detected conflicting print statement (Python 2) vs print function (Python 3). Reconciled in favor of Python 3.10+.")

    # Reconciled sources prioritize official stdlib
    reconciled = sorted(
        sources,
        key=lambda s: 0 if "stdlib" in s.get("source", "") or "python:" in s.get("source", "") else 1
    )

    conflict_msg = "; ".join(conflicts) if has_conflict else "No source conflicts detected."
    return has_conflict, conflict_msg, reconciled
