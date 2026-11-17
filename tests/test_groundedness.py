from src.groundedness import build_allowed_vocab, score_groundedness
from src.retrieval import Document

SONG = {"title": "Midnight Coding", "artist": "LoRoom", "genre": "lofi", "mood": "chill"}
USER_PREFS = {"genre": "lofi", "mood": "chill"}
REASONS = "energy match, genre match"
CONTEXT_DOCS = [
    Document(doc_id="genre:lofi", doc_type="genre", key="lofi",
             text="Lo-fi leans on warm, imperfect production, mellow tempos, and high acousticness."),
]


def test_grounded_explanation_scores_high():
    vocab = build_allowed_vocab(SONG, USER_PREFS, [REASONS], CONTEXT_DOCS)
    explanation = "This lofi track by LoRoom matches your preference for a chill, mellow mood with its warm production."
    score = score_groundedness(explanation, vocab)
    assert score >= 0.6


def test_fabricated_explanation_scores_low():
    vocab = build_allowed_vocab(SONG, USER_PREFS, [REASONS], CONTEXT_DOCS)
    explanation = (
        "This song was recorded live in Tokyo in 1998 and features a saxophone solo "
        "from a famous jazz legend who later won a Grammy for unrelated work."
    )
    score = score_groundedness(explanation, vocab)
    assert score < 0.6
