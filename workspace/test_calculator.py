import pytest
from calculator import calculate

def test_basic_operations():
    assert calculate("2 + 3") == 5
    assert calculate("10 - 4") == 6
    assert calculate("3 * 4") == 12
    assert calculate("8 / 2") == 4.0

def test_edge_cases_zero_and_negative():
    assert calculate("0 + 0") == 0
    assert calculate("-5 + 3") == -2
    assert calculate("5 * 0") == 0
    assert calculate("0 / 5") == 0.0

def test_empty_and_invalid_inputs():
    with pytest.raises(ValueError):
        calculate("")
    with pytest.raises(ValueError):
        calculate("   ")
    with pytest.raises(ValueError):
        calculate(None) # type: ignore
    with pytest.raises(ValueError):
        calculate("2 + __import__('os')")

def test_division_by_zero():
    with pytest.raises(ZeroDivisionError):
        calculate("5 / 0")
    with pytest.raises(ZeroDivisionError):
        calculate("10 / (2 - 2)")
