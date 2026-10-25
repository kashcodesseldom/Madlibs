import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app import create_app
from app.config import TestConfig
from app.extensions import db
from app.models.story import Story

TEMPLATE = "A {adjective} {animal} ate {plural noun}."


@pytest.fixture()
def app():
    app = create_app(TestConfig)
    with app.app_context():
        db.session.add(Story(title="Test Tale", category="Funny", template_text=TEMPLATE))
        db.session.commit()
        yield app
        db.session.remove()
        db.drop_all()


@pytest.fixture()
def client(app):
    return app.test_client()


def submit(client, answers, story_id=1):
    return client.post(f"/api/stories/{story_id}/submit", json={"answers": answers})


def test_home_lists_stories(client):
    res = client.get("/")
    assert res.status_code == 200
    assert b"Test Tale" in res.data


def test_home_category_filter(client):
    assert b"Test Tale" in client.get("/?category=Funny").data
    assert b"Test Tale" not in client.get("/?category=Spooky").data


def test_play_page_shows_a_field_per_blank(client):
    res = client.get("/play/1")
    assert res.status_code == 200
    assert res.data.count(b'name="answer"') == 3


def test_play_unknown_story_is_404(client):
    assert client.get("/play/999").status_code == 404


def test_api_lists_and_describes_stories(client):
    stories = client.get("/api/stories").get_json()["stories"]
    assert stories[0]["blank_count"] == 3
    detail = client.get("/api/stories/1").get_json()
    assert detail["blanks"] == ["adjective", "animal", "plural noun"]


def test_api_unknown_story_is_json_404(client):
    res = client.get("/api/stories/999")
    assert res.status_code == 404
    assert res.get_json()["error"]


def test_submit_creates_shareable_result(client):
    res = submit(client, ["enormous", "octopus", "spoons"])
    assert res.status_code == 201
    data = res.get_json()
    assert data["final_text"] == "An enormous octopus ate spoons."
    page = client.get(data["result_url"])
    assert page.status_code == 200
    assert b"octopus" in page.data


def test_submit_rejects_empty_words(client):
    res = submit(client, ["big", "", "spoons"])
    assert res.status_code == 422
    assert "1" in res.get_json()["fields"]


def test_submit_rejects_wrong_count_and_bad_body(client):
    assert submit(client, ["only one"]).status_code == 422
    assert client.post("/api/stories/1/submit", data="nope").status_code == 400


def test_result_escapes_html(client):
    data = submit(client, ["<script>x</script>", "cat", "hats"]).get_json()
    assert b"<script>x" not in client.get(data["result_url"]).data


def test_unknown_result_is_404(client):
    assert client.get("/result/nope").status_code == 404


def test_random_redirects_to_a_story(client):
    res = client.get("/random")
    assert res.status_code == 302
    assert "/play/" in res.headers["Location"]


def test_create_story_flow(client):
    assert client.get("/create").status_code == 200
    bad = client.post("/create", data={"title": "", "category": "", "template_text": "no blanks"})
    assert bad.status_code == 422
    good = client.post(
        "/create",
        data={"title": "Mine", "category": "school", "template_text": "{noun} {verb} {adjective}"},
    )
    assert good.status_code == 302
    assert b"Mine" in client.get("/").data
