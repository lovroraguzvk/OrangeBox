#!/bin/bash
readonly PING_URL="https://github.com"

wget -q --tries=5 --timeout=2 --spider "$PING_URL"
if [ $? -eq 0 ]; then
    echo "Internet connection is available."
    cd /home/rock/OrangeBox
    echo "... Pulling from main repository."
    git pull origin main
    echo "... Building."
    bash /home/rock/OrangeBox/system/build_all.sh
    echo "... Updating gitman dependencies."
    /home/rock/.local/bin/gitman install
else
    echo "Internet connection unavailable. Skipping update."
fi
