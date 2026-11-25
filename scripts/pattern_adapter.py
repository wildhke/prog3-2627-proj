"""Adapter: Make a interface fit our own.

When is it useful?
- A third-party library or web API delivers data in its own format: other
  method names, other units, nested JSON. An adapter translates it into our
  own data class, e.g. a fuel price API -> Station, h5py -> Measurement.
- The rest of the program only sees our interface (read() -> Measurement).
  If the provider changes, only the adapter changes.
"""
from dataclasses import dataclass


@dataclass
class Measurement:  # our own format
    time: list  # s
    speed: list  # km/h


class LegacyLogger:
    """Foreign library: Other method name, other units, other structure."""

    def fetch_rows(self):
        return [(0, 0.0), (1000, 10.0), (2000, 15.0)] # (ms, m/s)


class LoggerAdapter:
    """Looks like one of our readers: read() and returns a datclass."""

    def __init__(self, logger):
        self._logger = logger # the wrapped foreign object

    def read(self, file=None) -> Measurement:
        rows = self._logger.fetch_rows() # foreign call
        return Measurement( # translated into ours
            time=[ms / 1000 for ms, _ in rows],
            speed=[mps * 3.6 for _, mps in rows])


reader = LoggerAdapter(LegacyLogger())
print(reader.read())  # s and kph
