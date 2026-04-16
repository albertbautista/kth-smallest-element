from baseline import kth_smallest as baseline_kth
from quickselect import kth_smallest as quickselect_kth


def main():
    # Example array
    arr = [8, 2, 6, 4, 1, 5]
    k = 3

    print("Array:", arr)
    print(f"{k}-th smallest element:\n")

    baseline_result = baseline_kth(arr[:], k)
    quickselect_result = quickselect_kth(arr[:], k)

    print("Baseline (merge sort):", baseline_result)
    print("Quickselect:", quickselect_result)


if __name__ == "__main__":
    main()