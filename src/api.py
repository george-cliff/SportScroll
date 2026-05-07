# Standard library Imports

# Related third party imports
import requests

# Local application/library specific imports
from src.config import load_config

BASE_URL = "https://www.thesportsdb.com/api/v1/json"
PREM_URL = "https://www.thesportsdb.com/api/v2/json"

REQUEST_TIMEOUT = 10

def get_url():
    """returns the URL depending if the user has toggled premium in config"""
    url = PREM_URL if load_config()["premium"] else BASE_URL
    return f"{url}/{load_config()['key']}"

def get_events_on_date(league_id, target_date):
    """calls the api to get the event details as a json and returns that json"""
    url = f"{get_url()}/eventsday.php"
    response = requests.get(url, params={"d": target_date.strftime("%Y-%m-%d"), "l": league_id}, timeout = REQUEST_TIMEOUT)
    if not response.text:
        return []
    events = response.json().get("events") or []
    return events

def get_tv(event_id):
    """planned: uses the timezone in config to get TV stations showing the event, returns a list of tv stations or unknown (WIP — not yet wired into the PDF pipeline.)"""
    url = f"{get_url()}/lookuptv.php"
    response = requests.get(url, params={"id": event_id}, timeout = REQUEST_TIMEOUT)
    channels = response.json().get("tvevent") or []
    region = load_config()["tv_region"]
    channel_list = [] # handles cases where multiple channels are showing the same event
    for c in channels:
        if c.get("strCountry", "").lower() == region.lower():
            channel_list.append(c["strChannel"])
    if channel_list:
        return ", ".join(channel_list)
    else:
        return "unknown"