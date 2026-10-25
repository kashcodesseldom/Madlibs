from datetime import datetime, timezone

from ..extensions import db
from ..services.parser import extract_blanks, make_teaser


class Story(db.Model):
    __tablename__ = "stories"

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120), nullable=False)
    category = db.Column(db.String(40), nullable=False, default="Everyday", index=True)
    template_text = db.Column(db.Text, nullable=False)
    created_at = db.Column(
        db.DateTime, nullable=False, default=lambda: datetime.now(timezone.utc)
    )

    submissions = db.relationship(
        "Submission", back_populates="story", cascade="all, delete-orphan"
    )

    @property
    def blanks(self):
        return extract_blanks(self.template_text)

    @property
    def blank_count(self):
        return len(self.blanks)

    @property
    def teaser(self):
        return make_teaser(self.template_text)

    def to_dict(self, include_blanks=False):
        data = {
            "id": self.id,
            "title": self.title,
            "category": self.category,
            "blank_count": self.blank_count,
            "teaser": self.teaser,
        }
        if include_blanks:
            data["blanks"] = self.blanks
        return data
