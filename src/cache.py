"""Cache manager for SportScroll.

Reads and writes a timestamped JSON file in .cache/ so the API is only
hit once per configured TTL window.
"""


# Standard library Imports
from datetime import timedelta, datetime
import json
from pathlib import Path


# Related third party imports


# Local application/library specific imports
from src.config import load_config, get_timezone

CACHE_DIR = Path(".cache")
CACHE_GLOB = "events-*.json"
CACHE_TIMESTAMP = "%Y%m%dT%H%M%SZ"


def save_cache(data):
    """Writes a json to .cache which contains the API information to prevent hitting rate limits.
    
    Args:
        data: A dict which contains event data from the API
    """
    timestamp = datetime.now(get_timezone()).strftime(CACHE_TIMESTAMP)
    CACHE_DIR.mkdir(exist_ok=True)
    file_path = CACHE_DIR / f"events-{timestamp}.json"
    with open(file_path, "w") as f:
        json.dump(data, f, indent=4)


def cache_valid():
    """Checks if there is a file in the cache and it is within the TTL.
    
    Returns:
        True if the cache can be used, False if there is no cache or it has expired
    """
    latest_file = _get_latest_cache_file()
    if latest_file is None:
        return False
    cache_str = latest_file.stem.removeprefix("events-")
    cache_time = datetime.strptime(cache_str, CACHE_TIMESTAMP).replace(tzinfo=get_timezone())
    timestamp = datetime.now(get_timezone())
    if timestamp > cache_time + timedelta(minutes=load_config()["cache_ttl_mins"]):
        return False

    return True


def load_cache():
    """Loads and returns the most recent json from .cache, or None if no cache exists.
    
    Returns:
        A dict containing cached event information
    """
    latest_file = _get_latest_cache_file()
    if latest_file is None:
        return None
    with open(latest_file) as f:
        return json.load(f)


def _get_latest_cache_file():
    """Sorts through CACHE_DIR and returns the most recently created file."""
    files = sorted(CACHE_DIR.glob(CACHE_GLOB))
    return files[-1] if files else None