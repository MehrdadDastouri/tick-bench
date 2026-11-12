"""Canonical market microstructure aggregation pipelines across Polars, DuckDB, and Arrow."""

import duckdb
import polars as pl
import pyarrow as pa
import pyarrow.compute as pc


class PolarsPipeline:
    """Polars multi-threaded SIMD execution pipeline."""

    @staticmethod
    def compute_vwap(table: pa.Table) -> float:
        df = pl.from_arrow(table)
        res = df.select((pl.col("price") * pl.col("volume")).sum() / pl.col("volume").sum())
        return float(res.item())

    @staticmethod
    def resample_1s_ohlcv(table: pa.Table) -> pl.DataFrame:
        df = pl.from_arrow(table)
        return (
            df.lazy()
            .with_columns((pl.col("timestamp_ns") // 1_000_000_000).alias("bar_time_sec"))
            .group_by("bar_time_sec")
            .agg([
                pl.col("price").first().alias("open"),
                pl.col("price").max().alias("high"),
                pl.col("price").min().alias("low"),
                pl.col("price").last().alias("close"),
                pl.col("volume").sum().alias("volume"),
                ((pl.col("price") * pl.col("volume")).sum() / pl.col("volume").sum()).alias("vwap"),
            ])
            .sort("bar_time_sec")
            .collect()
        )


class DuckDBPipeline:
    """DuckDB vectorized in-memory relational SQL pipeline."""

    def __init__(self) -> None:
        self.con = duckdb.connect(":memory:")

    def compute_vwap(self, table: pa.Table) -> float:
        self.con.register("ticks", table)
        query = "SELECT SUM(price * volume) / SUM(volume) AS vwap FROM ticks"
        result = self.con.execute(query).fetchone()
        self.con.unregister("ticks")
        return float(result[0])

    def resample_1s_ohlcv(self, table: pa.Table) -> pa.Table:
        self.con.register("ticks", table)
        query = """
            SELECT 
                (timestamp_ns // 1000000000) AS bar_time_sec,
                FIRST(price) AS open,
                MAX(price) AS high,
                MIN(price) AS low,
                LAST(price) AS close,
                SUM(volume) AS volume,
                SUM(price * volume) / SUM(volume) AS vwap
            FROM ticks
            GROUP BY 1
            ORDER BY 1
        """
        result_table = self.con.execute(query).arrow()
        self.con.unregister("ticks")
        return result_table


class ArrowComputePipeline:
    """Raw PyArrow Compute C++ kernel pipeline."""

    @staticmethod
    def compute_vwap(table: pa.Table) -> float:
        price_col = table["price"]
        volume_col = table["volume"]
        pv = pc.multiply(price_col, volume_col)
        sum_pv = pc.sum(pv).as_py()
        sum_v = pc.sum(volume_col).as_py()
        return float(sum_pv / sum_v)
