import os
import subprocess

from telegram_bot.telegram_bot import broadcast_message

if __name__=='__main__':
    command = "df -h / | awk '{print $5}' | grep -oP '\\d+%'"
    os.system(command)

    result = subprocess.run(command, shell=True, capture_output=True, text=True)

    percentage_info = result.stdout.strip()
    number = int(percentage_info.strip("%"))
    if number >= 80 and number < 90:
        broadcast_message(f"Memory usage ({str(number)}%) is above 80%, will soon delete")
    if number >= 90:
        broadcast_message(f"Memory usage ({str(number)}%) is above 90%, deleting files")
        #TODO: change path 
        folder_path = "/home/rock/measurements_backup"
        for folder in os.listdir(folder_path):
            # Get a list of files in the folder
            folder_joined = os.path.join(folder_path,folder)
            if os.path.isdir(folder_joined):
                files = os.listdir(folder_joined)

                # If there are files in the folder
                if len(files) > 1:
                    # Sort the files alphabetically
                    files.sort()

                    # Get the alphabetically first file
                    file_to_delete = files[0]

                    # Construct the full path to the file
                    file_path = os.path.join(folder_joined, file_to_delete)

                    # Delete the file
                    os.remove(file_path)
                    
                    #TODO: spojiti u jednu poruku
                    print(f"The file '{file_to_delete}' from '{folder}' has been deleted.")
                    broadcast_message(f"The file '{file_to_delete}' from '{folder}'  has been deleted.")
                else:
                    print(f"The folder '{folder}' doesn\'t contain enough files for deletion.")
                    broadcast_message(f"The folder '{folder}' doesn\'t contain enough files for deletion.")
                    