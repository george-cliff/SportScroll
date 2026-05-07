import yaml
from functools import lru_cache
from zoneinfo import ZoneInfo


@lru_cache(maxsize=1)
def load_config():
    """loads and returns the config.yaml file"""
    with open("config.yaml", "r") as f:
        config = yaml.safe_load(f)
    return config

@lru_cache(maxsize=1)
def get_timezone():
    """returns the configured timezone as a ZoneInfo object"""
    return ZoneInfo(load_config()["timezone"])

if __name__ == "__main__":
    load_config()
