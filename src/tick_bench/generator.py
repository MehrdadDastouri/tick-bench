"""High-speed synthetic market tick data generator emitting zero-copy Arrow Tables."""

import numpy as np
import pyarrow as pa


def generate_tick_table(
    num_ticks: int = 1_000_000,
    start_time_ns: int = 1_700_000_000_000_000_000,
    initial_price: float = 100.0,
    seed: int = 42,
) -> pa.Table:
    """
    Generate deterministic synthetic trade tick data.
    Columns:
    - timestamp_ns: int64 (nanosecond epoch)
    - price: float64
    - volume: float64
    - side: int8 (1 for Buy, -1 for Sell)
    """
    rng = np.random.default_rng(seed)

    # Monotonically increasing timestamps with Poisson-distributed intervals
    intervals = rng.exponential(scale=1_000_000, size=num_ticks).astype(np.int64)
    timestamps = start_time_ns + np.cumsum(intervals)

    # Brownian motion for price progression
    price_returns = rng.normal(loc=0.0, scale=0.0002, size=num_ticks)
    price_multipliers = np.cumprod(1.0 + price_returns)
    prices = np.round(initial_price * price_multipliers, 2)

    # Volume: Log-normal distribution
    volumes = np.round(rng.lognormal(mean=1.5, sigma=0.8, size=num_ticks), 2)
    volumes = np.clip(volumes, 0.01, 500.0)

    # Aggressor Side: 1 (Buy) or -1 (Sell)
    sides = rng.choice(np.array([1, -1], dtype=np.int8), size=num_ticks)

    schema = pa.schema([
        ("timestamp_ns", pa.int64()),
        ("price", pa.float64()),
        ("volume", pa.float64()),
        ("side", pa.int8()),
    ])

    return pa.Table.from_arrays(
        [
            pa.array(timestamps, type=pa.int64()),
            pa.array(prices, type=pa.float64()),
            pa.array(volumes, type=pa.float64()),
            pa.array(sides, type=pa.int8()),
        ],
        schema=schema,
    )
