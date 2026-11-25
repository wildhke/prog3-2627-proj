"""
I: Interface Segregation

Small interfaces instead of one big one.
"""
from abc import ABC, abstractmethod


# One big interface in which every file must also be writable.
class DataFile(ABC):
    @abstractmethod
    def read(self): ...

    @abstractmethod
    def write(self, data): ...


class MatFileBefore(DataFile):
    def read(self):
        return [0, 30]

    def write(self, data):  # forced to exist, makes no sense
        raise NotImplementedError("MAT files are read-only")


try:
    MatFileBefore().write([1, 2])
except NotImplementedError as error:
    print("BEFORE:", error)

# -----------------------------------------
# I-conform: Two small interfaces - each class takes only what it needs
# -----------------------------------------
class Readable(ABC):
    @abstractmethod
    def read(self): ...


class Writable(ABC):
    @abstractmethod
    def write(self, data): ...


class MatFile(Readable):  # only reads
    def read(self):
        return [0, 30]


class CsvFile(Readable, Writable):  # reads and writes
    def read(self):
        return [0, 40]

    def write(self, data):
        print("written:", data)


for file in [MatFile(), CsvFile()]:
    print(type(file).__name__, file.read(),
          "writable:", isinstance(file, Writable))
