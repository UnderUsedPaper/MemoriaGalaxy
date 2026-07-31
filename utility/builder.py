"""
Assembling a world.

build_planet() is the only thing main.py needs to know about. It runs the
analysis, gives the world a place to sit, derives the physical traits, and
hands back a finished planet dict.
"""

import math
import time

import streamlit as st

from ai_tools.memory_analyzer import analyze_memory, fuse_memories
from config import ALLOW_OFFLINE_FALLBACK, ORBIT_SCALE, SIZE_DISPLAY_RADIUS
from utility.traits import enrich_planet, measure_intensity

# Golden angle. Spacing successive worlds by it keeps them from lining up into
# spokes, which is the same reason sunflowers use it.
GOLDEN_ANGLE = math.pi * (3.0 - math.sqrt(5.0))


def display_radius(planet):
    return SIZE_DISPLAY_RADIUS.get(planet.get("size_class", "medium"), 1.25)


def find_non_overlapping_position(existing, orbital_radius_au, radius, attempts=80):
    """
    Find a spot on the world's orbit that isn't already occupied.

    The orbital distance is fixed by the memory's intensity, so only the angle
    is free. Walk the circle by the golden angle and take the first slot with
    real clearance; if the ring is crowded, take the roomiest slot going.
    """
    ring = max(orbital_radius_au, 0.35) * ORBIT_SCALE
    best_position, best_clearance = None, -1.0

    for step in range(attempts):
        angle = (len(existing) + step) * GOLDEN_ANGLE
        tilt = math.sin(angle * 1.7) * 1.9  # slight thickness to the disc

        candidate = (
            round(math.cos(angle) * ring, 3),
            round(tilt, 3),
            round(math.sin(angle) * ring, 3),
        )

        clearance = float("inf")
        for other in existing:
            position = other.get("position")
            if not position:
                continue
            gap = math.dist(candidate, tuple(position)) - radius - display_radius(other)
            clearance = min(clearance, gap)

        if clearance == float("inf"):
            return candidate
        if clearance > radius * 2.4:
            return candidate
        if clearance > best_clearance:
            best_position, best_clearance = candidate, clearance

    return best_position


def _finalize(design, memory_text, existing, extra=None):
    """Shared tail end of build_planet and build_fused_planet."""
    planet = dict(design)
    planet["text"] = memory_text
    planet["created_at"] = time.time()
    if extra:
        planet.update(extra)

    # Intensity has to exist before placement, since it sets the orbit.
    planet["intensity"] = measure_intensity(planet)
    planet["display_radius"] = display_radius(planet)
    planet["orbital_radius_au"] = round(0.4 + (100 - planet["intensity"]) / 100.0 * 3.2, 2)
    planet["position"] = find_non_overlapping_position(
        existing, planet["orbital_radius_au"], planet["display_radius"]
    )

    return enrich_planet(planet, index=len(existing))


def build_planet(memory_text, existing):
    """Analyze a memory and return a finished world."""
    design, source = analyze_memory(memory_text, allow_offline=ALLOW_OFFLINE_FALLBACK)
    return _finalize(design, memory_text, existing, {"source": source, "is_fusion": False})


def build_fused_planet(planet_a, planet_b, existing):
    """Merge two worlds into a third."""
    design, source = fuse_memories(planet_a, planet_b, allow_offline=ALLOW_OFFLINE_FALLBACK)

    combined_text = (
        f"{planet_a.get('title', '')} — {planet_a.get('text', '')}\n\n"
        f"{planet_b.get('title', '')} — {planet_b.get('text', '')}"
    )

    return _finalize(design, combined_text, existing, {
        "source": source,
        "is_fusion": True,
        "fusion_sources": [planet_a.get("title", "?"), planet_b.get("title", "?")],
        "fusion_story": design.get("fusion_story", ""),
    })


def format_planet_option(index):
    """Label for the fusion dropdowns."""
    planets = st.session_state.get("planets", [])
    if index >= len(planets):
        return str(index)
    planet = planets[index]
    return f"{planet.get('designation', f'MG-{index + 1:03d}')} · {planet.get('title', 'Untitled')}"
