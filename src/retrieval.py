"""
TF-IDF based retrieval over a small local knowledge base of genre, mood, and
per-song notes. This is the "R" in RAG: before an explanation is generated,
relevant text snippets are retrieved here and handed to the generator as
grounding context.
"""

import json
import logging
import os
from dataclasses import dataclass
from typing import Dict, List

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

logger = logging.getLogger(__name__)

KNOWLEDGE_DIR = os.path.join(os.path.dirname(__file__), "..", "data", "knowledge")


@dataclass
class Document:
    doc_id: str
    doc_type: str  # "song", "genre", or "mood"
    key: str
    text: str


class KnowledgeBase:
    """Loads the local note corpus and retrieves relevant documents by TF-IDF cosine similarity."""

    def __init__(self, knowledge_dir: str = KNOWLEDGE_DIR):
        self.documents: List[Document] = []
        self._by_id: Dict[str, Document] = {}
        self._load(knowledge_dir)
        self._vectorizer = TfidfVectorizer()
        self._matrix = self._vectorizer.fit_transform([doc.text for doc in self.documents])

    def _load(self, knowledge_dir: str) -> None:
        song_notes = self._read_json(os.path.join(knowledge_dir, "song_notes.json"))
        genre_notes = self._read_json(os.path.join(knowledge_dir, "genre_notes.json"))
        mood_notes = self._read_json(os.path.join(knowledge_dir, "mood_notes.json"))

        for song_id, text in song_notes.items():
            self._add_document("song", song_id, text)
        for genre, text in genre_notes.items():
            self._add_document("genre", genre.lower(), text)
        for mood, text in mood_notes.items():
            self._add_document("mood", mood.lower(), text)

        logger.info("Loaded knowledge base with %d documents", len(self.documents))

    @staticmethod
    def _read_json(path: str) -> Dict[str, str]:
        with open(path, encoding="utf-8") as f:
            return json.load(f)

    def _add_document(self, doc_type: str, key: str, text: str) -> None:
        doc = Document(doc_id=f"{doc_type}:{key}", doc_type=doc_type, key=key, text=text)
        self.documents.append(doc)
        self._by_id[doc.doc_id] = doc

    def get_by_id(self, doc_id: str) -> Document:
        return self._by_id.get(doc_id)

    def retrieve(self, query: str, k: int = 3, exclude_ids: List[str] = None) -> List[Document]:
        """Returns the top-k documents most similar to the query, by TF-IDF cosine similarity."""
        exclude_ids = set(exclude_ids or [])
        if not query.strip():
            return []

        query_vec = self._vectorizer.transform([query])
        similarities = cosine_similarity(query_vec, self._matrix)[0]

        ranked = sorted(
            enumerate(similarities), key=lambda pair: pair[1], reverse=True
        )
        results: List[Document] = []
        for idx, score in ranked:
            if score <= 0:
                break
            doc = self.documents[idx]
            if doc.doc_id in exclude_ids:
                continue
            results.append(doc)
            if len(results) >= k:
                break
        return results

    def get_context(self, song: Dict, user_prefs: Dict, k: int = 2) -> List[Document]:
        """
        Builds grounding context for one recommended song: the song's own note
        (authoritative, always included when present) plus the top semantically
        related genre/mood notes retrieved by TF-IDF similarity.
        """
        context: List[Document] = []
        seen_ids = set()

        song_doc = self.get_by_id(f"song:{song.get('id')}")
        if song_doc:
            context.append(song_doc)
            seen_ids.add(song_doc.doc_id)

        query_terms = [
            str(song.get("genre", "")),
            str(song.get("mood", "")),
            str(user_prefs.get("genre", "")),
            str(user_prefs.get("mood", "")),
        ]
        query = " ".join(term for term in query_terms if term)

        retrieved = self.retrieve(query, k=k, exclude_ids=seen_ids)
        context.extend(retrieved)
        return context
