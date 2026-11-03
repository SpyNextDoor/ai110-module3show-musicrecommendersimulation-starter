# 🎧 Model Card: Music Recommender Simulation

## 1. Model Name

**MusiMist 1.0**

---

## 2. Intended Use

MusiMist takes a listener's stated preferences (favorite genre, favorite mood, a target energy level, and whether they like acoustic tracks) and ranks a fixed catalog of songs to surface the ones that best match that taste. It returns a top-k list (default 5) along with a short, human-readable reason for each pick, such as "energy match, genre match."

It assumes the user can describe their taste as a small set of simple preferences rather than a rich listening history — there is no collaborative filtering, no learning from skips/likes over time, and no account for songs the user has already heard. This is a classroom exploration project (CodePath AI110), not a production recommender: the catalog is small and synthetic, and the scoring logic is meant to demonstrate how a simple, explainable content-based scoring system works rather than to compete with real-world streaming recommenders.

---

## 3. How the Model Works

Think of every song as having a handful of dials: how energetic it is, how positive/upbeat it feels (valence), how danceable it is, how acoustic it is, and its tempo. The user also sets those same dials for the "vibe" they want, plus two extra preferences: a favorite genre and a favorite mood.

For each song, the model compares the song's dial settings to the user's dial settings, one dial at a time. The closer a song's value is to what the user asked for, the more points that dial earns — a perfect match earns full points, and the points shrink the further apart they are. Each dial doesn't count equally: energy matters most, valence and danceability matter a medium amount, and acousticness and tempo matter somewhat less. These weighted dial scores are added together to get a base score between 0 and 1.

On top of that, the song gets a bonus if its genre exactly matches the user's favorite genre, and a smaller bonus if its mood matches the user's favorite mood. The final score is capped between 0 and 1, and whenever a dial or bonus lines up closely, the model jots down a plain-language reason (like "tempo match" or "genre match") so the recommendation can be explained, not just ranked.

Once every song in the catalog has a score, the model sorts them from highest to lowest and returns the top k as the recommendations.

What changed from the starter logic: the starter code only had empty placeholders (`recommend` returned the first k songs with no scoring, and `explain_recommendation` returned a static placeholder string). The scoring was implemented from scratch as the `score_song` function — weighted similarity on energy/valence/danceability/acousticness/tempo, plus genre and mood bonuses — and `recommend_songs` was added to score the whole catalog, sort it, and attach a reasons string to each result.

---

## 4. Data

The catalog (`data/songs.csv`) contains 30 songs, each with a title, artist, genre, mood, and numeric attributes (energy, tempo, valence, danceability, acousticness).

Genres represented include afrobeats, ambient, bossa nova, choral, classical, country, edm, experimental, folk, gospel, hip hop, indie pop, jazz, k-pop, lofi, metal, neo-soul, pacific fusion, pop, r&b, reggae, reggaeton, rock, soul, synthwave, trap, and world fusion. Moods include anxious, chill, confident, dreamy, energetic, euphoric, focused, happy, hopeful, intense, jubilant, melancholic, moody, nostalgic, peaceful, playful, rebellious, relaxed, romantic, sensual, somber, tense, tranquil, triumphant, uplifting, and wistful.

I added roughly 20 additional songs and a sample user profile to the original starter catalog, broadening the mix of genres and moods beyond what was initially provided. Since it's a hand-built, 30-song dataset, musical taste is still thinly represented — there's only one or two songs per genre/mood combination, no real listener data (play counts, skip rates, lyrics, language, or regional popularity), and no way to capture tastes that blend multiple genres or moods at once.

---

## 5. Strengths

The model works best for listeners who can state a clear, single "vibe" — a target energy level plus one favorite genre and mood — since the weighted scoring is built around rewarding closeness to one target, not balancing multiple competing tastes. For these straightforward profiles, the top recommendations consistently match the requested genre and energy level, and the reasons list makes it easy to verify the score "makes sense" (e.g., a high-energy edm fan with a dance preference reliably gets high-energy, danceable tracks near the top).

The feature-similarity math (1 minus the absolute difference) captures the intuitive pattern that "closer is better" smoothly, rather than treating matches as all-or-nothing, so songs that are close-but-not-exact on energy or tempo still rank reasonably rather than being thrown out. The genre and mood bonuses also correctly boost songs that are an exact match without overwhelming the underlying feature similarity.

---

## 6. Limitations and Bias

The model only considers the five numeric features plus genre and mood — it has no notion of artist familiarity, lyrical content, language, popularity, or release era, so it can't account for a listener who cares about those things. Genres and moods with only one or two songs in the catalog (e.g., choral, pacific fusion, world fusion) are underrepresented, so a user whose favorite genre is one of these has very few candidates to be recommended regardless of how well they'd otherwise match.

Because genre and mood matches are flat bonuses, a user who sets a favorite genre can end up with recommendations that all share that one genre even when the underlying feature values (energy, valence, etc.) are a mediocre fit — the model can overfit to the genre/mood preference and under-weight the "vibe" dials. The fixed feature weights (energy weighted highest) also mean the model implicitly favors users whose taste happens to hinge on energy and valence over users whose taste is more about acousticness or tempo, since those features count for less in the total score regardless of the individual listener's priorities.

---

## 7. Evaluation

I tested a few user profiles by hand: a high-energy dance-pop fan (high target energy, danceability-leaning, genre "pop"), a mellow acoustic listener (low target energy, `likes_acoustic=True`, genre "folk" or "jazz"), and a mood-driven listener (favorite mood "chill" or "melancholic" with no strong genre preference). For each, I checked that the top-5 results had the requested genre/mood appearing near the top, that the reasons string lined up with the score (e.g., songs flagged with "energy match" did have energy close to the target), and that scores were sorted correctly from highest to lowest.

What stood out was how much the flat genre/mood bonuses can override close-but-imperfect feature matches — a song with a matching genre but middling energy/valence fit could still outrank a non-matching-genre song with an almost-perfect feature fit, which shows the bonus weights (0.15 genre, 0.05 mood) have real influence on ranking order, not just a tiebreaker effect. No formal numeric metrics (precision/recall, etc.) were computed, since there's no ground-truth "correct" ranking to compare against — evaluation was done by spot-checking plausibility.

---

## 8. Future Work

Future versions could let users weight their own preferences (e.g., "I care more about mood than genre") instead of using one fixed set of feature weights for everyone. The explanation reasons could be made richer — e.g., stating by how much a feature matched, or ranking which factor contributed most to the score — rather than a flat list of matched feature names.

To improve diversity among the top results, the model could penalize recommending multiple songs from the same artist or genre in the same top-k list, or re-rank for variety after initial scoring. It could also support more complex, multi-dimensional tastes, such as blending two favorite genres or moods, or inferring preferences from a short list of songs the user already likes rather than requiring explicit dial values.

---

## 9. Personal Reflection

Prior to this project, I did not know anything about music recommendation which I believe might be the same logic with movie recommations. I learned that you can either use songs that the user share with a wider audience or just base on the metadata of those they listen to. I now know why spotify suggest the songs that I listen to. But how do streaming softwares know how to balance CF and CBF?
