"""Python Script Execution Tool.
Category: Code & Compute
"""

import subprocess
import sys
from pathlib import Path
from typing import Any

WORKSPACE = (Path(__file__).resolve().parent.parent / "workspace")


def execute_python(file_path: str) -> dict[str, Any]:
    """Execute a Python file inside the workspace safely.

    Validates return code, captures stdout/stderr, and returns evidence.
    """
    try:
        path = (WORKSPACE / file_path).resolve()

        if not path.is_relative_to(WORKSPACE):
            return {
                "success": False,
                "validated": False,
                "error": "Access outside workspace is strictly disallowed."
            }

        if not path.is_file():
            return {
                "success": False,
                "validated": False,
                "error": f"File '{file_path}' does not exist."
            }

        if path.suffix != ".py":
            return {
                "success": False,
                "validated": False,
                "error": "Only Python (.py) files can be executed."
            }

        result = subprocess.run(
            [sys.executable, str(path)],
            cwd=WORKSPACE,
            capture_output=True,
            text=True,
            timeout=10
        )

        is_success = result.returncode == 0
        summary = (
            f"Executed '{file_path}' successfully (exit code 0)."
            if is_success
            else f"Execution of '{file_path}' failed with exit code {result.returncode}."
        )

        return {
            "success": is_success,
            "validated": True,
            "validation_summary": summary,
            "file_path": file_path,
            "stdout": result.stdout,
            "stderr": result.stderr,
            "returncode": result.returncode,
            "source": f"execution:{file_path}",
            "evidence": {
                "source": f"subprocess_run:{file_path}",
                "exit_code": result.returncode,
                "stdout_sample": result.stdout[:200] if result.stdout else "None",
                "stderr_sample": result.stderr[:200] if result.stderr else "None"
            }
        }

    except subprocess.TimeoutExpired:
        return {
            "success": False,
            "validated": False,
            "error": "Execution timed out after 10 seconds (check for infinite loops)."
        }

    except Exception as e:
        return {
            "success": False,
            "validated": False,
            "error": str(e)
        }
