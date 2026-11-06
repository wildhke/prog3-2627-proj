"""A vehicle with its loaded measurements."""
from pathlib import Path

from .readers import CsvDataReader, MatDataReader


class Vehicle:
    """A vehicle with its loaded measurement."""

    # This is the central point (single point of truth) where all readers must be noted. The rest is done automatically.
    readers = {
        ".csv": CsvDataReader(),
        ".mat": MatDataReader(),
    }

    def __init__(self, data):
        self.data = data

    @classmethod
    def from_csv(cls, file):
        return cls(CsvDataReader().read(file))

    @classmethod
    def from_mat(cls, file):
        return cls(MatDataReader().read_data(file))

    @classmethod
    def from_file(cls, file):
        """This class shows the polymorphism approach: 
        1. Get the file type by using the suffix.
        2. With the file type, we are extracting the specific instance of the data reader class from the dict.
        3. The read-method of the reader is called.
        4. An object/instance of the specific class is returned.
        """

        suffix = Path(file).suffix.lower()

        reader = cls.readers[suffix]
        return cls(reader.read(file))


    def status(self):
        return (f"{self.data.size} samples")
