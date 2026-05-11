"""Cache manager for SportScroll.

Reads and writes a timestamped JSON file in .cache/ so the API is only
hit once per configured TTL window.
"""

# Standard library Imports
import json
import logging
from datetime import datetime, timedelta
from pathlib import Path

# Related third party imports

# Local application/library specific imports
from sportscroll.config import load_config, get_timezone

logger = logging.getLogger(__name__)

CACHE_DIR = Path(".cache")
CACHE_GLOB = "events-*.json"
CACHE_TIMESTAMP = "%Y%m%dT%H%M%S"


def save_cache(data):
    """Saves a json to .cache which contains the API information to prevent hitting rate limits.

    Args:
        data: A dict which contains event data from the API.
    """
    timestamp = datetime.now(get_timezone()).strftime(CACHE_TIMESTAMP)
    try:
        CACHE_DIR.mkdir(exist_ok=True)
        if any(CACHE_DIR.glob(CACHE_GLOB)):
            logger.info("Cleaning cache - new file on the way")
            for old_file in CACHE_DIR.glob(CACHE_GLOB):
                old_file.unlink()
        file_path = CACHE_DIR / f"events-{timestamp}.json"
        with open(file_path, "w") as f:
            json.dump(data, f, indent=4)
    except OSError as e:
        logger.warning(f"Failed to save cache - PDF will still generate - {e}")
        return
    logger.info(f"Cache file saved successfully - {file_path}")


def cache_valid(date_from, date_to):
    """Checks if a cache file exists, is within TTL, and covers the required date window.

    Args:
        date_from: A datetime object for the start of the required window.
        date_to: A datetime object for the end of the required window.

    Returns:
        True if the cache can be used, False if there is no cache, it has expired,
        or it does not cover all dates in the window.
    """

    # Check for cache file existing
    latest_file = _get_latest_cache_file()
    if latest_file is None:
        logger.info("No cache file found - fetching new data")
        return False

    # Check for TTL expiry
    cache_str = latest_file.stem.removeprefix("events-")
    cache_time = datetime.strptime(cache_str, CACHE_TIMESTAMP).replace(tzinfo=get_timezone())
    timestamp = datetime.now(get_timezone())
    if timestamp > cache_time + timedelta(minutes=load_config()["cache_ttl_mins"]):
        logger.info("Cache expired - fetching new data")
        return False

    # Check for correct date of cache (stops date mismatches around midnight)
    num_days = (date_to - date_from).days
    try:
        with open(latest_file) as f:
            cached_data = json.load(f)
    except (OSError, json.JSONDecodeError) as e:
        logger.warning(f"Cache file unreadable - fetching fresh data - {e}")
        return False
    for i in range(num_days + 1):
        date_str = (date_from + timedelta(days=i)).strftime("%Y-%m-%d")
        if date_str not in cached_data:
            logger.info("Cache date mismatch - fetching new data")
            return False
    logger.info("Cache valid - loading from cache")
    return True


def load_cache():
    """Loads and returns the most recent json from .cache, or None if no cache exists.

    Returns:
        A dict containing cached event information.
    """
    latest_file = _get_latest_cache_file()
    if latest_file is None:
        logger.warning("Cache file missing after cache_valid() returned True - this shouldn't happen")
        return None
    try:
        with open(latest_file) as f:
            latest_json = json.load(f)
    except (OSError, json.JSONDecodeError) as e:
        logger.warning(f"Failed to read cache file {latest_file} - {e}")
        return None
    logger.info(f"Cache file loaded successfully - {latest_file}")
    return latest_json


def _get_latest_cache_file():
    """Sorts through CACHE_DIR using alphabetical sorting on the timestamp (YYYMMDDTHHMMSS) and returns the most recently created file."""
    files = sorted(CACHE_DIR.glob(CACHE_GLOB))
    return files[-1] if files else None