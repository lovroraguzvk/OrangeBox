# Set working directory.
cd /home/rock/OrangeBox

# Connect to WIFI.
echo "Trying to connect to WiFi."
bash scripts/connect.sh

# Check internet connection and update all repositories.
echo "Updating drivers."
bash scripts/update_drivers.sh
echo "Updating drivers complete."

# Run the main tmuxinator file.
echo "Starting tmuxinator."
tmuxinator start -p start_all.yaml
echo "Tmuxinator running."
