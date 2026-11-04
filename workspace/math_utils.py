"""
Module containing basic mathematical utility functions.
"""

def add(a: float, b: float) -> float:
    """
    Adds two numbers together and returns the result.

    Parameters:
    a (float or int): The first number to add.
    b (float or int): The second number to add.

    Returns:
    float or int: The sum of a and b.
    """
    return a + b


if __name__ == "__main__":
    # Automatic demonstration
    num1 = 5
    num2 = 7
    result = add(num1, num2)
    print(f"Demonstration: add({num1}, {num2}) = {result}")
