from agent.model import llm_with_tools
from agent.tool_executor import execute_tool


def run_tool_loop(task: str, max_iterations: int = 10) -> str:
    """Let Gemini use tools to complete a developer task."""

    messages = [
        (
            "system",
            """You are an autonomous AI coding assistant.

            Your job is to complete the developer's coding task.

            You have access to tools for:
            - Listing project files
            - Reading files
            - Writing files
            - Executing Python files
            - Running tests
            - Managing your implementation plan

            Instructions:
            - Understand the developer's request.
            - Use tools when necessary.
            - Check your work by executing code and running tests.
            - If something fails, analyze the error and try to fix it.
            - Do not claim success unless you have verified it.
            - Explain what you accomplished when finished.
            """
        ),
        ("human", task)
    ]

    for iteration in range(max_iterations):

        # Ask Gemini what to do next
        response = llm_with_tools.invoke(messages)

        # Store Gemini's response in conversation history
        messages.append(response)

        # Check whether Gemini requested any tools
        tool_calls = response.tool_calls

        if not tool_calls:
            return response.content

        # Execute every requested tool
        for tool_call in tool_calls:

            tool_name = tool_call["name"]
            arguments = tool_call["args"]
            tool_call_id = tool_call["id"]

            print(f"\nCalling tool: {tool_name}")
            print(f"Arguments: {arguments}")

            result = execute_tool(tool_name, arguments)

            print(f"Tool result: {result}")

            # Send the tool result back to Gemini
            messages.append(
                {
                    "role": "tool",
                    "tool_call_id": tool_call_id,
                    "content": str(result)
                }
            )

    return "Maximum tool-calling iterations reached."
