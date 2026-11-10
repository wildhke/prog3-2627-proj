"""Animated dashboard (steering wheel, velocity, acceleration) that runs completely in the browser.

Python prepares the data once and hands it over to a small HTML/JavaScript page
(dashboard.html).
"""

import json
import math
from pathlib import Path

import streamlit as st

TEMPLATE = Path(__file__).with_name("dashboard.html")
DATA_RATE = 5  # Hz, samples sent to the browser.


def replay_data(vehicle, rate: int = DATA_RATE) -> dict:
    """Collects the signals for the dashboard with the sample generator of the vehicle."""
    step = max(1, round(vehicle.sample_rate / rate))
    columns = {"time": [], "speed": [], "accel": [], "steering": []}

    for sample in vehicle.samples(step=step):
        columns["time"].append(round(float(sample.time), 2))
        columns["speed"].append(round(float(sample.speed), 1))
        columns["accel"].append(round(math.hypot(sample.accel_x, sample.accel_y), 3))
        columns["steering"].append(round(float(sample.steering_wheel_angle), 1))

    # scale limits of the bars.
    columns["max_speed"] = math.ceil(vehicle.max_speed / 20) * 20
    columns["max_accel"] = math.ceil(vehicle.max_accel_g * 10) / 10

    return columns


def dashboard(vehicle, height: int = 400):
    """Shows the animated dashboard for the given vehicle."""

    html = TEMPLATE.read_text(encoding="utf-8")
    html = html.replace("__REPLAY_DATA__", json.dumps(replay_data(vehicle)))

    # the HTML is our own template filled with numbers, no user input -> safe to embed with JavaScript
    st.iframe(html, height=height)
