"""Readers for measurement files: one subclass per file format."""

import pandas as pd
import h5py
import numpy as np


class CsvDataReader:
    """Reads a CSV file with one column per signal."""

    file_format = ".csv"

    def read(self, file):
        table = pd.read_csv(file)

        # steering wheel angle (swa) holds the absolute angle, swa_sign == 1 means negative
        table["swa_signed"] = ( 1 - 2 * table["swa_sign"] ) * table["swa"]

        return table
