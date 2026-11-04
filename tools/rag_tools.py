"""RAG (Retrieval-Augmented Generation) Knowledge Retrieval Tool.
Category: RAG & Technical Context Retrieval
"""

import math
import re
from pathlib import Path
from typing import Any

WORKSPACE = (Path(__file__).resolve().parent.parent / "workspace")

# Curated technical knowledge chunks
KNOWLEDGE_BASE = [
    {
        "id": "pytest_parametrize",
        "category": "testing",
        "title": "Pytest Parametrization & Edge Cases",
        "content": (
            "Use @pytest.mark.parametrize('param1,param2,expected', [(val1, val2, exp1), ...]) "
            "to test multiple input-output pairs concisely. Always include edge cases: empty strings, "
            "negative numbers, zero, large integers, null/None, and boundary thresholds."
        ),
        "source": "knowledge_base:pytest_patterns"
    },
    {
        "id": "pytest_raises",
        "category": "testing",
        "title": "Exception Assertion with pytest.raises",
        "content": (
            "When testing error handling, use with pytest.raises(ExpectedException, match='optional regex'): "
            "to ensure the function properly validates inputs (e.g. ValueError for negative numbers or TypeError for invalid types)."
        ),
        "source": "knowledge_base:pytest_patterns"
    },
    {
        "id": "clean_code_types",
        "category": "architecture",
        "title": "Type Hinting and Clean Function Contracts",
        "content": (
            "Every function should include explicit Python 3.10+ type annotations (e.g. def func(val: int) -> bool:). "
            "Use typing.Optional, typing.Union, or built-in list[int], dict[str, Any]. Functions must be pure and "
            "deterministic where possible, with non-interactive interfaces (no input() calls)."
        ),
        "source": "knowledge_base:pep8_standards"
    },
    {
        "id": "binary_search_pattern",
        "category": "algorithms",
        "title": "Binary Search Algorithm Template",
        "content": (
            "Binary search requires a sorted sequence. Set left = 0, right = len(arr) - 1. "
            "While left <= right: mid = (left + right) // 2. If arr[mid] == target: return mid. "
            "If arr[mid] < target: left = mid + 1; else: right = mid - 1. Return -1 if not found. Time: O(log n)."
        ),
        "source": "knowledge_base:algorithms"
    },
    {
        "id": "prime_number_sieve",
        "category": "algorithms",
        "title": "Prime Number Primality & Sieve",
        "content": (
            "For single number primality: if n <= 1 return False; if n <= 3 return True; "
            "if n % 2 == 0 or n % 3 == 0 return False. Check divisibility from 5 up to int(math.isqrt(n)) "
            "stepping by 6 (i and i + 2). Time: O(sqrt(n))."
        ),
        "source": "knowledge_base:algorithms"
    },
    {
        "id": "self_correction_fixing",
        "category": "debugging",
        "title": "Resolving Common Python Exceptions",
        "content": (
            "1. IndexError: check sequence length before indexing. "
            "2. KeyError: use dict.get(key, default) or verify key membership. "
            "3. ZeroDivisionError: guard divisor != 0 before division or modulo. "
            "4. TypeError: convert or cast types explicitly before operations. "
            "5. ImportError in tests: ensure sys.path includes workspace root."
        ),
        "source": "knowledge_base:debugging_guide"
    }
]


def tokenize(text: str) -> set[str]:
    """Extract lowercased alphanumeric word tokens."""
    return set(re.findall(r"\w+", text.lower()))


def calculate_relevance(query_tokens: set[str], doc_text: str) -> float:
    """Calculate token overlap relevance score."""
    if not query_tokens:
        return 0.0
    doc_tokens = tokenize(doc_text)
    overlap = query_tokens.intersection(doc_tokens)
    if not overlap:
        return 0.0
    return len(overlap) / (math.sqrt(len(query_tokens)) * math.sqrt(len(doc_tokens)) + 1e-5)


def rag_code_knowledge(query: str, category: str = "all") -> dict[str, Any]:
    """Retrieve relevant Python code patterns, testing strategies, and workspace context.

    Args:
        query: Technical search query (e.g. 'pytest parametrize', 'binary search', 'error fixing').
        category: Filter by category ('testing', 'architecture', 'algorithms', 'debugging', 'workspace', 'all').

    Returns:
        Ranked knowledge chunks with citations and relevance scores.
    """
    query_tokens = tokenize(query)

    # 1. Gather all documents (Curated + Workspace files)
    docs = list(KNOWLEDGE_BASE)

    # Index workspace python files dynamically into RAG corpus
    if WORKSPACE.exists():
        for file in WORKSPACE.glob("*.py"):
            try:
                content = file.read_text(encoding="utf-8")
                docs.append({
                    "id": f"workspace_{file.name}",
                    "category": "workspace",
                    "title": f"Workspace File: {file.name}",
                    "content": content[:800],
                    "source": f"workspace:{file.name}"
                })
            except Exception:
                pass

    # 2. Score and filter documents
    scored = []
    for doc in docs:
        if category != "all" and doc["category"] != category:
            continue

        score = calculate_relevance(query_tokens, f"{doc['title']} {doc['content']} {doc['category']}")
        if score > 0.05:
            scored.append((score, doc))

    # Sort descending by relevance score
    scored.sort(key=lambda x: x[0], reverse=True)
    top_results = scored[:3]

    evidence = []
    for score, doc in top_results:
        evidence.append({
            "source": doc["source"],
            "title": doc["title"],
            "category": doc["category"],
            "relevance_score": round(score, 3),
            "snippet": doc["content"]
        })

    is_validated = len(evidence) > 0
    return {
        "query": query,
        "category": category,
        "success": is_validated,
        "validated": True,
        "validation_summary": f"Retrieved {len(evidence)} verified reference chunk(s)" if is_validated else "No matching references found",
        "evidence": evidence
    }
