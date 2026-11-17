from src.retrieval import KnowledgeBase


def test_knowledge_base_loads_all_document_types():
    kb = KnowledgeBase()
    doc_types = {doc.doc_type for doc in kb.documents}
    assert doc_types == {"song", "genre", "mood"}
    assert kb.get_by_id("genre:lofi") is not None
    assert kb.get_by_id("mood:chill") is not None


def test_retrieve_ranks_relevant_genre_note_highly():
    kb = KnowledgeBase()
    results = kb.retrieve("lofi", k=5)
    doc_ids = [doc.doc_id for doc in results]
    assert "genre:lofi" in doc_ids


def test_get_context_always_includes_the_songs_own_note():
    kb = KnowledgeBase()
    song = {"id": "5", "genre": "pop", "mood": "intense"}
    context = kb.get_context(song, user_prefs={"genre": "pop", "mood": "intense"}, k=2)
    doc_ids = [doc.doc_id for doc in context]
    assert "song:5" in doc_ids
    assert len(context) > 1
