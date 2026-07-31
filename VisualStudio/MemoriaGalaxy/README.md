# Memoria Galaxy

Write down a memory. It gets read, classified, and issued a world — palette,
geology, weather, gravity, orbit, and a catalog number. What you end up with is
a map of what you kept.

Runs entirely on your machine. No API keys, no accounts, no data leaving the
laptop.

---

## Running it

```bash
pip install -r requirements.txt
streamlit run main.py
```

That's the whole install. The app works immediately.

For AI-designed worlds, also run a local model:

```bash
# https://ollama.com/download
ollama serve
ollama pull llama3.1
```

The sidebar says which mode you're in. If Ollama isn't answering, the app falls
back to a built-in keyword analyzer and labels every world it designs as
`Designed offline` — it degrades instead of breaking, which matters when you're
demoing on conference wifi.

Change the model in `config.py`:

```python
OLLAMA_MODEL = "llama3.1"   # mistral, phi3, qwen2.5 all work
```

---

## How a world gets made

```
memory text
    │
    ├─ ai_tools/memory_analyzer.py ──── Ollama picks the symbolic traits
    │                                   (or the keyword analyzer does)
    │      emotion, theme, planet type, palette, surface features,
    │      rings, moons, atmosphere, weather, core, orbit behaviour…
    │
    ├─ ai_tools/trait_schema.py ─────── everything outside the vocabulary
    │                                   is stripped before it reaches the app
    │
    ├─ utility/traits.py ────────────── derives the physical readout
    │      intensity ← read off the language you used
    │      gravity, light, temperature, orbital distance ← follow from intensity
    │
    ├─ utility/builder.py ───────────── finds the world a place to sit
    │
    └─ ui/galaxyrender.py ───────────── paints and renders it in 3D
```

**Intensity is the hinge.** It's read off the memory's own language —
exclamation marks, capitals, absolutes like *never* and *forever*, length — and
then everything physical follows from it. Intense memories orbit close to the
core and burn bright and heavy. Quiet ones sit out at the rim.

**Derivation is deterministic.** Every trait is drawn from a hash of the memory
text salted with the field name. The same memory always makes the same world,
enrichment is idempotent, and a galaxy exported to JSON and loaded back is
byte-identical.

---

## Files

| Path | What's in it |
|---|---|
| `main.py` | Streamlit page, sidebar console, dossier, constellations |
| `config.py` | The whole trait vocabulary, palettes, physical reference tables |
| `ai_tools/ollama_client.py` | HTTP transport, availability probe, JSON repair |
| `ai_tools/memory_analyzer.py` | Prompts + the offline keyword analyzer |
| `ai_tools/trait_schema.py` | Prompt fragment and response coercion |
| `utility/traits.py` | Trait derivation, physical readout, constellations |
| `utility/builder.py` | Analysis → placement → enrichment |
| `ui/styles.py` | The visual system |
| `ui/galaxyrender.py` | Three.js scene, procedural surface painting |

---

## The traits

Everything a world can be is listed in `config.py`. Add an option there and it
flows through the prompt, the validator, and the renderer automatically.

**Chosen by the analyzer** — emotion, theme, planet type, size class, palette,
surface features, ring style, moon count, atmosphere density, environment
effect, surface texture, core type, orbit behaviour, luminosity, gravity class,
weather, time of day, moon style, age class, anomaly.

**Derived from those** — designation, intensity, radius, surface gravity in g,
mean temperature, orbital distance and period, rotation period, axial tilt,
stability, resonance frequency.

**Anomalies** fire on roughly 22% of worlds and each one gets a distinct object
in the 3D scene: a dilation halo, a pulsing chorus shell, an orbiting derelict,
a moon that shouldn't hold its orbit, a gap cut into the rings, a second light
source, a dark patch burned into the surface map.

---

## What the renderer reads

Nothing in the 3D scene is decorative. Every mesh and speed comes off a trait:

| Trait | Effect |
|---|---|
| `palette` + `surface_features` + `surface_texture` | the painted surface map |
| `luminosity` | emissive strength |
| `atmosphere_density` | the glow shell |
| `ring_style`, `ring_gap` anomaly | ring geometry |
| `moon_count` + `moon_style` | moon arrangement and orbits |
| `axial_tilt_deg`, `rotation_hours` | tilt and spin rate |
| `environment_effect` | the particle field |
| `orbital_radius_au` | distance from the core |
| `anomaly` | one extra, strange object |

Drag to orbit, scroll to zoom, click a world to focus, double-click to reset.
Worlds sharing an emotion *and* a theme are wired together with constellation
lines.

---

## The memory journey

**Begin memory journey** walks the galaxy in the order you wrote the memories
down. The camera flies to each world, holds for eleven seconds, and reads the
memory back to you alongside the traits it produced.

`space` pauses &middot; `←` `→` step &middot; `esc` exits &middot; clicking any
world leaves the journey and parks you there.

---

## Sound

Every world plays its own drone. Nothing is sampled — each one is built live in
the Web Audio API from the world's own numbers:

| Trait | What it controls |
|---|---|
| `resonance_hz` | the fundamental the drone sits on |
| `emotion` | the mode the melody notes are drawn from |
| `planet_type` | timbre — waveform, detune, filter shape |
| `intensity` | how often notes arrive |
| `atmosphere_density` | reverb length; thick air rings longer |
| `luminosity` | filter brightness |
| `stability_pct` | pitch drift, so unstable worlds wander |
| `weather` | the noise bed underneath |

Modes run happy → major pentatonic, calm → suspended, sad → aeolian, nostalgic →
dorian, angry → phrygian dominant, anxious → whole tone, which has no home note
to resolve to.

Sound is off until you press the toggle, because browsers block audio until
someone asks for it. Music follows the world you're parked on, not the one
you're hovering.

---

## Extending it

**A new surface feature** — add it to `ALLOWED_FEATURES` in `config.py`, then
add a painter to the `PAINT` object in `ui/galaxyrender.py`. Everything else
picks it up.

**A new trait** — add the allowed set to `config.py`, register it in
`VALIDATORS`, add a line to `TRAIT_PROMPT_BLOCK`, and give it a default in
`enrich_planet()`.

**A different model** — anything Ollama serves works. Smaller models need the
example response in `trait_schema.py` more than larger ones do.
