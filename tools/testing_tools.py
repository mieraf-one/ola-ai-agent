"""Pytest Unit Test Suite Execution Tool.
Category: Code & Compute
"""

import re
import subprocess
import sys
from pathlib import Path
from typing import Any

WORKSPACE = (Path(__file__).resolve().parent.parent / "workspace")


def run_tests(test_path: str = ".") -> dict[str, Any]:
    """Run pytest test suite inside the workspace and validate test outcomes."""
    try:
        path = (WORKSPACE / test_path).resolve()

        if not path.is_relative_to(WORKSPACE):
            return {
                "success": False,
                "validated": False,
                "error": "Access outside workspace is strictly disallowed."
            }

        if not path.exists():
            return {
                "success": False,
                "validated": False,
                "error": f"Test path '{test_path}' does not exist."
            }

        result = subprocess.run(
            [sys.executable, "-m", "pytest", str(path), "-v"],
            cwd=WORKSPACE,
            capture_output=True,
            text=True,
            timeout=30
        )

        output = result.stdout + "\n" + result.stderr

        # Parse test outcomes from pytest output
        passed_matches = re.findall(r"(\d+)\s+passed", output)
        failed_matches = re.findall(r"(\d+)\s+failed", output)
        error_matches = re.findall(r"(\d+)\s+error", output)

        passed_count = int(passed_matches[-1]) if passed_matches else 0
        failed_count = int(failed_matches[-1]) if failed_matches else 0
        error_count = int(error_matches[-1]) if error_matches else 0

        is_success = (result.returncode == 0) and (failed_count == 0) and (error_count == 0)

        # Extract failure tracebacks if failed
        failures = []
        if not is_success:
            failure_blocks = re.findall(r"(FAILURES.*?)(?===+ short test summary)", output, re.DOTALL)
            if failure_blocks:
                failures.append(failure_blocks[0][:800])
            else:
                failures.append(output[-600:])

        validation_summary = (
            f"Pytest verified: {passed_count} test(s) PASSED cleanly."
            if is_success
            else f"Pytest validation failed: {failed_count} failed, {error_count} error(s)."
        )

        return {
            "success": is_success,
            "validated": True,
            "validation_summary": validation_summary,
            "passed_count": passed_count,
            "failed_count": failed_count,
            "error_count": error_count,
            "stdout": result.stdout,
            "stderr": result.stderr,
            "returncode": result.returncode,
            "failures": failures,
            "source": f"pytest:{test_path}",
            "evidence": {
                "source": f"pytest:{test_path}",
                "passed": passed_count,
                "failed": failed_count,
                "summary": validation_summary
            }
        }

    except subprocess.TimeoutExpired:
        return {
            "success": False,
            "validated": False,
            "error": "Testing timed out after 30 seconds."
        }

    except Exception as e:
        return {
            "success": False,
            "validated": False,
            "error": str(e)
        }
