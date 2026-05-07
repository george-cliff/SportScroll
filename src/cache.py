# Standard library Imports
from datetime import timedelta, datetime
from pathlib import Path
import json

# Related third party imports


# Local application/library specific imports
from src.config import load_config, get_timezone

CACHE_DIR = Path(".cache")
CACHE_GLOB = "events-*.json"
CACHE_TIMESTAMP = "%Y%m%dT%H%M%SZ"

def save_cache(data):
    """writes a json to .cache which contains the api information to prevent hitting rate limits"""
    timestamp = datetime.now(get_timezone()).strftime(CACHE_TIMESTAMP)
    CACHE_DIR.mkdir(exist_ok=True)
    file_path = CACHE_DIR / f"events-{timestamp}.json"
    with open(file_path, "w") as f:
        json.dump(data, f, indent=4)

def cache_valid():
    """Returns False if no cache exists or if the cache has expired past the configured TTL."""
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
    """loads and returns the most recent json from .cache, or None if no cache exists"""
    latest_file = _get_latest_cache_file()
    if latest_file is None:
        return None
    with open(latest_file) as f:
        return json.load(f)

def _get_latest_cache_file():
    files = sorted(CACHE_DIR.glob(CACHE_GLOB))
    return files[-1] if files else None