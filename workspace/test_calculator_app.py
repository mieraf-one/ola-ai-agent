"""
Unit tests for the calculator backend logic matching the arithmetic operations.
"""

import pytest
from calculator_app import CalculatorBackend

def test_add():
    assert CalculatorBackend.add(2, 3) == 5
    assert CalculatorBackend.add(-1, 1) == 0

def test_subtract():
    assert CalculatorBackend.subtract(5, 2) == 3
    assert CalculatorBackend.subtract(2, 5) == -3

def test_multiply():
    assert CalculatorBackend.multiply(3, 4) == 12
    assert CalculatorBackend.multiply(-2, 3) == -6

def test_divide():
    assert CalculatorBackend.divide(10, 2) == 5
    assert CalculatorBackend.divide(7, 2) == 3.5

def test_divide_by_zero():
    with pytest.raises(ValueError, match="Division by zero"):
        CalculatorBackend.divide(5, 0)
