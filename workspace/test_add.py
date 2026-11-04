import pytest
from add import add

def test_add_positive_numbers():
    assert add(2, 3) == 5

def test_add_negative_numbers():
    assert add(-1, -1) == -2

def test_add_mixed_numbers():
    assert add(-5, 10) == 5

def test_add_floats():
    assert add(1.5, 2.5) == 4.0
