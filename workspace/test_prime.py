import pytest
from prime import is_prime

@pytest.mark.parametrize("number", [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 97, 104729])
def test_prime_numbers(number):
    assert is_prime(number) is True

@pytest.mark.parametrize("number", [-10, -1, 0, 1, 4, 6, 8, 9, 10, 15, 25, 100, 1000])
def test_composite_and_edge_numbers(number):
    assert is_prime(number) is False

def test_negative_primes_concept():
    # Negative numbers are not considered prime
    assert is_prime(-7) is False

def test_large_prime():
    # 7919 is a known prime number
    assert is_prime(7919) is True
    # 7920 is composite
    assert is_prime(7920) is False
