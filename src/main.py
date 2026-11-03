"""
Command line runner for the Music Recommender Simulation.

This file helps you quickly run and test your recommender.

You will implement the functions in recommender.py:
- load_songs
- score_song
- recommend_songs
"""

from recommender import load_songs, recommend_songs


def main() -> None:
    songs = load_songs("data/songs.csv") 

    # Starter example profile
    # user_prefs = {"genre": "pop", "mood": "happy", "energy": 0.8}
    user_prefs = {"genre": "pop",
                     "mood": "sad",
                     "energy": 0.4,
                     "valence": 0.2,
                     "danceability": 0.3,
                     "acousticness": 0.8,
                     "tempo": 65
    }

    # print(songs)

    recommendations = recommend_songs(user_prefs, songs, k=5)

    print("\n" + "=" * 50)
    print("TOP RECOMMENDATIONS")
    print("=" * 50)
    for rank, (song, score, explanation) in enumerate(recommendations, start=1):
        print(f"\n{rank}. {song['title']} (by {song['artist']})")
        print(f"   Score:   {score:.2f}")
        reasons = explanation if explanation else "no strong matches"
        print(f"   Reasons: {reasons}")
    print("\n" + "=" * 50 + "\n")


if __name__ == "__main__":
    main()
