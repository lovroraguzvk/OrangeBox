#!/bin/bash
if [ "$1" = "" ]
then
echo ""
echo "  This script will set up udev rules that will always symlink Cybress MU
devices connected to a USB hub in a form of CYB<ID> depending on the port of
the hub where the device is connected. For example, if you connect the device
to the left most port, it will always be CYB0."
echo ""
echo "  To begin, insert only one device to the desired port and specify the
corresponding ID. Then run this script as:"
echo "" 
echo "  sudo $0 <desired ID of the hub port> [-n (overwrite file)]"
echo ""
exit
fi

usb_conf="/etc/udev/rules.d/99-cybres.rules"

if [ "$2" = "-n" ]
then
	sudo rm "$usb_conf"
fi

idVendor=`( udevadm info -a -n /dev/ttyACM0 | grep '{idVendor}' | head -n1 | xargs | grep -oP "==\K.*")`
portPath=`( udevadm info -a -n /dev/ttyACM0 | grep KERNELS | sed -n '2p' | xargs | grep -oP "==\K.*")`

echo "SUBSYSTEM==\"tty\", SUBSYSTEMS==\"usb\", KERNELS==\"$portPath\", ATTRS{idVendor}==\"$idVendor\", SYMLINK+=\"CYB$1\"" | sudo tee -a "$usb_conf"