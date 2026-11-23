"""Main application file. It runs the app."""

import time

import folium
import pandas as pd
import plotly.graph_objects as go
import streamlit as st
from plotly.subplots import make_subplots

from src.app_config import FOOTER_HTML
from src.dashboard import dashboard
from src.exceptions import MeasurementError
from src.helper import get_files_in_directory
from src.readers import DataReader
from src import report
from src.trajectory import CAR_COLOR, build_trajectory_map
from src.vehicle import Vehicle

PANEL_HEIGHT = 450  # px, map and signal plot share one row and get the same height


def replay_channel(vehicle: Vehicle) -> str:
    """Name of the browser channel on which the replay publishes the vehicle position."""
    return f"vehicle-replay-{id(vehicle)}"


@st.cache_data(show_spinner=False)
def trajectory_html(track: pd.DataFrame, channel: str) -> str:
    """The map as HTML. Cached, so a rerun returns the identical HTML and the browser keeps the map as it is (no reload,
    no flickering, zoom and position stay)."""
    return build_trajectory_map(track, live_channel=channel).get_root().render()


def render_sidebar() -> Vehicle | None:
    """Control center: select and load a file, show its key figures. Returns the loaded vehicle."""
    with st.sidebar:
        selected_file_format = st.selectbox("Select data type", DataReader.supported_formats(),
                                            index=None, placeholder="Choose a data type")

        existing_measurement_files = get_files_in_directory(selected_file_format) if selected_file_format else []
        selected_file = st.selectbox("Select file from storage:", existing_measurement_files,
                                     format_func=lambda path: path.name, placeholder="Choose a file",
                                     index=None, disabled=selected_file_format is None)

        if st.button("Load data", disabled=selected_file is None):
            st.session_state["loaded_file"] = selected_file
            try:
                st.session_state["vehicle"] = Vehicle.from_file(selected_file)
            except MeasurementError as error:   # one except for every problem with the data
                st.error(f"Could not load {selected_file.name}: {error}")

        vehicle = st.session_state.get("vehicle")
        if vehicle is not None:
            render_summary(vehicle)
        return vehicle


def render_summary(vehicle: Vehicle) -> None:
    """Key figures as a small table, built only from Streamlit elements."""
    with st.container(border=True):
        st.markdown(f":green[●] **{report.status(vehicle)}**") # https://docs.streamlit.io/develop/api-reference/text/st.markdown
        summary = pd.DataFrame(report.summary(vehicle).items(), columns=["Figure", "Value"])
        st.dataframe(summary, hide_index=True, width="stretch")


def render_trajectory(vehicle: Vehicle) -> None:
    """GPS track of the drive on a map."""
    st.subheader("Trajectory")
    if not vehicle.data.has_gps_fix:
        st.info("This measurement has no GPS positions.")
        return

    # We use an iframe to change its content. An <iframe> in HTML allows you to embed another HTML document within the 
    # current page.
    st.iframe(trajectory_html(vehicle.data.gps_track, replay_channel(vehicle)), height=PANEL_HEIGHT)


def render_signals(vehicle: Vehicle) -> None:
    """Selected signals over time, one subplot per signal (different units), shared time axis."""
    st.subheader("Signals over time")
    signals = {
        "Velocity in km/h": vehicle.speed,
        "Longitudinal acceleration in m/s^2": vehicle.data.accel_x,
        "Lateral acceleration in m/s^2": vehicle.data.accel_y,
        "Steering angle in deg": vehicle.steering_angle,
        "Steering wheel angle in deg": vehicle.steering_wheel_angle,
        "Curvature in 1/m": vehicle.data.curvature,
    }

    selected_signals = st.multiselect("Signals", list(signals), default=list(signals)[0],
                                      label_visibility="collapsed", placeholder="Choose signals")
    if not selected_signals:
        st.info("Choose at least one signal.")
        return

    figure = make_subplots(rows=len(selected_signals), cols=1, shared_xaxes=True,
                           vertical_spacing=0.08, subplot_titles=selected_signals)
    for row, label in enumerate(selected_signals, start=1):
        figure.add_trace(go.Scatter(x=vehicle.time, y=signals[label], mode="lines", name=label), row=row, col=1)
    figure.update_xaxes(title_text="Time in s", row=len(selected_signals), col=1)
    # fill the panel next to the map, grow only when many signals are selected
    figure.update_layout(height=max(PANEL_HEIGHT - 60, 180 * len(selected_signals)),
                         showlegend=False, margin=dict(t=30, b=40, l=10, r=10))
    st.plotly_chart(figure, width="stretch")


def render_driving_dynamics(vehicle: Vehicle) -> None:
    """Replay of steering wheel, velocity and acceleration. Also moves the car on the map."""
    st.subheader("Driving dynamics")
    dashboard(vehicle, channel=replay_channel(vehicle))


def render_naive_replay(vehicle: Vehicle) -> None:
    """Replay of the measurement. 

    For every step Python builds a new folium map (track + current position), renders it to HTML
    and replaces the iframe. The browser has to load Leaflet and all map tiles again each time,
    so the map flickers.
    """
    st.subheader("Naive replay")
    if not vehicle.data.has_gps_fix:
        st.info("This measurement has no GPS positions.")
        return

    col_rate, col_play = st.columns([3, 1], vertical_alignment="bottom")
    with col_rate:
        rate = st.select_slider("Steps per second", options=[1, 2, 5, 10], value=2)
    with col_play:
        play = st.button("Play", width="stretch")

    status = st.empty() # st.empty() is a placeholder. Like allocating empty list. 
    map_slot = st.empty()

    track = vehicle.data.gps_track
    if not play:
        map_slot.iframe(build_trajectory_map(track).get_root().render(), height=PANEL_HEIGHT)
        status.caption("Press Play. Any other click (e.g. a widget) stops the replay, Streamlit reruns the script.")
        return

    step = max(1, round(vehicle.sample_rate / rate))
    started = time.perf_counter()
    for frame, sample in enumerate(vehicle.samples(step=step)):
        # no cache: the whole map (track with all points, markers, tiles) is built again for every step
        frame_map = build_trajectory_map(track)
        if sample.latitude != 0 and sample.longitude != 0:
            folium.CircleMarker([sample.latitude, sample.longitude], radius=8, color="white", weight=3,
                                fill=True, fill_color=CAR_COLOR, fill_opacity=1).add_to(frame_map)
        map_slot.iframe(frame_map.get_root().render(), height=PANEL_HEIGHT)

        lag = (time.perf_counter() - started) - frame / rate   # how far we are behind the planned clock
        status.markdown(f"t = **{sample.time:.1f} s** · v = **{sample.speed:.0f} km/h** · "
                        f"frame {frame} · lag **{max(lag, 0):.2f} s**")
        time.sleep(1 / rate)

st.set_page_config(page_title="Vehicle data visualizer", layout="wide")

vehicle = render_sidebar()

if vehicle is None:
    st.header("Vehicle data visualizer")
    st.info("Select a data type and a file in the sidebar, then press **Load data**.")
else:
    tab_overview, tab_naive = st.tabs(["Overview", "Naive map replay (Python only)"])
    with tab_overview:
        col_map, col_signals = st.columns(2, gap="large")
        with col_map:
            render_trajectory(vehicle)
        with col_signals:
            render_signals(vehicle)

        render_driving_dynamics(vehicle)

    with tab_naive:
        render_naive_replay(vehicle)

st.markdown(FOOTER_HTML, unsafe_allow_html=True)
