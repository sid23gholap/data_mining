import re
import html
from typing import Optional

TAG_RE = re.compile(r"<[^>]+>")

def strip_html(raw_html: str) -> str:
    if not raw_html:
        return ""
    # Remove tags and unescape entities
    text = TAG_RE.sub(" ", raw_html)
    text = html.unescape(text)
    return text

def normalize_text(s: Optional[str]) -> str:
    if not s:
        return ""
    s = strip_html(s)
    s = s.lower()
    # keep letters, numbers, and basic separators; collapse whitespace
    s = re.sub(r"[^a-z0-9]+", " ", s)
    s = re.sub(r"\s+", " ", s).strip()
    return s
