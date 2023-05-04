import zmq
import socket
from subprocess import Popen


def get_ip_address():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        return s.getsockname()[0]
    except OSError:
        return "127.0.0.1"
    
ipaddr = get_ip_address()
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