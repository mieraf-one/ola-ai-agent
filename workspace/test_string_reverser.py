import pytest
from string_reverser import reverse_string

def test_standard_string():
    assert reverse_string("hello") == "olleh"
    assert reverse_string("Python") == "nohtyP"

def test_empty_string():
    assert reverse_string("") == ""

def test_single_character():
    assert reverse_string("a") == "a"

def test_special_characters_and_spaces():
    assert reverse_string("Hello, World!") == "!dlroW ,olleH"
    assert reverse_string("   spaces   ") == "   secaps   "

def test_unicode_characters():
    assert reverse_string("café") == "éfac"

def test_invalid_input():
    with pytest.raises(TypeError):
        reverse_string(12345)  # type: ignore
