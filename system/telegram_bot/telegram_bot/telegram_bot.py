import requests
import json
import telebot
from telebot import types
import pandas as pd
import matplotlib.pyplot as plt
from io import BytesIO
import os


bot_token = '6832163710:AAFjVIaAw1IriO3joopizxC14ac06EqlpCM'
bot = telebot.TeleBot(bot_token)
'''
chat_id = '6958177589'


def send_telegram_message(message: str,
                          chat_id: str = chat_id,
                          api_key: str = bot_token,
                          proxy_username: str = None,
                          proxy_password: str = None,
                          proxy_url: str = None):
    responses = {}

    proxies = None
    headers = {'Content-Type': 'application/json',
               'Proxy-Authorization': 'Basic base64'}
    data_dict = {'chat_id': chat_id,
                 'text': message,
                 'parse_mode': 'HTML',
                 'disable_notification': True}
    data = json.dumps(data_dict)
    url = f'https://api.telegram.org/bot{api_key}/sendMessage'
    response = requests.post(url,
                             data=data,
                             headers=headers,
                             proxies=proxies,
                             verify=False)
    return response
'''

def broadcast_message(message):
    with open("/home/rock/OrangeBox/system/telegram_bot/telegram_bot/IDs.txt", "r") as file:
        for id in file.readlines():
            mes = "THIS IS A BROADCAST MESSAGE:\n\t" + message
            bot.send_message(id, mes)
            print("Message sent")

@bot.message_handler(commands=['start'])
def handle_start(message):
    welcome_message = """
Welcome to the Telegram Bot!

Here are the available commands:
/start - Start the bot and get a welcome message.
/file - Upload a file to the bot.
/plot - Generate a plot based on the data.
/disconnect - Disconnect from the bot.
/add_id - Add your user ID to bot's broadcast list.
/remove_id - Remove your user ID from the bot's records.

Feel free to explore the bot's functionalities! If you have any questions, use the /help command.
"""
    bot.send_message(message.chat.id, welcome_message)
    

@bot.message_handler(commands=['help'])
def handle_start(message):
    welcome_message = """
Here are the available commands:
/start - Start the bot and get a welcome message.
/file - Upload a file to the bot.
/plot - Generate a plot based on the data.
/disconnect - Disconnect from the bot.
/add_id - Add your user ID to bot's broadcast list.
/remove_id - Remove your user ID from the bot's records.
"""
    bot.send_message(message.chat.id, welcome_message)

@bot.message_handler(commands=['add_id']) # subs
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
            bot.reply_to(message, "Bot has added your chat ID to the broadcast list")
        else:
            bot.reply_to(message, "Bot already has your ID")

@bot.message_handler(commands=['remove_id']) # unsubs
def handle_remove_id(message):
    # Open a file in write mode ("w" or "a" for append)
    with open("IDs.txt", "r") as file:
        # Read all lines from the file into a list
        lines = file.readlines()
    
    lines = [line for line in lines if line.strip() not in str(message.chat.id)]
    with open("IDs.txt", "w") as file:
        # Write the modified lines back to the file
        bot.reply_to(message, "ID removed")

        file.writelines(lines)

@bot.message_handler(commands=['disconnect'])
def handle_disconnect(message):
    bot.reply_to(message, "Disconnected")
    #send_telegram_message("Disconnected")
    # You can add additional logic here if needed.

@bot.message_handler(commands=['file']) # zipa fileove i posalje zip
def handle_file(message):
    file_path = 'measurements.xlsx'  # Replace with the actual path to your file
    with open(file_path, 'rb') as file:
        bot.send_document(message.chat.id, file)

@bot.message_handler(commands=['plot']) # odvojiti plot_meas i plot_sens
def send_plot(message):
    file_path = 'measurements.xlsx'  # Replace with the actual path to your Excel file
    try:
        # Read the Excel file into a DataFrame
        df = pd.read_excel(file_path)

        # Create a plot
        plt.plot(df.iloc[:, 0], df.iloc[:, 1])
        plt.xlabel('X Axis')
        plt.ylabel('Y Axis')
        plt.title('Measurement Data')

        # Save the plot as an image
        image_path = 'measurement_plot.png'
        plt.savefig(image_path)
        plt.close()  # Close the plot to free up resources

        # Send the image via Telegram
        with open(image_path, 'rb') as image:
            bot.send_photo(message.chat.id, image)

        # Remove the temporary image file
        os.remove(image_path)

    except Exception as e:
        print(f"Error: {e}")

if __name__=='__main__': # neki flag za postojanje bota (while)
    try:
        print("Bot started")
        bot.polling(interval = 2)
    except Exception as e:
        print(f"Error: {e}")
        # Handle the error as needed, e.g., sleep and retry.

