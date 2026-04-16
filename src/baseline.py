def merge(left, right):
    """Merge two sorted lists into one sorted list."""
    merged = []
    i = 0
    j = 0

    while i < len(left) and j < len(right):
        if left[i] <= right[j]:
            merged.append(left[i])
            i += 1
        else:
            merged.append(right[j])
            j += 1

    merged.extend(left[i:])
    merged.extend(right[j:])
    return merged


def merge_sort(arr):
    """Return a new sorted copy of arr using merge sort."""
    if len(arr) <= 1:
        return arr[:]

    mid = len(arr) // 2
    left = merge_sort(arr[:mid])
    right = merge_sort(arr[mid:])

    return merge(left, right)


def kth_smallest(arr, k):
    """
    Return the k-th smallest element in arr using the baseline approach:
    fully sort the array, then index the k-th element.

    Assumes k is 1-based.
    """
    if not 1 <= k <= len(arr):
        raise ValueError("k is out of range")

    sorted_arr = merge_sort(arr)
    return sorted_arr[k - 1]