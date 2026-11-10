"""Measurement data of one drive, independent of the file format."""

from dataclasses import dataclass

import pandas as pd


@dataclass(eq=False)
class Measurement:
    """All signals of one measurement drive, one value per time step.

    Every reader returns an instance of this class, no matter which file format it reads.
    The @dataclass decorator generates __init__ from the annotated fields below, so
    Measurement(time=..., speed=..., ...) works without writing the constructor by hand.
    eq=False: comparing pandas Series with == returns a Series, not True/False.
    """

    time: pd.Series            # s
    speed: pd.Series           # km/h
    accel_x: pd.Series         # m/s^2, longitudinal
    accel_y: pd.Series         # m/s^2, lateral
    steering_wheel_angle: pd.Series  # deg, signed
    curvature: pd.Series       # 1/m
    latitude: pd.Series        # deg
    longitude: pd.Series       # deg

    def __post_init__(self):
        """Runs right after the generated __init__: all signals must have the same length."""
        lengths = {name: len(values) for name, values in vars(self).items()}
        if len(set(lengths.values())) != 1:
            raise ValueError(f"All signals need the same number of samples, got {lengths}")

    def __repr__(self):
        # the generated repr would print every value of every signal
        return f"Measurement({self.n_samples} samples, {self.duration:.1f} s)"

    @property
    def n_samples(self) -> int:
        return len(self.time)

    @property
    def duration(self) -> float:
        """Length of the measurement in seconds."""
        return float(self.time.iloc[-1] - self.time.iloc[0])

    @property
    def sample_rate(self) -> float:
        """Samples per second in Hz."""
        return (self.n_samples - 1) / self.duration

    @property
    def has_gps_fix(self) -> bool:
        """True if the GPS delivered a position at least once (0 means no fix)."""
        return bool((self.latitude != 0).any())

    def to_dataframe(self) -> pd.DataFrame:
        """All signals as one table, e.g. for printing or exporting."""
        return pd.DataFrame(vars(self))
