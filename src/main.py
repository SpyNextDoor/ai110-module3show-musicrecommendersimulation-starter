"""
Command line runner for the Music Recommender Simulation.

This file helps you quickly run and test your recommender.

You will implement the functions in recommender.py:
- load_songs
- score_song
- recommend_songs
"""

import logging
import os

from recommender import load_songs, recommend_songs
from retrieval import KnowledgeBase
from explain import generate_explanation

LOG_DIR = os.path.join(os.path.dirname(__file__), "..", "logs")
os.makedirs(LOG_DIR, exist_ok=True)

file_handler = logging.FileHandler(os.path.join(LOG_DIR, "app.log"))
file_handler.setLevel(logging.INFO)
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.WARNING)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    handlers=[file_handler, console_handler],
)

USER_PROFILES = {
    "High-Energy Pop": {
        "genre": "pop",
        "mood": "happy",
        "energy": 0.9,
        "valence": 0.85,
        "danceability": 0.9,
        "acousticness": 0.1,
        "tempo": 128,
    },
    "Chill Lofi": {
        "genre": "lofi",
        "mood": "relaxed",
        "energy": 0.2,
        "valence": 0.5,
        "danceability": 0.3,
        "acousticness": 0.7,
        "tempo": 75,
    },
    "Deep Intense Rock": {
        "genre": "rock",
        "mood": "intense",
        "energy": 0.95,
        "valence": 0.4,
        "danceability": 0.4,
        "acousticness": 0.05,
        "tempo": 150,
    },
    # --- Adversarial / edge-case profiles (see "System Evaluation" in README) ---
    "Adversarial: Conflicting Energy/Mood": {
        "genre": "pop",
        "mood": "sad",
        "energy": 0.9,
        "valence": 0.1,
        "danceability": 0.85,
        "acousticness": 0.05,
        "tempo": 140,
    },
    "Adversarial: Out-of-Range Values": {
        "genre": "edm",
        "mood": "euphoric",
        "energy": 1.5,
        "valence": -0.3,
        "danceability": 2.0,
        "acousticness": 0.0,
        "tempo": 999,
    },
    "Adversarial: Empty Preferences": {},
    "Adversarial: Unknown Genre/Mood": {
        "genre": "death-polka",
        "mood": "ecstatic-fear",
        "energy": 0.5,
        "valence": 0.5,
        "danceability": 0.5,
        "acousticness": 0.5,
        "tempo": 110,
    },
}


def print_recommendations(name: str, user_prefs: dict, recommendations, kb: KnowledgeBase) -> None:
    print("\n" + "=" * 50)
    print(f"TOP RECOMMENDATIONS — {name}")
    print("=" * 50)
    print(f"Profile: {user_prefs}")
    for rank, (song, score, explanation) in enumerate(recommendations, start=1):
        print(f"\n{rank}. {song['title']} (by {song['artist']})")
        print(f"   Score:   {score:.2f}")
        reasons = explanation if explanation else "no strong matches"
        print(f"   Reasons: {reasons}")

        result = generate_explanation(kb, user_prefs, song, score, reasons)
        tag = "LLM" if result.used_llm else "fallback"
        grounded_tag = "" if result.grounded else " [UNGROUNDED, reverted to fallback]"
        print(f"   AI Explanation ({tag}{grounded_tag}): {result.text}")
    print("\n" + "=" * 50 + "\n")


def main() -> None:
    songs = load_songs("data/songs.csv")
    kb = KnowledgeBase()

    for name, user_prefs in USER_PROFILES.items():
        recommendations = recommend_songs(user_prefs, songs, k=5)
        print_recommendations(name, user_prefs, recommendations, kb)


if __name__ == "__main__":
    main()
