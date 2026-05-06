import yaml

def load_config():
    """loads and returns the config.yaml file"""
    with open("config.yaml", "r") as f:
        config = yaml.safe_load(f)
    return config

if __name__ == "__main__":
    load_config()
