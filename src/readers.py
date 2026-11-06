"""Readers for measurement files: one subclass per file format."""

import pandas as pd
import h5py
import numpy as np

from abc import ABC, abstractmethod

class DataReader(ABC):
    """This is a abstract data class for any classes reading data. This can be interpreted as minimal requirement
    for any other data reader classes."""

    @abstractmethod
    def read(self, file):
        pass

class CsvDataReader(DataReader):
    """Reads a CSV file with one column per signal.
    This reader uses the in-build function from pandas. There are several other solutions possible. 
    Take a look at the csv package: https://docs.python.org/3/library/csv.html"""

    file_format = ".csv"

    def read(self, file):
        table = pd.read_csv(file)

        # steering wheel angle (swa) holds the absolute angle, swa_sign == 1 means negative
        table["swa_signed"] = ( 1 - 2 * table["swa_sign"] ) * table["swa"]

        return table

class MatDataReader(DataReader):
    """Reads a mat file.
    
    This data read uses the h5py implementation. If you are interested in further reading, take a look into: 
    https://docs.h5py.org/en/latest/quick.html
    """

    def __init__(self):
        self.signal_names = ["time","v_x","a_x","a_y","swa","swa_sign","curv","lat","lon"]

    def read(self, file) -> pd.DataFrame:
        signals = {}

        with h5py.File(file, "r") as mat_file:
            for name in self.signal_names:
                values = np.array(mat_file[name]).ravel()
                signals[name] = pd.Series(values)

        sign = 1 - 2 * signals.pop("swa_sign")
        signals["swa_signed"] = signals["swa"] * sign
        return pd.DataFrame(signals)