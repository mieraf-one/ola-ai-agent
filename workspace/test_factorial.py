import pytest
from factorial import factorial


def test_factorial_base_cases():
    assert factorial(0) == 1
    assert factorial(1) == 1


def test_factorial_positive_numbers():
    assert factorial(2) == 2
    assert factorial(3) == 6
    assert factorial(5) == 120
    assert factorial(10) == 3628800


def test_factorial_negative_numbers():
    with pytest.raises(ValueError):
        factorial(-1)
    with pytest.raises(ValueError):
        factorial(-5)


def test_factorial_invalid_types():
    with pytest.raises(TypeError):
        factorial(3.5)  # type: ignore
    with pytest.raises(TypeError):
        factorial("5")  # type: ignore
