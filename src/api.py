"""API Caller for SportScroll.

Gathers the event data, grouped by sport and date from the SportsDB API.
"""

# Standard library Imports

# Related third party imports
import requests

# Local application/library specific imports
from src.config import load_config

BASE_URL = "https://www.thesportsdb.com/api/v1/json"
PREM_URL = "https://www.thesportsdb.com/api/v2/json"

REQUEST_TIMEOUT = 10


def _get_url():
    """Returns the URL for the API checking if premium is enabled.

    Returns:
        A string containing the full URL, including the API key.
    """
    url = PREM_URL if load_config()["premium"] else BASE_URL
    return f"{url}/{load_config()['key']}"


def get_events_on_date(league_id, target_date):
    """Calls the API to get event details and returns them as a list of dicts.

    Args:
        league_id: TheSportsDB numeric ID for the league (e.g. 4328 for the Premier League).
        target_date: A datetime object for the day to query.

    Returns:
        A list of event dicts or an empty list if no events were found.
    """
    url = f"{_get_url()}/eventsday.php"
    response = requests.get(url, params={"d": target_date.strftime("%Y-%m-%d"), "l": league_id}, timeout=REQUEST_TIMEOUT)
    if not response.text:
        return []
    events = response.json().get("events") or []
    return events


def get_tv(event_id):
    """Returns a list of TV channels based on users region."""
    # TODO: finish docustring, wire up to pdf data pipeline and check free vs premium features for get_tv
    url = f"{_get_url()}/lookuptv.php"
    response = requests.get(url, params={"id": event_id}, timeout = REQUEST_TIMEOUT)
    channels = response.json().get("tvevent") or []
    region = load_config()["tv_region"]
    channel_list = []
    for c in channels:
        if c.get("strCountry", "").lower() == region.lower():
            channel_list.append(c["strChannel"])
    if channel_list:
        return ", ".join(channel_list)
    else:
        return "unknown"