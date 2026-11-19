"""Live demo for lecture 9: five design patterns in their simplest form."""

import json
from abc import ABC, abstractmethod
from dataclasses import dataclass


def title(text):
    """Prints a heading for each cell in the output."""
    print(f"\n=== {text} ===")


# %% Setup: a small measurement, as in the demo project
@dataclass
class Measurement:
    time: list    # s
    speed: list   # km/h

    @property
    def max_speed(self) -> float:
        return max(self.speed)


# Stands in for files on disk, so the demo runs without any data folder
FILES = {
    "drive.csv": "time,speed\n0,0\n1,30\n2,55\n3,50",
    "drive.json": '{"time": [0, 1, 2], "speed": [0, 40, 80]}',
}

measurement = Measurement(time=[0, 1, 2, 3], speed=[0, 30, 55, 50])


# %% Strategy: exchangeable behavior as its own object
title("Strategy")


class Exporter(ABC):
    @abstractmethod
    def export(self, data: Measurement) -> str: ...


class CsvExporter(Exporter):
    def export(self, data):
        rows = [f"{t},{v}" for t, v in zip(data.time, data.speed)]
        return "time,speed\n" + "\n".join(rows)


class JsonExporter(Exporter):
    def export(self, data):
        return json.dumps({"time": data.time, "speed": data.speed})


class Report:
    def __init__(self, exporter: Exporter):
        self.exporter = exporter          # the strategy

    def save(self, data):
        return self.exporter.export(data)


report = Report(CsvExporter())
print(report.save(measurement))
report.exporter = JsonExporter()          # swap the strategy at runtime
print(report.save(measurement))

# A strategy can also be a plain function: key= is a strategy for sorted()
print(sorted(["drive.json", "a.csv", "drive.mat"], key=len))


# %% Factory: create objects without knowing the concrete class
title("Factory")


class CsvReader:
    def read(self, file) -> Measurement:
        lines = FILES[file].splitlines()[1:]          # skip the header
        rows = [line.split(",") for line in lines]
        return Measurement(time=[float(t) for t, _ in rows],
                           speed=[float(v) for _, v in rows])


class JsonReader:
    def read(self, file) -> Measurement:
        return Measurement(**json.loads(FILES[file]))


class ReaderFactory:
    _readers = {".csv": CsvReader, ".json": JsonReader}

    @classmethod
    def register(cls, suffix, reader_class):
        cls._readers[suffix] = reader_class

    @classmethod
    def create(cls, file):
        suffix = "." + file.rsplit(".", 1)[-1]
        if suffix not in cls._readers:
            raise ValueError(f"No reader for '{suffix}' files")
        return cls._readers[suffix]()                 # the factory decides


for file in FILES:
    reader = ReaderFactory.create(file)
    print(file, "->", type(reader).__name__, reader.read(file))

try:
    ReaderFactory.create("drive.mat")
except ValueError as error:
    print("ValueError:", error)


# %% Observer: notify everyone who is interested in new data
title("Observer")


class Vehicle:
    def __init__(self, data):
        self._observers = []
        self.data = data

    def subscribe(self, callback):
        self._observers.append(callback)              # any callable

    @property
    def data(self):
        return self._data

    @data.setter
    def data(self, value):
        self._data = value
        for callback in self._observers:
            callback(self)                            # notify all


def log_status(vehicle):
    print(f"log: {len(vehicle.data.time)} samples loaded")


vehicle = Vehicle(measurement)
vehicle.subscribe(log_status)
vehicle.subscribe(lambda v: print(f"chart: max speed {v.data.max_speed} km/h"))
vehicle.data = JsonReader().read("drive.json")       # both observers react


# %% Adapter: make a foreign interface fit our own
title("Adapter")


class LegacyLogger:
    """Foreign library: other method name, other units, other structure."""

    def fetch_rows(self):
        return [(0, 0.0), (1000, 10.0), (2000, 15.0)]  # (ms, m/s)


class LegacyLoggerAdapter:
    """Looks like one of our readers: read() returns a Measurement."""

    def __init__(self, logger: LegacyLogger):
        self._logger = logger

    def read(self, file=None) -> Measurement:
        rows = self._logger.fetch_rows()
        return Measurement(time=[ms / 1000 for ms, _ in rows],
                           speed=[mps * 3.6 for _, mps in rows])


adapter = LegacyLoggerAdapter(LegacyLogger())
print(adapter.read())                       # s and km/h, like all readers


# %% Template Method: fixed order, exchangeable steps
title("Template Method")


class DataReader(ABC):
    def read(self, file) -> Measurement:              # the template
        text = FILES[file]
        signals = self.parse(text)                    # the variable step
        return Measurement(time=signals["time"], speed=signals["speed"])

    @abstractmethod
    def parse(self, text) -> dict: ...


class CsvDataReader(DataReader):
    def parse(self, text):
        rows = [line.split(",") for line in text.splitlines()[1:]]
        return {"time": [float(t) for t, _ in rows],
                "speed": [float(v) for _, v in rows]}


class JsonDataReader(DataReader):
    def parse(self, text):
        return json.loads(text)


print(CsvDataReader().read("drive.csv"))
print(JsonDataReader().read("drive.json"))
