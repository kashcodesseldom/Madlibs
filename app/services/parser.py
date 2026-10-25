"""Finds the {blanks} inside a story template."""
import re

# {adjective}, {plural noun}, {verb ending in ing} ... letters, spaces, - and ' only.
BLANK_RE = re.compile(r"\{\s*([A-Za-z][A-Za-z '\-]{0,39}?)\s*\}")
# An "a" / "an" sitting right before a blank, e.g. "I saw a " + {animal}
ARTICLE_RE = re.compile(r"(?<![A-Za-z'])([Aa]n?)(\s+)$")


def _clean_label(raw):
    return re.sub(r"\s+", " ", raw).strip().lower()


def extract_blanks(template):
    """'A {adjective} {animal}' -> ['adjective', 'animal'] (in order, repeats kept)."""
    return [_clean_label(m.group(1)) for m in BLANK_RE.finditer(template or "")]


def tokenize(template):
    """Split a template into segments:
    {"kind": "text", "text": ...}
    {"kind": "article", "text": "a"}          (only when directly before a blank)
    {"kind": "blank", "label": ..., "index": n}
    """
    template = template or ""
    segments, pos, index = [], 0, 0
    for match in BLANK_RE.finditer(template):
        _push_text(segments, template[pos:match.start()], before_blank=True)
        segments.append({"kind": "blank", "label": _clean_label(match.group(1)), "index": index})
        index += 1
        pos = match.end()
    _push_text(segments, template[pos:], before_blank=False)
    return segments


def _push_text(segments, text, before_blank):
    if before_blank:
        found = ARTICLE_RE.search(text)
        if found:
            head = text[: found.start()]
            if head:
                segments.append({"kind": "text", "text": head})
            segments.append({"kind": "article", "text": found.group(1)})
            segments.append({"kind": "text", "text": found.group(2)})
            return
    if text:
        segments.append({"kind": "text", "text": text})


def make_teaser(template, limit=70):
    """Short preview for story cards, with blanks shown as _____."""
    plain = re.sub(r"\s+", " ", BLANK_RE.sub("_____", template or "")).strip()
    if len(plain) <= limit:
        return plain
    return plain[:limit].rsplit(" ", 1)[0].rstrip(" ,.;:") + "…"
