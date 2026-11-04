import sys
from agent.graph import graph


def main():
    if len(sys.argv) > 1:
        task = " ".join(sys.argv[1:])
    else:
        print("=" * 60)
        print("          LANGGRAPH AI CODE AGENT")
        print("=" * 60)
        task = input("\nEnter your coding task:\n> ").strip()

    if not task:
        print("Error: No task provided.")
        sys.exit(1)

    print(f"\n[Agent] Initiating workflow for task: {task}\n")

    initial_state = {
        "task": task,
        "retry_count": 0
    }

    result = graph.invoke(initial_state)

    print("\n" + "=" * 25 + " PLAN " + "=" * 25)
    for index, step in enumerate(result.get("plan", []), start=1):
        print(f"{index}. {step}")

    print("\n" + "=" * 25 + " GENERATED FILES " + "=" * 25)
    for fname in result.get("files", []):
        print(f" - {fname}")

    print("\n" + "=" * 25 + " EXECUTION OUTPUT " + "=" * 25)
    print(result.get("execution_output", "No execution output."))
    print(f"Execution Successful: {result.get('execution_success', False)}")

    print("\n" + "=" * 25 + " TEST OUTPUT " + "=" * 25)
    print(result.get("test_output", "No test output."))
    print(f"Tests Passed: {result.get('tests_passed', False)}")

    print("\n" + "=" * 25 + " FINAL STATUS " + "=" * 25)
    print(f"Status: {result.get('status', 'unknown')}")
    print(f"Retries Used: {result.get('retry_count', 0)}")


if __name__ == "__main__":
    main()
