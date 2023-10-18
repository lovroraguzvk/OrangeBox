echo 1 > /tmp/led_state

# Set working directory.
cd /home/rock/OrangeBox

# Connect to WIFI.
echo "Trying to connect to WiFi."
bash scripts/connect.sh

# Check internet connection and update all repositories.
echo "Updating drivers."
# If DISABLE_UPDATE exists and is set to 1, then skip updating drivers.
if [ -z "$DISABLE_UPDATE" ] || [ "$DISABLE_UPDATE" != "1" ]; then
    bash scripts/update_drivers.sh
    echo "Updating drivers complete." 
else
    echo "Skipping driver update."
fi

# Run the main tmuxinator file.
echo "Starting tmuxinator."
cd /home/rock/OrangeBox
tmuxinator start -p start_all.yaml
echo "Tmuxinator running."
