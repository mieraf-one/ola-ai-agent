def binary_search(arr, target):
    """
    Perform binary search on a sorted list 'arr' to find the index of 'target'.
    Returns the index if found, else -1.
    """
    left = 0
    right = len(arr) - 1

    while left <= right:
        mid = left + (right - left) // 2
        if arr[mid] == target:
            return mid
        elif arr[mid] < target:
            left = mid + 1
        else:
            right = mid - 1

    return -1
