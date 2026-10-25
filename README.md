# Madlib Game

A Mad Libs style word game built with Flask, SQLAlchemy and SQLite. Pick a story, fill in the
blanks, and get a shareable link to the finished result. The UI is soft pink glass.

## Run it

```bash
python -m venv venv
venv\Scripts\activate          # Windows
# source venv/bin/activate     # macOS / Linux
pip install -r requirements.txt
python run.py
```

Open http://127.0.0.1:5000. The first run creates `data/madlib.db` and loads the starter stories.

```bash
python scripts/seed_db.py            # add any missing starter stories
python scripts/seed_db.py --reset    # delete all stories and results, then reseed
python -m pytest                     # run the tests
```

## How a story works

A story is plain text with blanks in curly braces:

```
Today a {adjective} {animal} learned to {verb}.
```

- Blanks use letters, spaces, `-` and `'` only, e.g. `{plural noun}`.
- The same label can appear more than once; each one gets its own input.
- `a {animal}` is switched to `an octopus` automatically.
- Write your own at `/create` (needs at least 3 blanks).

## Structure

| Path | Job |
|---|---|
| `app/__init__.py` | `create_app()` factory, blueprints, error pages |
| `app/models/` | `Story` and `Submission` tables |
| `app/routes/pages.py` | HTML pages: `/`, `/play/<id>`, `/result/<slug>`, `/random`, `/create` |
| `app/routes/api.py` | JSON: `GET /api/stories`, `GET /api/stories/<id>`, `POST /api/stories/<id>/submit` |
| `app/services/` | `parser` (find blanks), `renderer` (fill them), `validators` (clean input) |
| `app/templates/`, `app/static/` | Jinja pages, glass CSS, `play.js`, `result.js` |
| `data/seed_stories.json` | Starter stories |

Routes stay thin; the logic lives in `services/`, which is what the tests cover.

## API

```
POST /api/stories/1/submit
{"answers": ["sparkly", "llama", "tumble"]}

201 {"slug": "...", "result_url": "/result/...", "final_text": "..."}
422 {"error": "...", "errors": [...], "fields": {"1": "Fill in the animal."}}
```

## Settings

Set these as environment variables: `SECRET_KEY`, `DATABASE_URL` (defaults to the SQLite file in `data/`).

## Deploying

**PythonAnywhere (free):** upload the project, create a virtualenv, `pip install -r requirements.txt`,
run `python scripts/seed_db.py` once, then point a Manual configuration web app at the project and use
this WSGI file:

```python
import os, sys

path = "/home/YOUR_USERNAME/madlib-game"
if path not in sys.path:
    sys.path.insert(0, path)

os.environ["SECRET_KEY"] = "a-long-random-string"

from run import app as application  # noqa
```

**Other hosts:** use `gunicorn run:app` (not `app:create_app()`, which skips loading the starter
stories) and set `SECRET_KEY`. If the host's disk resets on every deploy, SQLite data is lost, so set
`DATABASE_URL` to a hosted Postgres database and add its driver (for example `psycopg2-binary`) to
`requirements.txt`.
