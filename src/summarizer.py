import re

import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from src.preprocessing import clean_text


def summarize_text(text: str, max_sentences: int = 3) -> str:
    """Create an extractive TextRank summary using sentences from the notice."""
    if max_sentences < 1:
        raise ValueError("max_sentences must be at least 1.")

    cleaned = clean_text(text)
    if not cleaned:
        return ""

    sentences = [
        sentence.strip()
        for sentence in re.split(r"(?<=[.!?])\s+", cleaned)
        if sentence.strip()
    ]
    if len(sentences) <= max_sentences:
        return " ".join(sentences)

    try:
        sentence_vectors = TfidfVectorizer(stop_words="english").fit_transform(sentences)
    except ValueError:
        return " ".join(sentences[:max_sentences])

    similarities = cosine_similarity(sentence_vectors)
    np.fill_diagonal(similarities, 0.0)
    row_sums = similarities.sum(axis=1)
    transition = np.divide(
        similarities,
        row_sums[:, np.newaxis],
        out=np.zeros_like(similarities),
        where=row_sums[:, np.newaxis] != 0,
    )

    sentence_count = len(sentences)
    scores = np.full(sentence_count, 1.0 / sentence_count)
    damping = 0.85
    for _ in range(50):
        dangling_score = scores[row_sums == 0].sum() / sentence_count
        updated_scores = (1 - damping) / sentence_count + damping * (
            transition.T @ scores + dangling_score
        )
        if np.abs(updated_scores - scores).sum() < 1e-6:
            scores = updated_scores
            break
        scores = updated_scores

    selected = sorted(
        range(sentence_count),
        key=lambda index: (-float(scores[index]), index),
    )[:max_sentences]
    return " ".join(sentences[index] for index in sorted(selected))