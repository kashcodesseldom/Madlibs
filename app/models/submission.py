import secrets
from datetime import datetime, timezone

from ..extensions import db


class Submission(db.Model):
    __tablename__ = "submissions"

    id = db.Column(db.Integer, primary_key=True)
    story_id = db.Column(db.Integer, db.ForeignKey("stories.id"), nullable=False, index=True)
    answers = db.Column(db.JSON, nullable=False)  # list of words, in blank order
    final_text = db.Column(db.Text, nullable=False)
    slug = db.Column(db.String(16), unique=True, nullable=False, index=True)
    created_at = db.Column(
        db.DateTime, nullable=False, default=lambda: datetime.now(timezone.utc)
    )

    story = db.relationship("Story", back_populates="submissions")

    @staticmethod
    def new_slug():
        """Short, unguessable id for the share link."""
        while True:
            slug = secrets.token_urlsafe(6)
            if db.session.query(Submission.id).filter_by(slug=slug).first() is None:
                return slug
