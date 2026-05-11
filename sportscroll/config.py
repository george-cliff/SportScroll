"""Config loader for SportScroll.

Reads config.yaml once on first call and caches the result for the
lifetime of the process.
"""

# Standard library Imports
import logging
import os
from functools import lru_cache
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError


# Related third party imports
import yaml
from dotenv import load_dotenv

# Local application/library specific imports


CONFIG_FILE = "config.yaml"
ENV_FILE = ".env"

load_dotenv(ENV_FILE)

logger = logging.getLogger(__name__)


@lru_cache(maxsize=1)
def load_config():
    """Loads and returns the contents of config.yaml.

    Returns:
        A dict of the full config file contents.
    """
    try:
        with open(CONFIG_FILE, "r") as f:
            config = yaml.safe_load(f)
    except FileNotFoundError:
        logger.exception("config.yaml not found - check it exists in the project root")
        raise
    except yaml.YAMLError:
        logger.exception("config.yaml is malformed - check the syntax")
        raise
    return config


@lru_cache(maxsize=1)
def get_timezone():
    """Returns the configured timezone as a ZoneInfo object.

    Returns:
        A ZoneInfo instance for the timezone string in config.yaml.
    """
    try:
        tz_name = load_config()["timezone"]
        return ZoneInfo(tz_name)
    except ZoneInfoNotFoundError:
        logger.exception(f"Invalid timezone {tz_name!r} - check config.yaml")
        raise
    except KeyError:
        logger.exception("Timezone key missing - check config.yaml")
        raise


def get_football_data_key():
    """Returns the football-data.org API key from the environment.

    Returns:
        A string containing the football-data.org API key, or None if not set.
    """
    return os.environ.get("FOOTBALL_DATA_API_KEY")


@lru_cache(maxsize=1)
def get_league_abbrs():
    """Returns a mapping of league names to their competition code keys.

    Returns:
        A dict of {league name: competition code} for all configured leagues.
    """
    abbrs = {}
    for _, leagues in load_config()["sports"].items():
        for code, league in leagues.items():
            abbrs[league["name"]] = code
    return abbrs


if __name__ == "__main__":
    print(load_config())
