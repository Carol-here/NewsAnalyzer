from groq import Groq
import os
from dotenv import load_dotenv

load_dotenv()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))


def expand_query(query):

    prompt = f"""
Generate 5 short alternative search queries related to:

{query}

Return only the queries as a list.
"""

    response = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.3
    )

    text = response.choices[0].message.content

    queries = [q.strip("- ").strip() for q in text.split("\n") if q.strip()]

    queries.append(query)

    return list(set(queries))