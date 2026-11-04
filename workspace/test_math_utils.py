"""
Unit tests for the math_utils module using pytest.
"""

import pytest
from math_utils import add


def test_add_positive_numbers():
    assert add(2, 3) == 5


def test_add_negative_numbers():
    assert add(-1, -1) == -2


def test_add_mixed_numbers():
    assert add(-5, 10) == 5


def test_add_floats():
    assert add(2.5, 3.1) == pytest.approx(5.6)


def test_add_zero():
    assert add(0, 5) == 5
    assert add(0, 0) == 0
