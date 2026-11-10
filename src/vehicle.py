"""A vehicle with its loaded measurements."""
from collections import namedtuple
from pathlib import Path

import numpy as np

from .measurement import Measurement
from .readers import CsvDataReader, MatDataReader


GRAVITY = 9.81

# One time step of the measurement.
Sample = namedtuple("Sample", ["time", "speed", "accel_x", "accel_y", "steering_wheel_angle"])


class Vehicle:
    """A vehicle with its loaded measurement."""

    # This is the central point (single point of truth) where all readers must be noted. The rest is done automatically.
    readers = {
        ".csv": CsvDataReader(),
        ".mat": MatDataReader(),
    }

    steering_ratio = 15.0

    def __init__(self, data: Measurement):
        self.data = data  # without underscore -> calls the setter

    @property
    def data(self) -> Measurement:
        return self._data

    @data.setter
    def data(self, value: Measurement):
        if value.n_samples < 2:
            raise ValueError("Measurement needs at least two samples")
        self._data = value

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

    @property
    def time(self):
        """Time since the start of the measurement in s."""
        return self.data.time - self.data.time.iloc[0]

    @property
    def speed(self):
        """Longitudinal velocity in km/h."""
        return self.data.speed

    @property
    def accel_x_g(self):
        """Longitudinal acceleration in g."""
        return self.data.accel_x / GRAVITY

    @property
    def accel_y_g(self):
        """Lateral acceleration in g."""
        return self.data.accel_y / GRAVITY

    @property
    def accel_combined_g(self):
        """Magnitude of the combined (longitudinal + lateral) acceleration in g."""
        return np.hypot(self.accel_x_g, self.accel_y_g)

    @property
    def steering_wheel_angle(self):
        """Steering wheel angle in deg, signed."""
        return self.data.steering_wheel_angle

    @property
    def steering_angle(self):
        """Steering angle at the wheels in deg, derived via the steering ratio."""
        return self.steering_wheel_angle / self.steering_ratio

    @property
    def max_steering_wheel_angle(self) -> float:
        """Largest absolute steering wheel angle in deg, e.g. used as range of the gauge."""
        return float(self.steering_wheel_angle.abs().max())

    @property
    def n_samples(self) -> int:
        return self.data.n_samples

    @property
    def duration(self) -> float:
        return self.data.duration

    @property
    def sample_rate(self) -> float:
        return self.data.sample_rate

    @property
    def max_speed(self) -> float:
        return float(self.speed.max())

    @property
    def max_accel_g(self) -> float:
        """Largest combined acceleration in g, e.g. used as range of the gauge."""
        return float(self.accel_combined_g.max())


    def samples(self, step: int = 1, start: int = 0):
        """Yields every n-th sample of the measurement, beginning at start."""
        time, speed = self.time, self.speed
        accel_x, accel_y = self.accel_x_g, self.accel_y_g
        steering_wheel_angle = self.steering_wheel_angle

        for index in range(start, self.n_samples, step):
            yield Sample(time.iloc[index], speed.iloc[index], accel_x.iloc[index], accel_y.iloc[index],
                         steering_wheel_angle.iloc[index])

    def __iter__(self):
        """Makes the vehicle iterable: for sample in vehicle: ..."""
        return self.samples()

    @property
    def status(self) -> str:
        """Short status line, e.g. used as title of the summary table in the sidebar."""
        return f"{self.n_samples} samples loaded"

    @property
    def summary(self) -> dict:
        """Key paramrters of the data."""
        return {
            "Duration": f"{self.duration:.1f} s",
            "Sample rate": f"{self.sample_rate:.0f} Hz",
            "Max speed": f"{self.max_speed:.0f} km/h",
            "Max acceleration": f"{self.max_accel_g:.2f} g",
            "Max steering wheel angle": f"{self.max_steering_wheel_angle:.0f} deg",
            "GPS fix": "yes" if self.data.has_gps_fix else "no",
        }
