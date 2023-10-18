LED_SETTING=$1

# Show default: green led on, blue led flashing
if [[ -z $LED_SETTING ]]; then
    exit 1
fi

# Show success: green led flashing, blue led off
if [[ $LED_SETTING -eq 3 ]]; then
    sudo sh -c "echo 0 > /sys/class/leds/rockpis\:blue\:user/brightness"
    sudo sh -c "echo heartbeat > /sys/class/leds/rockpis\:green\:power/trigger"
# Show failure: green led flashing, blue led flashing
elif [[ $LED_SETTING -eq 2 ]]; then
    sudo sh -c "echo heartbeat > /sys/class/leds/rockpis\:blue\:user/trigger"
    sudo sh -c "echo heartbeat > /sys/class/leds/rockpis\:green\:power/trigger"
fi
