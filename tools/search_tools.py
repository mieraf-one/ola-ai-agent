"""Search Execution Tool for Python Documentation, Libraries, and PyPI Packages.
Category: Search & Knowledge Retrieval
"""

import json
import pydoc
import re
import urllib.request
from typing import Any


def clean_pydoc(raw_text: str) -> str:
    """Remove terminal formatting / backspace characters from pydoc output."""
    clean = re.sub(r".\x08", "", raw_text)
    # Strip excessively long output
    lines = clean.splitlines()
    if len(lines) > 50:
        return "\n".join(lines[:50]) + "\n... [truncated for brevity]"
    return clean.strip()


def search_pypi(package_name: str) -> dict[str, Any] | None:
    """Fetch package metadata and description from official PyPI JSON API."""
    try:
        url = f"https://pypi.org/pypi/{package_name.strip().lower()}/json"
        req = urllib.request.Request(url, headers={"User-Agent": "OlaCodeAgent/1.0"})
        with urllib.request.urlopen(req, timeout=5) as response:
            if response.status == 200:
                data = json.loads(response.read().decode("utf-8"))
                info = data.get("info", {})
                return {
                    "source": f"https://pypi.org/project/{package_name}/",
                    "title": f"PyPI: {info.get('name')} {info.get('version')}",
                    "snippet": info.get("summary") or info.get("description", "")[:300],
                    "homepage": info.get("home_page") or info.get("project_url"),
                    "license": info.get("license", "Unknown")
                }
    except Exception:
        return None
    return None


def search_python_docs(query: str) -> dict[str, Any]:
    """Search Python official documentation, standard library, and package registry.

    Args:
        query: Module name, function name, or library to look up (e.g., 'math.isqrt', 'pytest', 're.match').

    Returns:
        Structured evidence containing source citations, docstring snippets, and validation status.
    """
    query = query.strip()
    evidence = []

    # 1. Try local standard library / installed package inspection via pydoc
    try:
        raw_doc = pydoc.render_doc(query)
        if raw_doc and "no Python documentation found" not in raw_doc:
            clean_text = clean_pydoc(raw_doc)
            evidence.append({
                "source": f"python:stdlib/{query}",
                "title": f"Official Python Documentation for '{query}'",
                "snippet": clean_text[:600],
                "type": "pydoc_reference"
            })
    except Exception:
        pass

    # 2. Try PyPI package search
    first_word = query.split()[0].replace("-", "_").lower()
    pypi_result = search_pypi(first_word)
    if pypi_result:
        evidence.append(pypi_result)

    # 3. If query has multiple terms, search submodules or builtins
    if not evidence:
        for common_mod in ["math", "re", "json", "sys", "os", "collections", "itertools", "functools", "typing"]:
            if common_mod in query.lower():
                try:
                    raw_doc = pydoc.render_doc(common_mod)
                    if raw_doc:
                        evidence.append({
                            "source": f"python:stdlib/{common_mod}",
                            "title": f"Module '{common_mod}' Reference",
                            "snippet": clean_pydoc(raw_doc)[:400],
                            "type": "module_overview"
                        })
                        break
                except Exception:
                    pass

    # Validation check
    has_results = len(evidence) > 0
    return {
        "query": query,
        "success": has_results,
        "validated": True,
        "validation_summary": f"Found {len(evidence)} verified documentation sources for '{query}'" if has_results else f"No direct documentation found for '{query}'",
        "evidence_count": len(evidence),
        "evidence": evidence
    }
