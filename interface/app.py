import dash
from dash import dcc
from dash import html
from dash import ctx
import dash_bootstrap_components as dbc
import pandas as pd
import plotly.express as px
from dash.dependencies import Output, Input, State
from datetime import datetime, timedelta
import pathlib

import os
import zmq

# Global variables
MEASUREMENT_PATH = pathlib.Path.home() / "measurements" #/ "measuerments" / "lrpi1"
DISPLAY_LAST_HOURS = 2
BOX_ID = 0
PORT = "ACM0"
ENERGY_PATH = pathlib.Path.home() / "measurements" / f"rockwp{BOX_ID}energy"
SUBDIRECTORY = f"rockwp{BOX_ID}_tty{PORT}"
context = zmq.Context()
SOCKET = context.socket(zmq.PUB)

print(SUBDIRECTORY)

# Set up the Dash app
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.LUX])


# Define the layout
app.layout = dbc.Container(
    [
        html.Div(id="intermediate-value", style={"display": "none"}),
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
                                    ["ACM0", "ACM1", "ACM2"],
                                    "ACM0",
                                    id="sensor-select",
                                    inline=True,
                                    inputStyle={
                                        "margin-left": "20px",
                                        "margin-right": "10px",
                                    },
                                )
                            ],
                            width=3,
                        ),
                        dbc.Col(
                            [html.Label("Orange/Grey Box ID")],
                            width=2,
                        ),
                        dbc.Col(
                            [
                                dbc.Input(
                                    type="number",
                                    value=BOX_ID,
                                    min=0,
                                    id="box_id-select",
                                ),
                            ],
                            width=1,
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
            style={"margin-top": "20px", "title": "Measurement Data"},
        ),
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
        dcc.Interval(
            id="interval-component",
            interval=2 * 1000,
            n_intervals=0,
        ),
    ],
    fluid=True,
)

# Callback for changing IP
@app.callback(
    Output("orange_box-ip", "invalid"),
    [Input("orange_box-ip", "value")],
)
def change_IP(value):
    context = zmq.Context()
    socket = context.socket(zmq.PUB)
    socket.connect(f"tcp://{value}:5557")
    global SOCKET
    SOCKET = socket
    print(SOCKET)
    return False

# Callback for change of measurement frequency
@app.callback(
    Output("orange_box-freq", "invalid"),
    [Input("orange_box-freq", "value")],
)
def change_freq(value):
    if value is None:
        return True
    SOCKET.send_string(f"freq {value}", flags=0)
    return False

# Callback for shutdown button
@app.callback(
    Output("orange_box-shutdown", "color"),
    [Input("orange_box-shutdown", "n_clicks")],
)
def shutdown(n):
    if n is None:
        raise dash.exceptions.PreventUpdate
    SOCKET.send_string("shutdown", flags=0)
    return "success" if n%2==0 else "danger"


# Callback for reboot button
@app.callback(
    Output("orange_box-reboot", "color"),
    [Input("orange_box-reboot", "n_clicks")],
)
def shutdown(n):
    if n is None:
        raise dash.exceptions.PreventUpdate
    SOCKET.send_string("reboot", flags=0)
    return "success" if n%2==0 else "danger"


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
        Input("box_id-select", "value"),
        Input("time-select", "value"),
    ],
)
def change_plot_settings(value1, value2, value3, value4, value5):
    trigger = ctx.triggered_id
    global BOX_ID, PORT, SUBDIRECTORY, MEASUREMENT_PATH, ENERGY_PATH, DISPLAY_LAST_HOURS
    if trigger == "measurement-path":
        new_path = pathlib.Path(value1)
        MEASUREMENT_PATH = new_path
    elif trigger == "energy-path":
        new_path = pathlib.Path(value2)
        ENERGY_PATH = new_path
    elif trigger == "sensor-select":
        PORT = value3
        SUBDIRECTORY = f"rockwp{BOX_ID}_tty{PORT}"
    elif trigger == "box_id-select":
        BOX_ID = value4
        SUBDIRECTORY = f"rockwp{BOX_ID}_tty{PORT}"
        ENERGY_PATH = pathlib.Path.home() / "measurements" / f"rockwp{BOX_ID}energy"
    elif trigger == "time-select":
        DISPLAY_LAST_HOURS = value5
    print(SUBDIRECTORY)
    return None


# Callback to update live plots
@app.callback(
    [Output("mu_plot", "figure"), Output("energy_plot", "figure")],
    [Input("interval-component", "n_intervals")],
)
def update_plots(n):
    # Load the updated data from the CSV file
    file_names = os.listdir(MEASUREMENT_PATH / SUBDIRECTORY)
    file_names.sort()
    df = pd.read_csv(MEASUREMENT_PATH / SUBDIRECTORY / file_names[-1])
    df["timestamp"] = pd.to_datetime(df["timestamp"])  # convert to datetime object

    # Filter the data for the sliding window
    df_window = df.loc[df['timestamp'] > pd.Timestamp.now() - pd.Timedelta(hours=2)]
    #df_window = df.loc[
    #    df["timestamp"]
    #    > pd.Timestamp(year=2021, month=5, day=31, hour=14, minute=30)
    #    - pd.Timedelta(hours=DISPLAY_LAST_HOURS)
    #]
    # Create the first plot
    fig1 = px.line(
        df_window,
        x="timestamp",
        y=[
            "temp_external",
            "light_external",
            "humidity_external",
            "differential_potential_ch1",
            "differential_potential_ch2",
        ],
        title="Measurement Data",
        template="plotly",
    )
    fig1["layout"]["uirevision"] = "1"

    # Create the third plot
    # Load the updated data from the CSV file
    file_names = os.listdir(ENERGY_PATH)
    file_names.sort()
    df = pd.read_csv(ENERGY_PATH / file_names[-1])
    df["timestamp"] = pd.to_datetime(df["timestamp"])  # convert to datetime object
    df_window = df.loc[df['timestamp'] > pd.Timestamp.now() - pd.Timedelta(hours=2)]

    fig3 = px.line(
        df_window, x="timestamp", y = ["bus_voltage_solar","current_solar","bus_voltage_battery","current_battery"]#x="time", y=["value1", "value2"], title="Energy Consumption"
    )
    fig3["layout"]["uirevision"] = "3"
    # Return the updated figures
    return fig1, fig3


# Run the app
if __name__ == "__main__":
    app.run_server(debug=True)
