"""
Derived planet traits.

The AI picks the symbolic traits. This module fills in everything it didn't
pick, and computes the physical numbers that follow from what it did pick.

Two rules hold everywhere:
  1. The AI always wins. A value already on the planet is never overwritten.
  2. Derivation is deterministic. The same memory always produces the same
     world, so a galaxy survives a rerun and an export/import round trip.
"""

import hashlib
import random

from config import (
    ALLOWED_ANOMALIES, ANOMALY_CHANCE, ANOMALY_DESCRIPTIONS,
    ALLOWED_AGE_CLASSES, ALLOWED_CORE_TYPES, ALLOWED_GRAVITY_CLASSES,
    ALLOWED_LUMINOSITY, ALLOWED_MOON_STYLES, ALLOWED_ORBIT_BEHAVIORS,
    ALLOWED_SURFACE_TEXTURES, ALLOWED_TIME_OF_DAY, ALLOWED_WEATHER,
    EMOTION_BASE_INTENSITY, EMOTION_CODES, EMOTION_FALLBACKS,
    GRAVITY_G, SIZE_NUMERALS, SIZE_RADIUS_KM, THEME_CODES, THEME_FALLBACKS,
    TYPE_BASE_TEMP_C, VALIDATORS,
)

# ---------------------------------------------------------
# Trait affinities: which options each emotion or theme leans toward.
# Weighted choice, not a lookup, so two "calm" worlds still differ.
# ---------------------------------------------------------

_EMOTION_AFFINITY = {
    "happy":     {"weather": ["clear", "warm_drizzle", "aurora_veil"],
                  "time_of_day": ["noon", "golden_hour", "dawn"],
                  "orbit_behavior": ["steady", "elliptical"],
                  "core_type": ["molten", "crystalline"]},
    "sad":       {"weather": ["warm_drizzle", "static_calm", "whiteout"],
                  "time_of_day": ["dusk", "midnight"],
                  "orbit_behavior": ["drifting", "tidally_locked"],
                  "core_type": ["frozen", "hollow"]},
    "angry":     {"weather": ["perpetual_storm", "ash_fall", "ion_rain"],
                  "time_of_day": ["eclipse", "midnight"],
                  "orbit_behavior": ["retrograde", "wobbling"],
                  "core_type": ["molten", "metallic"]},
    "calm":      {"weather": ["clear", "static_calm"],
                  "time_of_day": ["dawn", "golden_hour"],
                  "orbit_behavior": ["steady", "tidally_locked"],
                  "core_type": ["crystalline", "frozen"]},
    "nostalgic": {"weather": ["aurora_veil", "warm_drizzle", "static_calm"],
                  "time_of_day": ["golden_hour", "dusk"],
                  "orbit_behavior": ["elliptical", "drifting"],
                  "core_type": ["hollow", "crystalline"]},
    "anxious":   {"weather": ["ion_rain", "perpetual_storm", "whiteout"],
                  "time_of_day": ["eclipse", "midnight", "dawn"],
                  "orbit_behavior": ["wobbling", "retrograde"],
                  "core_type": ["singularity", "metallic"]},
}

_TYPE_TEXTURE = {
    "rocky": ["cratered", "fractured", "terraced"],
    "oceanic": ["smooth", "banded", "porous"],
    "icy": ["glassine", "fractured", "smooth"],
    "volcanic": ["molten", "fractured", "porous"],
    "gaseous": ["banded", "smooth"],
    "forest": ["terraced", "porous", "smooth"],
    "crystalline": ["glassine", "fractured"],
    "desert": ["smooth", "terraced", "cratered"],
    "storm": ["banded", "smooth"],
}

_INTENSITY_LUMINOSITY = [(30, "dim"), (55, "soft"), (80, "radiant"), (101, "blinding")]
_INTENSITY_GRAVITY = [(30, "feather"), (50, "low"), (70, "earthlike"), (86, "heavy"), (101, "crushing")]

# Fields the rest of the app reads unconditionally. If the model returns
# something outside the vocabulary for one of these, coerce rather than drop.
_CORE_DEFAULTS = {
    "emotion": "calm",
    "theme": "unknown",
    "planet_type": "rocky",
    "size_class": "medium",
    "ring_style": "none",
    "atmosphere_density": "thin",
    "environment_effect": "none",
}


# ---------------------------------------------------------
# Helpers
# ---------------------------------------------------------

def _rng(planet, salt):
    """
    A stable RNG keyed to the memory and to one specific field.

    Salting per field matters: it means each trait is drawn from its own
    independent stream, so enriching a planet twice — or loading one back from
    a saved file where some traits are already filled in — can never shift the
    other traits. Same memory, same world, every time.
    """
    basis = "|".join(str(planet.get(k, "")) for k in ("title", "text", "emotion", "theme", "planet_type"))
    digest = hashlib.sha256(f"{basis}#{salt}".encode("utf-8")).hexdigest()
    return random.Random(int(digest[:16], 16))


def _band(value, table):
    for ceiling, label in table:
        if value < ceiling:
            return label
    return table[-1][1]


def _pick(planet, salt, preferred, allowed):
    """Prefer the affinity list, but leave room for the rest of the vocabulary."""
    rng = _rng(planet, salt)
    pool = [option for option in preferred if option in allowed]
    if pool and rng.random() < 0.75:
        return rng.choice(pool)
    return rng.choice(sorted(allowed))


def measure_intensity(planet):
    """
    Emotional intensity, 0-100. Starts from the emotion, then reads the memory
    text: exclamation marks, shouting, and length all push it up.
    """
    emotion = planet.get("emotion", "calm")
    score = EMOTION_BASE_INTENSITY.get(emotion, 50)

    text = planet.get("text", "") or ""
    if text:
        letters = [c for c in text if c.isalpha()]
        shouting = sum(1 for c in letters if c.isupper()) / max(len(letters), 1)
        score += min(text.count("!") * 4, 12)
        score += min(shouting * 30, 10)
        score += min(len(text) / 90.0, 8)
        if any(w in text.lower() for w in ("never", "always", "first", "last", "forever")):
            score += 5

    return max(0, min(100, round(score)))


def build_designation(planet, index):
    """
    Catalog designation, e.g. MG-007 · CAL-OCE · III.
    Sequence, emotion, theme, size. Every part carries information.
    """
    emotion_code = EMOTION_CODES.get(planet.get("emotion", ""), "UNK")
    theme_code = THEME_CODES.get(planet.get("theme", ""), "UNK")
    numeral = SIZE_NUMERALS.get(planet.get("size_class", "medium"), "II")
    return f"MG-{index + 1:03d} · {emotion_code}-{theme_code} · {numeral}"


def resolve_palette(planet):
    """Palette from the AI if present, otherwise emotion, otherwise theme."""
    palette = planet.get("palette")
    if isinstance(palette, (list, tuple)) and len(palette) >= 3:
        return list(palette)[:3]
    emotion = planet.get("emotion", "")
    if emotion in EMOTION_FALLBACKS:
        return list(EMOTION_FALLBACKS[emotion])
    return list(THEME_FALLBACKS.get(planet.get("theme", "unknown"), THEME_FALLBACKS["unknown"]))


# ---------------------------------------------------------
# Main entry point
# ---------------------------------------------------------

def enrich_planet(planet, index=0):
    """
    Fill in every trait the AI left out and compute the physical readout.
    Safe to call repeatedly on the same planet.
    """
    # Reject anything the model invented outside the vocabulary. Core fields
    # fall back to a safe value so the rest of the app always has something to
    # read; the optional ones are simply dropped and re-derived below.
    for field, allowed in VALIDATORS.items():
        if field in planet and planet[field] is not None and planet[field] not in allowed:
            if field in _CORE_DEFAULTS:
                planet[field] = _CORE_DEFAULTS[field]
            else:
                planet.pop(field)

    emotion = planet.get("emotion", "calm")
    planet_type = planet.get("planet_type", "rocky")
    size_class = planet.get("size_class", "medium")
    affinity = _EMOTION_AFFINITY.get(emotion, _EMOTION_AFFINITY["calm"])

    planet.setdefault("palette", resolve_palette(planet))
    planet["designation"] = build_designation(planet, index)

    intensity = planet.get("intensity") or measure_intensity(planet)
    planet["intensity"] = intensity

    # --- symbolic traits ---
    planet.setdefault("surface_texture",
                      _pick(planet, "texture", _TYPE_TEXTURE.get(planet_type, []), ALLOWED_SURFACE_TEXTURES))
    planet.setdefault("core_type",
                      _pick(planet, "core", affinity["core_type"], ALLOWED_CORE_TYPES))
    planet.setdefault("orbit_behavior",
                      _pick(planet, "orbit", affinity["orbit_behavior"], ALLOWED_ORBIT_BEHAVIORS))
    planet.setdefault("weather",
                      _pick(planet, "weather", affinity["weather"], ALLOWED_WEATHER))
    planet.setdefault("time_of_day",
                      _pick(planet, "hour", affinity["time_of_day"], ALLOWED_TIME_OF_DAY))
    planet.setdefault("luminosity", _band(intensity, _INTENSITY_LUMINOSITY))
    planet.setdefault("gravity_class", _band(intensity, _INTENSITY_GRAVITY))

    if "moon_style" not in planet:
        rng = _rng(planet, "moons")
        moons = int(planet.get("moon_count", 0) or 0)
        if moons == 0:
            planet["moon_style"] = "none"
        elif moons == 1:
            planet["moon_style"] = rng.choice(["single", "shepherd", "captured"])
        elif moons == 2:
            planet["moon_style"] = "twin"
        elif moons >= 5:
            planet["moon_style"] = "swarm"
        else:
            planet["moon_style"] = rng.choice(["shepherd", "shattered", "swarm"])

    # Age reads the memory's temperature: raw memories are still forming,
    # settled ones have cooled, and nostalgia is what's already old.
    if "age_class" not in planet:
        if emotion == "nostalgic":
            preferred = ["ancient", "fading", "settled"]
        elif intensity >= 78:
            preferred = ["forming", "young"]
        elif intensity >= 50:
            preferred = ["young", "settled"]
        else:
            preferred = ["settled", "ancient", "fading"]
        planet["age_class"] = _pick(planet, "age", preferred, ALLOWED_AGE_CLASSES)

    if "anomaly" not in planet:
        anomaly_rng = _rng(planet, "anomaly")
        planet["anomaly"] = (
            anomaly_rng.choice(sorted(ALLOWED_ANOMALIES))
            if anomaly_rng.random() < ANOMALY_CHANCE else None
        )
    planet["anomaly_note"] = ANOMALY_DESCRIPTIONS.get(planet.get("anomaly") or "", "")

    # --- physical readout ---
    physical = _rng(planet, "physical")
    radius = SIZE_RADIUS_KM.get(size_class, 5100)
    planet["radius_km"] = radius + physical.randint(-380, 380)
    planet["gravity_g"] = round(
        GRAVITY_G.get(planet["gravity_class"], 1.0) * physical.uniform(0.92, 1.08), 2
    )

    temp = TYPE_BASE_TEMP_C.get(planet_type, 10)
    temp += {"blinding": 34, "radiant": 16, "soft": 0, "dim": -18}[planet["luminosity"]]
    if planet["weather"] in ("whiteout", "ash_fall"):
        temp -= 22
    planet["mean_temp_c"] = round(temp + physical.uniform(-6, 6))

    # Intense memories orbit close to the core. Quiet ones sit out at the rim.
    planet["orbital_radius_au"] = round(0.4 + (100 - intensity) / 100.0 * 3.2, 2)
    planet["orbital_period_yr"] = round(planet["orbital_radius_au"] ** 1.5, 2)
    planet["rotation_hours"] = round(physical.uniform(6, 92), 1)
    planet["axial_tilt_deg"] = round(physical.uniform(0, 86), 1)

    # How reliably you can return to this memory unchanged.
    stability = 100 - abs(intensity - 45) * 0.7
    stability -= {"wobbling": 14, "retrograde": 11, "drifting": 9}.get(planet["orbit_behavior"], 0)
    if planet.get("anomaly"):
        stability -= 8
    if planet.get("is_fusion"):
        stability -= 6
    planet["stability_pct"] = max(4, min(99, round(stability)))

    # A tone for the world. Low and slow when heavy, high and thin when light.
    planet["resonance_hz"] = round(55 * (2 ** ((100 - intensity) / 42.0)), 1)

    return planet


def enrich_all(planets):
    """Enrich a whole galaxy in place and return it."""
    for i, planet in enumerate(planets):
        enrich_planet(planet, i)
    return planets


# ---------------------------------------------------------
# Galaxy-level structure
# ---------------------------------------------------------

def find_constellations(planets, minimum=2):
    """
    Group worlds that share an emotion and a theme. These are the patterns a
    person keeps returning to, which is the only grouping worth surfacing.
    Returns a list of (name, [planets]) sorted largest first.
    """
    groups = {}
    for planet in planets:
        key = (planet.get("emotion", "unknown"), planet.get("theme", "unknown"))
        groups.setdefault(key, []).append(planet)

    named = [
        (f"{emotion.title()} {theme.title()}", members)
        for (emotion, theme), members in groups.items()
        if len(members) >= minimum
    ]
    return sorted(named, key=lambda item: len(item[1]), reverse=True)


def galaxy_summary(planets):
    """Headline numbers for the top of the page."""
    if not planets:
        return {
            "count": 0, "dominant_emotion": "—", "themes": 0,
            "mean_intensity": 0, "anomalies": 0, "constellations": 0,
        }

    counts = {}
    for planet in planets:
        counts[planet.get("emotion", "unknown")] = counts.get(planet.get("emotion", "unknown"), 0) + 1

    return {
        "count": len(planets),
        "dominant_emotion": max(counts, key=counts.get),
        "themes": len({p.get("theme") for p in planets}),
        "mean_intensity": round(sum(p.get("intensity", 0) for p in planets) / len(planets)),
        "anomalies": sum(1 for p in planets if p.get("anomaly")),
        "constellations": len(find_constellations(planets)),
    }
