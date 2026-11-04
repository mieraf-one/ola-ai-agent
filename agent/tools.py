"""Tool definitions for LangGraph agent function calling and dynamic dispatching.
Spans 5 execution-tool categories:
1. Search (Official documentation, PyPI)
2. RAG (Technical knowledge retrieval, best practices)
3. Code & Compute (Execution, Pytest)
4. System & Environment (Workspace reading, writing, listing)
5. Meta-Tools (Plan management, failure critique)
"""

from typing import Any
from langchain_core.tools import tool

from tools.search_tools import search_python_docs
from tools.rag_tools import rag_code_knowledge as rag_lookup
from tools.file_tools import list_files, read_file, write_file
from tools.execution_tools import execute_python
from tools.testing_tools import run_tests
from tools.meta_tools import update_plan, critique_test_failure


# 1. Search Tool
@tool
def search_documentation(query: str) -> dict[str, Any]:
    """Search Python official documentation, standard library, and package registry.
    Use this to look up function signatures, library methods, and official docs.
    """
    return search_python_docs(query)


# 2. RAG Knowledge Tool
@tool
def rag_code_knowledge(query: str, category: str = "all") -> dict[str, Any]:
    """Retrieve verified Python coding patterns, algorithm templates, and pytest strategies.
    Categories: 'testing', 'architecture', 'algorithms', 'debugging', 'workspace', 'all'.
    """
    return rag_lookup(query, category)


# 3. System & Environment: File Reading
@tool
def read_project_file(file_path: str) -> dict[str, Any]:
    """Read the contents of a file inside the project workspace directory."""
    return read_file(file_path)


# 4. System & Environment: File Writing
@tool
def write_project_file(file_path: str, content: str) -> dict[str, Any]:
    """Create or modify a file inside the workspace with AST syntax validation."""
    return write_file(file_path, content)


# 5. System & Environment: Directory Listing
@tool
def list_project_files(directory: str = ".") -> dict[str, Any]:
    """List all files and subdirectories inside the project workspace."""
    return list_files(directory)


# 6. Code & Compute: Script Execution
@tool
def execute_python_file(file_path: str) -> dict[str, Any]:
    """Execute a Python file inside the workspace and validate output/returncode."""
    return execute_python(file_path)


# 7. Code & Compute: Pytest Test Suite Execution
@tool
def test_project(test_path: str = ".") -> dict[str, Any]:
    """Execute the pytest test suite inside the workspace and validate test results."""
    return run_tests(test_path)


# 8. Meta-Tool: Plan Management
@tool
def manage_plan(plan: list[str], current_step: int = 0, status: str = "in_progress") -> dict[str, Any]:
    """Meta-Tool: Create or update task implementation plan and active progress."""
    return update_plan(plan, current_step, status)


# 9. Meta-Tool: Self-Correction Critique
@tool
def critique_code(error_output: str, test_output: str) -> dict[str, Any]:
    """Meta-Tool: Perform deep critique of execution errors and test failure tracebacks."""
    return critique_test_failure({}, error_output, test_output)


# All available tools
coding_tools = [
    search_documentation,
    rag_code_knowledge,
    read_project_file,
    write_project_file,
    list_project_files,
    execute_python_file,
    test_project,
    manage_plan,
    critique_code
]

tools_by_name = {t.name: t for t in coding_tools}
