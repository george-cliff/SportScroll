# Standard library Imports
from datetime import date, timedelta, datetime
import json

# Related third party imports

# Local application/library specific imports
from src.config import load_config, get_timezone
from src.api import get_events_on_date
from src.cache import load_cache, save_cache, cache_valid

def get_events(target_date):
    """returns a dict of raw events from the api for a target date, grouped by sport"""
    raw_events = {}
    for category, leagues in load_config()["sports"].items():
        raw_events[category] = {}
        for key, league in leagues.items():
            if league["enabled"]: 
                events = get_events_on_date(league_id=league["league_id"], event_date=target_date)
                if events:
                    raw_events[category][league['name']] = events
    return raw_events

def get_latest_data(target_date):
    """takes in a date object, Checks if there is a valid cached json, and loads the data from that, if not valid calls get_events for 5 days (yesterday -> 3 days ahead) and saves to cache, returns a json of raw event data"""
    valid = cache_valid()
    if valid:
        raw_events = load_cache()
    else:
        raw_events = {}
        for i in range(-1, 4):
            fetch_date = target_date + timedelta(days=i)
            raw_events[fetch_date.strftime("%Y-%m-%d")] = get_events(target_date=fetch_date)
        save_cache(raw_events)
    return raw_events

def get_pdf_data():
    """slices the 5 day data into yesterday, today, and upcoming sections ready for the pdf and returns the dict"""
    pdf_date = datetime.now(get_timezone())
    latest_data = get_latest_data(pdf_date)
    yesterday_data = latest_data[str((pdf_date - timedelta(days=1)).date())]
    today_data = latest_data[str(pdf_date.date())]
    upcoming_data = {}
    for i in range(1, 4):
        target_date = pdf_date +  timedelta(days=i)
        upcoming_data[str(target_date.date())] = latest_data[str(target_date.date())]

    pdf_data = {
        "yesterday": yesterday_data,
        "today": today_data,
        "upcoming": upcoming_data
    }
    return pdf_data
    

if __name__ == "__main__":
    raw_events = get_latest_data(date.today())
    print(json.dumps(raw_events, indent=4))
    