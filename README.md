# 🎵 Music Recommender Simulation

## Project Summary

In this project you will build and explain a small music recommender system.

Your goal is to:

- Represent songs and a user "taste profile" as data
- Design a scoring rule that turns that data into recommendations
- Evaluate what your system gets right and wrong
- Reflect on how this mirrors real world AI recommenders

Replace this paragraph with your own summary of what your version does.

---

## How The System Works

Explain your design in plain language.

Some prompts to answer:

- What features does each `Song` use in your system
  - For example: genre, mood, energy, tempo
- What information does your `UserProfile` store
- How does your `Recommender` compute a score for each song
- How do you choose which songs to recommend

You can include a simple diagram or bullet list if helpful.

**Real world song suggestions**

In the real world, streaming platforms use a combination of collaborative filtering(CF) and content-based filtering(CBF) to recommend songs that a user might enjoy based on what they are currently playing. If a user's song matches other users, CF assumes that this user might like what those other users are listening to. On the other side, CBF uses the song's metadata such ask mood, genre, danceability to recommend songs that closely align with the user's preferences. A combination of these cast a wide net for recommendations to a user.

**My design**

My recommender uses pure content-based filtering: it compares each song's audio features against the user's preferred values and scores how close the match is, rather than looking at what other users listened to. Each numeric feature gets its own distance-based score between 0 and 1, these are combined into a weighted total, and then a genre or mood match adds a small bonus on top. This keeps the scoring rule (how good is this one song for this user) separate from the ranking rule (sort all scored songs and return the top N).

- **Features used**: `energy`, `valence`, `danceability`, `acousticness`, and `tempo_bpm` (normalized), compared against the user's preferred value for each.
- **Scoring formula per feature**: `score = 1 - |song_value - user_preference|`, since these features already sit on a 0–1 scale.
- **Tempo scoring**: `tempo_bpm` isn't 0–1, so it's normalized by the catalog's range first: `score = 1 - |song_tempo - user_preferred_tempo| / (max_tempo - min_tempo)`.
- **Total score**: a weighted sum of the five feature scores, `total_score = w1*score_energy + w2*score_valence + w3*score_danceability + w4*score_acousticness + w5*score_tempo`, with weights summing to 1.0 so the base score stays interpretable as a 0–1 similarity.
- **Genre and mood bonuses**: a flat `+0.15` is added if `genre` matches the user's preference, and `+0.05` if `mood` matches. Genre is weighted higher than mood because it reflects a more stable, long-term taste signal, while mood is more situational.
- **Final score is clamped** at 1.0 so it stays readable as a similarity percentage even after bonuses are added.
- **Ranking**: once every song has a final score, songs are sorted in descending order and the top N are returned as recommendations.

**Algorithm Recipe**


---

## Getting Started

### Setup

1. Create a virtual environment (optional but recommended):

   ```bash
   python -m venv .venv
   source .venv/bin/activate      # Mac or Linux
   .venv\Scripts\activate         # Windows
   ```
2. Install dependencies

```bash
pip install -r requirements.txt
```

3. Run the app:

```bash
python -m src.main
```

### Running Tests

Run the starter tests with:

```bash
pytest
```

You can add more tests in `tests/test_recommender.py`.

---

## Sample Recommendation Output

Paste a sample of your recommender's output here as a text block so a reader can see what it produces:

```
# e.g.:
# User profile: genre=indie, mood=chill, energy=low
# Recommendations:
#   1. ...
#   2. ...
#   3. ...
```

**Screenshot or video** *(optional)*:

---

## Experiments You Tried

Use this section to document the experiments you ran. For example:

- What happened when you changed the weight on genre from 2.0 to 0.5
- What happened when you added tempo or valence to the score
- How did your system behave for different types of users

---

## Limitations and Risks

Summarize some limitations of your recommender.

Examples:

- It only works on a tiny catalog
- It does not understand lyrics or language
- It might over favor one genre or mood

You will go deeper on this in your model card.

---

## Reflection

Read and complete `model_card.md`:

[**Model Card**](model_card.md)

Write 1 to 2 paragraphs here about what you learned:

- about how recommenders turn data into predictions
- about where bias or unfairness could show up in systems like this
