# 🎧 Model Card: Music Recommender Simulation

## 1. Model Name

**MusiMist 1.0**

---

## 2. Goal / Task

MusiMist ranks a fixed song catalog for a listener. The listener gives a few preferences: favorite genre, favorite mood, target energy level, and whether they like acoustic tracks. The model scores every song against those preferences. It returns the top-k matches (default 5), each with a short reason like "energy match, genre match."

It does not predict future listens or learn from behavior. It only ranks the catalog it already has, based on the preferences given in that moment.

---

## 3. Data Used

The catalog is `data/songs.csv`. It has 30 songs. Each song has a title, artist, genre, mood, and five numeric features: energy, tempo, valence, danceability, and acousticness.

The catalog covers 27 genres and 26 moods, including afrobeats, ambient, bossa nova, classical, edm, folk, hip hop, jazz, k-pop, lofi, pop, r&b, rock, and more. I added about 20 songs and a sample user profile to the original starter catalog.

**Limits:** With only 30 songs across so many genres and moods, most genre/mood combinations have just one or two matching songs. There's no real listener data — no play counts, skip rates, lyrics, language, or popularity. The model also can't represent a listener whose taste blends two genres or moods at once.

---

## 4. Algorithm Summary

Every song has five "dials": energy, valence, danceability, acousticness, and tempo. The listener sets target values for the same dials, plus a favorite genre and mood.

For each dial, the model checks how close the song's value is to the listener's target. A perfect match earns full points; the score shrinks as the gap grows. Dials don't count equally — energy matters most, valence and danceability matter a medium amount, and acousticness and tempo matter less. Adding up the weighted dials gives a base score from 0 to 1.

On top of that, a song gets a bonus if its genre matches the listener's favorite genre, and a smaller bonus if its mood matches. The final score is capped at 0–1. Whenever a dial or bonus lines up closely, the model records a plain-language reason (like "tempo match") so each pick can be explained.

The model scores the whole catalog, sorts it high to low, and returns the top k.

---

## 5. Observed Behavior / Biases

**Mood barely matters.** Mood is worth only a small +0.05 bonus, while the five numeric dials make up most of the score. For example, "Gym Hero" (mood: intense) tied for the #1 pick for a listener who asked for mood "happy," just because its energy, danceability, and tempo were a near-perfect fit. Mood acts more like a tie-breaker than a real filter.

**Genre can crowd out fit.** Because genre match is a flat bonus, results can skew toward one genre even when the underlying dials are a mediocre fit for that listener.

**Fixed weights favor energy-driven tastes.** Since energy is weighted highest, listeners whose taste hinges on tempo or acousticness are underserved relative to listeners whose taste hinges on energy and valence.

**Underrepresented genres get thin results.** Genres with only one or two songs (e.g., choral, pacific fusion, world fusion) can't produce a strong top-5 no matter how good the match is.

---

## 6. Evaluation Process

I tested seven user profiles through `src/main.py`: three realistic listeners (High-Energy Pop, Chill Lofi, Deep Intense Rock) and four adversarial edge cases (conflicting energy/mood, out-of-range feature values, empty preferences, and an unknown genre/mood).

For each profile, I checked three things: did the requested genre/mood show up near the top, did the listed reasons match the song's real attributes, and were scores sorted correctly.

I also compared profiles pairwise. Opposite-taste profiles (e.g., High-Energy Pop vs. Chill Lofi) shared almost no songs, which is expected. Similar-energy profiles with different genres (High-Energy Pop vs. Deep Intense Rock) overlapped somewhat but still diverged on valence, which is also expected.

Two adversarial cases broke the model the same way: out-of-range values (e.g., danceability of 2.0) and empty preferences both caused every song to score 0.00, with no warning to the user that the result was meaningless. An unknown genre/mood did not break anything — it just fell back to pure numeric similarity.

As a follow-up, I doubled energy's weight and halved the genre bonus, then re-ran all seven profiles. Energy-extreme profiles barely changed at the top. The low-energy Chill Lofi profile got worse: genre-matching lofi tracks slipped down in favor of tracks that were merely energy-closer. This confirmed the bias in Section 5 — favoring energy weighting doesn't make results more accurate, just different.

No formal metrics (precision/recall) were computed, since there's no ground-truth ranking to compare against. Evaluation was done by checking plausibility across profiles.

---

## 7. Intended Use and Non-Intended Use

**Intended use:** A classroom demo (CodePath AI110) of a simple, explainable, content-based recommender. It's meant for listeners who can state one clear "vibe" — a target energy plus one favorite genre and mood.

**Not intended for:**

- Production or commercial recommendation — the catalog is small and synthetic.
- Listeners with mixed or multi-genre tastes — the model assumes one dominant preference.
- Any input validation step — out-of-range values silently break scoring instead of raising an error.
- Modeling real listening behavior — there's no collaborative filtering and no memory of past plays or skips.

---

## 8. Ideas for Improvement

1. **Let users weight their own preferences.** Right now one fixed weight set applies to everyone. User-adjustable weights would reduce the energy bias in Section 5.
2. **Validate inputs.** Reject or clamp out-of-range values instead of silently returning a meaningless 0.00 ranking.
3. **Add diversity re-ranking.** Penalize multiple songs from the same artist or genre in one top-k list, so results don't collapse into a single narrow cluster.

---

## 9. Personal Reflection

Before this project, I didn't know much about music recommendation — it seems to share logic with movie recommendation. I learned that recommenders can use what other listeners share, or just the metadata of what one person listens to. I now understand why Spotify suggests certain songs. Open question: how do streaming services balance collaborative filtering and content-based filtering?

AI tools helped me mostly by identifying loopholes in my design, but they also suggested some complex methods I didn't necessarily need, so I consulted Google as well — for instance, AI suggested using a bell-curve for calibration, but I realized that for small differences it would ignore them, and a simple system like this didn't need that. What surprised me most was seeing the calibration method used to keep all the different metric systems standardized — I learned it in math a long time ago and was surprised to see it in action. If I extended this project, I would make sure the app isn't biased toward the type of artists in `songs.csv`, by including all genders and races, and I would add another scoring metric like lyrical content, since I personally enjoy songs with rich lyrical content even when they fall outside my usual taste.

---

## Appendix A: Sample Outputs

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

---

## Appendix B: Sensitivity Experiment — Weight Shift

To test sensitivity to the fixed weights, I doubled energy's relative weight (0.30 → 0.60 before renormalizing) and halved the genre bonus (0.15 → 0.075), then renormalized the five feature weights to sum to 1.0:

```python
FEATURE_WEIGHTS = {
    "energy": 0.4615,       # was 0.30
    "valence": 0.1538,      # was 0.20
    "danceability": 0.1538, # was 0.20
    "acousticness": 0.1154, # was 0.15
    "tempo": 0.1154,        # was 0.15
}
GENRE_BONUS = 0.075  # was 0.15 (halved)
```

Results after re-running all seven profiles:

- Energy-extreme profiles (High-Energy Pop, Deep Intense Rock) barely changed at the top, but lower ranks reshuffled as genre mattered less.
- Chill Lofi (low-energy target) got worse: genre-matching lofi tracks slipped down in favor of tracks that were merely energy-closer.
- The Conflicting Energy/Mood profile skewed more toward loud tracks, since halving the genre bonus removed one of the few counterweights.
- Out-of-Range and Empty Preferences were unaffected — they already collapse to a 0.00 tie before weight ratios matter.

**Conclusion:** the results became different, not more accurate — and arguably worse for Chill Lofi. This confirms the bias in Section 5: fixed global weights favor energy-driven tastes, and raising that weight further only sharpens the favoritism.
