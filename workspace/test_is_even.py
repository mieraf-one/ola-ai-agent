import pytest
from is_even import is_even


@pytest.mark.parametrize(
    "number,expected",
    [
        (0, True),
        (2, True),
        (4, True),
        (-2, True),
        (-4, True),
        (1, False),
        (3, False),
        (-1, False),
        (-3, False),
    ],
)
def test_is_even(number, expected):
    assert is_even(number) == expected
