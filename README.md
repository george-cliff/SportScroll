# SportScroll

A configurable PDF that generates yesterday's results, today's events, and upcoming events using "TheSportsDB" api

## Table of Contents

- [Background](#background)
- [Install](#install)
- [Project Structure](#project-structure)
- [Configuration](#configuration)
- [Usage](#usage)
- [Examples](#examples)
- [Roadmap](#roadmap)
- [Contributing](#contributing)
- [License](#license)
- [Credits / Acknowledgements](#credits--acknowledgements)


## Background

I started this project as a way to aggregate multiple different sports, leagues, and tournaments into one easy to digest PDF, and move away from my phone.

Each morning I found myself reaching for my phone and scrolling through multiple different apps and websites to get sports results. With less popular sports it can be hard to find useful information, and events could easily be missed. The aim of this project is to produce one single document (printed or on screen) that contains all the information for the sports and leagues you follow, without scrolling on your phone.

## Install

1. Clone the Repo
2. Install Python (3.14.3)
3. Install WeasyPrint system dependencies -- [see installation guide](https://doc.courtbouillon.org/weasyprint/stable/first_steps.html)
4. `pip install -r requirements.txt`

## Project Structure

```
sportscroll/
├── main.py              — entry point
├── config.yaml          — user configuration
├── requirements.txt
├── assets/
│   ├── example_output.png
│   └── example_output.pdf
└── src/
    ├── api.py           — TheSportsDB API client
    ├── cache.py         — cache read/write/validation
    ├── config.py        — config loader
    ├── data.py          — data fetching and orchestration
    └── pdf.py           — HTML generation and PDF rendering
```

## Configuration

All configuration is in `config.yaml` in the project root.

| Key | Description | Default |
|-----|-------------|---------|
| `timezone` | Your local timezone (tz database format e.g. `Europe/London`) | `Europe/London` |
| `tv_region` | Country name for TV channel lookup | `United Kingdom` |
| `cache_ttl_mins` | How long cached data is considered fresh (in minutes) | `60` |
| `premium` | Set to `true` if you have a TheSportsDB premium key | `false` |
| `key` | Your TheSportsDB API key — `123` is the public free key | `123` |
| `tv_lookup` | Enable TV channel lookup | `false` |

To enable or disable a sport, set `enabled: true` or `enabled: false` under the relevant league in the `sports` section.

## Usage

1. edit `config.yaml` to your preferences and timezone
2. run `main.py`

## Examples

![example-output](assets/example_output.png)


## Roadmap

**Code improvements**

- untangle the spaghetti
- Small code review fixes — unused imports, PEP 8 nits, missing docstring periods
- Refactor HTML generation in `pdf.py` — extract sport-specific renderers so adding a new sport only requires a new function

**Features**

- Multi-sport support — the data layer already groups by category, just needs sport-specific renderers
- Wire TV channel lookup into the PDF output
- Improve PDF formatting and visual polish
- Add cache cleanup so old `.json` files don't accumulate in `.cache/`
- Favourite teams config and PDF highlighting
- Venue name and country flag per event, possibly weather
- Sport-specific layouts (league tables, championship standings)
- Logging
- CLI menu for configuration without editing `config.yaml`
- Cron job support with auto-print each morning


## Contributing

This is a personal learning project. However, feedback and bug reports are welcome and encouraged.


## License

MIT License © George Cliff

## Credits / Acknowledgements

- [TheSportsDB](https://www.thesportsdb.com/) — a big thank you to them for the sports data API that makes this whole project possible
