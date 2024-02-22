import socket

try:
    import ruamel.yaml
    yaml = ruamel.yaml.YAML()
    yaml.preserve_quotes = True
    yaml.top_level_colon_align = 19
except ImportError:
    import yaml

def get_ip_address():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        return s.getsockname()[0]
    except OSError:
        return "127.0.0.1"
    
def get_hostname():
    return socket.gethostname()

def parse_config_file(file_path):
    # Example config file
    # export SSID="WatchPlant"
    # export PASS="zamioculcas"
    # export SINK="127.0.0.1"

    config = {}
    with open(file_path, "r") as f:
        for line in f:
            line = line.strip()
            if line.startswith("export"):
                line = line.replace("export ", "")
                key, value = line.split("=")
                config[key] = value.replace("\"", "")
    
    return config

def write_config_file(file_path, wifi_ssid, wifi_pass, sink_ip="127.0.0.1"):
    with open(file_path, "w") as f:
        f.write(f"export SSID=\"{wifi_ssid}\"\n")
        f.write(f"export PASS=\"{wifi_pass}\"\n")
        f.write(f"export SINK=\"{sink_ip}\"\n")

def update_experiment_number(file_path, skip_update=False):
    with open(file_path, "r") as f:
        experiment_number = int(f.read().strip())
        
    if not skip_update:
        experiment_number += 1
        with open(file_path, "w") as f:
            f.write(str(experiment_number))

    return experiment_number

def read_data_fields_from_file(file_path):
    try:
        with open(file_path, 'r') as file:
            config = yaml.load(file)
        return config if config else {}
    except FileNotFoundError:
        raise FileNotFoundError("File not found", file_path)

def save_date_fields_to_file(config, file_path):
    with open(file_path, 'w') as file:
        yaml.dump(config, file)
