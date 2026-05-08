"""Config loader for SportScroll.

Reads config.yaml once on first call and caches the result for the
lifetime of the process.
"""

# Standard library Imports
from functools import lru_cache
from zoneinfo import ZoneInfo

# Related third party imports
import yaml

# Local application/library specific imports


CONFIG_FILE = "config.yaml"


@lru_cache(maxsize=1)
def load_config():
    """Loads and returns the contents of config.yaml.

    Returns:
        A dict of the full config file contents.
    """
    with open(CONFIG_FILE, "r") as f:
        config = yaml.safe_load(f)
    return config


@lru_cache(maxsize=1)
def get_timezone():
    """Returns the configured timezone as a ZoneInfo object.

    Returns:
        A ZoneInfo instance for the timezone string in config.yaml.
    """
    return ZoneInfo(load_config()["timezone"])

@lru_cache(maxsize=1)
def get_league_abbrs():
    """Returns a mapping of league config names to their abbreviations.

    Returns:
        A dict of {league name: abbreviation} for all configured leagues
        that have an abbr field set.
    """
    abbrs = {}
    for _, leagues in load_config()["sports"].items():
        for _, league in leagues.items():
            if "abbr" in league:
                abbrs[league["name"]] = league["abbr"]
    return abbrs



if __name__ == "__main__":
    print(load_config())
