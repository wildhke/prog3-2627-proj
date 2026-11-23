"""Readers for measurement files: one subclass per file format.

Open/closed principle: the package is open for new file formats, but closed for modification.
A new format is ONE new subclass with a `file_format`. It registers itself automatically,
nothing else has to be changed (no dict to extend, no if/elif, no list in a config file).
"""

from abc import ABC, abstractmethod
from pathlib import Path

import h5py
import numpy as np
import pandas as pd

from .exceptions import MissingSignalError, UnsupportedFormatError
from .measurement import Measurement


class DataReader(ABC):
    """Abstract base class of all readers: the minimal requirement for every reader class."""

    file_format: str                                    # every subclass sets it, e.g. ".csv"
    _registry: dict[str, type["DataReader"]] = {}       # file format -> reader class

    def __init_subclass__(cls, **kwargs):
        """Called by Python automatically when a subclass is defined (not when an object is created).
        This is where every reader registers itself for its file format."""
        super().__init_subclass__(**kwargs)

        # a missing file_format is a programming error -> built-in TypeError, not one of our own errors
        file_format = cls.__dict__.get("file_format")
        if file_format is None:
            raise TypeError(f"{cls.__name__} must define the class attribute file_format, e.g. '.csv'")
        if file_format in DataReader._registry:
            raise TypeError(f"{file_format} is already read by {DataReader._registry[file_format].__name__}")

        DataReader._registry[file_format] = cls

    @classmethod
    def supported_formats(cls) -> list[str]:
        """All file formats there is a reader for, e.g. for a selectbox."""
        return sorted(DataReader._registry)

    @classmethod
    def for_file(cls, file) -> "DataReader":
        """Factory: returns a reader object that matches the suffix of the file."""
        file_format = Path(file).suffix.lower()
        try:
            reader_class = DataReader._registry[file_format]
        except KeyError:
            # translate the technical KeyError into an error that explains the problem
            raise UnsupportedFormatError(file_format, cls.supported_formats()) from None
        return reader_class()

    @abstractmethod
    def read(self, file) -> Measurement:
        """Every reader must return a Measurement, independent of the file format."""

    @staticmethod
    def to_measurement(signals) -> Measurement:
        """Converts the raw signals (DataFrame or dict of Series, named as in the files) into a Measurement.
        Shared by all readers, so the mapping of the raw names is implemented only once."""
        try:
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
        except KeyError as error:
            raise MissingSignalError(error.args[0]) from error


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

    file_format = ".mat"

    def __init__(self):
        self._signal_names = ["time", "v_x", "a_x", "a_y", "swa", "swa_sign", "curv", "lat", "lon"]

    @property
    def signal_names(self):
        return tuple(self._signal_names)  # immutable copy

    def read(self, file) -> Measurement:
        signals = {}

        with h5py.File(file, "r") as mat_file:
            for name in self.signal_names:
                if name not in mat_file:
                    raise MissingSignalError(name)
                signals[name] = pd.Series(np.array(mat_file[name]).ravel())

        return self.to_measurement(signals)


def load_measurement(file) -> Measurement:
    """Reads any supported file. The caller does not need to know which reader is used."""
    return DataReader.for_file(file).read(file)
