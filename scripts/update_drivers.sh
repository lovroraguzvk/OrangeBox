#!/bin/bash
readonly PING_URL="https://www.github.com"

wget -q --tries=5 --timeout=2 --spider "$PING_URL"
if [ $? -eq 0 ]; then
    echo "Internet connection is available."
    git pull orgin main
    /home/rock/.local/bin/gitman install
else
    echo "Internet connection unavailable. Skipping update."
fi
