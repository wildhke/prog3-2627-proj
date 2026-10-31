"""A vehicle with its loaded measurements."""

from .readers import CsvDataReader


class Vehicle:
    """A vehicle with its loaded measurement."""

    def __init__(self, data):
        self.data = data

    @classmethod
    def from_csv(cls, file):
        return cls(CsvDataReader().read(file))

    def status(self):
        return (f"{self.data.size} samples")
