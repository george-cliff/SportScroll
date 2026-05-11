"""API Caller for SportScroll.

Fetches match data from football-data.org.
"""

# Standard library Imports
import json
import logging

# Related third party imports
import requests

# Local application/library specific imports
from sportscroll.config import get_football_data_key

logger = logging.getLogger(__name__)

REQUEST_TIMEOUT = 10
BASE_URL = "https://api.football-data.org/v4"

STATUS_MESSAGES = {
    400: "Bad request - check competition code and date range",
    403: "Access denied - resource may require a paid subscription",
    404: "Competition not found - check the competition code in config.yaml",
    429: "Rate limit exceeded - too many requests",
}


def get_football_matches(comp_code, date_from, date_to):
    """Fetches all matches for a competition within a date range.

    Args:
        comp_code: The football-data.org competition code (e.g. 'PL').
        date_from: A date object for the start of the range.
        date_to: A date object for the end of the range.

    Returns:
        A list of match dicts, or an empty list if no matches were found.
    """
    api_key = get_football_data_key()
    if api_key is None:
        raise ValueError("FOOTBALL_DATA_API_KEY not set - check .env file")

    url = f"{BASE_URL}/competitions/{comp_code}/matches"
    headers = {"X-Auth-Token": api_key}
    params = {
        "dateFrom": date_from.strftime("%Y-%m-%d"),
        "dateTo": date_to.strftime("%Y-%m-%d"),
    }

    try:
        response = requests.get(
            url, headers=headers, params=params, timeout=REQUEST_TIMEOUT
        )
    except requests.exceptions.RequestException:
        logger.exception(f"Network error fetching - fetching failed for{comp_code}")
        raise

    if not response.ok:
        try:
            api_message = response.json().get("error", "no details provided")
        except json.JSONDecodeError:
            api_message = "no details provided"
        msg = STATUS_MESSAGES.get(
            response.status_code, f"Unexpected error - {response.status_code}"
        )
        logger.error(f"{comp_code} - {msg} - {api_message}")
        response.raise_for_status()

    try:
        matches = response.json().get("matches") or []
    except json.JSONDecodeError:
        logger.exception(f"Invalid JSON response - invalid for {comp_code}")
        raise

    logger.debug(f"{comp_code} - {len(matches)} matches fetched successfully")
    return matches
