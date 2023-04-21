sleep 120
source /boot/orange_box.config
sudo nmcli -w 150 dev wifi connect "$SSID" password "$PASS"
echo success > /home/rock/orange_box/status/wifi_connect_success.txt
