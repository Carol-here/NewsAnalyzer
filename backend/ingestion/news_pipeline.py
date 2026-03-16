import json

from fetch_news import fetch_all_news
from scrape_articles import normalize_articles


OUTPUT_FILE = "../data/articles.json"


def remove_duplicates(articles):

    seen = set()
    unique_articles = []

    for a in articles:

        key = a["title"]

        if key not in seen:
            seen.add(key)
            unique_articles.append(a)

    return unique_articles


def run_pipeline(topic):

    print("Fetching news...")

    articles = fetch_all_news(topic)

    print("Normalizing articles...")

    articles = normalize_articles(articles)

    print("Removing duplicates...")

    articles = remove_duplicates(articles)

    print("Total articles collected:", len(articles))

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(articles, f, indent=2)

    print("Saved to", OUTPUT_FILE)


if __name__ == "__main__":

    topic = "artificial intelligence"

    run_pipeline(topic)