"""
Reliability guardrail for the RAG explanation feature.

A generated explanation is only trustworthy if its claims actually trace back
to the retrieved documents and the computed match reasons. This module scores
how "grounded" an explanation is by checking what fraction of its meaningful
words are backed by that allowed vocabulary, so a hallucinated explanation can
be caught and replaced with a safe fallback instead of shown to the user.
"""

import re
from typing import Dict, Iterable, List

_STOPWORDS = {
    "a", "an", "the", "is", "are", "was", "were", "be", "been", "being",
    "this", "that", "these", "those", "it", "its", "it's", "and", "or", "but",
    "with", "without", "to", "of", "in", "on", "for", "as", "by", "at", "from",
    "your", "you", "i", "we", "they", "he", "she", "has", "have", "had",
    "song", "track", "music", "makes", "make", "made", "fits", "fit", "well",
    "great", "good", "nice", "really", "very", "so", "also", "than", "then",
    "because", "since", "which", "who", "what", "when", "will", "would",
    "should", "could", "can", "might", "not", "no", "yes", "just", "like",
}

_WORD_RE = re.compile(r"[a-z']+")


def _tokenize(text: str) -> List[str]:
    return [w for w in _WORD_RE.findall(text.lower()) if len(w) > 2 and w not in _STOPWORDS]


def build_allowed_vocab(
    song: Dict,
    user_prefs: Dict,
    reasons: Iterable[str],
    context_docs: Iterable,
) -> set:
    """Collects every word the explanation is allowed to use: facts actually available to it."""
    vocab = set()
    for text in [
        str(song.get("title", "")),
        str(song.get("artist", "")),
        str(song.get("genre", "")),
        str(song.get("mood", "")),
        str(user_prefs.get("genre", "")),
        str(user_prefs.get("mood", "")),
        " ".join(reasons),
    ]:
        vocab.update(_tokenize(text))

    for doc in context_docs:
        vocab.update(_tokenize(doc.text))

    return vocab


def score_groundedness(explanation: str, allowed_vocab: set) -> float:
    """
    Fraction of meaningful words in the explanation that are supported by the
    allowed vocabulary. 1.0 = fully grounded, 0.0 = no overlap at all.
    An empty explanation is never grounded. One with content words but none
    checkable (e.g. only stopwords) is treated as trivially grounded.
    """
    if not explanation.strip():
        return 0.0

    tokens = _tokenize(explanation)
    if not tokens:
        return 1.0

    supported = sum(1 for token in tokens if token in allowed_vocab)
    return supported / len(tokens)


def is_grounded(explanation: str, allowed_vocab: set, threshold: float = 0.6) -> bool:
    return score_groundedness(explanation, allowed_vocab) >= threshold
