import pyarrow as pa
import pytest
from tick_bench.pipelines import ArrowComputePipeline, DuckDBPipeline, PolarsPipeline


def create_minimal_table(prices, volumes, timestamps=None):
    n = len(prices)
    ts = timestamps if timestamps is not None else [1_700_000_000_000_000_000 + (i * 1_000_000_000) for i in range(n)]
    return pa.Table.from_arrays(
        [
            pa.array(ts, type=pa.int64()),
            pa.array(prices, type=pa.float64()),
            pa.array(volumes, type=pa.float64()),
            pa.array([1] * n, type=pa.int8()),
        ],
        names=["timestamp_ns", "price", "volume", "side"],
    )


def test_single_tick_behavior():
    table = create_minimal_table([105.5], [10.0])
    
    vwap_polars = PolarsPipeline.compute_vwap(table)
    vwap_duck = DuckDBPipeline().compute_vwap(table)
    vwap_arrow = ArrowComputePipeline.compute_vwap(table)

    assert vwap_polars == 105.5
    assert vwap_duck == 105.5
    assert vwap_arrow == 105.5


def test_multi_tick_exact_window_resampling():
    # 3 ticks inside 1st second window, 2 ticks inside 2nd second window
    timestamps = [
        1_000_000_000, 1_200_000_000, 1_800_000_000,
        2_100_000_000, 2_500_000_000,
    ]
    prices = [100.0, 102.0, 101.0, 103.0, 104.0]
    volumes = [1.0, 2.0, 1.0, 5.0, 5.0]

    table = create_minimal_table(prices, volumes, timestamps)

    # Polars
    df_polars = PolarsPipeline.resample_1s_ohlcv(table)
    assert len(df_polars) == 2

    row_1 = df_polars.row(0, named=True)
    assert row_1["open"] == 100.0
    assert row_1["high"] == 102.0
    assert row_1["low"] == 100.0
    assert row_1["close"] == 101.0
    assert row_1["volume"] == 4.0
    assert pytest.approx(row_1["vwap"]) == ((100.0 * 1 + 102.0 * 2 + 101.0 * 1) / 4.0)

    # DuckDB
    duck_pipe = DuckDBPipeline()
    res_duck = duck_pipe.resample_1s_ohlcv(table).to_pydict()
    assert len(res_duck["bar_time_sec"]) == 2
    assert res_duck["open"][0] == 100.0
    assert res_duck["close"][0] == 101.0
