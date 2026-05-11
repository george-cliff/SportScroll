# Code Style Personal Reference

## A Note on Authorship
>
> Generated in collaboration with Claude Code. I showed my code to Claude and it mentioned PEP 8 standards for Python, we went through my preferences for how I write code. I struggle to know what to write for docstrings and comments as I've never received proper guidance on how to write them. This document is a helper for me to remember what to write, how to write it, and best practices for formatting functions and variables.

---

## 1. Import section comments

### The actual standard (PEP 8)

Imports must be grouped in this order, separated by **blank lines**:

1. Standard library imports
2. Related third-party imports
3. Local application / library imports

The blank line is the separator. Section comment labels are optional in PEP 8 — most large open-source codebases don't use them, but they're a valid stylistic choice.

### My choice: I keep the section comment labels

For my own readability, I label each group:

```python
# Standard library Imports
from datetime import datetime

# Related third party imports
import requests

# Local application/library specific imports
from src.config import load_config
```

Rules for keeping them consistent across the project:

- **Every module uses them, or none does.** Half-on/half-off is the worst option.
- **Capitalisation matches across all files.** Pick one form (e.g. `# Standard library Imports`) and use it everywhere.
- **Keep the comment even when the section is empty** — signals deliberate absence rather than a missing import.
- **Don't nest sub-groups.** No `# Date utilities` inside the standard library group.

### Other import rules worth keeping

- All imports go at the top of the file, after the module docstring and any `__future__` imports
- Within each group: `import x` statements first, then `from x import y` statements. Alphabetical within each sub-group.
- Avoid `from x import *` — it pollutes the namespace and breaks tooling
- Avoid imports inside functions unless you have a real reason (circular imports, optional dependencies, expensive modules)
- One import per line for `import` statements; `from x import a, b, c` on one line is fine

---

## 2. Inline comments

### The single rule

**Comments explain *why*, not *what*.**

The code already shows what it does. A comment earns its place when it adds context the code itself can't carry: a reason, a constraint, a workaround, a piece of domain knowledge.

### Good inline comments

- **Label logical phases of a multi-step function.** `# Check TTL expiry` above a block of 4 related lines is useful — it lets a reader scan the structure without reading every line. This is different from commenting a single obvious line.
- **Justify a non-obvious choice.** `# use strftime over str() so the format is explicit` — tells future-you the format wasn't accidental.
- **Explain a magic number.** `# API rate limit is 30/min, 10 keeps us well below` — the *number* is in the code, the *reason* lives in the comment.
- **Capture domain knowledge.** `# UEFA fixtures are always returned in UTC, regardless of venue` — this isn't visible from any line of code.
- **Flag a workaround.** `# library X chokes on inline SVG, fall back to PNG` — explains why the code is shaped weirdly so nobody "fixes" it.
- **Mark TODOs and FIXMEs.** `# TODO(george): handle empty channel list gracefully` — a name (or issue number) tells the reader who owns it. *Optional on solo projects — a bare `# TODO:` is fine when you're the only contributor.*
- **Warn future maintainers.** `# if you change this, also update render_summary()` — couples files that the type system can't.

### Bad inline comments

- **Restating the code.** `i += 1  # increment i` — adds nothing, wastes a reader's time.
- **Out-of-date comments.** Worse than no comment because they actively mislead. If you change code, change the comment in the same commit.
- **Comments that should be commit messages.** `# fixed bug from yesterday's PR` — that goes in `git log`, not the source.
- **Decorative banners.** `############# SECTION #############` — line noise; use blank lines and function boundaries instead.
- **Commented-out code.** Delete it. That's what version control is for. If you genuinely need to preserve it, write a comment explaining *why* it's commented and link an issue.
- **Apologies.** `# this is hacky sorry` — either fix it or describe what specifically is hacky and why you couldn't fix it.

### When you want to comment, try renaming first

Most "I should comment this" instincts are actually "I should rename this." A function called `process_data` will need a comment. A function called `merge_overlapping_fixtures` won't.

```python
# bad
x = a * 0.6 + b * 0.4  # 60/40 weighted average favouring recent

# better
recent_weight = 0.6
historical_weight = 0.4
score = recent * recent_weight + historical * historical_weight
```

### Format

- PEP 8: at least two spaces before an inline `#`, one space after: `code  # comment`
- Capitalise the first letter for full sentences; lowercase fragments are OK for very short notes
- Don't end short inline comments with a period; do end multi-sentence ones
- One short line max as inline. If you need a paragraph, put it as a block comment **above** the code (or it's actually a docstring)
- Block comments: each line starts with `#`, indented to match the code below it

---

## 3. Docstrings

### The actual standard (PEP 257)

- Every public module, function, class, and method should have a docstring
- Always triple double quotes: `"""..."""`
- One-line docstring: keep on one line, complete sentence, ending in a period

  ```python
  def is_active(user):
      """Returns True if the user has logged in within the last 30 days."""
  ```

- Multi-line docstring: summary line, blank line, more detail, closing `"""` on its own line

  ```python
  def build_report(records):
      """Returns the structured report dict consumed by the renderer.

      Groups records by region and computes per-region totals, returning
      a mapping of region name to ``{count, total, items}`` dicts.
      """
  ```

### Style choice — pick one and stick with it

The three common structured docstring formats:

- **Google style** — `Args:`, `Returns:`, `Raises:` blocks. Most readable, most popular in modern Python.
- **NumPy / SciPy style** — section headers underlined with dashes. Common in scientific code.
- **reStructuredText / Sphinx** — `:param x:`, `:returns:`. Older, Sphinx-friendly, less readable raw.

My choice: **Google style**. Example:

```python
def fetch_records(source_id, target_date):
    """Fetches all records for a source on a given date.

    Args:
        source_id: Identifier for the upstream data source.
        target_date: A datetime or date object for the day to query.

    Returns:
        A list of raw record dicts. Empty list if no records exist for that date.
    """
```

### Imperative vs indicative mood

PEP 257 says imperative ("Return the events"). Google style and most modern code uses indicative ("Returns the events"). Both are widely accepted.

**My choice: indicative mood** — `Returns`, `Fetches`, `Computes`, `Loads`. Reads more naturally as a description of the function rather than a command. Apply consistently across the codebase — it's mixing the two that looks unprofessional.

### Module docstrings

At the very top of the file, before imports. 1-3 lines. Says what the module is responsible for and any usage notes.

```python
"""HTTP client for the upstream data API.

Wraps the public and authenticated endpoints. Auth mode is driven by
``config.yaml``.
"""

# Standard library imports
import requests
...
```

### What to include

- **Always:** what the function does (in one line)
- **Often:** what each non-obvious parameter means
- **Often:** what's returned, especially for non-trivial return shapes (e.g. nested dicts)
- **When relevant:** what exceptions are raised
- **When relevant:** notable side effects ("writes to `.cache/`", "may make a network call")
- **Don't:** repeat type hints from the signature — that's duplication

### Private functions

Functions prefixed with `_` can have shorter docstrings or just a one-liner. The convention is "private = the public docs of this don't matter, but a one-line note still helps the next person reading it."

```python
def _latest_record():
    """Returns the most recent record dict, or None if the store is empty."""
```

### Tools

- `ruff` with the `D` rule set enforces pydocstyle
- `pydocstyle` standalone
- `interrogate` reports docstring coverage as a percentage — fun for a portfolio piece to hit 100%

---

## 4. Function and variable naming conventions

### The conventions

| Pattern | Meaning | Use for |
| --- | --- | --- |
| `_name` | Private / internal | Helpers not meant to be called from outside the module |
| `__name` | Dunder / magic | Python-reserved — `__init__`, `__str__` etc. Don't invent these |
| `name_` | Trailing underscore | Avoiding a clash with a Python keyword (`class_`, `type_`) |
| `UPPER_CASE` | Constant | Module-level values that don't change (`MAX_RETRIES`, `DATE_FORMAT`) |
| `CapWords` | Class name | Classes only — never functions or variables |
| `lower_snake_case` | Everything else | Functions, variables, parameters, module names |
| `_` (lone) | Throwaway | Loop variables and unpacked values you don't intend to use (`for _ in range(3)`) |

### The rule that matters most

If a function is only ever called from within the same module, prefix it with `_`. It signals "implementation detail — don't rely on this from outside." Python won't enforce it (anyone *can* still call `_name`), but the underscore is a contract: callers know they're reaching past the public surface and own the breakage if it changes.

Examples:

- `_parse_record()` — only called by `load_records()`, never from `main.py`
- `_format_timestamp()` — only called inside `render_html()`
- `_render_section()` — only called inside `generate_html()`

### Try renaming before adding a comment

If a function name needs a comment to explain what it does, the name is probably wrong. `_parse_timestamp_to_local()` needs no comment. `_convert()` does.

The same applies to variables. `x` and `data` need comments to be useful. `recent_events` and `pending_records` don't.

---

## 5. Logging levels

| Level | Python | When to use |
| --- | --- | --- |
| Trace | *(no native equivalent)* | Tracing one specific part of a function — granular enough that you'd only turn it on to hunt a single bug |
| Debug | `logging.DEBUG` | Diagnostically helpful detail for admins and devs — not needed day-to-day but valuable when things go wrong |
| Info | `logging.INFO` | Normal operation landmarks (start/stop, config loaded, cache hit). Always available, rarely acted on. **Default level.** |
| Warn | `logging.WARNING` | Something odd happened but the app recovered automatically — retrying an operation, falling back to a secondary source, missing optional data |
| Error | `logging.ERROR` | An operation failed and the user must intervene — missing required file, bad config, failed API auth. The app can keep running but this task is dead |
| Fatal | `logging.CRITICAL` | Shutting down to prevent data loss or corruption. Reserve for the most severe failures only |

Python has no native TRACE level. Use `DEBUG` with specific message text to cover it.

---

## Quick checklist for each `.py` file

When you open a file, can you tick all of these?

- Module docstring at the top, before imports
- Imports grouped per PEP 8 (with or without comment labels — consistent with the rest of the project)
- Every public function has a docstring with capital-letter first word and terminal period
- Non-trivial functions have Args / Returns sections in the chosen style
- Module-internal helpers prefixed with `_`; constants in `UPPER_CASE`; everything else `lower_snake_case`
- No `# i += 1` style restatement comments
- No commented-out code blocks
- Magic numbers/strings either pulled into named constants or have a one-line comment explaining them
- TODOs are searchable (tagged with a name or issue number on team projects; bare `# TODO:` is fine on solo projects)

If all of those are clean, the file's well-documented.
