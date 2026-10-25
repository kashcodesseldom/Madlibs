"""Input checks and cleanup. Nothing from a form or the API is trusted."""
import re

from .parser import BLANK_RE, extract_blanks

_CONTROL = re.compile(r"[\x00-\x1f\x7f]")
_UNSAFE = re.compile(r"[{}<>]")


class ValidationError(ValueError):
    def __init__(self, errors, fields=None):
        super().__init__("; ".join(errors))
        self.errors = errors          # list of messages
        self.fields = fields or {}    # {blank index: message}


def _collapse(value):
    return re.sub(r"\s+", " ", _CONTROL.sub(" ", str(value or ""))).strip()


def clean_word(value):
    """One player's word: no control characters, braces or angle brackets."""
    return _collapse(_UNSAFE.sub("", str(value)))


def validate_answers(answers, expected_count, max_length=40, labels=None):
    if not isinstance(answers, list):
        raise ValidationError(["Send the words as a list."])
    if len(answers) != expected_count:
        raise ValidationError(
            [f"This story needs {expected_count} words, but got {len(answers)}."]
        )
    cleaned, errors, fields = [], [], {}
    for i, raw in enumerate(answers):
        name = labels[i] if labels else f"word {i + 1}"
        word = clean_word(raw) if isinstance(raw, str) else ""
        if not word:
            message = f"Fill in the {name}."
        elif len(word) > max_length:
            message = f"Keep the {name} under {max_length} characters."
        else:
            message = None
        if message:
            errors.append(message)
            fields[i] = message
        cleaned.append(word)
    if errors:
        raise ValidationError(errors, fields)
    return cleaned


def validate_story(title, category, template_text, max_length=4000, max_blanks=40):
    errors = []
    title = _collapse(title)
    category = _collapse(category) or "Everyday"
    category = category[:1].upper() + category[1:]
    template = (template_text or "").replace("\r\n", "\n").strip()

    if not title:
        errors.append("Give your story a title.")
    elif len(title) > 120:
        errors.append("Keep the title under 120 characters.")
    if len(category) > 40:
        errors.append("Keep the category under 40 characters.")

    if not template:
        errors.append("Write the story text.")
    elif len(template) > max_length:
        errors.append(f"Keep the story under {max_length} characters.")
    else:
        count = len(extract_blanks(template))
        if count < 3:
            errors.append("Add at least 3 blanks, like {adjective}.")
        elif count > max_blanks:
            errors.append(f"Use at most {max_blanks} blanks.")
        leftover = BLANK_RE.sub("", template)
        if "{" in leftover or "}" in leftover:
            errors.append(
                "A { or } isn't part of a valid blank. Blanks use letters only, like {plural noun}."
            )

    if errors:
        raise ValidationError(errors)
    return {"title": title, "category": category, "template_text": template}
