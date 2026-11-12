import numpy as np
import pytest
from tick_bench.generator import generate_tick_table
from tick_bench.pipelines import ArrowComputePipeline, DuckDBPipeline, PolarsPipeline


@pytest.fixture(scope="module")
def sample_ticks():
    return generate_tick_table(num_ticks=50_000, seed=123)


def test_vwap_numerical_equivalence(sample_ticks):
    vwap_polars = PolarsPipeline.compute_vwap(sample_ticks)
    
    duck_pipeline = DuckDBPipeline()
    vwap_duckdb = duck_pipeline.compute_vwap(sample_ticks)

    vwap_arrow = ArrowComputePipeline.compute_vwap(sample_ticks)

    # All three engines must match to 8 decimal places
    assert pytest.approx(vwap_polars, rel=1e-8) == vwap_duckdb
    assert pytest.approx(vwap_polars, rel=1e-8) == vwap_arrow


def test_ohlcv_resampling_integrity(sample_ticks):
    df_polars = PolarsPipeline.resample_1s_ohlcv(sample_ticks)
    
    duck_pipeline = DuckDBPipeline()
    table_duck = duck_pipeline.resample_1s_ohlcv(sample_ticks)
    df_duck_arrow = table_duck.to_pydict()

    # Compare aggregated row counts
    assert len(df_polars) == len(table_duck)

    # Compare bar aggregates
    polars_opens = df_polars["open"].to_numpy()
    duck_opens = np.array(df_duck_arrow["open"])
    np.testing.assert_allclose(polars_opens, duck_opens, rtol=1e-6)

    polars_volumes = df_polars["volume"].to_numpy()
    duck_volumes = np.array(df_duck_arrow["volume"])
    np.testing.assert_allclose(polars_volumes, duck_volumes, rtol=1e-6)

    polars_vwaps = df_polars["vwap"].to_numpy()
    duck_vwaps = np.array(df_duck_arrow["vwap"])
    np.testing.assert_allclose(polars_vwaps, duck_vwaps, rtol=1e-6)
