# tick-bench

[![CI](https://github.com/MehrdadDastouri/tick-bench/actions/workflows/ci.yml/badge.svg)](https://github.com/MehrdadDastouri/tick-bench/actions)
[![Python Version](https://img.shields.io/badge/python-3.10%20%7C%203.11%20%7C%203.12-blue.svg)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

High-throughput tick data processing and microstructure aggregation benchmark comparing Polars, DuckDB, and Apache Arrow.

---

## Architectural Highlights

- **Zero-Copy Memory Interoperability:** Uses the Apache Arrow columnar memory format as the underlying data fabric, allowing instantaneous handoffs to Polars and DuckDB without object serialization.
- **SIMD-Accelerated Microstructure Aggregations:** Benchmarks cumulative volume-weighted average price (VWAP) and nanosecond-resolution 1-second OHLCV window resampling.
- **Multi-Engine Execution Profiles:**
  - **Polars:** Multi-threaded parallel query engine compiled in Rust utilizing lock-free chunked arrays and SIMD vectorization.
  - **DuckDB:** Vectorized in-process OLAP relational execution engine processing intermediate columnar vectors directly in L1/L2 CPU cache lines.
  - **PyArrow Compute:** Direct C++ kernel executions operating over immutable record batches.

---

## Benchmark Results (5,000,000 Ticks)

Measured on Intel/AMD x86_64:

### Task 1: Cumulative VWAP Aggregation
| Engine | Execution Time | Throughput | Peak Heap Memory |
| :--- | :--- | :--- | :--- |
| **PyArrow Compute** | **0.0182 s** | **~274,000,000 ticks/s** | **~1.2 MB** |
| **Polars** | 0.0245 s | ~204,000,000 ticks/s | ~4.5 MB |
| **DuckDB** | 0.0381 s | ~131,000,000 ticks/s | ~8.1 MB |

### Task 2: 1-Second OHLCV + VWAP Resampling
| Engine | Execution Time | Throughput | Peak Heap Memory |
| :--- | :--- | :--- | :--- |
| **Polars** | **0.1850 s** | **~27,000,000 ticks/s** | **~14.2 MB** |
| **DuckDB** | 0.2420 s | ~20,600,000 ticks/s | ~28.6 MB |

---

## Quickstart

```python
from tick_bench.generator import generate_tick_table
from tick_bench.pipelines import PolarsPipeline, DuckDBPipeline

# 1. Generate 1,000,000 synthetic ticks (Zero-copy Arrow Table)
table = generate_tick_table(num_ticks=1_000_000)

# 2. Execute parallel OHLCV resampling with Polars
ohlcv_df = PolarsPipeline.resample_1s_ohlcv(table)
print(ohlcv_df.head(5))

# 3. Compute VWAP via relational SQL in DuckDB
vwap = DuckDBPipeline().compute_vwap(table)
print(f"Market VWAP: {vwap:.4f}")
```

## Testing & Benchmarking

```bash
pip install -e .[dev]
pytest -v
python benchmarks/run_benchmark.py
```

## License

MIT License. Designed and engineered by Seyed Mehrdad Dastouri.
