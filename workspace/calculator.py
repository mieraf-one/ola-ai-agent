def calculate(expression: str):
    """
    Evaluates a mathematical expression safely using an alternative approach
    with strict edge-case handling for boundary conditions (zero, negative, empty).
    """
    if not expression or not isinstance(expression, str):
        raise ValueError("Expression cannot be empty or non-string")
    
    cleaned = expression.strip()
    if not cleaned:
        raise ValueError("Expression cannot be empty")

    # Allowed characters for safety (digits, basic operators, parentheses, decimal point, spaces, unary minus)
    allowed_chars = set("0123456789+-*/(). ")
    if not all(c in allowed_chars for c in cleaned):
        raise ValueError("Invalid characters in expression")

    try:
        # Using eval safely after strict character validation
        # Edge case: Division by zero will raise ZeroDivisionError
        result = eval(cleaned, {"__builtins__": {}}, {})
        
        # Handle potential complex numbers or invalid types resulting from eval
        if isinstance(result, complex):
            raise ValueError("Complex numbers not supported")
            
        return result
    except ZeroDivisionError:
        raise ZeroDivisionError("Division by zero is not allowed")
    except Exception as e:
        if isinstance(e, (ZeroDivisionError, ValueError)):
            raise e
        raise ValueError(f"Invalid mathematical expression: {e}")
