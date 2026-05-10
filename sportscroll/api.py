"""API Caller for SportScroll.

Fetches match data from football-data.org.
"""

# Standard library Imports

# Related third party imports
import requests

# Local application/library specific imports
from sportscroll.config import get_football_data_key

REQUEST_TIMEOUT = 10
FOOTBALL_DATA_BASE_URL = "https://api.football-data.org/v4"


def get_football_matches(comp_code, date_from, date_to):
    """Fetches all matches for a competition within a date range.

    Args:
        comp_code: The football-data.org competition code (e.g. 'PL').
        date_from: A date object for the start of the range.
        date_to: A date object for the end of the range.

    Returns:
        A list of match dicts, or an empty list if no matches were found.
    """
    url = f"{FOOTBALL_DATA_BASE_URL}/competitions/{comp_code}/matches"
    headers = {"X-Auth-Token": get_football_data_key()}
    params = {
        "dateFrom": date_from.strftime("%Y-%m-%d"),
        "dateTo": date_to.strftime("%Y-%m-%d")
    }
    response = requests.get(url, headers=headers, params=params, timeout=REQUEST_TIMEOUT)
    return response.json().get("matches") or []
