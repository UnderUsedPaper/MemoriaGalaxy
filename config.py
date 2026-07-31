"""
Memoria Galaxy — world-building vocabulary.

Everything the AI is allowed to choose lives here. Keeping the vocabulary in one
place means the model prompt, the validator, and the renderer can never drift
apart: if a trait isn't in one of these sets, it doesn't exist.
"""

# =========================================================
# MODEL
# =========================================================

OLLAMA_HOST = "http://localhost:11434"
OLLAMA_MODEL = "llama3.1"
OLLAMA_TIMEOUT = 90          # seconds; small models on CPU are slow
OLLAMA_TEMPERATURE = 0.85    # high enough that two similar memories still differ

# When Ollama isn't running, fall back to the keyword analyzer instead of
# failing. The UI always says which one produced a world.
ALLOW_OFFLINE_FALLBACK = True

# =========================================================
# CORE TRAITS  (already used by the app)
# =========================================================

ALLOWED_EMOTIONS = {"happy", "sad", "angry", "calm", "nostalgic", "anxious"}

ALLOWED_THEMES = {
    "fire", "ocean", "ice", "nature", "space",
    "city", "storm", "desert", "celebration", "unknown",
}

ALLOWED_PLANET_TYPES = {
    "rocky", "oceanic", "icy", "volcanic", "gaseous",
    "forest", "crystalline", "desert", "storm",
}

ALLOWED_SIZE_CLASSES = {"small", "medium", "large", "giant"}
ALLOWED_RING_STYLES = {"none", "thin", "wide", "double", "dust", "glowing"}
ALLOWED_ATMOSPHERE_DENSITY = {"none", "thin", "medium", "thick"}
ALLOWED_ENV_EFFECTS = {"none", "dust", "sparkles", "embers", "snow_mist", "debris", "plasma"}

ALLOWED_FEATURES = {
    "craters", "lava_cracks", "oceans", "ice_caps", "forests", "crystals",
    "dunes", "canyons", "storms", "cloud_bands", "city_lights", "aurora",
    # new surface features
    "salt_flats", "geysers", "reef_shelves", "ash_plains", "glass_seas",
    "terraced_cliffs", "root_networks", "meteor_scars", "tide_pools",
    "spire_fields", "bioluminescence", "shattered_crust",
}

# =========================================================
# NEW TRAITS  (the planet dossier)
# =========================================================

# What the surface actually looks like up close.
ALLOWED_SURFACE_TEXTURES = {
    "smooth", "cratered", "fractured", "banded",
    "molten", "glassine", "terraced", "porous",
}

# What sits at the center of the world. This is the memory's core truth.
ALLOWED_CORE_TYPES = {
    "molten", "crystalline", "hollow", "frozen", "metallic", "singularity",
}

# How the planet moves. Maps onto how settled the memory feels.
ALLOWED_ORBIT_BEHAVIORS = {
    "steady", "elliptical", "wobbling", "drifting", "tidally_locked", "retrograde",
}

# How brightly it burns.
ALLOWED_LUMINOSITY = {"dim", "soft", "radiant", "blinding"}

# How heavy it is to stand on.
ALLOWED_GRAVITY_CLASSES = {"feather", "low", "earthlike", "heavy", "crushing"}

# Persistent weather, distinct from one-off environment effects.
ALLOWED_WEATHER = {
    "clear", "perpetual_storm", "ash_fall", "ion_rain",
    "aurora_veil", "static_calm", "warm_drizzle", "whiteout",
}

# The hour the planet is frozen at. Memories rarely have a full day.
ALLOWED_TIME_OF_DAY = {"dawn", "noon", "golden_hour", "dusk", "midnight", "eclipse"}

# Moon arrangement, richer than a bare count.
ALLOWED_MOON_STYLES = {"none", "single", "twin", "shepherd", "shattered", "captured", "swarm"}

# How long ago it formed, emotionally rather than literally.
ALLOWED_AGE_CLASSES = {"forming", "young", "settled", "ancient", "fading"}

# Rare. At most one per planet, and most planets have none.
ALLOWED_ANOMALIES = {
    "ring_gap", "second_shadow", "orbiting_derelict", "impossible_moon",
    "time_dilation_halo", "chorus_signal", "twin_sunrise", "silent_zone",
}

ANOMALY_DESCRIPTIONS = {
    "ring_gap": "A clean break in the rings. Something passed through and never came back.",
    "second_shadow": "Two shadows fall from one light. Nobody has found the second source.",
    "orbiting_derelict": "An abandoned craft holds a stable orbit. Still transmitting.",
    "impossible_moon": "A moon that orbits faster than the math allows.",
    "time_dilation_halo": "Clocks run slow inside the halo. An hour here is a day out there.",
    "chorus_signal": "The magnetosphere sings. The pattern repeats every 41 minutes.",
    "twin_sunrise": "The sun rises, sets, and rises again before noon.",
    "silent_zone": "A band of the surface where no sound carries at all.",
}

# Odds that any given world carries an anomaly.
ANOMALY_CHANCE = 0.22

# =========================================================
# PALETTES
# =========================================================

EMOTION_FALLBACKS = {
    "happy":     ["#FFD166", "#FFB703", "#FB8500"],
    "sad":       ["#355070", "#4A6FA5", "#A8DADC"],
    "angry":     ["#FF595E", "#C1121F", "#5F0F40"],
    "calm":      ["#4CC9F0", "#4895EF", "#4361EE"],
    "nostalgic": ["#C084FC", "#F472B6", "#FDE68A"],
    "anxious":   ["#94A3B8", "#64748B", "#334155"],
}

THEME_FALLBACKS = {
    "fire":        ["#FF7B00", "#E63946", "#6A040F"],
    "ocean":       ["#4CC9F0", "#0077B6", "#023E8A"],
    "ice":         ["#CAF0F8", "#90E0EF", "#0077B6"],
    "nature":      ["#80ED99", "#57CC99", "#2D6A4F"],
    "space":       ["#7DD3FC", "#A78BFA", "#F472B6"],
    "city":        ["#94A3B8", "#64748B", "#334155"],
    "storm":       ["#94A3B8", "#475569", "#0F172A"],
    "desert":      ["#E9C46A", "#D4A373", "#A97142"],
    "celebration": ["#FFD166", "#FF70A6", "#70D6FF"],
    "unknown":     ["#7DD3FC", "#C084FC", "#F472B6"],
}

# =========================================================
# PHYSICAL REFERENCE TABLES
# =========================================================

# Rough mean surface temperature in Celsius, used for the dossier readout.
TYPE_BASE_TEMP_C = {
    "rocky": 14, "oceanic": 11, "icy": -78, "volcanic": 240, "gaseous": -120,
    "forest": 19, "crystalline": -31, "desert": 47, "storm": -6,
}

SIZE_RADIUS_KM = {"small": 2400, "medium": 5100, "large": 9800, "giant": 26400}

# Display radius in the 3D scene, in scene units.
SIZE_DISPLAY_RADIUS = {"small": 0.85, "medium": 1.25, "large": 1.8, "giant": 2.6}

# Planet types that read as a given theme. Used by the offline analyzer and as
# a sanity net when the model picks an odd pairing.
THEME_PLANET_TYPES = {
    "fire":        ["volcanic", "rocky", "desert"],
    "ocean":       ["oceanic", "storm", "icy"],
    "ice":         ["icy", "crystalline", "rocky"],
    "nature":      ["forest", "oceanic", "rocky"],
    "space":       ["gaseous", "crystalline", "rocky"],
    "city":        ["rocky", "desert", "crystalline"],
    "storm":       ["storm", "gaseous", "oceanic"],
    "desert":      ["desert", "rocky", "volcanic"],
    "celebration": ["crystalline", "gaseous", "forest"],
    "unknown":     ["rocky", "gaseous", "crystalline"],
}

# Scene units per AU. Sets how far apart the orbits sit.
ORBIT_SCALE = 13.0

GRAVITY_G = {"feather": 0.18, "low": 0.47, "earthlike": 1.0, "heavy": 2.3, "crushing": 4.1}

# Emotional weight, 0-100, before the memory text adjusts it.
EMOTION_BASE_INTENSITY = {
    "angry": 82, "anxious": 74, "happy": 63,
    "nostalgic": 57, "sad": 51, "calm": 34,
}

# Three-letter catalog codes, so designations stay stable and readable.
EMOTION_CODES = {
    "happy": "HAP", "sad": "SAD", "angry": "ANG",
    "calm": "CAL", "nostalgic": "NOS", "anxious": "ANX",
}

THEME_CODES = {
    "fire": "FIR", "ocean": "OCE", "ice": "ICE", "nature": "NAT", "space": "SPC",
    "city": "CTY", "storm": "STM", "desert": "DSR", "celebration": "CEL",
    "unknown": "UNK",
}

SIZE_NUMERALS = {"small": "I", "medium": "II", "large": "III", "giant": "IV"}

# =========================================================
# SCHEMA
# =========================================================

# Fields the AI is expected to produce. Anything missing is derived
# deterministically by utility.traits.enrich_planet(), so the app never
# breaks on an incomplete model response.
PLANET_SCHEMA_FIELDS = [
    "title", "emotion", "theme", "planet_type", "size_class",
    "palette", "surface_features", "ring_style", "moon_count",
    "atmosphere_density", "environment_effect",
    # dossier fields
    "surface_texture", "core_type", "orbit_behavior", "luminosity",
    "gravity_class", "weather", "time_of_day", "moon_style",
    "age_class", "anomaly",
]

VALIDATORS = {
    "emotion": ALLOWED_EMOTIONS,
    "theme": ALLOWED_THEMES,
    "planet_type": ALLOWED_PLANET_TYPES,
    "size_class": ALLOWED_SIZE_CLASSES,
    "ring_style": ALLOWED_RING_STYLES,
    "atmosphere_density": ALLOWED_ATMOSPHERE_DENSITY,
    "environment_effect": ALLOWED_ENV_EFFECTS,
    "surface_texture": ALLOWED_SURFACE_TEXTURES,
    "core_type": ALLOWED_CORE_TYPES,
    "orbit_behavior": ALLOWED_ORBIT_BEHAVIORS,
    "luminosity": ALLOWED_LUMINOSITY,
    "gravity_class": ALLOWED_GRAVITY_CLASSES,
    "weather": ALLOWED_WEATHER,
    "time_of_day": ALLOWED_TIME_OF_DAY,
    "moon_style": ALLOWED_MOON_STYLES,
    "age_class": ALLOWED_AGE_CLASSES,
    "anomaly": ALLOWED_ANOMALIES,
}
