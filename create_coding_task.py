from agent.tool_loop import run_tool_loop

task = """
Create a Python calculator.

Requirements:
1. Create calculator.py inside the workspace.
2. Implement addition, subtraction, multiplication, and division.
3. Handle division by zero.
4. Execute the Python file to check for errors.
5. Create appropriate pytest tests.
6. Run the tests.
7. If any tests fail, analyze the errors and fix the code.

Use your available tools to complete the task.
"""

result = run_tool_loop(task)

print("\n========== FINAL RESPONSE ==========")
print(result)