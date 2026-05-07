import yaml
from functools import lru_cache
from zoneinfo import ZoneInfo

CONFIG_FILE = "config.yaml"


@lru_cache(maxsize=1)
def load_config():
    """loads and returns the config file"""
    with open(CONFIG_FILE, "r") as f:
        config = yaml.safe_load(f)
    return config

@lru_cache(maxsize=1)
def get_timezone():
    """returns the configured timezone as a ZoneInfo object"""
    return ZoneInfo(load_config()["timezone"])

if __name__ == "__main__":
    print(load_config())
