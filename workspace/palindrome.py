import re


def is_palindrome(text: str) -> bool:
    """
    Determine if a given string is a palindrome.
    
    Handles spaces, capitalization, and punctuation by removing them
    and comparing the normalized string with its reverse.
    
    Args:
        text (str): The string to check.
        
    Returns:
        bool: True if the string is a palindrome, False otherwise.
    """
    if not isinstance(text, str):
        raise TypeError("Input must be a string")
    
    # Remove all non-alphanumeric characters and convert to lowercase
    cleaned = re.sub(r'[^a-zA-Z0-9]', '', text).lower()
    
    return cleaned == cleaned[::-1]


if __name__ == "__main__":
    # Automatic demonstration
    samples = [
        "A man, a plan, a canal: Panama",
        "race a car",
        "Madam, I'm Adam",
        "Was it a car or a cat I saw?",
        "hello",
        ""
    ]
    
    print("--- Palindrome Checker Demonstration ---\n")
    for sample in samples:
        result = is_palindrome(sample)
        print(f"'{sample}' -> Palindrome: {result}")
