"""Data layer for SportScroll.

Fetches, caches, and slices event data into the structure consumed by the PDF renderer.
"""

# Standard library Imports
from datetime import date, timedelta, datetime
import json

# Related third party imports

# Local application/library specific imports
from sportscroll.config import load_config, get_timezone
from sportscroll.api import get_events_on_date
from sportscroll.cache import load_cache, save_cache, cache_valid

LOOKBACK_DAYS = 1
LOOKAHEAD_DAYS = 3
DATE_FORMAT = "%Y-%m-%d"


def _get_events(target_date):
    """Gathers all event information for a target_date, grouped by sport.
    
    Args:
        target_date: A datetime object.

    Returns:
        A dict containing all event information for all events on target_date.
    """
    raw_events = {}
    for category, leagues in load_config()["sports"].items():
        raw_events[category] = {}
        for _, league in leagues.items():
            if league["enabled"]: 
                events = get_events_on_date(league_id=league["league_id"], target_date=target_date)
                if events:
                    raw_events[category][league['name']] = events
    return raw_events


def get_latest_data(target_date=None):
    """Returns a full 5-day window of event data, using the cache if valid.

    Args:
        target_date: a date object for the fetch window. Defaults to now if not provided.

    Returns:
        A dict keyed by ISO date string, each value being a dict of categories and leagues.
    """
    if target_date is None:
        target_date = datetime.now(get_timezone())
    valid = cache_valid()
    if valid:
        raw_events = load_cache()
    else:
        raw_events = {}
        for i in range(-LOOKBACK_DAYS, LOOKAHEAD_DAYS + 1):
            fetch_date = target_date + timedelta(days=i)
            raw_events[fetch_date.strftime(DATE_FORMAT)] = _get_events(target_date=fetch_date)
        save_cache(raw_events)
    return raw_events


def get_pdf_data():
    """Returns event data sliced into yesterday, today, and upcoming sections.

    Returns:
        A dict with keys 'yesterday', 'today', and 'upcoming', ready for the PDF renderer.
    """
    pdf_date = datetime.now(get_timezone())
    latest_data = get_latest_data(pdf_date)
    yesterday_data = latest_data[(pdf_date - timedelta(days=LOOKBACK_DAYS)).strftime(DATE_FORMAT)]
    today_data = latest_data[pdf_date.strftime(DATE_FORMAT)]
    upcoming_data = {}
    for i in range(1, LOOKAHEAD_DAYS + 1):
        target_date = pdf_date + timedelta(days=i)
        upcoming_data[target_date.strftime(DATE_FORMAT)] = latest_data[target_date.strftime(DATE_FORMAT)]

    pdf_data = {
        "yesterday": yesterday_data,
        "today": today_data,
        "upcoming": upcoming_data
    }
    return pdf_data


if __name__ == "__main__":
    raw_events = get_latest_data(datetime(2026, 5, 10))