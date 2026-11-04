"""
Roman Numeral Converter Module.

Handles bidirectional conversion between integers and Roman numerals,
with strict validation for bounds and formatting.
"""

import re


# Mapping for integer to roman conversion
VAL_MAP = [
    (1000, 'M'),
    (900, 'CM'),
    (500, 'D'),
    (400, 'CD'),
    (100, 'C'),
    (90, 'XC'),
    (50, 'L'),
    (40, 'XL'),
    (10, 'X'),
    (9, 'IX'),
    (5, 'V'),
    (4, 'IV'),
    (1, 'I'),
]

# Regex pattern to validate standard Roman numeral strings
ROMAN_REGEX = re.compile(
    r"^M{0,3}(CM|CD|D?C{0,3})(XC|XL|L?X{0,3})(IX|IV|V?I{0,3})$",
    re.IGNORECASE,
)


def to_roman(number: int) -> str:
    """Convert an integer to a Roman numeral string.

    Args:
        number: An integer between 1 and 3999 inclusive.

    Returns:
        The corresponding Roman numeral string.

    Raises:
        TypeError: If number is not an integer.
        ValueError: If number is out of the valid range (1-3999).
    """
    if not isinstance(number, int):
        raise TypeError("Input must be an integer")
    if not (1 <= number <= 3999):
        raise ValueError("Number must be between 1 and 3999 inclusive")

    result = []
    for val, symbol in VAL_MAP:
        if number == 0:
            break
        count, number = divmod(number, val)
        result.append(symbol * count)

    return "".join(result)


def from_roman(roman: str) -> int:
    """Convert a Roman numeral string to an integer.

    Args:
        roman: A valid Roman numeral string (case-insensitive).

    Returns:
        The corresponding integer value.

    Raises:
        TypeError: If input is not a string.
        ValueError: If string is empty or invalid.
    """
    if not isinstance(roman, str):
        raise TypeError("Input must be a string")

    roman_upper = roman.upper()
    if not roman_upper:
        raise ValueError("Input string cannot be empty")

    if not ROMAN_REGEX.match(roman_upper):
        raise ValueError(f"Invalid Roman numeral format: '{roman}'")

    roman_map = {'I': 1, 'V': 5, 'X': 10, 'L': 50, 'C': 100, 'D': 500, 'M': 1000}

    total = 0
    prev_value = 0

    for char in reversed(roman_upper):
        value = roman_map[char]
        if value < prev_value:
            total -= value
        else:
            total += value
            prev_value = value

    return total


if __name__ == '__main__':
    print("Demonstration of Roman Numeral Converter:")
    demo_pairs = [(1994, to_roman(1994)), (3999, to_roman(3999)), ('MCMXCIV', from_roman('MCMXCIV'))]
    for original, converted in demo_pairs:
        print(f"{original} -> {converted}")
