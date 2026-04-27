def kth_smallest(A, k):
    # returns the kth smallest element in array A

    # baseline algorithm:
    # 1. sort the array using merge sort (based on textbook pseudocode)
    # 2. return element at index k-1 (0-based indexing)

    # assumes k is 1-based (i.e., k = 1 returns smallest element)

    if not 1 <= k <= len(A):
        raise ValueError("k is out of range")

    merge_sort(A)
    return A[k - 1]

def merge_sort(A):
    # sorts array A in nondecreasing order using merge sort (divide and conquer)

    # process:
    # - split A into two halves (B and C)
    # - recursively sort each half
    # - merge sorted halves back into A

    n = len(A)

    if n > 1:
        # divide step: split array into two halves
        mid = n // 2
        B = A[:mid]
        C = A[mid:]

        # conquer step: recursively sort halves
        merge_sort(B)
        merge_sort(C)

        # combine step: merge sorted halves into A
        merge(B, C, A)

def merge(B, C, A):
    # merges two sorted arrays B and C into array A
    # A is overwritten with the merged result

    i = 0  # index for B
    j = 0  # index for C
    k = 0  # index for A (output position)

    # compare elements from B and C and place the smaller into A
    while i < len(B) and j < len(C):
        if B[i] <= C[j]:
            A[k] = B[i]
            i += 1
        else:
            A[k] = C[j]
            j += 1
        k += 1

    # copy any remaining elements from B 
    while i < len(B):
        A[k] = B[i]
        i += 1
        k += 1

    # copy any remaining elements from C 
    while j < len(C):
        A[k] = C[j]
        j += 1
        k += 1