def is_even(n: int) -> bool:
    """
    Determine if an integer is even.

    Args:
        n (int): The integer to check.

    Returns:
        bool: True if the number is even, False otherwise.
    """
    return n % 2 == 0


if __name__ == "__main__":
    # Automatic demonstration
    demo_numbers = [0, 1, 2, -4, 7, -3]
    print("Running is_even demonstration:")
    for num in demo_numbers:
        print(f"is_even({num}) = {is_even(num)}")
