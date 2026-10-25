import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.services.renderer import build_segments, fill_template
from app.services.validators import ValidationError, validate_answers, validate_story


def test_fill_template():
    assert fill_template("The {adjective} {animal} sat.", ["tiny", "goat"]) == "The tiny goat sat."


def test_a_becomes_an_before_vowel():
    assert fill_template("I saw a {animal}.", ["octopus"]) == "I saw an octopus."


def test_an_becomes_a_before_consonant_and_case_is_kept():
    assert fill_template("I saw an {animal}.", ["goat"]) == "I saw a goat."
    assert fill_template("A {adjective} day", ["epic"]) == "An epic day"


def test_wrong_answer_count_raises():
    with pytest.raises(ValueError):
        fill_template("{noun} {noun}", ["one"])


def test_build_segments_without_answers_has_no_values():
    blanks = [s for s in build_segments("a {noun}") if s["kind"] == "blank"]
    assert blanks[0]["value"] is None


def test_validate_answers_cleans_words():
    assert validate_answers(["  big   dog ", "<b>hi</b>"], 2) == ["big dog", "bhi/b"]


def test_validate_answers_rejects_empty_and_long():
    with pytest.raises(ValidationError) as err:
        validate_answers(["", "x" * 50], 2, max_length=40, labels=["noun", "verb"])
    assert set(err.value.fields) == {0, 1}


def test_validate_answers_wrong_count():
    with pytest.raises(ValidationError):
        validate_answers(["one"], 2)


def test_validate_story_needs_three_blanks_and_valid_braces():
    with pytest.raises(ValidationError):
        validate_story("T", "Funny", "Only {one} blank")
    with pytest.raises(ValidationError):
        validate_story("T", "Funny", "{a} {b} {c} but {broken")
    ok = validate_story("T", "funny", "{a} {b} {c}")
    assert ok["category"] == "Funny"
