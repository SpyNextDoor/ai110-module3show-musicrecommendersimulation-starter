import csv
import heapq
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass

FEATURE_WEIGHTS = {
    "energy": 0.30,
    "valence": 0.20,
    "danceability": 0.20,
    "acousticness": 0.15,
    "tempo": 0.15,
}
GENRE_BONUS = 0.15
MOOD_BONUS = 0.05


@dataclass
class Song:
    """
    Represents a song and its attributes.
    Required by tests/test_recommender.py
    """
    id: int
    title: str
    artist: str
    genre: str
    mood: str
    energy: float
    tempo_bpm: float
    valence: float
    danceability: float
    acousticness: float

@dataclass
class UserProfile:
    """
    Represents a user's taste preferences.
    Required by tests/test_recommender.py
    """
    favorite_genre: str
    favorite_mood: str
    target_energy: float
    likes_acoustic: bool

class Recommender:
    """
    OOP implementation of the recommendation logic.
    Required by tests/test_recommender.py
    """
    def __init__(self, songs: List[Song]):
        self.songs = songs

    def recommend(self, user: UserProfile, k: int = 5) -> List[Song]:
        """Returns the top-k songs for the user."""
        # TODO: Implement recommendation logic
        return self.songs[:k]

    def explain_recommendation(self, user: UserProfile, song: Song) -> str:
        """Builds a human-readable explanation for why a song was recommended."""
        # TODO: Implement explanation logic
        return "Explanation placeholder"

def load_songs(csv_path: str) -> List[Dict]:
    """
    Loads songs from a CSV file.
    Required by src/main.py
    """
    with open(csv_path, newline="", encoding="utf-8") as csv_file:
        return list(csv.DictReader(csv_file))

def score_song(user_prefs: Dict, song: Dict, tempo_range: Tuple[float, float] = (60.0, 180.0)) -> Tuple[float, List[str]]:
    """
    Scores a single song against user preferences.
    Required by recommend_songs() and src/main.py
    """
    reasons: List[str] = []
    total = 0.0

    for feature in ("energy", "valence", "danceability", "acousticness"):
        if feature not in user_prefs:
            continue
        song_value = float(song[feature])
        user_value = float(user_prefs[feature])
        feature_score = 1 - abs(song_value - user_value)
        total += FEATURE_WEIGHTS[feature] * feature_score
        if feature_score >= 0.85:
            reasons.append(f"{feature} match")

    if "tempo" in user_prefs:
        min_tempo, max_tempo = tempo_range
        tempo_span = max_tempo - min_tempo or 1.0
        song_tempo = float(song["tempo_bpm"])
        user_tempo = float(user_prefs["tempo"])
        tempo_score = 1 - abs(song_tempo - user_tempo) / tempo_span
        total += FEATURE_WEIGHTS["tempo"] * tempo_score
        if tempo_score >= 0.85:
            reasons.append("tempo match")

    if "genre" in user_prefs and song["genre"].lower() == str(user_prefs["genre"]).lower():
        total += GENRE_BONUS
        reasons.append("genre match")

    if "mood" in user_prefs and song["mood"].lower() == str(user_prefs["mood"]).lower():
        total += MOOD_BONUS
        reasons.append("mood match")

    total = max(0.0, min(1.0, total))
    return total, reasons

def recommend_songs(user_prefs: Dict, songs: List[Dict], k: int = 5) -> List[Tuple[Dict, float, str]]:
    """
    Functional implementation of the recommendation logic.
    Required by src/main.py
    """
    scored = (
        (song, *score_song(user_prefs, song))
        for song in songs
    )
    ranked = sorted(scored, key=lambda item: item[1], reverse=True)[:k]
    return [(song, score, ", ".join(reasons)) for song, score, reasons in ranked]
