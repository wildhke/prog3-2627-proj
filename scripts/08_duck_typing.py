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
    thing.fly()            # only fly() matters, not the class


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
for thing in things:       # nothing to change for new classes
    thing.fly()


# %% Not every bird swims: Python checks only at runtime
title("Missing method")

for bird in [Duck(), Pigeon()]:
    bird.fly()
    try:
        bird.swim()        # Pigeon has no swim()
    except AttributeError as error:
        print("AttributeError:", error)


# %% Our own duck: from_file() only calls read()
title("Our own duck")


@dataclass
class Measurement:
    time: list# s
    speed: list # km/h

    @property
    def n_samples(self) -> int:
        return len(self.time)


measurement = Measurement(time=[0, 1, 2, 3], speed=[0, 30, 55, 50])


class ReplayReader:        # no base class
    """Returns a prepared measurement, e.g. for tests."""

    def __init__(self, data):
        self.data = data

    def read(self, file) -> Measurement:
        return self.data


class ConstantSpeedReader: # no base class either
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
        return cls(reader.read(file)) # works with every duck

    @property
    def status(self) -> str:
        return f"{self.data.n_samples} samples loaded"


print(Vehicle.from_file("test.replay").status)
print(Vehicle.from_file("drive.sim").status)
