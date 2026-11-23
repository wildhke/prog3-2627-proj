"""Turns the numbers of a vehicle into text for humans (units, rounding, wording).

Single responsibility: the Vehicle computes values, this module decides how they are shown.
A new unit or another language changes only this module, never the Vehicle.
"""


def status(vehicle) -> str:
    """Short status line, e.g. used as title of the summary table in the sidebar."""
    return f"{vehicle.n_samples} samples loaded"


def summary(vehicle) -> dict[str, str]:
    """Key figures of the measurement as label -> formatted value."""
    return {
        "Duration": f"{vehicle.duration:.1f} s",
        "Sample rate": f"{vehicle.sample_rate:.0f} Hz",
        "Max speed": f"{vehicle.max_speed:.0f} km/h",
        "Max acceleration": f"{vehicle.max_accel_g:.2f} g",
        "Max steering wheel angle": f"{vehicle.max_steering_wheel_angle:.0f} deg",
        "GPS fix": "yes" if vehicle.data.has_gps_fix else "no",
    }
