import json

import requests
import feedparser
from dotenv import load_dotenv
import os
import urllib.parse
import sys

from sentence_transformers import SentenceTransformer
from torch import cosine_similarity

# allow importing from backend/ai
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "ai")))

from query_expand import expand_query

load_dotenv()

NEWSDATA_KEY = os.getenv("NEWSDATA_KEY")
GNEWS_KEY = os.getenv("GNEWS_KEY")

model = SentenceTransformer("all-MiniLM-L6-v2")


# -----------------------------
# Fetch NewsData API
# -----------------------------
def fetch_newsdata(topic, limit=8):

    url = "https://newsdata.io/api/1/news"

    params = {
        "apikey": NEWSDATA_KEY,
        "q": topic,
        "language": "en"
    }

    response = requests.get(url, params=params)
    data = response.json()

    articles = []

    if "results" in data:
        for a in data["results"][:limit]:

            summary = a.get("description") or ""

            if len(summary) < 20:
                continue

            articles.append({
                "title": a.get("title"),
                "summary": summary,
                "source": a.get("source_id"),
                "url": a.get("link"),
                "date": a.get("pubDate")
            })

    return articles


# -----------------------------
# Fetch GNews API
# -----------------------------
def fetch_gnews(topic, limit=8):

    url = "https://gnews.io/api/v4/search"

    params = {
        "q": topic,
        "apikey": GNEWS_KEY,
        "lang": "en"
    }

    response = requests.get(url, params=params)
    data = response.json()

    articles = []

    if "articles" in data:
        for a in data["articles"][:limit]:

            summary = a.get("description") or ""

            if len(summary) < 20:
                continue

            articles.append({
                "title": a.get("title"),
                "summary": summary,
                "source": a["source"].get("name"),
                "url": a.get("url"),
                "date": a.get("publishedAt")
            })

    return articles


# -----------------------------
# Fetch Google RSS
# -----------------------------
def fetch_google_rss(topic, limit=6):

    rss_url = f"https://news.google.com/rss/search?q={urllib.parse.quote(topic)}"

    feed = feedparser.parse(rss_url)

    articles = []

    for entry in feed.entries[:limit]:

        articles.append({
            "title": entry.title,
            "summary": "",
            "source": "Google News",
            "url": entry.link,
            "date": entry.published
        })

    return articles


# -----------------------------
# Fetch all sources
# -----------------------------
def fetch_all_news(topic):

    articles = []

    try:
        articles.extend(fetch_newsdata(topic))
    except Exception as e:
        print("NewsData failed:", e)

    try:
        articles.extend(fetch_gnews(topic))
    except Exception as e:
        print("GNews failed:", e)

    try:
        articles.extend(fetch_google_rss(topic))
    except Exception as e:
        print("RSS failed:", e)

    return articles


# -----------------------------
# Remove duplicate titles
# -----------------------------
def remove_duplicates(articles):

    seen = set()
    unique = []

    for article in articles:

        title = article["title"]

        if title not in seen:
            seen.add(title)
            unique.append(article)

    return unique


# -----------------------------
# Semantic Filtering
# -----------------------------
def semantic_filter(articles, topic, keep_top=25, threshold=0.35):

    texts = [
        f"{a['title']} {a['summary']}"
        for a in articles
    ]

    article_embeddings = model.encode(texts)

    topic_embedding = model.encode([topic])[0]

    scores = cosine_similarity(
        [topic_embedding],
        article_embeddings
    )[0]

    ranked = list(zip(articles, scores))

    ranked.sort(key=lambda x: x[1], reverse=True)

    # keep only articles above threshold
    filtered = [
        a for a, score in ranked
        if score >= threshold
    ]

    return filtered[:keep_top]


# -----------------------------
# Main Pipeline
# -----------------------------
def main():

    topic = "AI chip industry"

    print("\nExpanding search query...")

    queries = expand_query(topic)

    print("Search queries:", queries)

    articles = []

    # limit total API usage
    for q in queries[:4]:

        print("\nFetching:", q)

        articles.extend(fetch_all_news(q))

    print("\nTotal fetched:", len(articles))

    print("Removing duplicates...")

    articles = remove_duplicates(articles)

    print("After dedup:", len(articles))

    print("Applying semantic filtering...")

    articles = semantic_filter(articles, topic, keep_top=25)

    print("Final articles:", len(articles))

    os.makedirs("../data", exist_ok=True)

    with open("../data/articles.json", "w", encoding="utf-8") as f:
        json.dump(articles, f, indent=2)

    print("\nSaved to ../data/articles.json")


if __name__ == "__main__":
    main()