
"""Load data/seed_stories.json into the database.

Run from the project root:
    python scripts/seed_db.py            # add any stories that are missing
    python scripts/seed_db.py --reset    # delete all stories and results first
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from app import create_app  # noqa: E402
from app.extensions import db  # noqa: E402
from app.models.story import Story  # noqa: E402
from app.models.submission import Submission  # noqa: E402

SEED_FILE = ROOT / "data" / "seed_stories.json"


def seed():
    """Add stories that aren't in the database yet. Needs an app context."""
    existing = {title for (title,) in db.session.query(Story.title)}
    stories = json.loads(SEED_FILE.read_text(encoding="utf-8"))
    added = 0
    for item in stories:
        if item["title"] in existing:
            continue
        db.session.add(
            Story(
                title=item["title"],
                category=item["category"],
                template_text=item["template_text"],
            )
        )
        added += 1
    db.session.commit()
    return added


def seed_if_empty():
    if db.session.query(Story.id).first() is None:
        return seed()
    return 0


if __name__ == "__main__":
    app = create_app()
    with app.app_context():
        if "--reset" in sys.argv:
            Submission.query.delete()
            Story.query.delete()
            db.session.commit()
        print(f"Added {seed()} stories.")
