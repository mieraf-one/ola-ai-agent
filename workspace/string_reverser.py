def reverse_string(s: str) -> str:
    """
    Reverses the input string using Python's slice notation.
    
    Args:
        s (str): The string to reverse.
        
    Returns:
        str: The reversed string.
    """
    if not isinstance(s, str):
        raise TypeError("Input must be a string")
    return s[::-1]

if __name__ == "__main__":
    # Automatic demonstration
    sample_strings = [("Hello, World!"), ("Python"), (""), ("12345"), ("a\u00e9i\u00f3u")]
    for original in sample_strings:
        print(f"Original: {original!r} -> Reversed: {reverse_string(original)!r}")
