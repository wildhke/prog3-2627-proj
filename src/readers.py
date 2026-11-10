"""Readers for measurement files: one subclass per file format."""

import pandas as pd
import h5py
import numpy as np

from abc import ABC, abstractmethod

from .measurement import Measurement


class DataReader(ABC):
    """This is a abstract data class for any classes reading data. This can be interpreted as minimal requirement
    for any other data reader classes."""

    @abstractmethod
    def read(self, file) -> Measurement:
        """Every reader must return a Measurement, independent of the file format."""

    @staticmethod
    def to_measurement(signals) -> Measurement:
        """Converts the raw signals (DataFrame or dict of Series, named as in the files) into a Measurement.
        Shared by all readers, so the mapping of the raw names is implemented only once."""
        # steering wheel angle (swa) holds the absolute angle, swa_sign == 1 means negative
        steering_wheel_angle = (1 - 2 * signals["swa_sign"]) * signals["swa"]

        return Measurement(
            time=signals["time"],
            speed=signals["v_x"],
            accel_x=signals["a_x"],
            accel_y=signals["a_y"],
            steering_wheel_angle=steering_wheel_angle,
            curvature=signals["curv"],
            latitude=signals["lat"],
            longitude=signals["lon"],
        )

class CsvDataReader(DataReader):
    """Reads a CSV file with one column per signal.
    This reader uses the in-build function from pandas. There are several other solutions possible. 
    Take a look at the csv package: https://docs.python.org/3/library/csv.html"""

    file_format = ".csv"

    def read(self, file) -> Measurement:
        table = pd.read_csv(file)
        return self.to_measurement(table)

class MatDataReader(DataReader):
    """Reads a mat file.
    
    This data read uses the h5py implementation. If you are interested in further reading, take a look into: 
    https://docs.h5py.org/en/latest/quick.html
    """

    def __init__(self):
        self._signal_names = ["time", "v_x", "a_x", "a_y", "swa", "swa_sign", "curv", "lat", "lon"]

    @property
    def signal_names(self):
        return tuple(self._signal_names)  # immutable copy

    def read(self, file) -> Measurement:
        signals = {}

        with h5py.File(file, "r") as mat_file:
            for name in self.signal_names:
                values = np.array(mat_file[name]).ravel()
                signals[name] = pd.Series(values)

        return self.to_measurement(signals)
