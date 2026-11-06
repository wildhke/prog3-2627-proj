"""Measurement data of one drive, independent of the file format."""


class MeasurementData:
    """All signals of one measurement drive, one value per time step."""

    def __init__(self, time, speed, accel_x, accel_y, steering_angle,
                 curvature, latitude, longitude):
        self.time = time                      # s
        self.speed = speed                    # km/h
        self.accel_x = accel_x                # m/s^2, longitudinal
        self.accel_y = accel_y                # m/s^2, lateral
        self.steering_angle = steering_angle  # deg, signed
        self.curvature = curvature            # 1/m
        self.latitude = latitude              # deg, 0 before GPS fix
        self.longitude = longitude            # deg, 0 before GPS fix

    def n_samples(self) -> int:
        return len(self.time)

    def duration(self) -> float:
        """Length of the measurement in seconds."""
        return float(self.time.iloc[-1] - self.time.iloc[0])

    def sample_rate(self) -> float:
        """Samples per second in Hz."""
        return (self.n_samples() - 1) / self.duration()

    def summary(self) -> dict:
        """Key figures of the measurement, e.g. for the sidebar."""
        return {
            "samples": self.n_samples(),
            "duration in s": round(self.duration(), 1),
            "sample rate in Hz": round(self.sample_rate(), 1),
            "max speed in km/h": round(float(self.speed.max()), 1),
        }
