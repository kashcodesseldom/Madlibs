import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.services.parser import extract_blanks, make_teaser, tokenize


def test_extract_blanks_in_order_with_repeats():
    assert extract_blanks("A {adjective} {animal} and another {adjective} one") == [
        "adjective", "animal", "adjective",
    ]


def test_labels_are_normalised():
    assert extract_blanks("{  Plural   Noun }") == ["plural noun"]


def test_invalid_braces_are_ignored():
    assert extract_blanks("Empty {} and digits {123} and {unclosed") == []


def test_no_blanks():
    assert extract_blanks("Just text.") == []
    assert extract_blanks("") == []


def test_tokenize_marks_article_before_blank():
    kinds = [s["kind"] for s in tokenize("I saw a {animal}.")]
    assert kinds == ["text", "article", "text", "blank", "text"]


def test_tokenize_ignores_a_inside_words():
    kinds = [s["kind"] for s in tokenize("I ate banana {food}")]
    assert "article" not in kinds


def test_teaser_shows_blanks_and_truncates():
    assert make_teaser("A {adjective} day", 50) == "A _____ day"
    assert make_teaser("word " * 50, 20).endswith("…")
