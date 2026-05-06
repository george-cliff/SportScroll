# Standard library Imports
from datetime import datetime, timedelta, timezone
from zoneinfo import ZoneInfo
from pathlib import Path
import json

# Related third party imports
from weasyprint import HTML

# Local application/library specific imports
from src.config import load_config
from src.data import get_pdf_data

config = load_config()
tz = ZoneInfo(config["timezone"])

def generate_html(data):
    """takes in the data dict, returns an HTML string"""
    # TITLE
    html = '<html><body style="text-align:center;">'
    display_date = datetime.now(tz).strftime("%a, %-d %b %Y")
    html += f"<h1>The Sport Scroll - {display_date}</h1>"

    # Yesterdays Results
    html += "<h2>Yesterdays Results</h2>"
    for category, leagues in data["yesterday"].items():
        if leagues:
            html += f"<h2>{category}</h2>"
        for league_name, events in leagues.items():
            html += f"<h3>{league_name}</h3>"
            for event in events:
                html += f'<p>{event["strHomeTeam"]} <img src="{event["strHomeTeamBadge"]}" style="width:30px; height:30px;"> {event["intHomeScore"]} - {event["intAwayScore"]} <img src="{event["strAwayTeamBadge"]}" style="width:30px; height:30px;"> {event["strAwayTeam"]} </p>'

    # Todays Sports
    html += "<h2>Todays Sports</h2>"
    for category, leagues in data["today"].items():
        if leagues:
            html += f"<h2>{category}</h2>"
        for league_name, events in leagues.items():
            html += f"<h3>{league_name}</h3>"
            for event in events:
                start_time = datetime.strptime(event["strTimestamp"], "%Y-%m-%dT%H:%M:%S").replace(tzinfo=timezone.utc).astimezone(tz).strftime("%H:%M")
                html += f'<p>{event["strHomeTeam"]} <img src="{event["strHomeTeamBadge"]}" style="width:30px; height:30px;"> Vs. <img src="{event["strAwayTeamBadge"]}" style="width:30px; height:30px;"> {event["strAwayTeam"]} </p>'
                html += f'<p style="font-size:0.8em; color:grey; margin-top:-10px;">{start_time}</p>'

    # Upcoming Events
    html += "<h2>Upcoming Events</h2>"
    for upcoming_date, day_data in data["upcoming"].items():
        html += f"<h3>{upcoming_date}</h3>"
        upcoming_events = []
        for category, leagues in day_data.items():
            for league_name, events in leagues.items():
                for event in events:
                    upcoming_events.append(event)
        upcoming_events = sorted(upcoming_events, key=lambda e: e["strTimestamp"])[:10]
        if not upcoming_events:
            html += "<p>No events</p>"
        else:
            for event in upcoming_events:
                start_time = datetime.strptime(event["strTimestamp"], "%Y-%m-%dT%H:%M:%S").replace(tzinfo=timezone.utc).astimezone(tz).strftime("%H:%M")
                html += f'<p>{event["strHomeTeam"]} Vs. {event["strAwayTeam"]}</p>'
                html += f'<p style="font-size:0.8em; color:grey; margin-top:-10px;">{start_time}</p>'


    
    html += '</body></html>'
    return html

def generate_pdf():
    """renders HTML into a PDF in the folder output/"""
    datestamp = datetime.now(tz).strftime("%Y-%m-%d")
    Path("output").mkdir(exist_ok=True)
    pdf_file = "output/SportScroll_" + datestamp + ".pdf"
    pdf_data = get_pdf_data()
    html = generate_html(data=pdf_data)
    HTML(string=html).write_pdf(pdf_file)


if __name__ == "__main__":
    generate_pdf()