
"""Main application file. It runs the app."""

import plotly.graph_objects as go
import pandas as pd
import streamlit as st
from plotly.subplots import make_subplots

from src.config import SUPPORTED_DATA_FORMATS
from src.app_config import FOOTER_HTML
from src.dashboard import dashboard
from src.helper import get_files_in_directory
from src.vehicle import Vehicle


# Sidebar as control-center of the app. Every setting etc. is located in here.
with st.sidebar:
    selected_file_format = st.selectbox(
        "Select data type",
        SUPPORTED_DATA_FORMATS, 
        index=None,
        placeholder="Choose a data type"
        )

    existing_measurement_files = (get_files_in_directory(selected_file_format) if selected_file_format else [])
    selected_file = st.selectbox("Select file from storage:",
        existing_measurement_files,
        format_func=lambda path: path.name,
        placeholder="Choose a file",
        index=None,
        disabled=selected_file_format is None,
        )

    btn_load_data = st.button("Load data", disabled=selected_file is None)

    if btn_load_data:
        # the vehicle chooses the matching reader for the file format
        st.session_state["loaded_file"] = selected_file
        st.session_state["vehicle"] = Vehicle.from_file(selected_file)


    if "vehicle" in st.session_state:
        vehicle = st.session_state["vehicle"]
        # key figures as a small table, built only from Streamlit elements
        with st.container(border=True):
            st.markdown(f":green[●] **{vehicle.status}**")
            summary = pd.DataFrame(vehicle.summary.items(), columns=["Figure", "Value"])
            st.dataframe(summary, hide_index=True, width="stretch")

# Show basic signals over the time.
if "vehicle" in st.session_state:
    vehicle = st.session_state["vehicle"]
    data = vehicle.data
    signals = {
        "Velocity in km/h": data.speed,
        "Longitudinal acceleration in m/s^2": data.accel_x,
        "Lateral acceleration in m/s^2": data.accel_y,
        "Steering angle in deg": vehicle.steering_angle,
        "Steering wheel angle in deg": vehicle.steering_wheel_angle,
        "Curvature in 1/m": data.curvature,
    }

    selected_signals = st.multiselect("Signals over time", list(signals),
                                      default=list(signals)[0])
    if selected_signals:
        time = vehicle.time
        # one subplot per signal (different units), all share the time axis
        figure = make_subplots(rows=len(selected_signals), cols=1,
                               shared_xaxes=True, vertical_spacing=0.06,
                               subplot_titles=selected_signals)
        for row, label in enumerate(selected_signals, start=1):
            figure.add_trace(go.Scatter(x=time, y=signals[label],
                                        mode="lines", name=label),
                             row=row, col=1)
        figure.update_xaxes(title_text="Time [s]",
                            row=len(selected_signals), col=1)
        figure.update_layout(height=220 * len(selected_signals) + 60,
                             showlegend=False, margin=dict(t=40, b=40))
        st.plotly_chart(figure, width="stretch")

    st.subheader("Driving dynamics")

    # Steering wheel, velocity and acceleration as animation.
    dashboard(vehicle)


st.markdown(FOOTER_HTML, unsafe_allow_html=True)
