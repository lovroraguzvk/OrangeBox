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
DISPLAY_LAST_HOURS = 2
PORT = "CYB1"
ENERGY_PATH = pathlib.Path.home() / "measurements" / "Power"
MEASUREMENT_PATH = pathlib.Path.home() / "measurements" / PORT
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
        html.Hr(),
        # Collapsable settings menu
        dbc.Collapse(
            [
                dbc.Row(
                    [
                        dbc.Col(
                            [
                                html.Label("Measurment File Path"),
                                dbc.Input(
                                    type="text",
                                    id="measurement-path",
                                    value=str(MEASUREMENT_PATH),
                                    debounce=True,
                                    className="mb-3",
                                ),
                            ],
                            width=6,
                        ),
                        dbc.Col(
                            [
                                html.Label("Energy Consumption File Path"),
                                dbc.Input(
                                    type="text",
                                    id="energy-path",
                                    value=str(ENERGY_PATH),
                                    debounce=True,
                                    className="mb-3",
                                ),
                            ],
                            width=6,
                        ),
                    ]
                ),
                dbc.Row(
                    [
                        dbc.Col(
                            [html.Label("What sensor node should be displayed?")],
                            width=3,
                        ),
                        dbc.Col(
                            [
                                dcc.RadioItems(
                                    ["CYB1", "CYB2", "CYB3", "CYB4"],
                                    "CYB1",
                                    id="sensor-select",
                                    inline=True,
                                    inputStyle={
                                        "margin-left": "20px",
                                        "margin-right": "10px",
                                    },
                                )
                            ],
                            width=4,
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
                html.Hr(),
            ],
            id="settings-collapse",
            is_open=False,
        ),
        # Main data plot
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
                        html.H3("Orange Box Settings"),
                        html.Label("IP address of Orange Box"),
                        dbc.Input(
                            type="text",
                            id="orange_box-ip",
                            value="172.16.0.197",
                            debounce=True,
                            className="mb-3",
                        ),
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


# Callback for show ip button
@app.callback(
    [Output("modal", "is_open"), Output("modal-body", "children"), Output("orange_box-ip", "value")],
    [Input("orange_box-show_ip", "n_clicks"), Input("close", "n_clicks")],
    [State("modal", "is_open")],
)
def toggle_modal(n1, n2, is_open):
    file_names = os.listdir(ENERGY_PATH)
    file_names.sort()
    df = pd.read_csv(ENERGY_PATH / file_names[-1])
    lastline = df.iloc[-1]
    text = f"IP address of Orange Box is: unknown"
    if n1 or n2:
        return not is_open, text, f"unknown"
    return is_open, text, f"unknown"


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
        MEASUREMENT_PATH = pathlib.Path.home() / "measurements" / PORT
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
    try:
        file_names = os.listdir(MEASUREMENT_PATH)
        file_names.sort()
        df = pd.read_csv(MEASUREMENT_PATH / file_names[-1])
        df["timestamp"] = pd.to_datetime(df["timestamp"])  # convert to datetime object

        # Filter the data for the sliding window
        df_window = df.loc[df['timestamp'] > pd.Timestamp.now() - pd.Timedelta(hours=DISPLAY_LAST_HOURS)]
        # Create the first plot (MU data)
        fig1 = px.line(
            df_window,
            x="timestamp",
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
        fig1["layout"]["uirevision"] = "1"
    except FileNotFoundError:
        fig1 = {}

    # Load the updated data from the CSV file (energy measurements)
    try:
        file_names = os.listdir(ENERGY_PATH)
        file_names.sort()
        df = pd.read_csv(ENERGY_PATH / file_names[-1])
        df["timestamp"] = pd.to_datetime(df["timestamp"])  # convert to datetime object
        df_window = df.loc[df['timestamp'] > pd.Timestamp.now() - pd.Timedelta(hours=DISPLAY_LAST_HOURS)]

        # Create the second plot (energy data)
        fig2 = make_subplots(specs=[[{"secondary_y": True}]])
        # Add traces
        fig2.add_trace(
            go.Scatter(x=df_window["timestamp"], y=df_window["bus_voltage_solar"],
            name="bus_voltage_solar", mode='lines', line_color="red", line = dict(dash='dash')), secondary_y=False,
        )

        fig2.add_trace(
            go.Scatter(x=df_window["timestamp"], y=df_window["current_solar"], name="current_solar", mode='lines', line_color="blue", line = dict(dash='dash')),
            secondary_y=True,
        )

        fig2.add_trace(
            go.Scatter(x=df_window["timestamp"], y=df_window["bus_voltage_battery"],
            name="bus_voltage_battery", mode='lines', line_color="red"), secondary_y=False,
        )

        fig2.add_trace(
            go.Scatter(x=df_window["timestamp"], y=df_window["current_battery"], name="current_battery", mode='lines', line_color="blue"),
            secondary_y=True,
        )

            # Add figure title
        fig2.update_layout(title_text="Energy Consumption")

        # Set x-axis title
        fig2.update_xaxes(title_text="timestamp")

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
    app.run_server(host= '0.0.0.0', debug=False)
