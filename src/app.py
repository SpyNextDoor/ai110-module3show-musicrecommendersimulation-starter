"""
Streamlit web interface for the Music Recommender Simulation.

Reuses the same recommend_songs / generate_explanation pipeline as main.py,
just with a browser UI instead of printed CLI output.
"""

import os

import streamlit as st

from recommender import load_songs, recommend_songs
from retrieval import KnowledgeBase
from explain import generate_explanation

SONGS_DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data", "songs.csv")

PRESET_PROFILES = {
    "Custom": None,
    "High-Energy Pop": {
        "genre": "pop", "mood": "happy", "energy": 0.9, "valence": 0.85,
        "danceability": 0.9, "acousticness": 0.1, "tempo": 128,
    },
    "Chill Lofi": {
        "genre": "lofi", "mood": "relaxed", "energy": 0.2, "valence": 0.5,
        "danceability": 0.3, "acousticness": 0.7, "tempo": 75,
    },
    "Deep Intense Rock": {
        "genre": "rock", "mood": "intense", "energy": 0.95, "valence": 0.4,
        "danceability": 0.4, "acousticness": 0.05, "tempo": 150,
    },
}


@st.cache_resource
def get_knowledge_base() -> KnowledgeBase:
    return KnowledgeBase()


@st.cache_data
def get_songs():
    return load_songs(SONGS_DATA_DIR)


def main() -> None:
    st.set_page_config(page_title="Music Recommender", page_icon="🎵", layout="centered")
    st.title("🎵 Music Recommender")
    st.caption("RAG-grounded song recommendations with AI-generated explanations.")

    if not os.environ.get("ANTHROPIC_API_KEY"):
        st.info("No ANTHROPIC_API_KEY set — explanations will use the deterministic fallback.", icon="ℹ️")

    preset_name = st.selectbox("Start from a preset profile", list(PRESET_PROFILES.keys()))
    preset = PRESET_PROFILES[preset_name] or {}

    with st.form("preferences"):
        col1, col2 = st.columns(2)
        with col1:
            genre = st.text_input("Favorite genre", preset.get("genre", ""))
            mood = st.text_input("Favorite mood", preset.get("mood", ""))
            tempo = st.number_input("Preferred tempo (BPM)", 0, 300, int(preset.get("tempo", 120)))
        with col2:
            energy = st.slider("Energy", 0.0, 1.0, float(preset.get("energy", 0.5)))
            valence = st.slider("Valence (positivity)", 0.0, 1.0, float(preset.get("valence", 0.5)))
            danceability = st.slider("Danceability", 0.0, 1.0, float(preset.get("danceability", 0.5)))
            acousticness = st.slider("Acousticness", 0.0, 1.0, float(preset.get("acousticness", 0.5)))

        k = st.slider("Number of recommendations", 1, 10, 5)
        submitted = st.form_submit_button("Get recommendations")

    if not submitted:
        return

    user_prefs = {
        "genre": genre, "mood": mood, "energy": energy, "valence": valence,
        "danceability": danceability, "acousticness": acousticness, "tempo": tempo,
    }
    user_prefs = {k_: v for k_, v in user_prefs.items() if v not in ("", None)}

    songs = get_songs()
    kb = get_knowledge_base()
    recommendations = recommend_songs(user_prefs, songs, k=k)

    st.subheader("Your profile")
    st.json(user_prefs)

    st.subheader("Top recommendations")
    for rank, (song, score, reasons) in enumerate(recommendations, start=1):
        with st.container(border=True):
            st.markdown(f"**{rank}. {song['title']}** — {song['artist']}")
            st.progress(min(max(score, 0.0), 1.0), text=f"Score: {score:.2f}")
            st.caption(f"Reasons: {reasons or 'no strong matches'}")

            with st.spinner("Generating explanation..."):
                result = generate_explanation(kb, user_prefs, song, score, reasons)

            tag = "🤖 LLM" if result.used_llm else "📋 Fallback"
            if result.used_llm and not result.grounded:
                tag += " (ungrounded, reverted to fallback)"
            st.markdown(f"_{tag}:_ {result.text}")


if __name__ == "__main__":
    main()
