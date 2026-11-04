def reverse_string(s: str) -> str:
    """
    Reverses the given string using Python's slice notation.
    
    Args:
        s (str): The string to reverse.
        
    Returns:
        str: The reversed string.
    """
    return s[::-1]


if __name__ == "__main__":
    # Automatic demonstration
    sample = "Hello, World!"
    reversed_sample = reverse_string(sample)
    print(f"Original: {sample}")
    print(f"Reversed: {reversed_sample}")
