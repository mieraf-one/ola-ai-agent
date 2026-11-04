def factorial(n: int) -> int:
    """Calculate the factorial of a non-negative integer n."""
    if not isinstance(n, int):
        raise TypeError("Factorial is only defined for integers.")
    if n < 0:
        raise ValueError("Factorial is not defined for negative numbers.")
    
    # Base cases for 0 and 1
    if n == 0 or n == 1:
        return 1
        
    # Iterative logic to compute factorial for integers greater than 1
    result = 1
    for i in range(2, n + 1):
        result *= i
        
    return result


if __name__ == "__main":
    # Automatic demonstration
    for num in [0, 1, 5, 10]:
        print(f"factorial({num}) = {factorial(num)}")
