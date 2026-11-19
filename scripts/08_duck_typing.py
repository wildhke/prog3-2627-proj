"""Duck typing.
If it walks like a duck and quacks like a duck, it is a duck.

Side info: to run a so-called notebook, simply install ms-toolsai.jupyter
(extension) and ipykernel (via pip).
"""

import csv
import io
import json
from abc import ABC, abstractmethod
from dataclasses import dataclass
from pathlib import Path
from typing import Protocol, runtime_checkable


def title(text):
    """Prints a heading for each cell in the output."""
    print(f"\n=== {text} ===")


# %% Everything that flies: three classes, no common base class
title("Everything that flies")


class Duck:
    def fly(self):
        print("Duck is flying")

    def swim(self):
        print("Duck is swimming")


class Pigeon:
    def fly(self):
        print("Pigeon is flying")


class Airplane:
    def fly(self):
        print("Airplane is flying")


things = [Duck(), Pigeon(), Airplane()]
for thing in things:
    thing.fly()                      # only fly() matters, not the class


# %% Without duck typing: one check per class -- compare polymorphism
title("Without duck typing")


class SpaceStation:
    def fly(self):
        print("SpaceStation is flying")

# Adding SpaceStation-instance to the things-list.
things.append(SpaceStation())


print("-- with isinstance():")
for thing in things:
    if isinstance(thing, Duck):
        thing.fly()
    elif isinstance(thing, Pigeon):
        thing.fly()
    elif isinstance(thing, Airplane):
        thing.fly()
    # the SpaceStation is skipped. The chain must be extended

print("-- with duck typing:")
for thing in things:                 # nothing to change for new classes
    thing.fly()


# %% Not every bird swims: Python checks only at runtime
title("Missing method")

for bird in [Duck(), Pigeon()]:
    bird.fly()
    try:
        bird.swim()                  # Pigeon has no swim()
    except AttributeError as error:
        print("AttributeError:", error)


# %% Our own duck: from_file() only calls read()
title("Our own duck")


@dataclass
class Measurement:
    time: list    # s
    speed: list   # km/h

    @property
    def n_samples(self) -> int:
        return len(self.time)


measurement = Measurement(time=[0, 1, 2, 3], speed=[0, 30, 55, 50])


class ReplayReader:                  # no base class
    """Returns a prepared measurement, e.g. for tests."""

    def __init__(self, data):
        self.data = data

    def read(self, file) -> Measurement:
        return self.data


class ConstantSpeedReader:           # no base class either
    """Generates a measurement instead of reading a file."""

    def read(self, file) -> Measurement:
        return Measurement(time=[0, 1, 2], speed=[50, 50, 50])


class Vehicle:
    readers = {".replay": ReplayReader(measurement),
               ".sim": ConstantSpeedReader()}

    def __init__(self, data: Measurement):
        self.data = data

    @classmethod
    def from_file(cls, file):
        reader = cls.readers[Path(file).suffix]
        return cls(reader.read(file))           # works with every duck

    @property
    def status(self) -> str:
        return f"{self.data.n_samples} samples loaded"


print(Vehicle.from_file("test.replay").status)
print(Vehicle.from_file("drive.sim").status)


# ======================================================================
# EXTRA DEMO - optional, for self-study
# ======================================================================

# %% Extra setup: a CSV reader and some fake files
title("Extra setup")

# Stands in for files on disk, so the demo runs without any data folder
FILES = {
    "drive.csv": "time,speed\n0,0\n1,30\n2,55",
    "broken.csv": "time,velocity\n0,0\n1,30",
}


class CsvReader:
    def read(self, file) -> Measurement:
        rows = list(csv.DictReader(io.StringIO(FILES[file])))
        return Measurement(time=[float(row["time"]) for row in rows],
                           speed=[float(row["speed"]) for row in rows])


Vehicle.readers[".csv"] = CsvReader()
print(Vehicle.from_file("drive.csv").status)


# %% Extra: a missing method - late with duck typing, early with an ABC
title("Missing method vs. ABC")


class BrokenReader:
    def load(self, file):            # wrong name: load() instead of read()
        return measurement


Vehicle.readers[".broken"] = BrokenReader()   # nobody complains here ...
try:
    Vehicle.from_file("test.broken")          # ... only when read() is used
except AttributeError as error:
    print("AttributeError:", error)


class DataReader(ABC):               # with an ABC the error comes early
    @abstractmethod
    def read(self, file) -> Measurement: ...


class StrictBrokenReader(DataReader):
    def load(self, file):
        return measurement


try:
    StrictBrokenReader()
except TypeError as error:
    print("TypeError:", error)


# %% Extra: LBYL vs. EAFP
title("LBYL vs. EAFP")

suffix = ".mat"

# LBYL - Look Before You Leap: check first, then act
if suffix in Vehicle.readers:
    reader = Vehicle.readers[suffix]
else:
    print("LBYL: no reader for", suffix)

# EAFP - Easier to Ask Forgiveness than Permission: try, handle the error
try:
    reader = Vehicle.readers[suffix]
except KeyError:
    print("EAFP: no reader for", suffix)


# %% Extra: keep the try block narrow
title("Narrow try block")

# Too wide: the KeyError from the missing column "speed" inside read()
# is caught as well and reported with the wrong message
try:
    reader = Vehicle.readers[".csv"]
    reader.read("broken.csv")
except KeyError:
    print("too wide: no reader for '.csv'   <- wrong!")

# Narrow: each try block guards exactly one thing
try:
    reader = Vehicle.readers[".csv"]
except KeyError:
    print("no reader for '.csv'")

try:
    reader.read("broken.csv")
except KeyError as error:
    print("narrow: missing column", error)


# %% Extra: duck typing with type hints - typing.Protocol
title("Protocol")


@runtime_checkable                   # only needed for isinstance() below
class Readable(Protocol):
    def read(self, file) -> Measurement: ...


def load(reader: Readable, file) -> Measurement:
    """Editors and mypy check that reader has read() - Python does not."""
    return reader.read(file)


print(load(ReplayReader(measurement), "any.file"))


# %% Extra: structural vs. nominal typing
title("Structural vs. nominal")

replay = ReplayReader(measurement)
# nominal: is it declared as a DataReader? (inheritance)
print("isinstance(replay, DataReader):", isinstance(replay, DataReader))
# structural: does it have the right method? (no inheritance needed)
print("isinstance(replay, Readable):  ", isinstance(replay, Readable))
print("isinstance(BrokenReader(), Readable):",
      isinstance(BrokenReader(), Readable))


# %% Extra: duck typing in the built-ins
title("Built-ins")

for things in ([1, 2, 3], (1, 2, 3), "abc", {"a": 1, "b": 2}, range(3)):
    # for and len() work with anything that is iterable / has a length
    print(type(things).__name__, "->", list(things), len(things))

# in works with every container that can answer "do you contain this?"
print(2 in [1, 2, 3], "b" in "abc", "a" in {"a": 1}, 5 in range(3))

# sum() does not care where the numbers come from, a generator works too
print(sum(speed for speed in measurement.speed))


# %% Extra: file-like objects - anything with read() or with lines will do
title("File-like objects")

text_file = io.StringIO(FILES["drive.csv"])   # behaves like an open file
rows = list(csv.reader(text_file))            # csv only iterates over lines
print(rows)

json_file = io.StringIO('{"time": [0, 1], "speed": [0, 40]}')
print(Measurement(**json.load(json_file)))    # json.load only calls read()
