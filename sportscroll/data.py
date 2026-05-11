"""Data layer for SportScroll.

Fetches, caches, and slices event data into the structure consumed by the PDF renderer.
"""

# Standard library Imports
import logging
from datetime import datetime, timedelta

# Related third party imports

# Local application/library specific imports
from sportscroll.footballl_data_api import get_football_matches
from sportscroll.cache import cache_valid, load_cache, save_cache
from sportscroll.config import get_timezone, load_config

logger = logging.getLogger(__name__)

LOOKBACK_DAYS = 1
LOOKAHEAD_DAYS = 5
DATE_FORMAT = "%Y-%m-%d"


def _get_events(date_from, date_to):
    """Fetches all events across all enabled leagues for a date range and adds local time to each of the events.

    Args:
        date_from: A datetime object for the start of the date range.
        date_to: A datetime object for the end of the date range.

    Returns:
        A dict keyed by ISO date string, each value being a dict of categories and leagues.
    """
    raw_events = {}
    # walk through each league to send as a request to the API, due to API returning one competition per request
    for category, leagues in load_config()["sports"].items():
        logger.info(f"Processing {category} - starting loop")
        for comp_code, league in leagues.items():
            if not league["enabled"]:
                logger.debug(f"{league['name']} disabled - skipping")
                continue

            logger.info(
                f"{league['name']} enabled - fetching from {date_from.strftime(DATE_FORMAT)} to {date_to.strftime(DATE_FORMAT)}"
            )
            matches = get_football_matches(comp_code, date_from, date_to)
            # Go through each match received by the request, adds local time to the data, and adds each match to its date's list
            logger.info(f"{league['name']} - {len(matches)} matches found")
            for match in matches:
                utc_dt = datetime.fromisoformat(match["utcDate"].replace("Z", "+00:00"))
                local_dt = utc_dt.astimezone(get_timezone())
                date_str = local_dt.strftime(DATE_FORMAT)
                match["localTime"] = local_dt.isoformat()
                if date_str not in raw_events:
                    raw_events[date_str] = {}
                if category not in raw_events[date_str]:
                    raw_events[date_str][category] = {}
                if league["name"] not in raw_events[date_str][category]:
                    raw_events[date_str][category][league["name"]] = []
                raw_events[date_str][category][league["name"]].append(match)
                logger.debug(f"{league['name']} - match added on {date_str}")
    return raw_events


def get_latest_data(target_date):
    """Returns a full window of event data, using the cache if valid.

    Args:
        target_date: A datetime object for the fetch window.

    Returns:
        A dict keyed by ISO date string, each value being a dict of categories and leagues.
    """

    # check cache for data and return early if cache is valid
    date_from = target_date - timedelta(days=LOOKBACK_DAYS)
    date_to = target_date + timedelta(days=LOOKAHEAD_DAYS)
    valid = cache_valid(date_from=date_from, date_to=date_to)
    if valid:
        raw_events = load_cache()
        if raw_events is not None:
            return raw_events
        logger.warning("Cache validated but load failed - fetching fresh data")
    # set up the raw_events dict and prefill with dates
    raw_events = {}
    for i in range(LOOKBACK_DAYS + LOOKAHEAD_DAYS + 1):
        date_str = (date_from + timedelta(days=i)).strftime(DATE_FORMAT)
        raw_events[date_str] = {}

    # gather fresh data and save it to the cache
    logger.info("Fetching fresh data")
    raw_events.update(_get_events(date_from, date_to))
    save_cache(raw_events)
    return raw_events


def get_pdf_data(target_date):
    """Returns event data sliced into yesterday, today, and upcoming sections.

    Args:
        target_date: A datetime object for the date the scroll is being generated for.

    Returns:
        A dict with keys 'yesterday', 'today', and 'upcoming', ready for the PDF renderer.
    """

    # Gather the latest for given date
    latest_data = get_latest_data(target_date)

    # Slice the date window into named sections ready for the renderer
    yesterday_data = latest_data[
        (target_date - timedelta(days=LOOKBACK_DAYS)).strftime(DATE_FORMAT)
    ]
    logger.debug("Sliced data for yesterday")
    today_data = latest_data[target_date.strftime(DATE_FORMAT)]
    logger.debug("Sliced data for today")
    upcoming_data = {}
    for i in range(1, LOOKAHEAD_DAYS + 1):
        upcoming_date = target_date + timedelta(days=i)
        upcoming_data[upcoming_date.strftime(DATE_FORMAT)] = latest_data[
            upcoming_date.strftime(DATE_FORMAT)
        ]
    logger.debug("Sliced data for upcoming")

    # Build and return the pdf_data dict ready for rendering
    pdf_data = {
        "yesterday": yesterday_data,
        "today": today_data,
        "upcoming": upcoming_data,
    }
    logger.info("PDF data ready for rendering")
    return pdf_data


if __name__ == "__main__":
    import json

    raw_events = get_latest_data(datetime.now(get_timezone()))
    with open("test_output.json", "w") as f:
        json.dump(raw_events, f, indent=2)
