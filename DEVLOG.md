# Dev Log

## Table of Contents

- [Dev Log](#dev-log)
  - [Table of Contents](#table-of-contents)
  - [Day 1 - 2026-05-04](#day-1---2026-05-04)
  - [Day 2 - 2026-05-05](#day-2---2026-05-05)
  - [Day 3 - 2026-05-06](#day-3---2026-05-06)
  - [Day 4 - 2026-05-07](#day-4---2026-05-07)
  - [Day 5 - 2026-05-08](#day-5---2026-05-08)
  - [Bonus Day - 2026-05-09](#bonus-day---2026-05-09)
  - [Day 6 - 2026-05-10](#day-6---2026-05-10)

## Day 1 - 2026-05-04

### Scope - Day 1

- Get the config loading.
- Printing football matches for the day into CLI.

### Design - Overall Project Plans

- I want to create a PDF that prints each morning which contains all the info for sports i watch, even the *nicher* ones as i often end up missing field hockey games, or WEC races as Im not even aware they're on and/or i dont know what tv channel there on.
- I want to learn cleaner coding practices using this project, stuff like docstrings, src folders etc, and want to keep version control as a top priority, ive used github in the past but never really properly.
- Im keeping it interesting by utilising new skills like PDF rendering, ive never done it before, or tried to communicate with other network devices like printers, so should be some good learning there.
- `TheSportsDB` seems to be an **amazing** aggregator for sport information and looks like a **fantastic** API for this project.
- all other apis seem to be sport specific e.g. `OpenF1`, which is also a fantastic resource but might be too cluttered for what basic information I need.

### Achieved - Day 1

- [x] `config.py` loads correctly using `config.yaml`.
- [x] `api.py` fetches event information from `TheSportsDB` using the league id.
- [x] `main.py` loops through enabled sports (currently just football leagues), grouped with category (football), prints yesterday's results and today's fixtures to the CLI.
- [x] `get_tv()` created, where it filters channels based on your given region.

### Issues - Day 1

- TV Channel data doesn't seem to be completed when pulled from `lookuptv.php` could be free tier limitations, need investigation.
- `channels` variable will crash if `tv_lookup` is false, needs a default value.

### Day 2 Ideas

- Clean up test code.
- Test `get_tv()` against a live upcoming fixture to confirm if channel data improves for future events.
- Fix `channels` default value bug in `todays_events()`.
- Start working on `pdf.py` render the working CLI output as a PDF.

## Day 2 - 2026-05-05

### Scope - Day 2

- Determine best PDF libraries to use.
  - Get basic PDF printout - `WeasyPrint` seems like a good option for starting out, `Jinja2` seems a bit more involved.
- Ignoring channels for now, it seems to be limited.
- Set up GitHub for this project.
  - ***Should*** be at the MVP by the end of today.
    - A configurable PDF that lists: yesterday's results, today's upcoming events in detail, and a smaller section for future events that week.
  - Flesh out the README so it has the information needed.
  - Set up `.gitignore`, LICENSE, etc.

### Design - What I want from the PDF

- Title at the top.
- Yesterday's results filtered by sports category (e.g. football scores all together, motorsports results all together).
- Each event will have `strLeagueBadge` followed by the result/fixture, with the names of the teams and `strHomeTeamBadge` on the left and `strAwayTeamBadge` on the right.
- Today's fixtures with the teams and the time (based on my timezone).
- Very basic 3 day forecast.

### Achieved - Day 2

- [x] `data.py` created to streamline the fetching and have all data focused functions in one file.
- [x] `cache.py` created, ive ***never*** used caching before but feel this is important when working with APIs as to not overload them the functions in there should help with reducing unnecessary api calls.
- [x] created `get_latest_data()` to get `data.py` to utilise `cache.py` and added cache TTL (Time To Live) to `config.yaml` to ease testing so i can reduce it to fetch new data quicker, unsure if its going to be kept in the final version yet.
- [x] streamlined separate day functions into one so rather than yesterdays results and todays events being separate functions, its now a single function with a date argument.

### Issues - Day 2

- `get_events()` currently only fetches for one date, need to set up loops
- still no PDF renderer

### Day 3 Ideas

- Fetch yesterday + today in one run, merge into single cache file
- Build `pdf.py`, render cached data to PDF
- Commit to GitHub once PDF produces output as MVP achieved.

## Day 3 - 2026-05-06

### Scope - Day 3

- Extend `get_latest_data()` to fetch the full date range in one run
- Build `pdf.py`, render cached data to a PDF

### Design - The github day

- today I want to get this uploaded to github and start using proper version control, as the MVP should be achieved
- I realise this is likely later than it should be and in best practice I should have been using version control from day one. I was *too* focused on feeling this project had to achieve its MVP beforehand that it meant it was delayed.
- in future even if the project is not fully doing everything my goals included as long as the code is in a functional state **I should initialise git and start using it**.
- I also decided to go with tz database for timezones, as somewhere like the UK uses daylight savings and I didn't want to have to mainly change this each time the timezone changed. in the future it might be useful to communicate somehow with the computer to get the timezone from the PC directly rather than users having to add their timezone manually, although this could also be a privacy concern (toggable option?) set Timezone to auto or something if you want to opt-in

### Achieved - Day 3

- [x] improved `get_latest_data()` so it now fetches 5 days (yesterday through 3 days ahead) and merges into a single cache file
- [x] `get_pdf_data()` added to `data.py` I designed this function to slice through the 5-day blob into yesterday, today, and upcoming sections ready for the renderer, although my main concern now is my data is getting *too* nested, this is an Issue I will flag and once im settled into the flow, I will revisit it
- [x] created `pdf.py` in which `generate_html()` and `generate_pdf()` so i can now get the HTML to autowrite and generate it to a pdf in the folder `output/` - **MVP achieved!!!**
- [x] wired up `main.py` its very simple and just runs `generate_pdf()` and produces a dated PDF on each run, it currently overwrites existing PDFs, but I don't believe that to be an issue as this should be only run once a day, I likely want to make it so this is toggable in config as someone might want this to run on a server for multiple different people and produce multiple different PDFs each day, and set up some user profile stuff, but that's a long way down the line for now
- [x] PDF covers all three sections: **yesterday's results** (with scores), **today's fixtures** (with kick-off times in local timezone), and **upcoming events** (next 3 days, sorted by time, capped at 10 per day)

### Issues - Day 3

- six issues have been spotted, which I want to sort before adding any features, these were spotted by claude code when I used it for a code review, as this is a solo project I am using claude code as another pair of eyes for when im stuck or need a code review (the below issues are copied directly from claude).
  - **Heading hierarchy bug** — `<h2>` used for both section titles ("Yesterdays Results") and category names below them. Categories should be `<h3>`, league names `<h4>`.
  - **GNU-only date format** — `%-d` in `pdf.py` is Linux-only; crashes on macOS and Windows. Needs replacing before sharing.
  - **Module-level config loading** — all four modules (`api.py`, `cache.py`, `data.py`, `pdf.py`) run `config = load_config()` on import. Reads `config.yaml` four times per run; breaks imports in any context where `config.yaml` isn't in the working directory.
  - **Hidden data flow** — `generate_pdf()` calls `get_pdf_data()` internally, so the renderer secretly drives the data pipeline. Should take `data` as a parameter; `main.py` should wire them together.
  - **`if valid / if not valid` pattern** — `data.py` uses two separate `if` checks instead of `if/else`. Not a bug now, but fragile.
  - **Type mismatch in `__main__` block** — `data.py` line 63 passes `date.today()` to `get_latest_data()`, which calls `.date()` on it internally — `date` has no `.date()` method and would crash.

### Day 4 Ideas

- Fix the six issues above before adding any new features and see where the day takes me from there

## Day 4 - 2026-05-07

### Scope - Day 4

1. fix the Six Issues

### Design - Why Claude?

- I am currently Studying Computer Science at university, where we have learnt C and Java in our first year. I recreationally used Python and completed the CS50 Intro to Python Course before deciding to go to Uni as a Mature Student.
- Due to being a Solo Learner of Python and University on break for the Summer, I wanted a summer project to keep my skills fresh, learn new skills, and allow me to dive deeper and start making things that will benefit my life.
- Claude Code has allowed me to have someone act as a Senior Developer to me who will spot errors help guide me or prompt me in the right direction. I have given instructions to Claude to enable this and most importantly ***not*** write the code for me.
- Claude's Instructions are:
  - Default to pseudocode or prose when explaining how something should work. Walk me through logic, structure, and edge cases. I translate it into real code myself.
  - **Plans over implementations.** Numbered steps describing what each part *does*, not the syntax.
  - Real code only when I explicitly ask, "show me the code", "give me a working example". When I do ask, give complete code, no "// fill this in" gaps.
  - When I share my code for review, point at problems and ask leading questions. Don't rewrite it for me.
  - When I'm stuck on a bug, ask me what I expect the code to do before diagnosing. Often I'll spot it myself.
  - Always explain the *why*, not just the *what*.
  - **Don't write code I didn't ask for.**
- As someone who has Dyslexia and is currently on a diagnosis pathway for ADHD, I have found with the correct prompting Claude has allowed me to be a ***creative ideas machine*** and problem solver, whilst also keeping focused on the current task at hand.
- to aid this I added more instructions to Claude:
  - Within a task: if I start fixing something that isn't the current problem, call it out: "Is this the thing we're working on?"
  - Within a session: when a new idea pops up mid-task, capture it to a "Not Now" list, don't silently fold it in, don't lose it.
  - Within the project: if I propose adding something to scope mid-task, ask whether it belongs now or in a later version.
  - Also: push back if I'm polishing something that doesn't work end-to-end yet. **Ugly-but-working ships before optimization.**

### Achieved - Day 4

- [x] **All six Day 3 issues fixed**
- [x] `load_config()` and `get_timezone()` now use `@lru_cache` so they only need calling once
- [x] `get_latest_data()` given a `target_date=None` default
- [x] separated `generate_pdf` from `get_pdf_data` so now they are individually controlled through `main.py`
- [x] `cache.py` tidied, added constants and created helper function `_get_latest_cache_file()`
- [x] Magic numbers and hardcoded strings replaced with named constants across all modules, **this was big**
- [x] Date keys consistent throughout, all use `strftime(DATE_FORMAT)`
- [x] Assorted nits: apostrophes in PDF headings, import order, spacing, docstring fixes, `get_url()` tightened
- [x] Commenting and coding standards documented in `CODE_STYLE.md`.

### Issues - Day 4

- cosmetic issues, tidying up is needed
- Comments and docstrings inconsistent across all modules some functions are patchy
- `generate_html()` has two near-identical loop nests and repeated inline styles
- It is also not yet sport-aware so will only work for Football
- No `strTimestamp` guard in upcoming sort. `sorted()` on events with a `null` timestamp throws a `TypeError`
  - F1 events are especially likely to hit this due to them being manually added data from `TheSportDB`
- No HTTP error handling in `get_events_on_date()`. a 429 (rate limit) or 500 response will crash on `.json()` or silently return wrong data
- `__main__` block in `data.py` uses a naive datetime. `datetime(2026, 5, 3)` has no timezone. the rest of the codebase passes tz-aware objects from `get_timezone()` so behaviour will be inconsistent if the block is ever run

### Day 5 Ideas

- Tidy `pdf.py`
- Docstrings and comments pass I need to go through `api.py`, `cache.py`, `data.py`, `pdf.py`, `main.py` one by one
- Refactor `generate_html()`, look into CSS and make a `<style>` block, extract `_format_event_time()`, build `_render_section()` + sport-specific renderers (`_render_football_result`, `_render_football_fixture`, `_render_f1_result`, `_render_f1_event`, `_render_generic`)
- add a render mapping dict for easier adding of sports in the future
- HTTP error handling in `api.py`, add `response.raise_for_status()` to `get_events_on_date()` decide whether to retry on 429 or raise an error

## Day 5 - 2026-05-08

### Scope - Day 5

- Finish and tidy PDF rendering

### Design - What's with all the commits?

- Yesterday I committed nine different times, that's a lot for not a lot of changes
- I do this as I find it's really helpful for me as a closing ritual for a task, once a task is done it gets committed and now I can focus on the next task
- I find shorter, clear commits, easier to keep track of
- I don't know if this is bad practice but I find if a commit message is over 100 chars, it should've been two commits, I will likely look into good committing practices to rectify any mistakes I'm currently making.

### Achieved - Day 5

- [x] this was a ***surprisingly big day*** and the project has started shaping into something **I'm proud of**
- [x] `generate_html()` **fully refactored**
- [x] set up `CSS` constant
- [x] set up sport-aware mapping dicts (`RESULT_RENDERERS`, `SCHEDULED_RENDERERS`, `UPCOMING_RENDERERS`) wired up
- [x] League abbreviations added. `abbr` field added to all leagues in `config.yaml`. `get_league_abbrs()` added to `config.py`. Premier League corrected to `"English Premier League"` to match the API
- [x] `_render_section()` helper stopped the duplicate yesterday/today loop nests
- [x] added `_render_upcoming_cells()` which meant I could tighten the upcoming section
- [x] `_render_generic()` updated, accepts the new optional `abbr` from config
- [x] Upcoming table styled with borders, padding, and centered using `WeasyPrint` `presentational_hints=True` and `align="center"` attribute, before it was rendering left aligned and ***nothing*** I was doing seemed to fix it (shout out to this [github issue](https://github.com/Kozea/WeasyPrint/issues/527))
- [x] `src/` renamed to `sportscroll/`, suggested by claude as it's "the proper Python package layout"
- [x] `__main__.py` added so **now you can run `python -m sportscroll`**

### Issues - Day 5

- HTTP error handling in `api.py` missing. a 429 or 500 from `TheSportDB` will still crash or return bad data
- `get_tv()` empty response guard missing, will crash with `JSONDecodeError` if API returns empty body
- `__main__` block in `data.py` uses a hardcoded date
- `TheSportsDB` data inconsistency. data quality is unreliable for some sports (F1, WEC) need to start looking into sport-specific APIs like `OpenF1`
- 3-letter team name truncation is bad practice. `strHomeTeam[:3]` produces ambiguous results (e.g. "Man" for both Manchester clubs), should be replaced with a proper lookup table such as Reuters sports team codes

### Day 6 Ideas

- Set up F1 rendering
- HTTP error handling in `api.py`, adding `response.raise_for_status()` and other api handling bits
- `get_tv()` empty response guard, even though it's not currently a used function still better to fix now than be lost later
- start looking into Roadmap ideas, likely going to start with proper F1 data and going to be using `OpenF1` to get f1 data due to the limitation of data available on `TheSportDB`

## Bonus Day - 2026-05-09

- No coding today but tidied up `DEVLOG.md` and added a note about authorship to `CODE_STYLE.md`
- removed both from `.gitignore` as even though these are both mainly for me, to have them documented is an important part of the project learning process

## Day 6 - 2026-05-10

### Scope - Day 6

- fix missing matches bug, eventds day php on returns max 3 results
- fix null scores bug
- sort ToC for devlog, get rid of all the H3s
- fix abbr handling for upocming cells
- add guards where needed and error handling
- OpenF1 research and start hunting for a WEC API

### Design - API limitiations and looking for others

- `TheSportsDB`'s free tier caps responses at 3 results per request, found out when several matches failed to appear today.
- I have decided to swap to football-data.org, which has no result cap on the free tier but only covers 12 competitions.
  - these competitions cover everything that I need for now.
- I will likely utilise `TheSportsDB` in the future, likley for sports with no specialised API but i've placed it on the back burner for now.
- Another likely use case for TheSportsDB is using it to discover the events and aggregate them. then fetch the detail from a specialist API.
- This means the project is now going to be utlising multiple apis, each sport gets the best free API available.

### Achieved

- As the APIs now have personal keys I've added .env and .env.example to keep keys private
- refactored `api.py` and the data pipeline for football to use `football-data` API
- edited ToC to only show `H1`s and `H2`s
