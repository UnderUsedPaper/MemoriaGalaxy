"""
Prompt fragment for the new traits.

Additive and self-contained: nothing here runs unless you call it. Wire it into
whatever builds the Ollama prompt today.

    from ai_tools.trait_schema import TRAIT_PROMPT_BLOCK, coerce_response

    prompt = existing_prompt + "\\n" + TRAIT_PROMPT_BLOCK
    data = coerce_response(json.loads(model_output))

Anything the model omits or gets wrong is filled in by
utility.traits.enrich_planet(), so a partial response is fine.
"""

import json

from config import (
    ALLOWED_AGE_CLASSES, ALLOWED_ANOMALIES, ALLOWED_CORE_TYPES,
    ALLOWED_FEATURES, ALLOWED_GRAVITY_CLASSES, ALLOWED_LUMINOSITY,
    ALLOWED_MOON_STYLES, ALLOWED_ORBIT_BEHAVIORS, ALLOWED_SURFACE_TEXTURES,
    ALLOWED_TIME_OF_DAY, ALLOWED_WEATHER, VALIDATORS,
)


def _options(allowed):
    return " | ".join(sorted(allowed))


TRAIT_PROMPT_BLOCK = f"""
Also choose these traits. Pick the option that matches the memory's meaning,
not the one that sounds most dramatic. Use exactly the strings listed.

  surface_texture   {_options(ALLOWED_SURFACE_TEXTURES)}
  core_type         {_options(ALLOWED_CORE_TYPES)}
  orbit_behavior    {_options(ALLOWED_ORBIT_BEHAVIORS)}
  luminosity        {_options(ALLOWED_LUMINOSITY)}
  gravity_class     {_options(ALLOWED_GRAVITY_CLASSES)}
  weather           {_options(ALLOWED_WEATHER)}
  time_of_day       {_options(ALLOWED_TIME_OF_DAY)}
  moon_style        {_options(ALLOWED_MOON_STYLES)}
  age_class         {_options(ALLOWED_AGE_CLASSES)}
  anomaly           null, or one of: {_options(ALLOWED_ANOMALIES)}

Guidance:
  - gravity_class is how heavy the memory feels to carry, not the planet's mass.
  - age_class is how long ago it settled emotionally, not how old the event is.
  - anomaly should be null for most memories. Only use one when the memory has
    something genuinely unresolved in it.
  - surface_features must come from: {_options(ALLOWED_FEATURES)}

Return JSON only. No prose, no markdown fences.
"""


EXAMPLE_RESPONSE = json.dumps({
    "title": "The Tide Came Back",
    "emotion": "calm",
    "theme": "ocean",
    "planet_type": "oceanic",
    "size_class": "large",
    "palette": ["#4CC9F0", "#0077B6", "#023E8A"],
    "surface_features": ["oceans", "tide_pools", "reef_shelves"],
    "ring_style": "thin",
    "moon_count": 2,
    "atmosphere_density": "medium",
    "environment_effect": "sparkles",
    "surface_texture": "smooth",
    "core_type": "crystalline",
    "orbit_behavior": "steady",
    "luminosity": "soft",
    "gravity_class": "low",
    "weather": "clear",
    "time_of_day": "golden_hour",
    "moon_style": "twin",
    "age_class": "settled",
    "anomaly": None,
}, indent=2)


def coerce_response(data):
    """
    Strip anything outside the vocabulary before it reaches the app.
    Missing fields are left missing on purpose — enrich_planet() derives them.
    """
    if not isinstance(data, dict):
        raise ValueError("model returned something that isn't an object")

    cleaned = dict(data)

    for field, allowed in VALIDATORS.items():
        value = cleaned.get(field)
        if value is None:
            continue
        if isinstance(value, str):
            value = value.strip().lower().replace(" ", "_").replace("-", "_")
        if value in allowed:
            cleaned[field] = value
        else:
            cleaned.pop(field, None)

    features = cleaned.get("surface_features")
    if isinstance(features, list):
        cleaned["surface_features"] = [
            str(f).strip().lower().replace(" ", "_").replace("-", "_")
            for f in features
        ]
        cleaned["surface_features"] = [
            f for f in cleaned["surface_features"] if f in ALLOWED_FEATURES
        ][:5]
    else:
        cleaned["surface_features"] = []

    try:
        cleaned["moon_count"] = max(0, min(9, int(cleaned.get("moon_count", 0) or 0)))
    except (TypeError, ValueError):
        cleaned["moon_count"] = 0

    palette = cleaned.get("palette")
    if not (isinstance(palette, list) and len(palette) >= 3
            and all(isinstance(c, str) and c.startswith("#") and len(c) in (4, 7) for c in palette[:3])):
        cleaned.pop("palette", None)

    return cleaned
