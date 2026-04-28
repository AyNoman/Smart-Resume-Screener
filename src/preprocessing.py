import re
import pandas as pd

from src.config import NORMALIZATION_MAP


def clean_text(text: str) -> str:
    if text is None:
        return ""

    text = str(text).lower()
    text = text.replace("\n", " ")
    text = re.sub(r"[^a-z0-9+.#/\-\s]", " ", text)
    text = re.sub(r"\s+", " ", text).strip()

    for old, new in NORMALIZATION_MAP.items():
        text = text.replace(old, new)

    return text


def unique_preserve_order(items):
    seen = set()
    output = []
    for item in items:
        if item not in seen:
            seen.add(item)
            output.append(item)
    return output


def extract_skills(text: str, skills_catalog: list[str]) -> list[str]:
    text = clean_text(text)
    found = []

    for skill in skills_catalog:
        skill_clean = clean_text(skill)
        pattern = r"\b" + re.escape(skill_clean) + r"\b"
        if re.search(pattern, text):
            found.append(skill_clean)

    return unique_preserve_order(found)


def extract_top_keywords(job_description: str, top_n: int = 15) -> list[str]:
    text = clean_text(job_description)
    words = text.split()

    stop_words = {
        "the", "a", "an", "and", "or", "to", "for", "of", "in", "on", "with", "is", "are",
        "as", "by", "at", "from", "this", "that", "will", "be", "can", "should", "have",
        "has", "our", "your", "you", "we", "their", "they", "role", "job", "candidate",
        "experience", "work", "ability", "skills", "requirements", "preferred", "required"
    }

    filtered = [w for w in words if len(w) > 2 and w not in stop_words]
    if not filtered:
        return []

    freq = pd.Series(filtered).value_counts()
    return freq.head(top_n).index.tolist()
