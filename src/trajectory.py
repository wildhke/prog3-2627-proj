"""Trajectory map of a measurement drive.

This module only builds the folium map. It does not know Streamlit, so the map can also be
saved as HTML or tested without running the app (single responsibility).
"""

import folium
import pandas as pd

from .exceptions import NoGpsDataError
from folium.template import Template

TILES = "OpenStreetMap"  # free tiles without API key
TRACK_COLOR = "#0A84FF"
START_COLOR = "#30D158"
END_COLOR = "#FF453A"
CAR_COLOR = "#FFB000"     # same color as the marker on the steering wheel
MAX_POINTS = 2000  # more points do not look better, they only slow down the browser


# The Template was AI-generates used Claude Opus 5.5 Medium.
class LiveMarker(folium.MacroElement):
    """Marker for the current vehicle position, moved by the replay in the browser.

    It listens on a BroadcastChannel for messages {latitude, longitude} and moves itself.
    Everything happens in the browser, Python is not involved while the replay runs.
    The map is extended by adding this element, the map itself is not changed (open/closed).
    """

    _template = Template("""
        {% macro script(this, kwargs) %}
        (function () {
            const map = {{ this._parent.get_name() }};
            const marker = L.circleMarker([0, 0], {
                radius: 8, color: "white", weight: 3, fillColor: "{{ this.color }}", fillOpacity: 1,
            });
            const channel = new BroadcastChannel({{ this.channel|tojson }});

            channel.onmessage = (event) => {
                const { latitude, longitude } = event.data;
                if (latitude === null || longitude === null) { marker.remove(); return; }  // no GPS fix

                const position = [latitude, longitude];
                marker.setLatLng(position);
                if (!map.hasLayer(marker)) marker.addTo(map);
                if (!map.getBounds().contains(position)) map.panTo(position);  // keep the car in view
            };
            channel.postMessage("request-position");  // the replay may have started before the map
        })();
        {% endmacro %}
    """)

    def __init__(self, channel: str, color: str = CAR_COLOR):
        super().__init__()
        self._name = "LiveMarker"
        self.channel = channel
        self.color = color


def build_trajectory_map(track: pd.DataFrame, live_channel: str | None = None,
                         max_points: int = MAX_POINTS) -> folium.Map:
    """Draws the GPS track (columns latitude, longitude) as a line with start and end marker.
    With `live_channel`, a marker follows the position broadcast by the replay."""
    if track.empty:
        raise NoGpsDataError("The track has no GPS positions")

    step = max(1, len(track) // max_points)
    points = track[["latitude", "longitude"]].iloc[::step].values.tolist()
    points.append(track[["latitude", "longitude"]].iloc[-1].tolist())  # keep the real end point

    trajectory_map = folium.Map(tiles=TILES, control_scale=True)
    folium.PolyLine(points, color=TRACK_COLOR, weight=4, opacity=0.9, tooltip="Trajectory").add_to(trajectory_map)
    _add_marker(trajectory_map, points[0], "Start", START_COLOR)
    _add_marker(trajectory_map, points[-1], "End", END_COLOR)
    if live_channel is not None:
        LiveMarker(live_channel).add_to(trajectory_map)

    trajectory_map.fit_bounds([track[["latitude", "longitude"]].min().tolist(),
                               track[["latitude", "longitude"]].max().tolist()])
    return trajectory_map


def _add_marker(trajectory_map: folium.Map, location: list, label: str, color: str) -> None:
    folium.CircleMarker(location, radius=7, color="white", weight=2, fill=True, fill_color=color,
                        fill_opacity=1, tooltip=label).add_to(trajectory_map)
