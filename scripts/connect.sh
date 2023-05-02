WIFI_FILE="/home/rock/OrangeBox/status/wifi_connect_success.txt"
if [ ! -f "$WIFI_FILE" ]; then
    sleep 120
    source /boot/orange_box.config
    sudo nmcli -w 180 dev wifi connect "$SSID" password "$PASS" && \
    echo success > "$WIFI_FILE" && \
    echo "Successfully created WIFI connection." && \
    bash scripts/set_leds.sh
else
    echo "WIFI connection was already created."
    bash scripts/set_leds.sh
fi
