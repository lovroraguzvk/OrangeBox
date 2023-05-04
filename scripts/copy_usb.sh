CONFIG_FILE=$1

if [[ -z $CONFIG_FILE ]]; then
    echo "Provide file name as first positional argument."
    exit 1
fi

sudo mkdir /media/usb
sudo mount /dev/sda1 /media/usb
if [ -f "/media/usb/orange_box.config" ]; then
    cp /media/usb/orange_box.config "$CONFIG_FILE"
    dos2unix "$CONFIG_FILE"
else
    cp /home/rock/OrangeBox/config/example.config "$CONFIG_FILE"
fi
sudo umount /media/usb
