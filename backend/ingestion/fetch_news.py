import requests
import feedparser
from dotenv import load_dotenv
import os

load_dotenv() 

NEWSDATA_KEY = os.getenv("NEWSDATA_KEY")
GNEWS_KEY = os.getenv("GNEWS_KEY")


def fetch_newsdata(topic, limit=10):

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

            articles.append({
                "title": a.get("title"),
                "summary": a.get("description"),
                "source": a.get("source_id"),
                "url": a.get("link"),
                "date": a.get("pubDate")
            })

    return articles


def fetch_gnews(topic, limit=10):

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

            articles.append({
                "title": a.get("title"),
                "summary": a.get("description"),
                "source": a["source"].get("name"),
                "url": a.get("url"),
                "date": a.get("publishedAt")
            })

    return articles


def fetch_google_rss(topic, limit=10):

    rss_url = f"https://news.google.com/rss/search?q={topic}"

    feed = feedparser.parse(rss_url)

    articles = []

    for entry in feed.entries[:limit]:

        articles.append({
            "title": entry.title,
            "summary": "Summary not available",
            "source": "Google News",
            "url": entry.link,
            "date": entry.published
        })

    return articles


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


if __name__ == "__main__":

    topic = "artificial intelligence"

    news = fetch_all_news(topic)

    for n in news:
        print(n["title"])