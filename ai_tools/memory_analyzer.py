"""
Turning a memory into a world design.

Two paths, same output shape:

  Ollama path   — the local model reads the memory and picks the traits.
  Offline path  — a keyword model does it instead, when Ollama isn't running.

The offline path exists so the app is never a blank screen. It is clearly
labelled in the UI as offline; it is not pretending to be the model.
"""

import hashlib
import random
import re

from ai_tools.ollama_client import (
    OllamaBadResponse, OllamaUnavailable, generate_json, is_available,
)
from ai_tools.trait_schema import TRAIT_PROMPT_BLOCK, EXAMPLE_RESPONSE, coerce_response
from config import (
    ALLOWED_EMOTIONS, ALLOWED_FEATURES, ALLOWED_THEMES,
    EMOTION_FALLBACKS, THEME_FALLBACKS, THEME_PLANET_TYPES,
)

SOURCE_MODEL = "model"
SOURCE_OFFLINE = "offline"

# =========================================================
# PROMPTS
# =========================================================

SYSTEM_PROMPT = (
    "You are a world designer for a memory observatory. You read a personal "
    "memory and design the planet that memory would be if it were a place. "
    "Work from what the memory actually says. Do not invent events that aren't "
    "there. Prefer the quiet, specific reading over the dramatic one. "
    "Answer with a single JSON object and nothing else."
)


def _design_prompt(memory_text):
    return f"""A person wrote down this memory:

\"\"\"{memory_text}\"\"\"

Design the world it becomes.

  title             3-6 words. Concrete and a little strange. Name the place,
                    don't summarize the memory. No colons, no subtitles.
  emotion           {" | ".join(sorted(ALLOWED_EMOTIONS))}
  theme             {" | ".join(sorted(ALLOWED_THEMES))}
  planet_type       rocky | oceanic | icy | volcanic | gaseous | forest | crystalline | desert | storm
  size_class        small | medium | large | giant
  palette           exactly 3 hex colors, e.g. ["#4CC9F0", "#0077B6", "#023E8A"]
  surface_features  2-4 items, all from the allowed list below
  ring_style        none | thin | wide | double | dust | glowing
  moon_count        integer 0-6
  atmosphere_density  none | thin | medium | thick
  environment_effect  none | dust | sparkles | embers | snow_mist | debris | plasma
{TRAIT_PROMPT_BLOCK}
Shape of the answer:

{EXAMPLE_RESPONSE}
"""


def _fusion_prompt(planet_a, planet_b):
    return f"""Two charted worlds are being merged into a third.

World A — {planet_a.get('title')}
  emotion {planet_a.get('emotion')}, theme {planet_a.get('theme')}, type {planet_a.get('planet_type')}
  from the memory: \"\"\"{(planet_a.get('text') or '')[:400]}\"\"\"

World B — {planet_b.get('title')}
  emotion {planet_b.get('emotion')}, theme {planet_b.get('theme')}, type {planet_b.get('planet_type')}
  from the memory: \"\"\"{(planet_b.get('text') or '')[:400]}\"\"\"

Design the world they make together. It should read as a third thing, not as A
with some of B bolted on. Use the same fields as a normal design, plus:

  fusion_story   1-2 sentences. What these two memories have in common that
                 neither of them showed on its own. Plain language.
{TRAIT_PROMPT_BLOCK}
Shape of the answer:

{EXAMPLE_RESPONSE}
"""


# =========================================================
# OFFLINE MODEL
# =========================================================

_EMOTION_WORDS = {
    "happy": ["happy", "laugh", "joy", "won", "win", "smile", "proud", "excited", "birthday",
              "celebrat", "sunny", "warm", "best", "loved", "fun", "danc"],
    "sad": ["sad", "cry", "cried", "lost", "loss", "gone", "miss", "missed", "alone",
            "goodbye", "funeral", "empty", "hurt", "left", "died", "grief"],
    "angry": ["angry", "mad", "furious", "fight", "fought", "argu", "yell", "shout",
              "hate", "unfair", "slam", "broke", "betray", "rage"],
    "calm": ["calm", "quiet", "peace", "still", "slow", "breath", "rest", "gentle",
             "soft", "float", "sleep", "morning", "silence"],
    "nostalgic": ["remember", "used to", "back then", "childhood", "grandma", "grandpa",
                  "old", "years ago", "summer", "smell of", "again", "younger", "before"],
    "anxious": ["nervous", "anxious", "scared", "afraid", "worry", "worried", "panic",
                "shaking", "waiting", "exam", "test", "interview", "hospital", "late"],
}

_THEME_WORDS = {
    "ocean": ["ocean", "sea", "beach", "wave", "tide", "swim", "shore", "boat", "water", "sand"],
    "fire": ["fire", "burn", "flame", "smoke", "campfire", "candle", "heat", "ash"],
    "ice": ["snow", "ice", "cold", "winter", "frozen", "frost", "freezing", "blizzard"],
    "nature": ["forest", "tree", "woods", "garden", "mountain", "grass", "leaves", "river",
               "hike", "flower", "field", "spring", "autumn", "farm", "lake", "trail",
               "backyard", "creek", "orchard"],
    "space": ["star", "sky", "night", "moon", "space", "universe", "constellation", "planet"],
    "city": ["city", "street", "apartment", "traffic", "subway", "downtown", "bus",
             "building", "neon", "school", "office", "kitchen", "house", "home",
             "room", "hallway", "door", "window", "hospital", "classroom", "car",
             "train", "station", "airport", "store", "elevator", "stairs"],
    "storm": ["storm", "rain", "thunder", "lightning", "wind", "hurricane", "flood", "gray"],
    "desert": ["desert", "dust", "dry", "heat", "road trip", "highway", "dune", "canyon"],
    "celebration": ["party", "birthday", "wedding", "graduat", "holiday", "christmas",
                    "concert", "cake", "gift", "tournament", "trophy", "won", "champion",
                    "medal", "anniversary", "reunion", "festival", "fireworks"],
}

# When no theme word appears, the emotion picks the setting. "unknown" is a
# last resort, not a default.
_EMOTION_THEME = {
    "happy": "celebration",
    "sad": "ocean",
    "angry": "storm",
    "calm": "nature",
    "nostalgic": "nature",
    "anxious": "city",
}

_THEME_FEATURES = {
    "ocean": ["oceans", "tide_pools", "reef_shelves", "bioluminescence"],
    "fire": ["lava_cracks", "ash_plains", "canyons", "meteor_scars"],
    "ice": ["ice_caps", "glass_seas", "crystals", "shattered_crust"],
    "nature": ["forests", "root_networks", "canyons", "geysers"],
    "space": ["craters", "crystals", "aurora", "spire_fields"],
    "city": ["city_lights", "terraced_cliffs", "canyons", "salt_flats"],
    "storm": ["storms", "cloud_bands", "aurora", "shattered_crust"],
    "desert": ["dunes", "salt_flats", "canyons", "terraced_cliffs"],
    "celebration": ["city_lights", "aurora", "crystals", "bioluminescence"],
    "unknown": ["craters", "canyons", "cloud_bands", "crystals"],
}

_STOPWORDS = {
    # function words
    "the", "a", "an", "and", "but", "or", "so", "if", "of", "to", "in", "on", "at", "for",
    "with", "was", "were", "is", "are", "am", "be", "been", "being", "it", "its", "this",
    "that", "these", "those", "as", "from", "by", "into", "onto", "than", "because",
    "while", "after", "before", "until", "since", "though", "whether",
    # people
    "i", "me", "my", "mine", "we", "us", "our", "ours", "you", "your", "yours", "he",
    "she", "they", "them", "his", "her", "hers", "their", "theirs", "myself", "everyone",
    "everybody", "someone", "somebody", "nobody", "anyone", "anything", "everything",
    "nothing", "something",
    # verbs that carry no image
    "had", "have", "has", "did", "do", "does", "done", "went", "gone", "going", "come",
    "came", "coming", "get", "got", "getting", "make", "made", "said", "says", "saying",
    "know", "knew", "think", "thought", "want", "wanted", "kept", "keep", "felt", "feel",
    "feeling", "remember", "remembered", "seemed", "looked", "started", "stopped",
    # degree, time, and place filler
    "just", "very", "really", "quite", "much", "many", "more", "most", "less", "least",
    "like", "when", "then", "there", "here", "where", "what", "which", "who", "how",
    "why", "up", "down", "out", "about", "over", "under", "again", "still", "even",
    "all", "not", "no", "some", "any", "each", "every", "both", "other", "another",
    "would", "could", "should", "will", "can", "cant", "couldnt", "wouldnt", "didnt",
    "back", "away", "around", "through", "always", "never", "ever", "only", "also",
    "first", "last", "next", "one", "two", "three", "four", "five", "time", "times",
    "day", "days", "year", "years", "way", "thing", "things", "asleep", "awake",
}

_TITLE_TEMPLATES = {
    "happy": ["The {noun} Held", "Bright {noun} Season", "Where the {noun} Turned Gold", "Every {noun} At Once"],
    "sad": ["After the {noun}", "The {noun} Kept Going", "Nothing Left of the {noun}", "The Long {noun}"],
    "angry": ["The {noun} Never Cooled", "Break Line, {noun}", "The {noun} That Wouldn't Stop", "Hard {noun}"],
    "calm": ["Where the {noun} Settles", "The Quiet {noun}", "{noun} At Rest", "Low Tide, {noun}"],
    "nostalgic": ["The {noun} Came Back", "Old {noun} Light", "Before the {noun} Moved", "The {noun} We Kept"],
    "anxious": ["Waiting on the {noun}", "The {noun} Before It Broke", "Thin {noun} Air", "Held {noun}"],
}

_FALLBACK_NOUNS = ["Hour", "Room", "Shoreline", "Window", "Signal", "Distance", "Weather", "Threshold"]


def _seeded(text):
    return random.Random(int(hashlib.sha256(text.encode("utf-8")).hexdigest()[:16], 16))


def _score(text, lexicon):
    lowered = text.lower()
    return {
        key: sum(lowered.count(word) for word in words)
        for key, words in lexicon.items()
    }


def _salient_noun(text, rng):
    """
    The most memory-specific word we can find, for use in a title.

    Possessives get trimmed ("Grandma's" -> "Grandma"), adverbs get dropped, and
    anything in the stoplist is out. What's left is ranked by length, because in
    a short personal memory the long word is almost always the concrete one.
    """
    candidates = []
    for raw in re.findall(r"[A-Za-z][A-Za-z']{2,}", text):
        word = re.sub(r"'s$|'$", "", raw).strip("'")
        lowered = word.lower()
        if len(word) < 4 or lowered in _STOPWORDS:
            continue
        if lowered.endswith("ly") or lowered.endswith("ing") and len(word) > 7:
            continue
        candidates.append(word)

    if not candidates:
        return rng.choice(_FALLBACK_NOUNS)

    candidates.sort(key=lambda w: (-len(w), text.lower().index(w.lower())))
    return candidates[0].capitalize()


def heuristic_analysis(memory_text):
    """
    A keyword read of the memory. Deterministic: the same text always produces
    the same world, so offline mode is stable across reruns.
    """
    rng = _seeded(memory_text)

    emotion_scores = _score(memory_text, _EMOTION_WORDS)
    emotion = max(emotion_scores, key=emotion_scores.get)
    if emotion_scores[emotion] == 0:
        emotion = "nostalgic" if "remember" in memory_text.lower() else "calm"

    theme_scores = _score(memory_text, _THEME_WORDS)
    theme = max(theme_scores, key=theme_scores.get)
    if theme_scores[theme] == 0:
        theme = _EMOTION_THEME.get(emotion, "unknown")

    planet_type = rng.choice(THEME_PLANET_TYPES.get(theme, ["rocky"]))

    length = len(memory_text)
    size_class = "small" if length < 90 else "medium" if length < 240 else "large" if length < 520 else "giant"

    palette = list(EMOTION_FALLBACKS.get(emotion, THEME_FALLBACKS["unknown"]))
    if theme in THEME_FALLBACKS and rng.random() < 0.5:
        palette = [palette[0], THEME_FALLBACKS[theme][1], THEME_FALLBACKS[theme][2]]

    pool = [f for f in _THEME_FEATURES.get(theme, _THEME_FEATURES["unknown"]) if f in ALLOWED_FEATURES]
    features = rng.sample(pool, min(len(pool), rng.randint(2, 3)))

    noun = _salient_noun(memory_text, rng)
    title = rng.choice(_TITLE_TEMPLATES.get(emotion, _TITLE_TEMPLATES["calm"])).format(noun=noun)

    return {
        "title": title,
        "emotion": emotion,
        "theme": theme,
        "planet_type": planet_type,
        "size_class": size_class,
        "palette": palette,
        "surface_features": features,
        "ring_style": rng.choice(["none", "none", "thin", "wide", "dust", "double", "glowing"]),
        "moon_count": rng.randint(0, 4),
        "atmosphere_density": rng.choice(["thin", "medium", "medium", "thick"]),
        "environment_effect": rng.choice(["none", "dust", "sparkles", "embers", "snow_mist", "debris", "plasma"]),
    }


def heuristic_fusion(planet_a, planet_b):
    """Blend two worlds without the model. Takes the stronger half of each."""
    combined = f"{planet_a.get('text', '')} {planet_b.get('text', '')}"
    rng = _seeded(f"fuse:{planet_a.get('title')}:{planet_b.get('title')}")

    design = heuristic_analysis(combined)
    design["emotion"] = rng.choice([planet_a.get("emotion", "calm"), planet_b.get("emotion", "calm")])
    design["theme"] = rng.choice([planet_a.get("theme", "unknown"), planet_b.get("theme", "unknown")])
    design["size_class"] = "giant"
    design["ring_style"] = "double"
    design["palette"] = [
        (planet_a.get("palette") or EMOTION_FALLBACKS["calm"])[0],
        (planet_b.get("palette") or EMOTION_FALLBACKS["calm"])[1],
        (planet_a.get("palette") or EMOTION_FALLBACKS["calm"])[2],
    ]
    merged = list(dict.fromkeys(
        (planet_a.get("surface_features") or [])[:2] + (planet_b.get("surface_features") or [])[:2]
    ))
    design["surface_features"] = merged or design["surface_features"]
    design["fusion_story"] = (
        f"Both memories sit in the same weather: {planet_a.get('emotion', 'something')} and "
        f"{planet_b.get('emotion', 'something')} turned out to be the same feeling seen from "
        f"two distances."
    )
    return design


# =========================================================
# PUBLIC API
# =========================================================

def analyze_memory(memory_text, allow_offline=True):
    """
    Returns (design_dict, source). Source is "model" or "offline".
    Raises OllamaUnavailable only when allow_offline is False.
    """
    if is_available():
        try:
            raw = generate_json(_design_prompt(memory_text), system=SYSTEM_PROMPT)
            design = coerce_response(raw)
            if design.get("title"):
                return design, SOURCE_MODEL
        except (OllamaUnavailable, OllamaBadResponse):
            if not allow_offline:
                raise

    if not allow_offline:
        raise OllamaUnavailable("Ollama isn't reachable and offline mode is off")

    return heuristic_analysis(memory_text), SOURCE_OFFLINE


def fuse_memories(planet_a, planet_b, allow_offline=True):
    """Returns (design_dict, source) for a fused world."""
    if is_available():
        try:
            raw = generate_json(_fusion_prompt(planet_a, planet_b), system=SYSTEM_PROMPT)
            design = coerce_response(raw)
            if design.get("title"):
                design.setdefault("fusion_story", "")
                return design, SOURCE_MODEL
        except (OllamaUnavailable, OllamaBadResponse):
            if not allow_offline:
                raise

    if not allow_offline:
        raise OllamaUnavailable("Ollama isn't reachable and offline mode is off")

    return heuristic_fusion(planet_a, planet_b), SOURCE_OFFLINE
