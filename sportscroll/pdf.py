"""PDF renderer for SportScroll.

Generates a dated HTML string from event data and renders it to a PDF
file in the output/ directory via WeasyPrint.
"""

# Standard library Imports
from datetime import datetime
from pathlib import Path

# Related third party imports
from weasyprint import HTML

# Local application/library specific imports
from sportscroll.config import get_league_abbrs

MAX_UPCOMING = 10
OUTPUT_DIR = Path("output")
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
    """Returns the local time as a HH:MM string."""
    return datetime.fromisoformat(event["localTime"]).strftime(TIME_FORMAT)


def _render_generic(start_time, event, abbr=None):
    """Returns a minimal fallback HTML string when no sport-specific renderer is available."""
    label = abbr if abbr else "Event"
    return f"<p>{label}</p><p class='event-info'>{start_time}</p>"


def _render_football_result(start_time, event):
    """Returns an HTML string for a football result with team badges and score."""
    football_result = f"<p>{event['homeTeam']['shortName']} <img src='{event['homeTeam']['crest']}' class='team-badge'> {event['score']['fullTime']['home']} - {event['score']['fullTime']['away']} <img src='{event['awayTeam']['crest']}' class='team-badge'> {event['awayTeam']['shortName']} </p>"
    return football_result


RESULT_RENDERERS = {
    "Football": _render_football_result,
    "Formula 1": _render_generic
}


def _render_football_fixture(start_time, event):
    """Returns an HTML string for a football fixture with team badges and time."""
    football_fixture = f"<p>{event['homeTeam']['shortName']} <img src='{event['homeTeam']['crest']}' class='team-badge'> Vs. <img src='{event['awayTeam']['crest']}' class='team-badge'> {event['awayTeam']['shortName']} </p>"
    football_fixture += f"<p class='event-info'> {start_time}</p>"
    return football_fixture


SCHEDULED_RENDERERS = {
    "Football": _render_football_fixture,
    "Formula 1": _render_generic
}


def _render_football_upcoming(start_time, event, abbr=None):
    """Returns an HTML string for a football fixture with league abbreviation, team abbreviations, date and time."""
    if abbr:
        football_upcoming = f"<p> {abbr}. "
    else:
        football_upcoming = f"<p>"
    football_upcoming += (f"{event['homeTeam']['tla']} vs {event['awayTeam']['tla']}</p>")
    football_upcoming += (f"<p class='event-info-upc'>{event['localTime'][:10]} @ {start_time}</p>")
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
    # Collect all events from the upcoming window, and sort them by time, capped by MAX_UPCOMING
    upcoming_events = []
    for _, day_data in data["upcoming"].items():
        for category, leagues in day_data.items():
            for league_name, events in leagues.items():
                for event in events:
                    upcoming_events.append((category, league_name, event))
    upcoming_events = sorted(upcoming_events, key=lambda item: item[2]["localTime"])[:MAX_UPCOMING]
    if not upcoming_events:
        return "<p>No events</p>"
    
    # Render each event into a HTML cell
    cells = []
    abbrs_dict = get_league_abbrs()
    for category, league_name, event in upcoming_events:
        abbr = abbrs_dict.get(league_name)
        start_time = _format_event_time(event)
        cells.append(UPCOMING_RENDERERS.get(category, _render_generic)(start_time, event, abbr=abbr))
    if not cells:
        return "<p>No events</p>"

    # Build Table Rows
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


def generate_html(data, target_date):
    """Generates an HTML string from the structured event data dict.

    Args:
        data: A dict with keys 'yesterday', 'today', and 'upcoming', as returned by get_pdf_data().
        target_date: A datetime object for the date the scroll is being generated for.

    Returns:
        A complete HTML string ready for rendering.
    """
    display_date = f"{target_date:%a} {target_date.day} {target_date:%b %Y}"

    html = f"<html><head>{CSS}</head><body>"
    html += f"<h1>The Sport Scroll - {display_date}</h1>"
    html += _render_section("Yesterday's Results", RESULT_RENDERERS, data["yesterday"])
    html += _render_section("Today's Sports", SCHEDULED_RENDERERS, data["today"])
    html += "<h2>Upcoming Events</h2>"
    html += _render_upcoming_cells(data)
    html += "</body></html>"
    return html


def generate_pdf(pdf_data, target_date):
    """Renders the event data to a dated PDF file in output/.

    Args:
        pdf_data: A dict with keys 'yesterday', 'today', and 'upcoming',
            as returned by get_pdf_data().
        target_date: A datetime object for the date the scroll is being generated for.
    """
    datestamp = target_date.strftime("%Y-%m-%d")
    OUTPUT_DIR.mkdir(exist_ok=True)
    pdf_file = OUTPUT_DIR / f"SportScroll_{datestamp}.pdf"
    html = generate_html(data=pdf_data, target_date=target_date)
    HTML(string=html).write_pdf(pdf_file, presentational_hints=True)
