import sys
import os
import random
import time
import tracemalloc
from datetime import datetime

import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))
from baseline import kth_smallest as mergesort_kth
from quickselect import kth_smallest as quickselect_kth

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------
MERGESORT_SIZES = [128, 256, 512, 1024, 2048, 4096, 8192, 16384,
                   32768, 65536, 131072, 262144, 524288, 1048576]
QUICKSELECT_SIZES = [100, 1000, 10000, 100000, 1000000]
RUNS = 5

RESULTS_DIR = os.path.join(os.path.dirname(__file__), '..', 'results')
RUNTIME_TXT = os.path.join(RESULTS_DIR, 'runtime.txt')

# ---------------------------------------------------------------------------
# Chart styling constants (shared across all charts)
# ---------------------------------------------------------------------------
C_MS  = '#0077BB'   # blue   — mergesort
C_QS  = '#EE7733'   # orange — quickselect
C_REF = '#9B59B6'   # purple — reference curves

STYLE = {
    'data_lw':   2.5,
    'ref_lw':    1.5,
    'ms_marker': 'o',
    'qs_marker': 's',
    'markersize': 6,
    'title_fs':  14,
    'label_fs':  12,
    'tick_fs':   10,
    'legend_fs': 10,
    'annot_fs':   9,
}

plt.rcParams.update({
    'axes.facecolor':   '#F8F8F8',
    'figure.facecolor': 'white',
    'axes.spines.top':   False,
    'axes.spines.right': False,
})


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
def make_array(n):
    """Return a fresh random array of n distinct integers."""
    return random.sample(range(n * 10), n)


def bench_one(fn, n, runs=RUNS, base_seed=None):
    """
    Run fn(arr, k) `runs` times on independently generated arrays.

    Fixed-seed mode (base_seed is not None): sets random.seed(base_seed + i)
    before each trial so results are fully reproducible.
    Random-seed mode (base_seed is None): relies on whatever global random
    state was set before the benchmark loop began.

    Returns (avg_time_seconds, avg_peak_bytes, status_string).
    """
    k = n // 2
    times = []
    peaks = []
    status = 'PASS'

    for i in range(runs):
        if base_seed is not None:
            random.seed(base_seed + i)

        arr = make_array(n)
        expected = sorted(arr)[k - 1]

        # --- timing (array generation excluded) ---
        t0 = time.perf_counter()
        result = fn(arr[:], k)          # copy so fn may sort in-place
        t1 = time.perf_counter()
        times.append(t1 - t0)

        # --- memory (fresh array, same trial seed offset) ---
        if base_seed is not None:
            random.seed(base_seed + i + 10000)  # distinct offset → different array
        arr2 = make_array(n)
        tracemalloc.start()
        fn(arr2[:], k)
        _, peak = tracemalloc.get_traced_memory()
        tracemalloc.stop()
        peaks.append(peak)

        # --- correctness ---
        if result != expected:
            status = f'FAIL (got {result}, expected {expected})'

    avg_time = sum(times) / len(times)
    avg_peak = sum(peaks) / len(peaks)
    return avg_time, avg_peak, status


def fmt_row(n, avg_time, avg_peak_bytes, status):
    """Format one result row with consistent column widths."""
    peak_kb = avg_peak_bytes / 1024
    return (f"n={n:<10}  avg_time={avg_time:.6f}s    "
            f"peak_mem={peak_kb:>7.1f}KB    status={status}")


# ---------------------------------------------------------------------------
# Chart helpers
# ---------------------------------------------------------------------------
def save_runtime_chart(ms_times, qs_times, path, title_suffix):
    ms_ns   = sorted(ms_times)
    ms_vals = [ms_times[n] for n in ms_ns]
    qs_ns   = sorted(qs_times)
    qs_vals = [qs_times[n] for n in qs_ns]

    fig, ax = plt.subplots(figsize=(10, 6))

    ax.plot(ms_ns, ms_vals,
            marker=STYLE['ms_marker'], markersize=STYLE['markersize'],
            linewidth=STYLE['data_lw'], color=C_MS,
            label='Mergesort (baseline)', zorder=3)
    ax.plot(qs_ns, qs_vals,
            marker=STYLE['qs_marker'], markersize=STYLE['markersize'],
            linewidth=STYLE['data_lw'], color=C_QS,
            label='Quickselect (improved)', zorder=3)

    # Θ(n log n) reference anchored to first mergesort data point
    n0_ms, t0_ms = ms_ns[0], ms_vals[0]
    C_nlogn = t0_ms / (n0_ms * np.log2(n0_ms))
    ref_ns_ms = np.array(ms_ns)
    ax.plot(ref_ns_ms, C_nlogn * ref_ns_ms * np.log2(ref_ns_ms),
            linestyle='--', linewidth=STYLE['ref_lw'], color=C_REF,
            label='Θ(n log n) reference', zorder=2)

    # Θ(n) reference anchored to first quickselect data point
    n0_qs, t0_qs = qs_ns[0], qs_vals[0]
    C_n = t0_qs / n0_qs
    ref_ns_qs = np.array(qs_ns)
    ax.plot(ref_ns_qs, C_n * ref_ns_qs,
            linestyle=':', linewidth=STYLE['ref_lw'], color=C_REF,
            label='Θ(n) avg case', zorder=2)

    ax.set_xscale('log')
    ax.set_yscale('log')
    ax.set_xlabel('Input size n', fontsize=STYLE['label_fs'])
    ax.set_ylabel('Average runtime (seconds)', fontsize=STYLE['label_fs'])
    ax.set_title(f'Runtime vs Input Size: Mergesort vs Quickselect\n{title_suffix}',
                 fontsize=STYLE['title_fs'], fontweight='bold', pad=12)
    ax.tick_params(labelsize=STYLE['tick_fs'])
    ax.grid(True, which='major', linestyle='-',  alpha=0.4, color='#CCCCCC')
    ax.grid(True, which='minor', linestyle=':', alpha=0.2, color='#CCCCCC')
    ax.legend(fontsize=STYLE['legend_fs'], framealpha=0.9, edgecolor='#CCCCCC')

    ax.annotate(
        "Quickselect worst case is Θ(n²) but not reflected here —\n"
        "random input arrays used throughout.",
        xy=(0.02, 0.97), xycoords='axes fraction',
        va='top', ha='left', fontsize=STYLE['annot_fs'],
        color='#555555',
        bbox=dict(boxstyle='round,pad=0.4', fc='white', ec='#CCCCCC', alpha=0.8),
    )

    fig.tight_layout()
    fig.savefig(path, dpi=150, bbox_inches='tight')
    plt.close(fig)
    print(f"  Runtime chart saved to {path}")


def save_memory_chart(ms_times, ms_peaks, qs_times, qs_peaks, path, title_suffix):
    ms_ns = sorted(ms_times)
    qs_ns = sorted(qs_times)

    ms_pmem = [ms_peaks[n] / 1024 for n in ms_ns]
    qs_pmem = [qs_peaks[n] / 1024 for n in qs_ns]

    common_ns = sorted(set(ms_peaks) & set(qs_peaks))
    crossover_n = None
    for n in common_ns:
        if qs_peaks[n] >= ms_peaks[n]:
            crossover_n = n
            break

    n0_ms = ms_ns[0]
    n0_qs = qs_ns[0]
    ref_ns_ms = np.array(ms_ns)
    ref_ns_qs = np.array(qs_ns)

    fig, ax = plt.subplots(figsize=(10, 6))

    ax.plot(ms_ns, ms_pmem,
            marker=STYLE['ms_marker'], markersize=STYLE['markersize'],
            linewidth=STYLE['data_lw'], color=C_MS,
            label='Mergesort (baseline)', zorder=3)
    ax.plot(qs_ns, qs_pmem,
            marker=STYLE['qs_marker'], markersize=STYLE['markersize'],
            linewidth=STYLE['data_lw'], color=C_QS,
            label='Quickselect (improved)', zorder=3)

    # Θ(n) reference for mergesort memory
    pm0_ms = ms_pmem[0]
    C_mem_ms = pm0_ms / n0_ms
    ax.plot(ref_ns_ms, C_mem_ms * ref_ns_ms,
            linestyle='--', linewidth=STYLE['ref_lw'], color=C_REF,
            label='Θ(n) reference', zorder=2)

    # Θ(log n) reference for quickselect memory
    pm0_qs = qs_pmem[0]
    C_mem_qs = pm0_qs / np.log2(n0_qs)
    ax.plot(ref_ns_qs, C_mem_qs * np.log2(ref_ns_qs),
            linestyle=':', linewidth=STYLE['ref_lw'], color=C_REF,
            label='Θ(log n) avg case stack', zorder=2)

    if crossover_n is not None:
        cx_ms_kb = ms_peaks[crossover_n] / 1024
        cx_qs_kb = qs_peaks[crossover_n] / 1024
        cx_y = (cx_ms_kb + cx_qs_kb) / 2
        ax.annotate(
            f'Crossover at n={crossover_n}',
            xy=(crossover_n, cx_y),
            xytext=(crossover_n * 1.5, cx_y * 2),
            arrowprops=dict(arrowstyle='->', color='#333333'),
            fontsize=STYLE['annot_fs'], color='#333333',
        )
    else:
        if common_ns:
            qs_lower = all(qs_peaks[n] < ms_peaks[n] for n in common_ns)
            ms_lower = all(ms_peaks[n] < qs_peaks[n] for n in common_ns)
            if qs_lower:
                note = "Quickselect uses less memory across all tested sizes"
            elif ms_lower:
                note = "Mergesort uses less memory across all tested sizes"
            else:
                note = "No consistent dominance across tested sizes"
        else:
            note = "No overlapping sizes between algorithms"
        ax.text(0.02, 0.97, note, transform=ax.transAxes,
                va='top', ha='left', fontsize=STYLE['annot_fs'],
                color='#555555',
                bbox=dict(boxstyle='round,pad=0.4', fc='white',
                          ec='#CCCCCC', alpha=0.8))

    ax.set_xscale('log')
    ax.set_yscale('log')
    ax.set_xlabel('Input size n', fontsize=STYLE['label_fs'])
    ax.set_ylabel('Peak auxiliary memory (KB)', fontsize=STYLE['label_fs'])
    ax.set_title(
        f'Auxiliary Memory vs Input Size: Mergesort vs Quickselect\n{title_suffix}',
        fontsize=STYLE['title_fs'], fontweight='bold', pad=12)
    ax.tick_params(labelsize=STYLE['tick_fs'])
    ax.grid(True, which='major', linestyle='-',  alpha=0.4, color='#CCCCCC')
    ax.grid(True, which='minor', linestyle=':', alpha=0.2, color='#CCCCCC')
    ax.legend(fontsize=STYLE['legend_fs'], framealpha=0.9, edgecolor='#CCCCCC')

    fig.tight_layout()
    fig.savefig(path, dpi=150, bbox_inches='tight')
    plt.close(fig)
    print(f"  Memory chart saved to {path}")


def save_comparison_chart(qs_times_fixed, seed_fixed, qs_times_random, seed_random):
    """Overlay quickselect runtime from both seed modes on one log-log axes."""
    path = os.path.join(RESULTS_DIR, 'quickselect_seed_comparison.png')

    qs_ns_fixed  = sorted(qs_times_fixed)
    qs_ns_random = sorted(qs_times_random)
    vals_fixed   = [qs_times_fixed[n]  for n in qs_ns_fixed]
    vals_random  = [qs_times_random[n] for n in qs_ns_random]

    # Θ(n) reference anchored to the fixed-seed run
    n0, t0 = qs_ns_fixed[0], vals_fixed[0]
    C_n = t0 / n0
    ref_ns = np.array(qs_ns_fixed)

    fig, ax = plt.subplots(figsize=(10, 6))

    ax.plot(qs_ns_fixed, vals_fixed,
            marker=STYLE['qs_marker'], markersize=STYLE['markersize'],
            linewidth=STYLE['data_lw'], color='#0077BB',
            label=f'Fixed seed (seed={seed_fixed})', zorder=3)
    ax.plot(qs_ns_random, vals_random,
            marker='D', markersize=STYLE['markersize'],
            linewidth=STYLE['data_lw'], color='#EE7733',
            label=f'Random seed (seed={seed_random})', zorder=3)
    ax.plot(ref_ns, C_n * ref_ns,
            linestyle='--', linewidth=STYLE['ref_lw'], color=C_REF,
            label='Θ(n) avg case', zorder=2)

    ax.set_xscale('log')
    ax.set_yscale('log')
    ax.set_xlabel('Input size n', fontsize=STYLE['label_fs'])
    ax.set_ylabel('Average runtime (seconds)', fontsize=STYLE['label_fs'])
    ax.set_title('Quickselect Runtime: Fixed Seed vs Random Seed',
                 fontsize=STYLE['title_fs'], fontweight='bold', pad=12)
    ax.tick_params(labelsize=STYLE['tick_fs'])
    ax.grid(True, which='major', linestyle='-',  alpha=0.4, color='#CCCCCC')
    ax.grid(True, which='minor', linestyle=':', alpha=0.2, color='#CCCCCC')
    ax.legend(fontsize=STYLE['legend_fs'], framealpha=0.9, edgecolor='#CCCCCC')

    ax.annotate(
        "Both lines should track Θ(n) — confirming average-case behavior\n"
        "is independent of the specific input family.",
        xy=(0.02, 0.97), xycoords='axes fraction',
        va='top', ha='left', fontsize=STYLE['annot_fs'],
        color='#555555',
        bbox=dict(boxstyle='round,pad=0.4', fc='white', ec='#CCCCCC', alpha=0.8),
    )

    fig.tight_layout()
    fig.savefig(path, dpi=150, bbox_inches='tight')
    plt.close(fig)
    print(f"  Comparison chart saved to {path}")


# ---------------------------------------------------------------------------
# Single benchmark run
# ---------------------------------------------------------------------------
def run_single(mode_label, seed, is_fixed):
    """
    Run the full benchmark suite under one seed mode.

    Fixed mode:  bench_one re-seeds per trial using seed + trial_index,
                 making every measurement individually reproducible.
    Random mode: global RNG is seeded once before all trials and then
                 left to flow naturally — simulates arbitrary input families.

    Returns (ms_times, ms_peaks, qs_times, qs_peaks).
    """
    base_seed = seed if is_fixed else None
    if not is_fixed:
        random.seed(seed)

    suffix = 'fixed' if is_fixed else 'random'

    ms_times = {}
    ms_peaks = {}
    qs_times = {}
    qs_peaks = {}
    ms_rows  = []
    qs_rows  = []

    print(f"\n{'='*60}")
    print(f"[Mode: {mode_label} | seed={seed}]")
    print(f"{'='*60}")

    print("  Benchmarking baseline (mergesort)...")
    for n in MERGESORT_SIZES:
        avg_time, avg_peak, status = bench_one(mergesort_kth, n, base_seed=base_seed)
        ms_times[n] = avg_time
        ms_peaks[n] = avg_peak
        ms_rows.append(fmt_row(n, avg_time, avg_peak, status))
        print(f"    mergesort  {ms_rows[-1]}")

    print("  Benchmarking quickselect...")
    for n in QUICKSELECT_SIZES:
        avg_time, avg_peak, status = bench_one(quickselect_kth, n, base_seed=base_seed)
        qs_times[n] = avg_time
        qs_peaks[n] = avg_peak
        qs_rows.append(fmt_row(n, avg_time, avg_peak, status))
        print(f"    quickselect  {qs_rows[-1]}")

    # --- summary ---
    common_ns = sorted(set(ms_peaks) & set(qs_peaks))
    crossover_n = None
    for n in common_ns:
        if qs_peaks[n] >= ms_peaks[n]:
            crossover_n = n
            break
    crossover_str = f"n={crossover_n}" if crossover_n is not None else "no crossover detected"

    qs_at_1M = qs_times.get(1000000)
    ms_at_1M = ms_times.get(1000000)
    if qs_at_1M is not None and ms_at_1M is not None:
        fastest_str = (f"quickselect ({qs_at_1M:.6f}s) vs "
                       f"mergesort ({ms_at_1M:.6f}s)")
    elif qs_at_1M is not None:
        fastest_str = f"quickselect ({qs_at_1M:.6f}s) [mergesort not tested at this size]"
    else:
        fastest_str = "data unavailable"

    # --- write runtime.txt ---
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    sep  = '=' * 60
    dash = '-' * 60
    lines = [
        sep,
        f"Run timestamp: {timestamp}",
        f"[Mode: {mode_label} | seed={seed}]",
        sep,
        '',
        '[BASELINE - Mergesort] (n must be power of 2, k = n//2)',
    ] + ms_rows + [
        '',
        '[IMPROVED - Quickselect] (avg case Theta(n), random input, k = n//2)',
    ] + qs_rows + [
        '',
        dash,
        'SUMMARY',
        f'Crossover point (memory): {crossover_str}',
        f'Fastest algorithm at n=1000000: {fastest_str}',
        dash,
        '',
    ]

    with open(RUNTIME_TXT, 'a') as f:
        f.write('\n'.join(lines) + '\n')
    print(f"\n  Results appended to {RUNTIME_TXT}")

    # --- charts ---
    title_suffix = f'[Mode: {mode_label} | seed={seed}]'
    save_runtime_chart(
        ms_times, qs_times,
        os.path.join(RESULTS_DIR, f'runtime_chart_{suffix}.png'),
        title_suffix,
    )
    save_memory_chart(
        ms_times, ms_peaks, qs_times, qs_peaks,
        os.path.join(RESULTS_DIR, f'memory_chart_{suffix}.png'),
        title_suffix,
    )

    return ms_times, ms_peaks, qs_times, qs_peaks


# ---------------------------------------------------------------------------
if __name__ == '__main__':
    os.makedirs(RESULTS_DIR, exist_ok=True)

    # RUN 1 — fixed seed (reproducible baseline)
    FIXED_SEED = 42
    _, _, qs_times_fixed, _ = run_single(
        mode_label='Fixed Seed', seed=FIXED_SEED, is_fixed=True
    )

    # RUN 2 — random seed (generalization check)
    random.seed(None)
    rand_seed = random.randrange(2**32)
    _, _, qs_times_random, _ = run_single(
        mode_label='Random Seed', seed=rand_seed, is_fixed=False
    )

    # Chart 5 — quickselect overlay: fixed vs random
    print(f"\n{'='*60}")
    print("Generating quickselect seed comparison chart...")
    save_comparison_chart(qs_times_fixed, FIXED_SEED, qs_times_random, rand_seed)
