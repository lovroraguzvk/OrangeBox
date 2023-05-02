# Set working directory.
cd /home/rock/OrangeBox

# Connect to WIFI.
bash scripts/connect.sh

# Check internet connection and update all repositories.
bash scripts/update_drivers.sh

# Run the main tmuxinator file.
tmuxinator start -p start_all.yaml
