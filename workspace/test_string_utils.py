import pytest
from string_utils import reverse_string


def test_reverse_string_standard():
    """Test reversing a standard alphanumeric string."""
    assert reverse_string("abc123xyz") == "zyx321cba"
    assert reverse_string("Hello, World!") == "!dlroW ,olleH"


def test_reverse_string_edge_cases():
    """Test edge cases like an empty string and a single-character string."""
    assert reverse_string("") == ""
    assert reverse_string("a") == "a"


def test_reverse_string_palindrome():
    """Test that a palindrome remains unchanged when reversed."""
    assert reverse_string("racecar") == "racecar"
