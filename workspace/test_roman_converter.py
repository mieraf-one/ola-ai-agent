"""Comprehensive pytest test suite for the Roman numeral converter module.

Citations:
    - knowledge_base:pytest_patterns: Parametrization & Edge Cases
"""

import pytest
from roman_converter import from_roman, to_roman


@pytest.mark.parametrize(
    "number,expected",
    [
        (1, "I"),
        (3, "III"),
        (4, "IV"),
        (5, "V"),
        (9, "IX"),
        (10, "X"),
        (40, "XL"),
        (50, "L"),
        (90, "XC"),
        (100, "C"),
        (400, "CD"),
        (500, "D"),
        (900, "CM"),
        (1000, "M"),
        (1994, "MCMXCIV"),
        (2023, "MMXXIII"),
        (3999, "MMMCMXCIX"),
    ],
)
def test_to_roman_valid(number, expected):
    assert to_roman(number) == expected


@pytest.mark.parametrize(
    "roman,expected",
    [
        ("I", 1),
        ("III", 3),
        ("iv", 4),
        ("V", 5),
        ("ix", 9),
        ("X", 10),
        ("XL", 40),
        ("L", 50),
        ("XC", 90),
        ("C", 100),
        ("CD", 400),
        ("D", 500),
        ("CM", 900),
        ("M", 1000),
        ("MCMXCIV", 1994),
        ("mmxxiii", 2023),
        ("MMMCMXCIX", 3999),
    ],
)
def test_from_roman_valid(roman, expected):
    assert from_roman(roman) == expected


@pytest.mark.parametrize(
    "invalid_input",
    [
        (0),
        (-1),
        (4000),
        (100.5),
        ("123"),
        (None),
    ],
)
def test_to_roman_invalid(invalid_input):
    with pytest.raises((ValueError, TypeError)):
        to_roman(invalid_input)


@pytest.mark.parametrize(
    "invalid_roman",
    [
        (""),
        ("IIII"),
        ("VV"),
        ("IC"),
        ("XM"),
        ("ABC"),
        (123),
        (None),
    ],
)
def test_from_roman_invalid(invalid_roman):
    with pytest.raises((ValueError, TypeError)):
        from_roman(invalid_roman)
