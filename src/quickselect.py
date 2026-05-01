def quickselect(arr, k):
    """
    Returns the kth smallest element (1-based index)
    Example: k=1 returns smallest element
    """

    if k < 1 or k > len(arr):
        raise ValueError("k is out of bounds")

    left = 0
    right = len(arr) - 1

    k_index = k - 1  # convert to 0-based index

    while left <= right:
        pivot_index = partition(arr, left, right)

        if pivot_index == k_index:
            return arr[pivot_index]
        elif pivot_index > k_index:
            right = pivot_index - 1
        else:
            left = pivot_index + 1

    return None  # should never reach here


def partition(arr, left, right):
    """
    Lomuto partition scheme
    Uses last element as pivot
    """

    pivot = arr[right]
    i = left

    for j in range(left, right):
        if arr[j] <= pivot:
            arr[i], arr[j] = arr[j], arr[i]
            i += 1

    # place pivot in correct position
    arr[i], arr[right] = arr[right], arr[i]
    return i


# Example usage
arr = [7, 10, 4, 3, 20, 15]
k = 3

result = quickselect(arr, k)
print(f"{k}rd smallest element is:", result)
