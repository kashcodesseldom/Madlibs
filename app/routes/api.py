"""JSON endpoints."""
from flask import Blueprint, current_app, jsonify, request, url_for

from ..extensions import db
from ..models.story import Story
from ..models.submission import Submission
from ..services.renderer import fill_template
from ..services.validators import ValidationError, validate_answers

api_bp = Blueprint("api", __name__, url_prefix="/api")


@api_bp.get("/stories")
def list_stories():
    query = db.select(Story).order_by(Story.id)
    category = request.args.get("category", "").strip()
    if category:
        query = query.where(Story.category == category)
    return jsonify(stories=[s.to_dict() for s in db.session.scalars(query)])


@api_bp.get("/stories/<int:story_id>")
def get_story(story_id):
    story = db.session.get(Story, story_id)
    if story is None:
        return jsonify(error="Story not found."), 404
    return jsonify(story.to_dict(include_blanks=True))


@api_bp.post("/stories/<int:story_id>/submit")
def submit(story_id):
    story = db.session.get(Story, story_id)
    if story is None:
        return jsonify(error="Story not found."), 404

    payload = request.get_json(silent=True)
    if not isinstance(payload, dict):
        return jsonify(error='Send JSON like {"answers": ["word", ...]}.'), 400

    try:
        answers = validate_answers(
            payload.get("answers"),
            story.blank_count,
            max_length=current_app.config["MAX_ANSWER_LENGTH"],
            labels=story.blanks,
        )
    except ValidationError as err:
        return jsonify(
            error="Some words need another look.",
            errors=err.errors,
            fields={str(i): msg for i, msg in err.fields.items()},
        ), 422

    submission = Submission(
        story=story,
        answers=answers,
        final_text=fill_template(story.template_text, answers),
        slug=Submission.new_slug(),
    )
    db.session.add(submission)
    db.session.commit()

    return jsonify(
        slug=submission.slug,
        result_url=url_for("pages.result", slug=submission.slug),
        final_text=submission.final_text,
    ), 201
