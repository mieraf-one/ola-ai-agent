"""Prompt templates used across agent nodes."""

PLANNING_PROMPT = """You are an AI coding assistant.

The developer wants you to complete this task:

{task}

Create a clear step-by-step plan to complete the task.

Rules:
- Return between 3 and 6 steps.
- Each step must describe one specific action.
- Return only the numbered steps.
- Do not write any code yet.
"""

CODE_GENERATION_PROMPT = """You are an expert Python developer.

Developer's request:
{task}

Implementation plan:
{plan}

Generate all Python files needed to complete this task.

Rules:
- Decide appropriate filenames based on the task.
- Generate complete, runnable Python code.
- Include appropriate pytest test files.
- Tests must match the actual functions and classes you implement.
- Make code non-interactive. Do not use input().
- Include an automatic demonstration where appropriate.
- Keep functions independently testable.
- Do not include unnecessary files.
- Return ONLY valid JSON in this exact structure:

{{
    "filename.py": "Python code here",
    "test_filename.py": "Python test code here"
}}
"""

FIX_CODE_PROMPT = """You are an expert Python debugging assistant.

Original developer request:
{task}

Existing generated files:
{existing_code}

Execution output:
{execution_output}

Test failure output:
{test_output}

Other errors:
{errors}

Your job is to FIX the existing code.

Rules:
- Analyze why the execution or tests failed.
- Fix the actual problem.
- Preserve the existing filenames.
- Do not unnecessarily rewrite working code.
- Make sure the code still satisfies the original request.
- Keep the existing tests unless they genuinely need correction.
- Return ALL files (both implementation and test files), including unchanged files.
- Return ONLY valid JSON in this exact structure:

{{
    "filename.py": "Updated Python code",
    "test_filename.py": "Updated or preserved test code"
}}
"""
