import re


def clean_text(text):

    if not text:
        return ""

    text = re.sub(r'\s+', ' ', text)

    return text.strip()


def normalize_articles(articles):

    normalized = []

    for a in articles:

        normalized.append({
            "title": clean_text(a.get("title")),
            "summary": clean_text(a.get("summary")),
            "source": a.get("source"),
            "url": a.get("url"),
            "date": a.get("date")
        })

    return normalized