# Standard library Imports
from datetime import timedelta, datetime
from pathlib import Path
from zoneinfo import ZoneInfo

# Related third party imports
import json

# Local application/library specific imports
from src.config import load_config

config = load_config()
tz = ZoneInfo(config["timezone"])

def save_cache(data):
    """writes a json to .cache which contains the api information to prevent hitting rate limits"""
    timestamp = datetime.now(tz).strftime("%Y%m%dT%H%M%SZ")
    cache_path = Path(".cache")
    cache_path.mkdir(exist_ok=True)
    file_path = cache_path / f"events-{timestamp}.json"
    with open(file_path, "w") as f:
        json.dump(data, f, indent=4)

def cache_valid():
    """Returns False if no cache exists or if the cache has expired past the configured TTL."""
    files = sorted(Path(".cache").glob("events-*.json"))
    if not files:
        return False
    latest = files[-1]
    latest = latest.stem
    _, latest = latest.split("-")
    cache_time = datetime.strptime(latest, "%Y%m%dT%H%M%SZ").replace(tzinfo=tz)
    timestamp = datetime.now(tz)
    if timestamp > cache_time + timedelta(minutes=config["cache_ttl_mins"]):
        return False

    return True

def load_cache():
    """loads and returns the most recent json from .cache, or None if no cache exists"""
    files = sorted(Path(".cache").glob("events-*.json"))
    if not files:
        return None
    latest = files[-1]
    with open(latest) as f:
        return json.load(f)
