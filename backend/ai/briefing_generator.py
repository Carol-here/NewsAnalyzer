import os
from dotenv import load_dotenv
from groq import Groq

from story_cluster import load_articles, create_embeddings, cluster_articles

load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")

if not GROQ_API_KEY:
    raise ValueError("GROQ_API_KEY not found in .env file")

# Initialize Groq client
client = Groq(api_key=GROQ_API_KEY)


def build_cluster_context(articles_in_cluster):
    """
    Build context text from articles in the cluster
    """

    context = ""

    for article in articles_in_cluster:
        context += f"""
Title: {article['title']}
Summary: {article['summary']}
Source: {article['source']}
"""

    return context


def generate_briefing(articles_in_cluster):
    """
    Generate AI briefing for a cluster of news articles
    """

    if not articles_in_cluster:
        return "No articles available for this cluster."

    context = build_cluster_context(articles_in_cluster)

    prompt = f"""
You are a financial and technology news analyst.

Using the following news articles, generate a structured intelligence briefing.

Articles:
{context}

Provide output in this format:

Topic:
Executive Summary:
Key Developments:
Market Implications:
Future Outlook:
"""

    try:

        response = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[
                {
                    "role": "system",
                    "content": "You are a professional financial news analyst."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            temperature=0.3
        )

        return response.choices[0].message.content

    except Exception as e:
        return f"Error generating briefing: {str(e)}"


def main():

    print("\nLoading articles...")

    articles = load_articles()

    print("Creating embeddings...")

    embeddings = create_embeddings(articles)

    print("Clustering stories...")

    clusters = cluster_articles(articles, embeddings)

    for cid, articles_in_cluster in clusters.items():

        print("\n==========================")
        print("NEWS BRIEFING FOR CLUSTER", cid)
        print("==========================")

        briefing = generate_briefing(articles_in_cluster)

        print(briefing)


if __name__ == "__main__":
    main()