"""
RAG-powered explanation generation for recommended songs.

Pipeline: retrieve grounding documents (retrieval.py) -> generate a natural
language explanation with Claude, constrained to those documents -> check the
result is actually grounded in what was retrieved (groundedness.py) -> fall
back to a deterministic, always-safe explanation if the API is unavailable or
the generated text isn't grounded.
"""

import logging
import os
from dataclasses import dataclass, field
from typing import Dict, List

try:
    from groundedness import build_allowed_vocab, score_groundedness
    from retrieval import Document, KnowledgeBase
except ImportError:
    from src.groundedness import build_allowed_vocab, score_groundedness
    from src.retrieval import Document, KnowledgeBase

logger = logging.getLogger(__name__)

GROUNDEDNESS_THRESHOLD = 0.6
CLAUDE_MODEL = "claude-sonnet-5-5"


@dataclass
class ExplanationResult:
    text: str
    used_llm: bool
    grounded: bool
    groundedness_score: float
    sources: List[str] = field(default_factory=list)


def _deterministic_explanation(song: Dict, reasons: str) -> str:
    """Always-available fallback: no LLM, just the computed match reasons. Never fails."""
    if reasons:
        return f"Recommended based on: {reasons}."
    return "Recommended as a closest available match, though no individual feature stood out strongly."


def _build_prompt(user_prefs: Dict, song: Dict, score: float, reasons: str, context_docs: List[Document]) -> str:
    context_text = "\n".join(f"- {doc.text}" for doc in context_docs) or "(no additional notes available)"
    return (
        "You are explaining one music recommendation to a listener in 1-2 sentences.\n"
        "Only use the facts given below. Do not invent details about the song, artist, "
        "or genre that are not stated here, and do not claim things the match reasons "
        "don't support.\n\n"
        f"Song: \"{song.get('title')}\" by {song.get('artist')} "
        f"(genre: {song.get('genre')}, mood: {song.get('mood')})\n"
        f"Listener preferences: {user_prefs}\n"
        f"Computed match score: {score:.2f}\n"
        f"Computed match reasons: {reasons or 'none'}\n"
        f"Notes:\n{context_text}\n\n"
        "Write the explanation now:"
    )


def _call_claude(prompt: str) -> str:
    import anthropic

    client = anthropic.Anthropic()
    response = client.messages.create(
        model=CLAUDE_MODEL,
        max_tokens=150,
        messages=[{"role": "user", "content": prompt}],
    )
    return "".join(block.text for block in response.content if block.type == "text").strip()


def generate_explanation(
    kb: KnowledgeBase,
    user_prefs: Dict,
    song: Dict,
    score: float,
    reasons: str,
) -> ExplanationResult:
    context_docs = kb.get_context(song, user_prefs)
    sources = [doc.doc_id for doc in context_docs]
    fallback_text = _deterministic_explanation(song, reasons)

    if not os.environ.get("ANTHROPIC_API_KEY"):
        logger.info("No ANTHROPIC_API_KEY set; using deterministic explanation for song %s", song.get("id"))
        return ExplanationResult(
            text=fallback_text, used_llm=False, grounded=True, groundedness_score=1.0, sources=sources
        )

    try:
        prompt = _build_prompt(user_prefs, song, score, reasons, context_docs)
        generated_text = _call_claude(prompt)
    except Exception:
        logger.exception("Claude API call failed for song %s; falling back to deterministic explanation", song.get("id"))
        return ExplanationResult(
            text=fallback_text, used_llm=False, grounded=True, groundedness_score=1.0, sources=sources
        )

    allowed_vocab = build_allowed_vocab(song, user_prefs, [reasons], context_docs)
    groundedness = score_groundedness(generated_text, allowed_vocab)
    grounded = groundedness >= GROUNDEDNESS_THRESHOLD

    if not grounded:
        logger.warning(
            "Generated explanation for song %s failed groundedness check (score=%.2f); using fallback",
            song.get("id"), groundedness,
        )
        return ExplanationResult(
            text=fallback_text, used_llm=True, grounded=False, groundedness_score=groundedness, sources=sources
        )

    return ExplanationResult(
        text=generated_text, used_llm=True, grounded=True, groundedness_score=groundedness, sources=sources
    )
