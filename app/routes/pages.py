"""HTML pages."""
from flask import (
    Blueprint, abort, current_app, flash, redirect, render_template, request, url_for,
)
from sqlalchemy import func

from ..extensions import db
from ..models.story import Story
from ..models.submission import Submission
from ..services.renderer import build_segments
from ..services.validators import ValidationError, validate_story

pages_bp = Blueprint("pages", __name__)

SUGGESTED_CATEGORIES = ["Funny", "Spooky", "School", "Adventure", "Everyday"]


@pages_bp.get("/")
def index():
    selected = request.args.get("category", "").strip()
    query = db.select(Story).order_by(Story.id)
    if selected:
        query = query.where(Story.category == selected)
    stories = db.session.scalars(query).all()
    categories = db.session.scalars(
        db.select(Story.category).distinct().order_by(Story.category)
    ).all()
    return render_template("index.html", stories=stories, categories=categories, selected=selected)


@pages_bp.get("/play/<int:story_id>")
def play(story_id):
    story = db.get_or_404(Story, story_id)
    return render_template(
        "play.html",
        story=story,
        segments=build_segments(story.template_text),
        max_len=current_app.config["MAX_ANSWER_LENGTH"],
    )


@pages_bp.get("/result/<slug>")
def result(slug):
    submission = db.first_or_404(db.select(Submission).filter_by(slug=slug))
    story = submission.story
    return render_template(
        "result.html",
        submission=submission,
        story=story,
        segments=build_segments(story.template_text, submission.answers),
    )


@pages_bp.get("/random")
def random_story():
    story = db.session.scalars(db.select(Story).order_by(func.random()).limit(1)).first()
    if story is None:
        abort(404)
    return redirect(url_for("pages.play", story_id=story.id))


@pages_bp.route("/create", methods=["GET", "POST"])
def create():
    form = {"title": "", "category": "", "template_text": ""}
    errors = []
    if request.method == "POST":
        form = {key: request.form.get(key, "") for key in form}
        try:
            data = validate_story(
                **form,
                max_length=current_app.config["MAX_TEMPLATE_LENGTH"],
                max_blanks=current_app.config["MAX_BLANKS"],
            )
        except ValidationError as err:
            errors = err.errors
        else:
            story = Story(**data)
            db.session.add(story)
            db.session.commit()
            flash("Your story is ready to play.", "success")
            return redirect(url_for("pages.play", story_id=story.id))
    return (
        render_template("create.html", form=form, errors=errors, categories=SUGGESTED_CATEGORIES),
        422 if errors else 200,
    )
