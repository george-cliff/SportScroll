# SportScroll

A configurable PDF that generates yesterday's results, today's events, and upcoming events using multiple APIs

## Table of Contents

- [SportScroll](#sportscroll)
  - [Table of Contents](#table-of-contents)
  - [Background](#background)
  - [Install](#install)
  - [Project Structure](#project-structure)
  - [Configuration](#configuration)
  - [Usage](#usage)
  - [Examples](#examples)
  - [Roadmap](#roadmap)
  - [Dev Log](#dev-log)
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

```text
sportscroll/
├── main.py              # entry point
├── config.yaml          # user configuration
├── requirements.txt
├── assets/
│   ├── example_output.png
│   └── example_output.pdf
└── sportscroll/
    ├── api.py           # TheSportsDB API client
    ├── cache.py         # cache read/write/validation
    ├── config.py        # config loader
    ├── data.py          # data fetching and orchestration
    └── pdf.py           # HTML generation and PDF rendering
```

## Configuration

All configuration is in `config.yaml` in the project root.

| Key | Description | Default |
| ----- | ------------- | --------- |
| `timezone` | Your local timezone (tz database format e.g. `Europe/London`) | `Europe/London` |
| `tv_region` | Country name for TV channel lookup | `United Kingdom` |
| `cache_ttl_mins` | How long cached data is considered fresh (in minutes) | `60` |
| `premium` | Set to `true` if you have a TheSportsDB premium key | `false` |
| `key` | Your TheSportsDB API key — `123` is the public free key | `123` |
| `tv_lookup` | Enable TV channel lookup (currently does not work) | `false` |

To enable or disable a sport, set `enabled: true` or `enabled: false` under the relevant league in the `sports` section.

## Usage

1. edit `config.yaml` to your preferences and timezone
2. run `python -m sportscroll`
3. check `output/` for your *SportScroll PDF*

## Examples

![example-output](assets/example_output.png)

## Roadmap

### Code improvements

- Untangle the spaghetti
- Small code review fixes
- Fix issues with pipeline when date given is not `date.today`

### Features

- Multi-sport support with sport specific layouts
- Use offical sports/teams codes (e.g. <https://liaison.reuters.com/tools/sports-team-codes> and <https://en.wikipedia.org/wiki/Template:F1stat>)
- Wire TV channel lookup into the PDF output
- Improve PDF formatting and visual polish
- Add cache cleanup so old `.json` files don't accumulate in `.cache/`
- Favourite teams config and PDF highlighting
- Venue name and country flag per event, possibly weather
- Sport-specific layouts for feature days (Championship standings after an f1 Weekend)
- Logging
- CLI menu for configuration without editing `config.yaml`
- Cron job support with auto-print each morning

## Dev Log

I've been keeping daily notes in [Dev Log](DEVLOG.md) this helps myself and others understand the design ideas, my thought proccess, and where I am currently at within the project. If you have the time and want to, feel free to give it a read!

## Contributing

This is a personal learning project. However, feedback and bug reports are welcome and encouraged.

## License

MIT License © George Cliff

## Credits / Acknowledgements

- [TheSportsDB](https://www.thesportsdb.com/) - a big thank you to them for the sports data API that inspired this whole project
- [football-data.org](https://www.football-data.org/) - for the footbal API.
