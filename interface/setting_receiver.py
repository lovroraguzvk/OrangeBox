import zmq
import socket
from subprocess import Popen

ipaddr = socket.gethostbyname(socket.gethostname()) 
context = zmq.Context()
zsocket = context.socket(zmq.SUB)
zsocket.bind(f"tcp://{ipaddr}:5557")
zsocket.subscribe("")

while True:
    command = zsocket.recv_string(flags=0)
    command = command.split()
    print(f"received: {command}")
    if command[0] == "shutdown":
        p = Popen("sudo shutdown -h now", shell=True)
    elif command[0] == "reboot":
        p = Popen("sudo shutdown -r now", shell=True)
    elif command [0] == "freq":
        p = Popen (f"sed -i '/export MEAS_INT/c\export MEAS_INT={command[1]}' ~/.bashrc", shell=True)
    else:
        print(f'Unknown command: {command}')