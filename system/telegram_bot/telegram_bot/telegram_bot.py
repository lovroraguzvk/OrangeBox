import requests
import json
import telebot
from telebot import types
import pandas as pd
import matplotlib.pyplot as plt
from io import BytesIO
import os
import shutil
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import plotly.express as px
import pathlib
import subprocess
import dash
import dash_bootstrap_components as dbc
from datetime import datetime
from time import sleep


bot_token = os.getenv('BOT_TOKEN')
bot = telebot.TeleBot(bot_token)

def broadcast_message(message):
    with open("/home/rock/OrangeBox/system/telegram_bot/telegram_bot/IDs.txt", "r") as file:
        for id in file.readlines():
            bot.send_message(id, message)
            print("Message sent")

@bot.message_handler(commands=['start'])
def handle_start(message):
    welcome_message = """
Welcome to the Telegram Bot!

Here are the available commands:
/start - Start the bot and get a welcome message.
/meas_files - Get .zip folder of all measurements.
/power_plot - Generate a plot based on the data.
/subscribe - Recieve update messages from the bot.
/unsubscribe - Unsubscribe from update messages.

Feel free to explore the bot's functionalities! If you have any questions, use the /help command.
"""
    bot.send_message(message.chat.id, welcome_message)
    

@bot.message_handler(commands=['help'])
def handle_start(message):
    welcome_message = """
Here are the available commands:
/start - Start the bot and get a welcome message.
/meas_files - Get .zip folder of all measurements.
/power_plot - Generate a plot based on the data.
/subscribe - Recieve update messages from the bot.
/unsubscribe - Unsubscribe from update messages.
"""
    bot.send_message(message.chat.id, welcome_message)

@bot.message_handler(commands=['subscribe']) # subs
def handle_add_id(message):
    # Open a file in write mode ("w" or "a" for append)
    existing_ids = []
    with open("IDs.txt", "r") as file:
        for line in file.readlines():
            existing_ids.append(line.strip())
    with open("IDs.txt", "a+") as file:
        # List of strings to store in the file
        #existing_ids = [line.strip() for line in file.readlines()]
        print(existing_ids)
        id = message.chat.id
        if str(id) not in existing_ids:
            file.write(str(id) + "\n")
            bot.reply_to(message, "Subscribed")
        else:
            bot.reply_to(message, "Already subscribed")

@bot.message_handler(commands=['unsubscribe']) # unsubs
def handle_remove_id(message):
    # Open a file in write mode ("w" or "a" for append)
    with open("IDs.txt", "r") as file:
        # Read all lines from the file into a list
        lines = file.readlines()
    
    lines = [line for line in lines if line.strip() not in str(message.chat.id)]
    with open("IDs.txt", "w") as file:
        # Write the modified lines back to the file
        file.writelines(lines)
    bot.reply_to(message, "Unsubscribed")

@bot.message_handler(commands=['meas_files']) 
def handle_file(message):
    folder_path = '/home/rock/measurements/'  
    try:
        shutil.make_archive('measurements', 'zip', folder_path)
        with open('measurements.zip', 'rb') as file:
            bot.send_document(message.chat.id, file)
        os.remove('measurements.zip')
    except Exception as e:
        print(f"Error: {e}")


@bot.message_handler(commands=['power_plot']) # odvojiti plot_meas i plot_sens
def send_plot(message):
    file_path = 'measurements.xlsx'  # Replace with the actual path to your Excel file
    try:
        MEASUREMENT_PATH = pathlib.Path.home() / "measurements"
        ENERGY_PATH = MEASUREMENT_PATH / "Power"
        time_select = 2

        file_names = os.listdir(ENERGY_PATH)
        file_names.sort()
        df = pd.read_csv(ENERGY_PATH / file_names[-1])
        # TODO: change back to datetime
        df["datetime"] = pd.to_datetime(df["timestamp"])  # convert to datetime object
        df_window = df.loc[df['datetime'] > pd.Timestamp.now() - pd.Timedelta(hours=time_select)]

        fig_power = make_subplots(specs=[[{"secondary_y": True}]])
        # Add traces
        fig_power.add_trace(
            go.Scatter(x=df_window["datetime"], y=df_window["bus_voltage_solar"],
            name="bus_voltage_solar", mode='lines', line_color="red", line = dict(dash='dash')), secondary_y=False,
        )

        fig_power.add_trace(
            go.Scatter(x=df_window["datetime"], y=df_window["current_solar"], name="current_solar", mode='lines', line_color="blue", line = dict(dash='dash')),
            secondary_y=True,
        )

        fig_power.add_trace(
            go.Scatter(x=df_window["datetime"], y=df_window["bus_voltage_battery"],
            name="bus_voltage_battery", mode='lines', line_color="red"), secondary_y=False,
        )

        fig_power.add_trace(
            go.Scatter(x=df_window["datetime"], y=df_window["current_battery"], name="current_battery", mode='lines', line_color="blue"),
            secondary_y=True,
        )

            # Add figure title
        fig_power.update_layout(title_text="Energy Consumption")

        # Set x-axis title
        fig_power.update_xaxes(title_text="datetime")

        # Set y-axes titles
        fig_power.update_yaxes(
            title_text="voltage [V]", 
            color="red",
            secondary_y=False)
        fig_power.update_yaxes(
            title_text="current [mA]", 
            color="blue",
            secondary_y=True)

        image_path = 'power_plot.png'
        fig_power.write_image(image_path)

        # Send the image via Telegram
        with open(image_path, 'rb') as image:
            bot.send_photo(message.chat.id, image)

        # Remove the temporary image file
        os.remove(image_path)

    except Exception as e:
        print(f"Error: {e}")

if __name__=='__main__': # neki flag za postojanje bota (while)
    while True:
        sleep(0.1)
        try:
            print("Bot started")
            bot.polling(non_stop=True)
        except Exception as e:
            print(f"Error: {e}")
            # Handle the error as needed, e.g., sleep and retry.

