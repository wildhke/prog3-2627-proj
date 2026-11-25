"""Factory: Create objects without knowing the specific class.

When is it useful?
- Measurement files come from different data loggers (CSV, MAT, MF4). The
  factory picks the matching reader from the file suffix. The rest of the
  program only asks for "a reader for this file".
- Together with Strategy: the maneuver detection returns a name such as
  "curve" or "emergency_brake", and the factory creates the matching
  evaluation object from it. The mapping name -> class lives in one place,
  e.g. also driven by a configuration file or a test plan.
"""


class CsvReader:
    def read(self, file):
        return f"reading {file} as CSV"


class JsonReader:
    def read(self, file):
        return f"reading {file} as JSON"


class ReaderFactory:
    readers = {".csv": CsvReader, ".json": JsonReader}

    @classmethod
    def create(cls, file):
        suffix = file[file.rfind("."):]  # another way to find the suffix :-)
        if suffix not in cls.readers:
            raise ValueError(f"No reader for '{suffix}' files")
        return cls.readers[suffix]() # the factory picks the class


for file in ["drive.csv", "drive.json"]:
    reader = ReaderFactory.create(file)  # the caller names no class
    print(reader.read(file))


class MatReader:
    def read(self, file):
        return f"reading {file} as MAT"


ReaderFactory.readers[".mat"] = MatReader  # extend at exactly one place
print(ReaderFactory.create("drive.mat").read("drive.mat"))
