
"""Main application file. It runs the app."""

import plotly.graph_objects as go
import streamlit as st
from plotly.subplots import make_subplots

from src.config import SUPPORTED_DATA_FORMATS
from src.app_config import FOOTER_HTML
from src.helper import get_files_in_directory
from src.vehicle import Vehicle


st.set_page_config(page_title="Data visualizer", layout="wide")
st.header("Vehicle data visualizer")
st.write("A lightweight vehicle data visualization tool")

# Sidebar as control-center of the app. Every setting etc. is located in here.
with st.sidebar:
    selected_file_format = st.selectbox("Select data type", SUPPORTED_DATA_FORMATS, index=None, placeholder="Choose a data type")

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
        if selected_file.suffix == ".csv":
            st.session_state["vehicle"] = Vehicle.from_csv(selected_file)
        else:
            raise NotImplementedError(f"File format {selected_file.suffix} is not supported yet.")


    if "vehicle" in st.session_state:
        vehicle = st.session_state["vehicle"]
        st.success(vehicle.status())

# Show basic signals over the time, the user decides which ones
if "vehicle" in st.session_state:
    data = st.session_state["vehicle"].data
    signals = {
        "Velocity [km/h]": data.v_x,
        "Longitudinal acceleration [m/s²]": data.a_x,
        "Lateral acceleration [m/s²]": data.a_y,
        "Steering wheel angle [deg]": data.swa_signed,
        "Curvature [1/m]": data.curv,
    }
    selected_signals = st.multiselect("Signals over time", list(signals),
                                      default=list(signals)[:2])
    if selected_signals:
        time = data.time - data.time.iloc[0]
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


st.markdown(FOOTER_HTML, unsafe_allow_html=True)
