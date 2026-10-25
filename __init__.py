"""Application factory for the Madlib Game."""
from flask import Flask, jsonify, render_template_string, request

from .config import Config
from .extensions import db

ERROR_PAGE = """{% extends "base.html" %}
{% block title %}{{ heading }} | Madlib Game{% endblock %}
{% block content %}
<section class="glass panel notice">
  <h1>{{ heading }}</h1>
  <p class="lede">{{ message }}</p>
  <a class="btn btn-primary" href="{{ url_for('pages.index') }}">Back to stories</a>
</section>
{% endblock %}
"""


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)
    db.init_app(app)

    from .models import story, submission  # noqa: F401  (registers the tables)
    from .routes.api import api_bp
    from .routes.pages import pages_bp

    app.register_blueprint(pages_bp)
    app.register_blueprint(api_bp)

    @app.errorhandler(404)
    def not_found(_err):
        if request.path.startswith("/api/"):
            return jsonify(error="Not found."), 404
        return render_template_string(
            ERROR_PAGE,
            heading="We couldn't find that page",
            message="The link may be old, or the story may have been removed.",
        ), 404

    @app.errorhandler(500)
    def server_error(_err):
        if request.path.startswith("/api/"):
            return jsonify(error="Something went wrong on our side."), 500
        return render_template_string(
            ERROR_PAGE,
            heading="Something went wrong",
            message="That one's on us. Go back and try again.",
        ), 500

    with app.app_context():
        db.create_all()

    return app
