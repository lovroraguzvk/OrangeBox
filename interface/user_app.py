from ast import In
from ipaddress import ip_address
from math import exp
import os
import pathlib
import re
import socket
from datetime import datetime, timedelta
from subprocess import Popen
from turtle import ht
from requests import get
from sympy import O

import zmq
import dash
import pandas as pd
import plotly.express as px
import dash_bootstrap_components as dbc
from dash import dcc, html, ctx
from dash.dependencies import Output, Input, State
from plotly.subplots import make_subplots
import plotly.graph_objects as go

import utils

# Constants
WIFI_FILE = pathlib.Path("/home/marko/PROJECTS/WatchPlant/OrangeBox/interface/orange_box.config")
MEASUREMENT_PATH = pathlib.Path.home() / "measurements"
EXPERIMENT_PATH = MEASUREMENT_PATH / "Legion-MK_1"
ENERGY_PATH = MEASUREMENT_PATH / "Power"



DISPLAY_LAST_HOURS = 2
PORT = "P06"
SENSORTYP = "BLE"  # MU, BLE
# MEASUREMENT_PATH = pathlib.Path.home() / "measurements/OB-KON-2_1" / SENSORTYP / PORT
# context = zmq.Context()
# SOCKET = context.socket(zmq.PUB)


infoPane = dbc.Col(
    [
        dbc.Row(
            [
                dbc.Col(
                    [html.H3("Orange Box Information")],
                ),
                dbc.Col(
                    [
                        dbc.Button(
                            "Refresh",
                            id="refresh-button",
                            color="primary",
                            className="ml-auto",
                        ),
                    ]
                ),
            ]
        ),
        dbc.Row(
            [
                dbc.Col(
                    [html.Label(f"IP address:")],
                    width='auto'
                ),
                dbc.Col(
                    [html.Label(f"N/A", id="orange_box-ip")]
                ),
            ],
        ),
        dbc.Row(
            [
                dbc.Col(
                    [html.Label(f"Hostname:")],
                    width='auto'
                ),
                dbc.Col(
                    [html.Label(f"N/A", id="orange_box-hostname")]
                ),
            ],
        ),
    ]
)

settingsPane = dbc.Col(
    [
        dbc.Row(
            [
                dbc.Col(
                    [html.H3("Orange Box Settings")],
                ),
                dbc.Col(
                    [
                        dbc.Button(
                            "Write",
                            id="update-button",
                            color="primary",
                            className="ml-auto",
                        ),
                    ],
                        width='auto'
                ),
                dbc.Col(
                    [html.Label(id="wifi-success", children="")],
                )
            ]
        ),
        dbc.Row(
            [
                dbc.Col(
                    [html.Label(f"WiFi name:")],
                    width='auto'
                ),
                dbc.Col(
                    [dbc.Input(id="wifi-name", type="text", value="")],
                    width=4,
                )
            ],
        ),
        dbc.Row(
            [
                dbc.Col(
                    [html.Label(f"WiFi password:")],
                    width='auto'
                ),
                dbc.Col(
                    [dbc.Input(id="wifi-password", type="text", value="")],
                    width=4,
                )
            ],
        ),
    ]
)

liveDataPlot = [
    
]
# Set up the Dash app
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.LUX])

# Define the layout
app.layout = dbc.Container(
    [
        html.Div(id="default-div", style={"display": "none"}),
        # Name
        dbc.Row(
            [
                dbc.Col(
                    [html.H1("WatchPlant Dashboard")],
                    width=True,
                ),
                dbc.Col(
                    [
                        dbc.Button(
                            "Settings",
                            id="settings-button",
                            color="primary",
                            className="ml-auto",
                        ),
                    ],
                    width=1,
                    className="ml-auto",
                ),
            ],
            style={"margin-top": "20px"},
        ),
        # Collapsable settings menu
        dbc.Collapse(
            [
                html.Hr(),
                dbc.Row(
                    [
                        infoPane,
                        settingsPane
                    ]
                ),
            ],
            id="settings-collapse",
            is_open=False,
        ),
        html.Hr(),
        # Live plot settings
        dbc.Row(
            [
                dbc.Col(
                    [html.H3("Live data plotting")], width=True)
            ],
        ),
        dbc.Row(
            [
                dbc.Col(
                    [html.Label("Select sensor node:")],
                    width='auto',
                ),
                dbc.Col(
                    [
                        dcc.Dropdown(
                            id="sensor-select",
                            options=[],
                            value="",
                        )
                    ],
                    width=2,
                ),
                dbc.Col(
                    [html.Label("How many hours to display?")],
                    width=2,
                ),
                dbc.Col(
                    [
                        dbc.Input(
                            type="number",
                            value=DISPLAY_LAST_HOURS,
                            min=1,
                            max=12,
                            id="time-select",
                        ),
                    ],
                    width=1,
                ),
            ]
        ),
        # Live plot graph
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
            style={"margin-top": "20px"},# "title": "Measurement Data"},
        ),
        # User controls and energy plot
        dbc.Row(
            [
                dbc.Col(
                    [
                        html.Hr(),
                        html.H3("Orange Box Configuration"),
                        html.Label("Change measurement frequency (in ms)"),
                        dbc.Input(
                            type="number",
                            id="orange_box-freq",
                            value="10000",
                            min="100",
                            max="10000000",
                            debounce=True,
                            className="mb-3",
                        ),
                        dbc.Button("Shutdown", id="orange_box-shutdown", outline=True, color="danger", className="me-1"),
                        dbc.Button("Reboot", id="orange_box-reboot", outline=True, color="danger", className="me-1"),
                        dbc.Button("Show IP of selected Orange Box", id="orange_box-show_ip", outline=True, color="success", className="me-1"),
                        dbc.Modal(
                            [
                                dbc.ModalHeader(dbc.ModalTitle("IP address of connected Orange Box")),
                                dbc.ModalBody("ip", id="modal-body"),
                                dbc.ModalFooter(
                                    dbc.Button(
                                        "Close", id="close", className="ms-auto", n_clicks=0
                                    )
                                ),
                            ],
                            id="modal",
                            is_open=False,
                        ),
                    ],
                    width=4,
                ),
                dbc.Col(
                    [
                        html.Hr(),
                        html.H3("Live power consumption"),
                        dcc.Graph(
                            id="energy_plot",
                            config={
                                "displaylogo": False,
                                "edits": {"legendPosition": True},
                                "modeBarButtonsToRemove": ["autoScale2d"],
                                "scrollZoom": True,
                            },
                        )
                    ],
                    width=8,
                ),
            ],
            style={"margin-top": "20px"},
        ),
        # Modal confirm dialog
        dcc.ConfirmDialog(
            id="confirm_shutdown",
            message="Are you sure you want to shutdown the Orange Box?",
        ),
        dcc.ConfirmDialog(
            id="confirm_reboot",
            message="Are you sure you want to reboot the Orange Box?",
        ),
        # Auto refresh
        dcc.Interval(
            id="interval-component",
            interval=10 * 1000,
            n_intervals=0,
        ),
        dcc.Store(id="sensor-select-store", data=[])
    ],
    fluid=True,
)

# Callback for changing IP
# @app.callback(
#     Output("orange_box-ip", "invalid"),
#     [Input("orange_box-ip", "value")],
# )
# def change_IP(value):
#     context = zmq.Context()
#     socket = context.socket(zmq.PUB)
#     socket.connect(f"tcp://{value}:5557")
#     global SOCKET
#     SOCKET = socket
#     return False

# Callback for change of measurement frequency
# @app.callback(
#     Output("orange_box-freq", "invalid"),
#     [Input("orange_box-freq", "value")],
# )
# def change_freq(value):
#     if value is None:
#         return True
#     SOCKET.send_string(f"freq {value}", flags=0)
#     return False

@app.callback(
    [
        Output("orange_box-ip", "children"), 
        Output("orange_box-hostname", "children"),
        Output("wifi-name", "value"),
        Output("wifi-password", "value"),
    ],
    Input("refresh-button", "n_clicks"),
)
def refresh_infoPane(value):
    ip_address = utils.get_ip_address()
    hostname = utils.get_hostname()
    
    wifi_config = utils.parse_config_file(WIFI_FILE)
    wifi_name = wifi_config.get("SSID", "N/A")
    wifi_password = wifi_config.get("PASS", "N/A")
    
    return ip_address, hostname, wifi_name, wifi_password


@app.callback(
        Output("wifi-success", "children"),
        Input("update-button", "n_clicks"),
        State("wifi-name", "value"),
        State("wifi-password", "value"),
)
def update_settings(n_clicks, wifi_name, wifi_password):
    if n_clicks is None:
        raise dash.exceptions.PreventUpdate
    
    try:
        utils.write_config_file(WIFI_FILE, wifi_name, wifi_password)
        return 'success'
    except Exception as e:
        return f"Error: {e}"


@app.callback(
    [Output("sensor-select", "options"), Output("sensor-select", "value")],
    Input("sensor-select-store", "data"),
    Input("sensor-select", "value"),
)
def update_dropdown_options(options, selected_value):
    return [{"label": entry, "value": entry} for entry in options], selected_value


@app.callback(
    Output("sensor-select-store", "data"),
    Input("interval-component", "n_intervals"),
)
def update_storages(n):
    experiment_path = pathlib.Path(EXPERIMENT_PATH)
    nodes = [node.name for node_type in experiment_path.iterdir() for node in node_type.iterdir()]
    
    return sorted(nodes)


# Callback for confirm shutdown dialog
@app.callback(
    Output("confirm_shutdown", "displayed"),
    [Input("orange_box-shutdown", "n_clicks")]
)
def confirm_shutdown(n_clicks):
    if n_clicks is None:
        raise dash.exceptions.PreventUpdate
    return True

# Callback for confirm reboot dialog
@app.callback(
    Output("confirm_reboot", "displayed"),
    [Input("orange_box-reboot", "n_clicks")]
)
def confirm_reboot(n_clicks):
    if n_clicks is None:
        raise dash.exceptions.PreventUpdate
    return True

# Callback for shutdown button
@app.callback(
    Output("orange_box-shutdown", "color"),
    [Input("confirm_shutdown", "submit_n_clicks")],
)
def shutdown(submit_n_clicks):
    if submit_n_clicks:
        Popen("~/OrangeBox/scripts/shutdown.sh", shell=True)
    return "danger" # if n%2==0 else "danger"


# Callback for reboot button
@app.callback(
    Output("orange_box-reboot", "color"),
    [Input("confirm_reboot", "submit_n_clicks")],
)
def reboot(submit_n_clicks):
    if submit_n_clicks:
        Popen("sudo shutdown -r now", shell=True)
    return "danger" # if n%2==0 else "danger"


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
    Output("default-div", "children"),
    [
        Input("sensor-select", "value"),
        Input("time-select", "value"),
    ],
)
def change_plot_settings(value3, value4):
    trigger = ctx.triggered_id
    global PORT, MEASUREMENT_PATH, ENERGY_PATH, DISPLAY_LAST_HOURS
    if trigger == "sensortyyp-select":
        #SENSORTYP = ?
        PORT = "P06"
    elif trigger == "sensor-select":
        PORT = value3
        SENSORTYP = "MU"
        MEASUREMENT_PATH = pathlib.Path.home() / "measurements/OB-KON-2_1" / SENSORTYP / PORT
    elif trigger == "time-select":
        DISPLAY_LAST_HOURS = value4
    return None


# Callback to update live plots
@app.callback(
    [Output("mu_plot", "figure"), Output("energy_plot", "figure")],
    [Input("interval-component", "n_intervals")],
)
def update_plots(n):
    # Load the updated data from the CSV file (plant measurements)
    print("showing plot")
    try:
        file_names = os.listdir(MEASUREMENT_PATH)
        file_names.sort()
        df = pd.read_csv(MEASUREMENT_PATH / file_names[-1])
        df["datetime"] = pd.to_datetime(df["datetime"],format='%Y-%m-%d %H:%M:%S:%f')  # convert to datetime object

        # Filter the data for the sliding window
        df_window = df.loc[df['datetime'] > pd.Timestamp.now() - pd.Timedelta(hours=DISPLAY_LAST_HOURS)]
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
        elif SENSORTYP == "BLE":
            fig1 = px.line(
                df_window,
                x="datetime",
                y=[
                    "temperature1",
                    "temperature2",
                    "temperature3",
                    "temperature4",
                ],
                title="Measurement Data",
                template="plotly",
            )



        fig1["layout"]["uirevision"] = "1"
    except FileNotFoundError:
        fig1 = {}

    # Load the updated data from the CSV file (energy measurements)
    try:
        file_names = os.listdir(ENERGY_PATH)
        file_names.sort()
        df = pd.read_csv(ENERGY_PATH / file_names[-1])
        df["datetime"] = pd.to_datetime(df["datetime"])  # convert to datetime object
        df_window = df.loc[df['datetime'] > pd.Timestamp.now() - pd.Timedelta(hours=DISPLAY_LAST_HOURS)]

        # Create the second plot (energy data)
        fig2 = make_subplots(specs=[[{"secondary_y": True}]])
        # Add traces
        fig2.add_trace(
            go.Scatter(x=df_window["datetime"], y=df_window["bus_voltage_solar"],
            name="bus_voltage_solar", mode='lines', line_color="red", line = dict(dash='dash')), secondary_y=False,
        )

        fig2.add_trace(
            go.Scatter(x=df_window["datetime"], y=df_window["current_solar"], name="current_solar", mode='lines', line_color="blue", line = dict(dash='dash')),
            secondary_y=True,
        )

        fig2.add_trace(
            go.Scatter(x=df_window["datetime"], y=df_window["bus_voltage_battery"],
            name="bus_voltage_battery", mode='lines', line_color="red"), secondary_y=False,
        )

        fig2.add_trace(
            go.Scatter(x=df_window["datetime"], y=df_window["current_battery"], name="current_battery", mode='lines', line_color="blue"),
            secondary_y=True,
        )

            # Add figure title
        fig2.update_layout(title_text="Energy Consumption")

        # Set x-axis title
        fig2.update_xaxes(title_text="datetime")

        # Set y-axes titles
        fig2.update_yaxes(
            title_text="voltage [V]", 
            color="red",
            secondary_y=False)
        fig2.update_yaxes(
            title_text="current [mA]", 
            color="blue",
            secondary_y=True)
        fig2["layout"]["uirevision"] = "3"
    except FileNotFoundError:
        fig2 = {}
    
    # Return the updated figures
    return fig1, fig2

# Run the app
if __name__ == "__main__":
    app.run_server(host= '0.0.0.0', debug=True)
