"""Comprehensive performance and memory benchmarking suite across 5,000,000 ticks."""

import gc
import time
import tracemalloc
from typing import Callable, Dict, Tuple
import pyarrow as pa
from tick_bench.generator import generate_tick_table
from tick_bench.pipelines import ArrowComputePipeline, DuckDBPipeline, PolarsPipeline


def profile_operation(func: Callable[[], object]) -> Tuple[float, float]:
    """Execute target function while measuring wall time and peak heap memory."""
    gc.collect()
    tracemalloc.start()
    t0 = time.perf_counter()
    _ = func()
    t1 = time.perf_counter()
    _, peak_bytes = tracemalloc.get_traced_memory()
    tracemalloc.stop()

    duration_sec = t1 - t0
    peak_mb = peak_bytes / (1024 * 1024)
    return duration_sec, peak_mb


def run_benchmark(num_ticks: int = 5_000_000) -> None:
    print(f"[*] Generating {num_ticks:,} synthetic market ticks in Arrow Table format...")
    t_gen_start = time.perf_counter()
    table = generate_tick_table(num_ticks=num_ticks, seed=42)
    print(f"[*] Dataset ready in {time.perf_counter() - t_gen_start:.2f}s | Uncompressed Size: {table.nbytes / (1024 * 1024):.1f} MB")

    duck_pipe = DuckDBPipeline()

    benchmarks: Dict[str, Dict[str, Tuple[float, float]]] = {
        "Cumulative VWAP": {},
        "1-Second OHLCV Resampling": {},
    }

    # 1. Benchmark VWAP
    print("\n[*] Running Task 1: Cumulative VWAP Aggregation...")
    
    # Polars
    dur, mem = profile_operation(lambda: PolarsPipeline.compute_vwap(table))
    benchmarks["Cumulative VWAP"]["Polars"] = (dur, mem)

    # DuckDB
    dur, mem = profile_operation(lambda: duck_pipe.compute_vwap(table))
    benchmarks["Cumulative VWAP"]["DuckDB"] = (dur, mem)

    # Arrow Compute Kernel
    dur, mem = profile_operation(lambda: ArrowComputePipeline.compute_vwap(table))
    benchmarks["Cumulative VWAP"]["PyArrow"] = (dur, mem)

    # 2. Benchmark OHLCV Resampling
    print("[*] Running Task 2: 1-Second Window OHLCV + VWAP Resampling...")

    # Polars
    dur, mem = profile_operation(lambda: PolarsPipeline.resample_1s_ohlcv(table))
    benchmarks["1-Second OHLCV Resampling"]["Polars"] = (dur, mem)

    # DuckDB
    dur, mem = profile_operation(lambda: duck_pipe.resample_1s_ohlcv(table))
    benchmarks["1-Second OHLCV Resampling"]["DuckDB"] = (dur, mem)

    # Print Formatted Report
    print("\n" + "=" * 78)
    print(f"       TICK-BENCH PERFORMANCE REPORT ({num_ticks:,} TICKS)")
    print("=" * 78)

    for task_name, results in benchmarks.items():
        print(f"\n>> Task: {task_name}")
        print(f"{'Engine':<12} | {'Time (s)':<10} | {'Throughput (ticks/s)':<22} | {'Peak RAM (MB)':<12}")
        print("-" * 65)
        for engine, (dur, mem) in results.items():
            throughput = num_ticks / dur
            print(f"{engine:<12} | {dur:<10.4f} | {throughput:>18,.0f} | {mem:>10.2f} MB")

    print("\n" + "=" * 78)


if __name__ ==

cat << 'EOF' > benchmarks/run_benchmark.py
"""Comprehensive performance and memory benchmarking suite across 5,000,000 ticks."""

import gc
import time
import tracemalloc
from typing import Callable, Dict, Tuple
import pyarrow as pa
from tick_bench.generator import generate_tick_table
from tick_bench.pipelines import ArrowComputePipeline, DuckDBPipeline, PolarsPipeline


def profile_operation(func: Callable[[], object]) -> Tuple[float, float]:
    """Execute target function while measuring wall time and peak heap memory."""
    gc.collect()
    tracemalloc.start()
    t0 = time.perf_counter()
    _ = func()
    t1 = time.perf_counter()
    _, peak_bytes = tracemalloc.get_traced_memory()
    tracemalloc.stop()

    duration_sec = t1 - t0
    peak_mb = peak_bytes / (1024 * 1024)
    return duration_sec, peak_mb


def run_benchmark(num_ticks: int = 5_000_000) -> None:
    print(f"[*] Generating {num_ticks:,} synthetic market ticks in Arrow Table format...")
    t_gen_start = time.perf_counter()
    table = generate_tick_table(num_ticks=num_ticks, seed=42)
    print(f"[*] Dataset ready in {time.perf_counter() - t_gen_start:.2f}s | Uncompressed Size: {table.nbytes / (1024 * 1024):.1f} MB")

    duck_pipe = DuckDBPipeline()

    benchmarks: Dict[str, Dict[str, Tuple[float, float]]] = {
        "Cumulative VWAP": {},
        "1-Second OHLCV Resampling": {},
    }

    # 1. Benchmark VWAP
    print("\n[*] Running Task 1: Cumulative VWAP Aggregation...")
    
    # Polars
    dur, mem = profile_operation(lambda: PolarsPipeline.compute_vwap(table))
    benchmarks["Cumulative VWAP"]["Polars"] = (dur, mem)

    # DuckDB
    dur, mem = profile_operation(lambda: duck_pipe.compute_vwap(table))
    benchmarks["Cumulative VWAP"]["DuckDB"] = (dur, mem)

    # Arrow Compute Kernel
    dur, mem = profile_operation(lambda: ArrowComputePipeline.compute_vwap(table))
    benchmarks["Cumulative VWAP"]["PyArrow"] = (dur, mem)

    # 2. Benchmark OHLCV Resampling
    print("[*] Running Task 2: 1-Second Window OHLCV + VWAP Resampling...")

    # Polars
    dur, mem = profile_operation(lambda: PolarsPipeline.resample_1s_ohlcv(table))
    benchmarks["1-Second OHLCV Resampling"]["Polars"] = (dur, mem)

    # DuckDB
    dur, mem = profile_operation(lambda: duck_pipe.resample_1s_ohlcv(table))
    benchmarks["1-Second OHLCV Resampling"]["DuckDB"] = (dur, mem)

    # Print Formatted Report
    print("\n" + "=" * 78)
    print(f"       TICK-BENCH PERFORMANCE REPORT ({num_ticks:,} TICKS)")
    print("=" * 78)

    for task_name, results in benchmarks.items():
        print(f"\n>> Task: {task_name}")
        print(f"{'Engine':<12} | {'Time (s)':<10} | {'Throughput (ticks/s)':<22} | {'Peak RAM (MB)':<12}")
        print("-" * 65)
        for engine, (dur, mem) in results.items():
            throughput = num_ticks / dur
            print(f"{engine:<12} | {dur:<10.4f} | {throughput:>18,.0f} | {mem:>10.2f} MB")

    print("\n" + "=" * 78)


if __name__ == "__main__":
    run_benchmark(num_ticks=5_000_000)
