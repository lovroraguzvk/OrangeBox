#rm ~/OrangeBox/config/orange_box.config
rm ~/OrangeBox/status/wifi_connect_success.txt
rm -rf ~/OrangeBox/drivers/mu_interface/mu_interface/Sensor/logs
rm -rf ~/measurements/*
sudo rm /etc/NetworkManager/system-connections/*
echo 1 > ~/OrangeBox/status/experiment_number.txt
