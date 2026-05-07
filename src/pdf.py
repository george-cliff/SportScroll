"""PDF renderer for SportScroll.

Generates a dated HTML string from event data and renders it to a PDF
file in the output/ directory via WeasyPrint.
"""

# Standard library Imports
from datetime import datetime, timezone
from pathlib import Path

# Related third party imports
from weasyprint import HTML

# Local application/library specific imports
from src.config import get_timezone

MAX_UPCOMING = 10
OUTPUT_DIR = Path("output")
UTC_TIMESTAMP_FORMAT = "%Y-%m-%dT%H:%M:%S"
TIME_FORMAT = "%H:%M"

def generate_html(data):
    """Generates an HTML string from the structured event data dict.

    Args:
        data: A dict with keys 'yesterday', 'today', and 'upcoming',
            as returned by get_pdf_data().

    Returns:
        A complete HTML string ready for rendering.
    """
    html = '<html><body style="text-align:center;">'
    date_now = datetime.now(get_timezone())
    display_date = f"{date_now:%a} {date_now.day} {date_now:%b %Y}"
    html += f"<h1>The Sport Scroll - {display_date}</h1>"

    html += "<h2>Yesterday's Results</h2>"
    for category, leagues in data["yesterday"].items():
        if leagues:
            html += f"<h3>{category}</h3>"
        for league_name, events in leagues.items():
            html += f"<h4>{league_name}</h4>"
            for event in events:
                html += f'<p>{event["strHomeTeam"]} <img src="{event["strHomeTeamBadge"]}" style="width:30px; height:30px;"> {event["intHomeScore"]} - {event["intAwayScore"]} <img src="{event["strAwayTeamBadge"]}" style="width:30px; height:30px;"> {event["strAwayTeam"]} </p>'

    html += "<h2>Today's Sports</h2>"
    for category, leagues in data["today"].items():
        if leagues:
            html += f"<h3>{category}</h3>"
        for league_name, events in leagues.items():
            html += f"<h4>{league_name}</h4>"
            for event in events:
                start_time = datetime.strptime(event["strTimestamp"], UTC_TIMESTAMP_FORMAT).replace(tzinfo=timezone.utc).astimezone(get_timezone()).strftime(TIME_FORMAT)
                html += f'<p>{event["strHomeTeam"]} <img src="{event["strHomeTeamBadge"]}" style="width:30px; height:30px;"> Vs. <img src="{event["strAwayTeamBadge"]}" style="width:30px; height:30px;"> {event["strAwayTeam"]} </p>'
                html += f'<p style="font-size:0.8em; color:grey; margin-top:-10px;">{start_time}</p>'

    html += "<h2>Upcoming Events</h2>"
    upcoming_events = []
    for _, day_data in data["upcoming"].items():
        for category, leagues in day_data.items():
            for league_name, events in leagues.items():
                for event in events:
                    upcoming_events.append(event)
    upcoming_events = sorted(upcoming_events, key=lambda e: e["strTimestamp"])[:MAX_UPCOMING]
    if not upcoming_events:
        html += "<p>No events</p>"
    else:
        for event in upcoming_events:
            start_time = datetime.strptime(event["strTimestamp"], UTC_TIMESTAMP_FORMAT).replace(tzinfo=timezone.utc).astimezone(get_timezone()).strftime(TIME_FORMAT)
            html += f'<p>{event["strHomeTeam"]} Vs. {event["strAwayTeam"]}</p>'
            html += f'<p style="font-size:0.8em; color:grey; margin-top:-10px;">{event["dateEvent"]} @ {start_time}</p>'

    html += '</body></html>'
    return html


def generate_pdf(pdf_data):
    """Renders the event data to a dated PDF file in output/.

    Args:
        pdf_data: A dict with keys 'yesterday', 'today', and 'upcoming',
            as returned by get_pdf_data().
    """
    datestamp = datetime.now(get_timezone()).strftime("%Y-%m-%d")
    OUTPUT_DIR.mkdir(exist_ok=True)
    pdf_file = OUTPUT_DIR / f"SportScroll_{datestamp}.pdf"
    html = generate_html(data=pdf_data)
    HTML(string=html).write_pdf(pdf_file)