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

1. Start with every song in the catalog — no pre-filtering.
2. For each numeric feature, compute a per-feature score (distance-based, normalized for tempo).
3. Combine into a weighted base score (weights sum to 1.0).
4. Apply genre (+0.15) and mood (+0.05) bonuses.
5. Clamp the final score to a max of 1.0 (and min of 0.0, to be safe).
6. Rank all songs by final score, descending.
7. **Tie-breaking** (when two songs have the same final score):
   * Prefer the song whose `genre` matches the user's preferred genre.
   * If still tied, prefer the song whose `energy` is closer to the user's preferred energy (smaller `abs(song_energy - user_energy)` wins).
8. Return the top N songs as the recommendation list.
9. **NB: Bias** --> my design prioritizes genre because mood is something that changes, but listeners are usually committed to a particular genre.

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
==================================================
TOP RECOMMENDATIONS
==================================================

1. Requiem for Dawn (by Dmitri Volkov)
   Score:   0.90
   Reasons: energy match, valence match, danceability match, acousticness match, tempo match

2. Tears in the Hallway (by Keisha Johnson)
   Score:   0.89
   Reasons: energy match, valence match, tempo match

3. Emerald Hills (by Siobhan O'Malley)
   Score:   0.87
   Reasons: energy match, danceability match, acousticness match, tempo match

4. Focus Flow (by LoRoom)
   Score:   0.84
   Reasons: energy match, acousticness match, tempo match

5. Dust Road Letters (by Marcus Bellweather)
   Score:   0.84
   Reasons: energy match, acousticness match

==================================================
```

**Screenshot or video** *(optional)*:

---

## System Evaluation: Multiple User Profiles

`src/main.py` now defines a `USER_PROFILES` dict with three distinct "normal" taste profiles plus four adversarial / edge-case profiles designed to see if the scoring logic in `score_song` could be tricked or produce unexpected results. The adversarial profiles were suggested by asking an AI coding assistant (given `recommender.py` and `main.py` for context) to propose edge cases likely to break a weighted-similarity scorer like this one: conflicting signals, out-of-range inputs, missing data, and values that don't exist in the catalog.

Running `PYTHONPATH=src python src/main.py` from the project root produces the following output for all seven profiles:

### High-Energy Pop (normal)

```
==================================================
TOP RECOMMENDATIONS — High-Energy Pop
==================================================
Profile: {'genre': 'pop', 'mood': 'happy', 'energy': 0.9, 'valence': 0.85, 'danceability': 0.9, 'acousticness': 0.1, 'tempo': 128}

1. Sunrise City (by Neon Echo)
   Score:   1.00
   Reasons: energy match, valence match, danceability match, acousticness match, tempo match, genre match, mood match

2. Gym Hero (by Max Pulse)
   Score:   1.00
   Reasons: energy match, valence match, danceability match, acousticness match, tempo match, genre match

3. Pulse Horizon (by Kai Nakamura)
   Score:   0.97
   Reasons: energy match, valence match, danceability match, acousticness match, tempo match

4. Rooftop Lights (by Indigo Parade)
   Score:   0.94
   Reasons: energy match, valence match, danceability match, tempo match, mood match

5. Lagos Nights (by Ngozi Adeyemi)
   Score:   0.94
   Reasons: energy match, valence match, danceability match, acousticness match, tempo match

==================================================
```

### Chill Lofi (normal)

```
==================================================
TOP RECOMMENDATIONS — Chill Lofi
==================================================
Profile: {'genre': 'lofi', 'mood': 'relaxed', 'energy': 0.2, 'valence': 0.5, 'danceability': 0.3, 'acousticness': 0.7, 'tempo': 75}

1. Midnight Coding (by LoRoom)
   Score:   1.00
   Reasons: valence match, acousticness match, tempo match, genre match

2. Library Rain (by Paper Lanterns)
   Score:   1.00
   Reasons: energy match, valence match, tempo match, genre match

3. Focus Flow (by LoRoom)
   Score:   0.99
   Reasons: valence match, acousticness match, tempo match, genre match

4. Still Waters (by Mei Lin Zhao)
   Score:   0.91
   Reasons: energy match, valence match, danceability match, tempo match

5. Emerald Hills (by Siobhan O'Malley)
   Score:   0.91
   Reasons: energy match, valence match, danceability match, tempo match

==================================================
```

### Deep Intense Rock (normal)

```
==================================================
TOP RECOMMENDATIONS — Deep Intense Rock
==================================================
Profile: {'genre': 'rock', 'mood': 'intense', 'energy': 0.95, 'valence': 0.4, 'danceability': 0.4, 'acousticness': 0.05, 'tempo': 150}

1. Storm Runner (by Voltline)
   Score:   1.00
   Reasons: energy match, valence match, acousticness match, tempo match, genre match, mood match

2. Iron Reckoning (by Bjorn Eriksson)
   Score:   0.93
   Reasons: energy match, valence match, danceability match, acousticness match, tempo match

3. Shadow Walk (by Tyrese Banks)
   Score:   0.85
   Reasons: energy match, valence match, acousticness match, tempo match

4. Gym Hero (by Max Pulse)
   Score:   0.85
   Reasons: energy match, acousticness match, tempo match, mood match

5. Night Drive Loop (by Neon Echo)
   Score:   0.78
   Reasons: valence match

==================================================
```

### Adversarial: Conflicting Energy/Mood

High `energy` (0.9) paired with `mood: "sad"` — a combination that shouldn't really occur together. Result: the model happily recommends high-energy, low-valence/low-mood-match songs near the top, since energy/valence/danceability dominate the weighted score and the small mood bonus (+0.05) isn't enough to pull in genuinely "sad-feeling" tracks. The system doesn't notice or flag the internal contradiction in the user's own preferences — it just optimizes the numbers it's given.

```
==================================================
TOP RECOMMENDATIONS — Adversarial: Conflicting Energy/Mood
==================================================
Profile: {'genre': 'pop', 'mood': 'sad', 'energy': 0.9, 'valence': 0.1, 'danceability': 0.85, 'acousticness': 0.05, 'tempo': 140}

1. Gym Hero (by Max Pulse)
   Score:   0.99
   Reasons: energy match, danceability match, acousticness match, tempo match, genre match

2. Sunrise City (by Neon Echo)
   Score:   0.92
   Reasons: energy match, danceability match, acousticness match, genre match

3. Shadow Walk (by Tyrese Banks)
   Score:   0.89
   Reasons: energy match, danceability match, acousticness match, tempo match

4. Storm Runner (by Voltline)
   Score:   0.86
   Reasons: energy match, acousticness match, tempo match

5. Iron Reckoning (by Bjorn Eriksson)
   Score:   0.85
   Reasons: energy match, acousticness match

==================================================
```

### Adversarial: Out-of-Range Values

Values outside the expected 0–1 scale (`energy: 1.5`, `valence: -0.3`, `danceability: 2.0`) and a `tempo` of 999 (far beyond the catalog's real range). Nothing in `score_song` validates or clamps these *inputs* before computing `1 - abs(song_value - user_value)`, so individual feature scores go negative and the final clamp (`max(0.0, min(1.0, total))`) floors nearly every song to **0.00**. Once everyone is tied at 0.00, the ranking falls back to whatever order `sorted()` happens to preserve (insertion order from the CSV), **not** the genre/energy tie-break described in "How The System Works" — that tie-break logic isn't actually implemented in `recommend_songs`, so this edge case exposes a gap between the documented design and the code.

```
==================================================
TOP RECOMMENDATIONS — Adversarial: Out-of-Range Values
==================================================
Profile: {'genre': 'edm', 'mood': 'euphoric', 'energy': 1.5, 'valence': -0.3, 'danceability': 2.0, 'acousticness': 0.0, 'tempo': 999}

1. Sunrise City (by Neon Echo)
   Score:   0.00
   Reasons: no strong matches

2. Midnight Coding (by LoRoom)
   Score:   0.00
   Reasons: no strong matches

3. Storm Runner (by Voltline)
   Score:   0.00
   Reasons: acousticness match

4. Library Rain (by Paper Lanterns)
   Score:   0.00
   Reasons: no strong matches

5. Gym Hero (by Max Pulse)
   Score:   0.00
   Reasons: acousticness match

==================================================
```

### Adversarial: Empty Preferences

An empty `{}` preferences dict — no genre, mood, or numeric targets at all. Every `if feature not in user_prefs` / `if "genre" in user_prefs` check short-circuits, so `total` stays `0.0` for *every* song and the "recommendations" are really just the first 5 rows of the CSV in file order. The system never tells the caller "I have nothing to go on" — it silently returns a confident-looking top-5 list with a score of 0.00, which could easily be mistaken for a real result if a caller doesn't check the score.

```
==================================================
TOP RECOMMENDATIONS — Adversarial: Empty Preferences
==================================================
Profile: {}

1. Sunrise City (by Neon Echo)
   Score:   0.00
   Reasons: no strong matches

2. Midnight Coding (by LoRoom)
   Score:   0.00
   Reasons: no strong matches

3. Storm Runner (by Voltline)
   Score:   0.00
   Reasons: no strong matches

4. Library Rain (by Paper Lanterns)
   Score:   0.00
   Reasons: no strong matches

5. Gym Hero (by Max Pulse)
   Score:   0.00
   Reasons: no strong matches

==================================================
```

### Adversarial: Unknown Genre/Mood

A `genre`/`mood` that doesn't exist anywhere in the catalog (`"death-polka"`, `"ecstatic-fear"`). The genre/mood bonus terms simply never fire (no row's `genre`/`mood` string can equal them), so the ranking degrades gracefully to pure feature-similarity on energy/valence/danceability/acousticness/tempo. This is actually the most "robust" of the adversarial cases — unlike the out-of-range or empty-dict cases, it still produces a sensible, differentiated ranking, because the numeric comparisons never depended on genre/mood existing in the first place.

```
==================================================
TOP RECOMMENDATIONS — Adversarial: Unknown Genre/Mood
==================================================
Profile: {'genre': 'death-polka', 'mood': 'ecstatic-fear', 'energy': 0.5, 'valence': 0.5, 'danceability': 0.5, 'acousticness': 0.5, 'tempo': 110}

1. Dust Road Letters (by Marcus Bellweather)
   Score:   0.91
   Reasons: energy match, valence match, danceability match

2. Monsoon Heart (by Priya Nair)
   Score:   0.89
   Reasons: energy match, danceability match, acousticness match

3. Tears in the Hallway (by Keisha Johnson)
   Score:   0.88
   Reasons: energy match, valence match, danceability match, acousticness match

4. Midnight Coding (by LoRoom)
   Score:   0.87
   Reasons: energy match, valence match, danceability match

5. Velvet Hours (by Jamal Whitfield)
   Score:   0.86
   Reasons: energy match, danceability match, acousticness match

==================================================
```

**Takeaway**: the scoring function trusts its inputs completely — it has no input validation/clamping, no detection of self-contradictory preferences, and no real fallback when preferences are empty. The two most "trickable" cases were out-of-range values (collapses nearly everything to a 0.00 tie, falling back to silent insertion-order ranking instead of the documented tie-break rule) and empty preferences (returns a confident-looking but meaningless top-5). This is documented further in `model_card.md` under Limitations and Bias.

---

## Experiments You Tried

### Sensitivity Test: Weight Shift (energy doubled, genre bonus halved)

**Change made** (in `src/recommender.py`): doubled `energy`'s importance from `0.30` to `0.60` relative to the other four features, then renormalized all five `FEATURE_WEIGHTS` so they still sum to `1.0` (validity check — the base score has to stay a 0–1 similarity before bonuses are added, and the final clamp still floors/ceilings it to `[0, 1]`):

```python
FEATURE_WEIGHTS = {
    "energy": 0.4615,       # was 0.30
    "valence": 0.1538,      # was 0.20
    "danceability": 0.1538, # was 0.20
    "acousticness": 0.1154, # was 0.15
    "tempo": 0.1154,        # was 0.15
}
GENRE_BONUS = 0.075  # was 0.15 (halved)
MOOD_BONUS = 0.05    # unchanged
```

I asked my AI coding assistant to make this exact change and verify the weights still summed to ~1.0 and that no score could land outside `[0, 1]` — it confirmed the renormalized weights sum to `0.9999` (rounding) and that the existing `max(0.0, min(1.0, total))` clamp still handles the genre/mood bonuses pushing the total slightly over 1.0, so the math stays valid.

**Result after re-running `src/main.py`:**

- **High-Energy Pop / Deep Intense Rock** (profiles where the user's target energy was already extreme, 0.9–0.95): the #1 and #2 picks barely moved, since those songs were already near-perfect on every dial. But further down the list, songs that matched on energy but were weaker on the now-devalued genre bonus started displacing songs that previously won mostly on genre — e.g., in Deep Intense Rock, `Pulse Horizon` (an energy-heavy, non-rock track) pushed into the #5 slot by displacing `Night Drive Loop`.
- **Chill Lofi** (a *low*-energy profile): scores dropped across the board (1.00 → 0.93 for the top pick) because energy now dominates the base score, but this profile's *target* energy is `0.2`, and no song is a perfect `energy == 0.2` match — so inflating energy's weight amplifies small energy mismatches instead of rewarding anything. The ranking also reshuffled: `Still Waters` and `Noche Eterna`-style energy-close tracks climbed, while genre-matching lofi tracks like `Focus Flow` slipped from #3 to #4.
- **Adversarial: Conflicting Energy/Mood**: results got *more* skewed toward energy, not less — with genre's bonus halved, the already-dominant high-energy/low-valence tracks became even more entrenched at the top, since there was less of a genre-match counterweight to pull in anything else.
- **Adversarial: Out-of-Range / Empty Preferences**: unchanged — these cases already collapse to a 0.00 tie regardless of how the weights are distributed, since the clamp floors everything before the weight ratios matter.

**Was it more accurate or just different?** Mostly just *different*, not more accurate — and for one profile, arguably worse. Doubling energy's weight makes the system better at scoring profiles that *want* high energy (it rewards near-perfect energy matches even more strongly), but it actively hurts low-energy profiles like Chill Lofi: it punishes small, inevitable gaps between a song's energy and a target like `0.2` harder than before, pulling the ranking away from genre-consistent picks. This confirms the model card's existing bias note — fixed feature weights implicitly favor users whose taste "hinges on energy," and this experiment made that bias measurably stronger rather than fixing it. A per-user weighting scheme (letting the user say "I care more about mood/genre than energy") would be a better fix than any single global weight change.

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
