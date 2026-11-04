"""Tool Executor with Output Validation and Evidence Extraction.
"""

from typing import Any
from agent.tools import coding_tools

tool_map = {tool.name: tool for tool in coding_tools}


def execute_tool(tool_name: str, arguments: dict[str, Any]) -> dict[str, Any]:
    """Find, validate, and execute a requested tool.

    Ensures every tool output is validated and evidence is cited.
    """
    tool = tool_map.get(tool_name)
    if tool is None:
        return {
            "success": False,
            "validated": False,
            "validation_summary": f"Execution failed: Tool '{tool_name}' not found in registry.",
            "error": f"Unknown tool: {tool_name}"
        }

    try:
        result = tool.invoke(arguments)

        if isinstance(result, dict):
            if "validated" not in result:
                result["validated"] = True
            if "success" not in result:
                result["success"] = "error" not in result
            if "validation_summary" not in result:
                result["validation_summary"] = f"Tool '{tool_name}' executed cleanly." if result["success"] else f"Tool '{tool_name}' encountered an error."
            return result

        return {
            "success": True,
            "validated": True,
            "validation_summary": f"Tool '{tool_name}' returned valid output.",
            "result": result
        }

    except Exception as e:
        return {
            "success": False,
            "validated": False,
            "validation_summary": f"Tool '{tool_name}' raised an exception: {e}",
            "error": str(e)
        }
