import pytest
from palindrome import is_palindrome


@pytest.mark.parametrize("text,expected", [
    ("racecar", True),
    ("A man, a plan, a canal: Panama", True),
    ("Madam, I'm Adam", True),
    ("Was it a car or a cat I saw?", True),
    ("No 'x' in Nixon", True),
    ("12321", True),
    ("a", True),
    ("", True),
])
def test_is_palindrome_true(text, expected):
    assert is_palindrome(text) == expected


@pytest.mark.parametrize("text,expected", [
    ("hello", False),
    ("race a car", False),
    ("openai", False),
    ("12345", False),
    ("ab", False),
])
def test_is_palindrome_false(text, expected):
    assert is_palindrome(text) == expected


def test_is_palindrome_invalid_type():
    with pytest.raises(TypeError):
        is_palindrome(None)  # type: ignore
    
    with pytest.raises(TypeError):
        is_palindrome(12321)  # type: ignore
