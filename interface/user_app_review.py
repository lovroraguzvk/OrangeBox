import os
import pathlib
from datetime import datetime, timedelta
from subprocess import Popen

import zmq
import dash
import pandas as pd
import plotly.express as px
import dash_bootstrap_components as dbc
from dash import dcc, html, ctx
from dash.dependencies import Output, Input, State
from plotly.subplots import make_subplots
import plotly.graph_objects as go

# Global variables
MEASUREMENT_PATH = pathlib.Path.home() / "measurements"
DISPLAY_LAST_HOURS = 1
PORT = "P06"
SENSORTYP = "BLE"  # MU, BLE
#ENERGY_PATH = pathlib.Path.home() / "measurements" / "Power"
#MEASUREMENT_PATH = pathlib.Path.home() / "measurements/OB-KON-2_1" / SENSORTYP / PORT

ORANGEBOX_LIST = []
SENSOR_LIST = []
SENSORTYP_LIST = []
DATAPATH_LIST = []

for sensortyp in os.listdir(MEASUREMENT_PATH / "OB-KON-2_1"):
    SENSORTYP_LIST.append(sensortyp)
    for sensor in os.listdir(MEASUREMENT_PATH / "OB-KON-2_1" /sensortyp):
        SENSOR_LIST.append(sensor)
        DATAPATH_LIST.append(MEASUREMENT_PATH / "OB-KON-2_1" / sensortyp / sensor)
MEASUREMENT_PATH =  pathlib.Path.home() / "measurements/OB-KON-2_1" / SENSORTYP / PORT

# context = zmq.Context()
# SOCKET = context.socket(zmq.PUB)

# Set up the Dash app
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.LUX])

# Define the layout
app.layout = dbc.Container(
    [
        html.Div(id="intermediate-value", style={"display": "none"}),
        # Name and settings button
        dbc.Row(
            [
                dbc.Col(
                    [
                        html.H1("WatchPlant Dashboard"),
                    ],
                    width=11,
                ),
            ],
            style={"margin-top": "20px"},
        ),
        html.Hr(),
        dbc.Row(
            [
                dbc.Col(
                    [
                        dcc.Dropdown(SENSOR_LIST, SENSOR_LIST[0], id='dropdown')
                    ]
                )
            ]
        ),
        dbc.Row(
            [
                dbc.Col(
                    [
                        dcc.Graph(
                            id="mu_plot",
                            config={
                                "displaylogo": False,
                                "edits": {"legendPosition": True},
                                "modeBarButtonsToRemove": ["autoScale2d"],
                                "scrollZoom": True,
                            },
                        )
                    ],
                    width=12,
                )
            ],
            style={"margin-top": "20px"},  # "title": "Measurement Data"},
        ),
        # Auto refresh
        dcc.Interval(
            id="interval-component",
            interval=5 * 1000,
            n_intervals=0,
        ),
    ],
    fluid=True,
)
# Main data plot
"""
dbc.Row(
    [
        dbc.Col(
            [
                dcc.Dropdown(SENSOR_LIST, SENSOR_LIST[0], id='dropdown')
            ]
        )
    ]
),
"""

@app.callback(
    Output("dropdown", "children"),
    Input('dropdown','value'),
)
def change_source(value):
    global PORT, MEASUREMENT_PATH, DATAPATH_LIST, SENSORTYP
    if "P06" in value:  # temperature node
        SENSORTYP = "BLE"
        PORT = "P06"
    elif "P" in value:  # electrical potential nodes
        SENSORTYP ="BLE"
        PORT = "P99"
    elif "CYB" in value:
        SENSORTYP = "MU"
    for path in DATAPATH_LIST:
        if value in str(path):
            MEASUREMENT_PATH = path
    return None



# Callback to toggle settings collaps
@app.callback(
    Output("settings-collapse", "is_open"),
    [Input("settings-button", "n_clicks")],
    [State("settings-collapse", "is_open")],
)
def toggle_collapse(n, is_open):
    return not is_open if n else is_open


# Callback to change settings
@app.callback(
    Output("intermediate-value", "children"),
    [
        Input("measurement-path", "value"),
        Input("energy-path", "value"),
        Input("sensor-select", "value"),
        Input("time-select", "value"),
    ],
)
def change_plot_settings(value1, value2, value3, value4):
    trigger = ctx.triggered_id
    global PORT, MEASUREMENT_PATH, ENERGY_PATH, DISPLAY_LAST_HOURS
    if trigger == "measurement-path":
        new_path = pathlib.Path(value1)
        MEASUREMENT_PATH = new_path
    elif trigger == "energy-path":
        new_path = pathlib.Path(value2)
        ENERGY_PATH = new_path
    elif trigger == "sensor-select":
        PORT = value3
        SENSORTYP = "MU"
        MEASUREMENT_PATH = pathlib.Path.home() / "measurements/OB-KON-2_1" / SENSORTYP / PORT
    elif trigger == "time-select":
        DISPLAY_LAST_HOURS = value4
    return None


# Callback to update live plots
@app.callback(
    Output("mu_plot", "figure"),
    Input("interval-component", "n_intervals"),
)
def update_plots(n):
    # Load the updated data from the CSV file (plant measurements)
    try:
        file_names = os.listdir(MEASUREMENT_PATH)
        file_names.sort()
        df = pd.DataFrame()
        counter = -1
        while df.empty:
            try:
                df = pd.read_csv(MEASUREMENT_PATH / file_names[counter])
                counter -=1
            except:
                print("no data stored")
                break
        df["datetime"] = pd.to_datetime(df["datetime"], format='%Y-%m-%d %H:%M:%S:%f')  # convert to datetime object
        # Filter the data for the sliding window
        df_window = df.loc[df['datetime'] > df['datetime'].iloc[-1]  - pd.Timedelta(hours=DISPLAY_LAST_HOURS)]
        # Create the first plot (MU data)
        if SENSORTYP == "MU":
            fig1 = px.line(
                df_window,
                x="datetime",
                y=[
                    "temp_external",
                    "light_external",
                    "humidity_external",
                    "differential_potential_ch1",
                    "differential_potential_ch2",
                    "transpiration",
                ],
                title="Measurement Data",
                template="plotly",
            )
        elif SENSORTYP == "BLE" and PORT == "P06":
            df_window.rename(columns={'temperature1': 'temperature_env_1', 'temperature2': 'temperature_env_2', 'temperature3': 'temperature_leaf_1', 'temperature4': 'temperature_leaf_2'}, inplace=True)
            fig1 = px.line(
                df_window,
                x="datetime",
                y=["temperature_env_1",
                    "temperature_env_2",
                    "temperature_leaf_1",
                    "temperature_leaf_2"
                ],
                title="Measurement Data",
                template="plotly",
            )
        elif SENSORTYP == "BLE" and PORT == "P99":
            fig1 = px.line(
                df_window,
                x="datetime",
                y="differential_potential",
                title="Measurement Data",
                template="plotly",
            )

        fig1["layout"]["uirevision"] = "1"
    except FileNotFoundError:
        fig1 = {}

    # Load the updated data from the CSV file (energy measurements)

    # Return the updated figures
    return fig1


# Run the app
if __name__ == "__main__":
    app.run_server(host='0.0.0.0', debug=False)
