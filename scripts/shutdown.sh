#!/bin/bash
drive_pin () {
    echo 17 | sudo tee /sys/class/gpio/export > /dev/null
    echo out | sudo tee /sys/class/gpio/gpio17/direction > /dev/null
    echo 1 | sudo tee /sys/class/gpio/gpio17/value > /dev/null     # output high
}

echo 0 > /tmp/led_state
sleep 0.2
drive_pin
sudo shutdown -h now
