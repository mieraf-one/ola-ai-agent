"""Workspace Filesystem Execution Tools.
Category: System & Environment
"""

import ast
from pathlib import Path
from typing import Any

WORKSPACE = (Path(__file__).resolve().parent.parent / "workspace")
WORKSPACE.mkdir(parents=True, exist_ok=True)


def get_safe_path(file_path: str) -> Path:
    """Ensure the requested path stays inside workspace."""
    path = (WORKSPACE / file_path).resolve()
    if not path.is_relative_to(WORKSPACE):
        raise ValueError("Access outside workspace is strictly disallowed.")
    return path


def validate_python_syntax(content: str, filename: str) -> tuple[bool, str]:
    """Parse Python code with AST to validate syntax before writing."""
    if not filename.endswith(".py"):
        return True, "Non-Python file, syntax check skipped."
    try:
        ast.parse(content, filename=filename)
        return True, "AST syntax check passed."
    except SyntaxError as e:
        return False, f"SyntaxError on line {e.lineno}: {e.msg}"


def list_files(directory: str = ".") -> dict[str, Any]:
    """List files inside a workspace directory."""
    try:
        path = get_safe_path(directory)
        if not path.is_dir():
            return {
                "success": False,
                "validated": False,
                "error": "Directory does not exist."
            }

        files = [
            str(item.relative_to(WORKSPACE))
            for item in path.iterdir()
            if not item.name.startswith(".") and item.name != "__pycache__"
        ]

        return {
            "success": True,
            "validated": True,
            "validation_summary": f"Found {len(files)} file(s) in workspace",
            "files": files,
            "source": f"workspace:{directory}"
        }
    except Exception as e:
        return {
            "success": False,
            "validated": False,
            "error": str(e)
        }


def read_file(file_path: str) -> dict[str, Any]:
    """Read a file inside the workspace."""
    try:
        path = get_safe_path(file_path)
        if not path.is_file():
            return {
                "success": False,
                "validated": False,
                "error": f"File '{file_path}' does not exist in workspace."
            }

        content = path.read_text(encoding="utf-8")
        return {
            "success": True,
            "validated": True,
            "validation_summary": f"Read {len(content)} characters from '{file_path}'",
            "file_path": file_path,
            "content": content,
            "source": f"workspace:{file_path}"
        }
    except Exception as e:
        return {
            "success": False,
            "validated": False,
            "error": str(e)
        }


def write_file(file_path: str, content: str) -> dict[str, Any]:
    """Create or modify a file inside the workspace with syntax validation."""
    try:
        path = get_safe_path(file_path)

        # 1. Validate syntax for Python files
        is_valid, validation_msg = validate_python_syntax(content, path.name)
        if not is_valid:
            return {
                "success": False,
                "validated": False,
                "error": f"Validation failed: {validation_msg}",
                "file_path": file_path
            }

        # 2. Write file
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")

        return {
            "success": True,
            "validated": True,
            "validation_summary": f"Syntax valid. Saved {len(content)} bytes to '{file_path}'",
            "file_path": file_path,
            "message": f"File saved successfully: {file_path}",
            "source": f"workspace:{file_path}"
        }
    except Exception as e:
        return {
            "success": False,
            "validated": False,
            "error": str(e)
        }
