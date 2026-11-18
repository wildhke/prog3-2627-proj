"""A vehicle with its loaded measurements.

Single responsibility: the Vehicle computes physical values from its measurement.
It does not know file formats (-> readers.py) and does not format text (-> report.py).
"""
from collections import namedtuple

import numpy as np

from .exceptions import InvalidMeasurementError
from .measurement import Measurement
from .readers import load_measurement


GRAVITY = 9.81

# One time step of the measurement.
Sample = namedtuple("Sample", ["time", "speed", "accel_x", "accel_y", "steering_wheel_angle",
                               "latitude", "longitude"])


class Vehicle:
    """A vehicle with its loaded measurement."""

    steering_ratio = 15.0

    def __init__(self, data: Measurement):
        self.data = data  # without underscore -> calls the setter

    @property
    def data(self) -> Measurement:
        return self._data

    @data.setter
    def data(self, value: Measurement):
        if value.n_samples < 2:
            raise InvalidMeasurementError("A measurement needs at least two samples")
        self._data = value

    @classmethod
    def from_file(cls, file):
        """Alternative constructor: Vehicle.from_file("drive.csv").
        Which reader is used is decided in readers.py, the Vehicle does not know any file format."""
        return cls(load_measurement(file))

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
        latitude, longitude = self.data.latitude, self.data.longitude

        for index in range(start, self.n_samples, step):
            yield Sample(time.iloc[index], speed.iloc[index], accel_x.iloc[index], accel_y.iloc[index],
                         steering_wheel_angle.iloc[index], latitude.iloc[index], longitude.iloc[index])

    def __iter__(self):
        """Makes the vehicle iterable: for sample in vehicle: ..."""
        return self.samples()
