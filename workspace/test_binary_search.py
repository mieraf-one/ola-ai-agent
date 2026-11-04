import pytest
from binary_search import binary_search


def test_binary_search_found():
    arr = [1, 3, 5, 7, 9, 11]
    assert binary_search(arr, 7) == 3
    assert binary_search(arr, 1) == 0
    assert binary_search(arr, 11) == 5


def test_binary_search_not_found():
    arr = [1, 3, 5, 7, 9, 11]
    assert binary_search(arr, 4) == -1
    assert binary_search(arr, 0) == -1
    assert binary_search(arr, 12) == -1


def test_binary_search_empty_and_single():
    assert binary_search([], 5) == -1
    assert binary_search([5], 5) == 0
    assert binary_search([5], 3) == -1
