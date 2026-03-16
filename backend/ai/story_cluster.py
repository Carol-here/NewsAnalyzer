import json
import math
from sentence_transformers import SentenceTransformer
from sklearn.cluster import KMeans
from sklearn.metrics.pairwise import cosine_similarity

INPUT_FILE = "../data/articles.json"

model = SentenceTransformer("all-MiniLM-L6-v2")


def load_articles():
    with open(INPUT_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def create_embeddings(articles):

    texts = []

    for a in articles:
        text = f"{a['title']} {a['summary']}"
        texts.append(text)

    embeddings = model.encode(texts)

    return embeddings


def remove_semantic_duplicates(articles, embeddings, threshold=0.90):

    unique_articles = []
    unique_embeddings = []

    for i, emb in enumerate(embeddings):

        if len(unique_embeddings) == 0:
            unique_articles.append(articles[i])
            unique_embeddings.append(emb)
            continue

        similarities = cosine_similarity([emb], unique_embeddings)[0]

        if max(similarities) < threshold:
            unique_articles.append(articles[i])
            unique_embeddings.append(emb)

    return unique_articles, unique_embeddings


def cluster_articles(articles, embeddings):

    num_articles = len(articles)

    # dynamic cluster count
    num_clusters = max(2, int(math.sqrt(num_articles)))

    kmeans = KMeans(n_clusters=num_clusters, random_state=42)

    labels = kmeans.fit_predict(embeddings)

    clusters = {}

    for i, label in enumerate(labels):

        if label not in clusters:
            clusters[label] = []

        clusters[label].append(articles[i])

    return clusters


def main():

    articles = load_articles()

    embeddings = create_embeddings(articles)

    # remove semantic duplicates
    articles, embeddings = remove_semantic_duplicates(articles, embeddings)

    clusters = cluster_articles(articles, embeddings)

    for cid, items in clusters.items():

        print("\nCLUSTER", cid)

        for article in items:
            print("-", article["title"])


if __name__ == "__main__":
    main()