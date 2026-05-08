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
from src.config import get_timezone, get_league_abbrs

MAX_UPCOMING = 10
OUTPUT_DIR = Path("output")
UTC_TIMESTAMP_FORMAT = "%Y-%m-%dT%H:%M:%S"
TIME_FORMAT = "%H:%M"
CSS = """
<style>
body { text-align: center; }
.team-badge {width: 25px; height: 25px;}
.event-info {font-size: 0.8em; color: grey; margin-top: -16px; }
.event-info-upc {font-size: 0.8em; color: grey; margin-top: -16px; }
.upcoming-table { border-collapse: collapse; width: 90%;}
.upcoming-table td { border: 4px solid #ccc; padding: 0px 0px; vertical-align: top; font-size: 0.85em; }
</style>
"""


def _format_event_time(event):
    """Converts an event's UTC timestamp to a HH:MM string in the local timezone."""
    return datetime.strptime(event["strTimestamp"], UTC_TIMESTAMP_FORMAT).replace(tzinfo=timezone.utc).astimezone(get_timezone()).strftime(TIME_FORMAT)


def _render_generic(start_time, event, abbr=None):
    """Returns a fallback HTML string containing the event name and time underneath."""
    if abbr:
        generic_event = f"<p> {abbr}. "
    else:
        generic_event = f"<p>"
    generic_event += f"{event['strEvent']}</p>"
    generic_event += f"<p class='event-info'> {start_time}</p>"
    return generic_event
    


def _render_football_result(start_time, event):
    """Returns an HTML string for a football result with team badges and score."""
    football_result = f"<p>{event['strHomeTeam']} <img src='{event['strHomeTeamBadge']}' class='team-badge'> {event['intHomeScore']} - {event['intAwayScore']} <img src='{event['strAwayTeamBadge']}' class='team-badge'> {event['strAwayTeam']} </p>"
    return football_result


RESULT_RENDERERS = {
    "Football": _render_football_result,
    "Formula 1": _render_generic
}


def _render_football_fixture(start_time, event):
    """Returns an HTML string for a football fixture with team badges and time."""
    football_fixture = f"<p>{event['strHomeTeam']} <img src='{event['strHomeTeamBadge']}' class='team-badge'> Vs. <img src='{event['strAwayTeamBadge']}' class='team-badge'> {event['strAwayTeam']} </p>"
    football_fixture += f"<p class='event-info'> {start_time}</p>"
    return football_fixture


SCHEDULED_RENDERERS = {
    "Football": _render_football_fixture,
    "Formula 1": _render_generic
}


def _render_football_upcoming(start_time, event, abbr=None):
    """Returns an HTML string for a football fixture with league abbreviation, team abbreviations, date and time."""
    football_upcoming = (f"<p>{abbr}. {event['strHomeTeam'][:3]} vs {event['strAwayTeam'][:3]}</p>")
    football_upcoming += (f"<p class='event-info-upc'>{event['dateEvent']} @ {start_time}</p>")
    return football_upcoming


UPCOMING_RENDERERS = {
    "Football": _render_football_upcoming,
    "Formula 1": _render_generic
}


def _render_upcoming_cells(data):
    """Builds an HTML table of the next upcoming events across all sports.

    Args:
        data: A dict with keys 'yesterday', 'today', and 'upcoming',
            as returned by get_pdf_data().

    Returns:
        An HTML string containing a table of up to MAX_UPCOMING events,
        sorted by start time, or a fallback '<p>No events</p>' string.
    """
    upcoming_events = []
    for _, day_data in data["upcoming"].items():
        for category, leagues in day_data.items():
            for league_name, events in leagues.items():
                for event in events:
                    upcoming_events.append((category, league_name, event))
    upcoming_events = sorted(upcoming_events, key=lambda item: item[2]["strTimestamp"])[:MAX_UPCOMING]
    if not upcoming_events:
        return "<p>No events</p>"
    cells = []
    abbrs_dict = get_league_abbrs()
    for category, league_name, event in upcoming_events:
        abbr = abbrs_dict.get(league_name)
        if abbr is None:
            continue
        start_time = _format_event_time(event)
        cells.append(UPCOMING_RENDERERS.get(category, _render_generic)(start_time, event, abbr=abbr))
    if not cells:
        return "<p>No events</p>"
    rows = ""
    for i in range(0, len(cells), 5):
        pair = cells[i:i+5]
        rows += "<tr>" + "".join(f"<td>{cell}</td>" for cell in pair) + "</tr>"
    return f"<table class='upcoming-table' align='center'>{rows}</table>"
    
def _render_section(heading, renderer, section_data):
    """Renders a titled section of events using a sport-specific renderer dict.

    Args:
        heading: Section heading (e.g. "Yesterday's Results").
        renderer: Dict of {category: render_function} — falls back to _render_generic.
        section_data: Dict of {category: {league: [events]}} for one day.

    Returns:
        An HTML string for the full section.
    """
    section_html = [f"<h2>{heading}</h2>"]
    for category, leagues in section_data.items():
        if leagues:
            section_html.append(f"<h3>{category}</h3>")
        for league_name, events in leagues.items():
            section_html.append(f"<h4>{league_name}</h4>")
            for event in events:
                start_time = _format_event_time(event)
                section_html.append(renderer.get(category, _render_generic)(start_time, event))
    return "".join(section_html)


def generate_html(data):
    """Generates an HTML string from the structured event data dict.

    Args:
        data: A dict with keys 'yesterday', 'today', and 'upcoming',
            as returned by get_pdf_data().

    Returns:
        A complete HTML string ready for rendering.
    """
    date_now = datetime.now(get_timezone())
    display_date = f"{date_now:%a} {date_now.day} {date_now:%b %Y}"

    html = f"<html><head>{CSS}</head><body>"
    html += f"<h1>The Sport Scroll - {display_date}</h1>"
    html += _render_section("Yesterday's Results", RESULT_RENDERERS, data["yesterday"])
    html += _render_section("Today's Sports", SCHEDULED_RENDERERS, data["today"])
    html += "<h2>Upcoming Events</h2>"
    html += _render_upcoming_cells(data)
    html += "</body></html>"
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
    HTML(string=html).write_pdf(pdf_file, presentational_hints=True)