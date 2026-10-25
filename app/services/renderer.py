"""Turns a template + answers into the finished story."""
from .parser import extract_blanks, tokenize


def _agree_article(article, word):
    base = "an" if word.strip()[:1].lower() in "aeiou" and word.strip() else "a"
    return base.capitalize() if article[:1].isupper() else base


def build_segments(template, answers=None):
    """Segments for display. Blank segments get a "value" (None when unanswered),
    and "a"/"an" before a filled blank is corrected to match the word."""
    answers = list(answers or [])
    segments = [dict(s) for s in tokenize(template)]
    for seg in segments:
        if seg["kind"] == "blank":
            seg["value"] = answers[seg["index"]] if seg["index"] < len(answers) else None
    for i, seg in enumerate(segments):
        if seg["kind"] == "article":
            value = segments[i + 2].get("value")  # article, spacing, blank
            if value:
                seg["text"] = _agree_article(seg["text"], value)
    return segments


def fill_template(template, answers):
    expected = len(extract_blanks(template))
    if len(answers) != expected:
        raise ValueError(f"Expected {expected} answers, got {len(answers)}.")
    return "".join(
        seg["value"] if seg["kind"] == "blank" else seg["text"]
        for seg in build_segments(template, answers)
    )
