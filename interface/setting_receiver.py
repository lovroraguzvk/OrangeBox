import zmq
from subprocess import Popen

context = zmq.Context()
socket = context.socket(zmq.SUB)
socket.bind("tcp://*:5557")
socket.subscribe("")

while True:
    command = socket.recv_string(flags=0)
    command = command.split()
    print(f"received: {command}")
    if command[0] == "shutdown":
        p = Popen("sudo shutdown -h now", shell=True)
    elif command[0] == "reboot":
        p = Popen("sudo shutdown -r now", shell=True)
    elif command [0] == "freq":
        p = Popen (f"sed -i '/export INTERVAL/c\export INTERVAL={command[1]}' ~/.bashrc", shell=True)