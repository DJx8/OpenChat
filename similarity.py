import math
import re

from embedding import generate_embeddings

# =================================
# STOP WORDS
# =================================

STOP_WORDS = {
    "what",
    "is",
    "are",
    "am",
    "i",
    "my",
    "me",
    "the",
    "a",
    "an",
    "and",
    "or",
    "but",
    "in",
    "on",
    "at",
    "to",
    "of",
    "for",
    "did",
    "do",
    "does",
    "have",
    "has",
    "which",
    "who",
    "where",
    "when",
    "why",
    "how",
    "can",
    "could",
    "would",
    "should",
    "was",
    "were",
    "be",
    "been",
    "being",
    "this",
    "that",
    "these",
    "those",
    "your",
    "you",
    "their",
    "they",
    "with",
    "from",
    "about",
    "tell",
}

# =================================
# RELEVANCE SETTINGS
# =================================

MIN_RELEVANCE_SCORE = 0.25


# =================================
# COSINE SIMILARITY
# =================================


def cosine_similarity(vector_a, vector_b):

    dot_product = sum(a * b for a, b in zip(vector_a, vector_b))

    magnitude_a = math.sqrt(sum(a * a for a in vector_a))
    magnitude_b = math.sqrt(sum(b * b for b in vector_b))

    if magnitude_a == 0 or magnitude_b == 0:
        return 0.0

    return dot_product / (magnitude_a * magnitude_b)


# =================================
# TEXT TOKENIZATION
# =================================


def tokenize(text):

    words = re.findall(r"\b[a-zA-Z0-9]+\b", text.lower())

    return {word for word in words if word not in STOP_WORDS}


# =================================
# KEYWORD SIMILARITY
# =================================


def keyword_similarity(query, chunk):

    query_words = tokenize(query)
    chunk_words = tokenize(chunk)

    if not query_words:
        return 0.0

    matching_words = query_words.intersection(chunk_words)

    return len(matching_words) / len(query_words)


# =================================
# RETRIEVE RELEVANT CHUNKS
# =================================


def retrieve_relevant_chunks(
    query, chunks, chunk_embeddings=None, top_k=4, min_score=MIN_RELEVANCE_SCORE
):

    if not chunks:
        return []

    # Generate or reuse document embeddings

    if chunk_embeddings is None:
        chunk_embeddings = generate_embeddings(chunks, task_type="RETRIEVAL_DOCUMENT")

    # Generate query embedding separately

    query_embedding = generate_embeddings([query], task_type="RETRIEVAL_QUERY")[0]

    if len(chunk_embeddings) != len(chunks):
        raise ValueError("Number of chunk embeddings does not match number of chunks.")

    results = []

    # Calculate scores

    for chunk, chunk_embedding in zip(chunks, chunk_embeddings):

        semantic_score = cosine_similarity(query_embedding, chunk_embedding)

        keyword_score = keyword_similarity(query, chunk)

        final_score = 0.35 * semantic_score + 0.65 * keyword_score

        results.append(
            {
                "text": chunk,
                "semantic_score": semantic_score,
                "keyword_score": keyword_score,
                "score": final_score,
            }
        )

    # Rank results

    results.sort(key=lambda item: item["score"], reverse=True)

    # Reject irrelevant chunks

    relevant_results = [result for result in results if result["score"] >= min_score]

    return relevant_results[:top_k]
