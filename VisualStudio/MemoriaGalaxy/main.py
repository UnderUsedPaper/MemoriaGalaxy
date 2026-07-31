import hashlib
import html
import json

import streamlit as st

from ai_tools.ollama_client import is_available, model_is_pulled
from config import OLLAMA_MODEL
from ui.styles import load_styles, spectral_strip, metric_box, dossier_row, chip
from ui.galaxyrender import render_galaxy
from utility.builder import build_planet, build_fused_planet, format_planet_option
from utility.traits import enrich_all, galaxy_summary, find_constellations

# =========================
# CONFIG
# =========================

st.set_page_config(
    page_title="Memoria Galaxy",
    page_icon="✦",
    layout="wide",
    initial_sidebar_state="expanded",
)

# =========================
# SESSION STATE
# =========================

if "planets" not in st.session_state:
    st.session_state.planets = []
if "last_analysis" not in st.session_state:
    st.session_state.last_analysis = None
if "imported_hash" not in st.session_state:
    st.session_state.imported_hash = None

load_styles()

# Every planet gets its derived traits before anything is drawn. Values the AI
# chose are never overwritten, so this is safe to run on every rerun.
enrich_all(st.session_state.planets)
summary = galaxy_summary(st.session_state.planets)


def esc(value):
    return html.escape(str(value))


def label(value):
    """snake_case trait -> readable label."""
    return str(value).replace("_", " ").title()


# =========================
# HEADER
# =========================

st.markdown('<div class="eyebrow">Memory Survey · Plate 01</div>', unsafe_allow_html=True)
st.markdown("# Memoria <em>Galaxy</em>", unsafe_allow_html=True)
st.markdown(
    '<div class="main-subtitle">Write down a memory. It gets read, classified, and issued a world — '
    'palette, geology, weather, gravity, orbit, and a catalog number. What you end up with is a map '
    'of what you kept.</div>',
    unsafe_allow_html=True,
)

st.markdown(
    '<div class="metric-row">'
    + metric_box(summary["count"], "Worlds Charted")
    + metric_box(label(summary["dominant_emotion"]), "Dominant Signal")
    + metric_box(summary["themes"], "Distinct Themes")
    + metric_box(f'{summary["mean_intensity"]}', "Mean Intensity")
    + metric_box(summary["constellations"], "Constellations")
    + metric_box(summary["anomalies"], "Anomalies Logged")
    + "</div>",
    unsafe_allow_html=True,
)

# =========================
# SIDEBAR — the console
# =========================

with st.sidebar:
    # ---- MODEL STATUS ----
    if not is_available():
        st.markdown(
            '<div class="status is-offline">Offline mode<br>'
            '<span>Ollama isn\'t answering. Worlds are being designed by the built-in '
            'keyword analyzer instead. Run <code>ollama serve</code> to switch over.</span></div>',
            unsafe_allow_html=True,
        )
    elif not model_is_pulled():
        st.markdown(
            f'<div class="status is-offline">Model missing<br>'
            f'<span>Ollama is running but <code>{OLLAMA_MODEL}</code> isn\'t pulled. '
            f'Run <code>ollama pull {OLLAMA_MODEL}</code>.</span></div>',
            unsafe_allow_html=True,
        )
    else:
        st.markdown(
            f'<div class="status is-online">{OLLAMA_MODEL} · connected</div>',
            unsafe_allow_html=True,
        )

    st.markdown("## Observation")
    st.markdown("Describe a memory, a feeling, or a moment. The model reads it and designs a world that matches its shape.")

    memory_input = st.text_area(
        "Memory",
        height=170,
        placeholder="The beach at sunset after my first tournament win. Peaceful, proud, a little unreal.",
    )

    if st.button("Chart this memory", use_container_width=True):
        if memory_input.strip():
            with st.spinner("Reading the memory and building the world…"):
                try:
                    planet = build_planet(memory_input.strip(), st.session_state.planets)
                    st.session_state.planets.append(planet)
                    enrich_all(st.session_state.planets)
                    st.session_state.last_analysis = st.session_state.planets[-1]
                    st.rerun()
                except Exception as error:
                    st.error(
                        f"Couldn't build the world: {error}\n\n"
                        "Check that Ollama is running and the model is pulled."
                    )
        else:
            st.warning("Write a memory first — even one line is enough.")

    st.markdown("---")

    # ---- FUSION ----
    st.markdown("## Fusion")
    st.markdown("Merge two charted worlds into a third that carries both.")

    if len(st.session_state.planets) >= 2:
        options = list(range(len(st.session_state.planets)))
        fusion_a = st.selectbox("First world", options, format_func=format_planet_option, key="fusion_a_index")
        fusion_b = st.selectbox("Second world", options, index=1, format_func=format_planet_option, key="fusion_b_index")

        if st.button("Fuse the pair", use_container_width=True):
            if fusion_a == fusion_b:
                st.warning("Pick two different worlds.")
            else:
                with st.spinner("Fusing…"):
                    try:
                        fused = build_fused_planet(
                            st.session_state.planets[fusion_a],
                            st.session_state.planets[fusion_b],
                            st.session_state.planets,
                        )
                        st.session_state.planets.append(fused)
                        enrich_all(st.session_state.planets)
                        st.session_state.last_analysis = st.session_state.planets[-1]
                        st.rerun()
                    except Exception as error:
                        st.error(f"Fusion failed: {error}")
    else:
        st.info("Fusion opens once you've charted two worlds.")

    st.markdown("---")

    # ---- ARCHIVE ----
    st.markdown("## Archive")

    if st.session_state.planets:
        query = st.text_input("Filter", placeholder="emotion, theme, or a word").strip().lower()

        matches = [
            planet for planet in reversed(st.session_state.planets)
            if not query or query in " ".join(
                str(planet.get(field, "")) for field in ("title", "text", "emotion", "theme", "planet_type", "designation")
            ).lower()
        ]

        if not matches:
            st.markdown(
                '<div class="card-body">Nothing matches that. Try an emotion or a theme.</div>',
                unsafe_allow_html=True,
            )

        for planet in matches[:10]:
            preview = planet.get("fusion_story") if planet.get("is_fusion") else planet.get("text", "")
            preview = esc((preview or "")[:78]) + ("…" if len(preview or "") > 78 else "")
            prefix = "Fusion · " if planet.get("is_fusion") else ""
            st.markdown(
                f'<div class="archive-card">'
                f'<div class="archive-tag">{esc(planet.get("designation", ""))}</div>'
                f'<div class="archive-title">{esc(planet.get("title", "Untitled"))}</div>'
                f'<div class="archive-body">{prefix}{label(planet.get("emotion"))} · '
                f'{label(planet.get("theme"))} · {label(planet.get("planet_type"))}<br>{preview}</div>'
                f'</div>',
                unsafe_allow_html=True,
            )
    else:
        st.markdown(
            '<div class="card-body">The archive is empty. Chart a memory and it lands here.</div>',
            unsafe_allow_html=True,
        )

    st.markdown("---")

    # ---- GALAXY FILE ----
    st.markdown("## Galaxy file")

    st.download_button(
        "Download galaxy",
        data=json.dumps(st.session_state.planets, indent=2),
        file_name="memoria-galaxy.json",
        mime="application/json",
        use_container_width=True,
        disabled=not st.session_state.planets,
    )

    uploaded = st.file_uploader("Restore from file", type="json", label_visibility="collapsed")
    if uploaded is not None:
        raw = uploaded.getvalue()
        fingerprint = hashlib.sha256(raw).hexdigest()
        if fingerprint != st.session_state.imported_hash:
            try:
                restored = json.loads(raw.decode("utf-8"))
                if not isinstance(restored, list):
                    raise ValueError("expected a list of worlds")
                st.session_state.planets = restored
                st.session_state.imported_hash = fingerprint
                st.session_state.last_analysis = restored[-1] if restored else None
                enrich_all(st.session_state.planets)
                st.rerun()
            except Exception as error:
                st.error(f"That file didn't load: {error}")

    st.markdown('<div class="btn-quiet">', unsafe_allow_html=True)
    if st.button("Clear the galaxy", use_container_width=True):
        st.session_state.planets = []
        st.session_state.last_analysis = None
        st.session_state.imported_hash = None
        st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)

# =========================
# DOSSIER — the most recent world
# =========================

if st.session_state.last_analysis:
    planet = st.session_state.last_analysis

    features = "".join(chip(label(feature)) for feature in planet.get("surface_features", []))
    if planet.get("is_fusion"):
        features = chip("Fused World", "flare") + features
    if planet.get("anomaly"):
        features = chip("Anomaly", "sodium") + features
    features = chip(
        f'Designed by {OLLAMA_MODEL}' if planet.get("source") == "model" else "Designed offline",
        "plasma" if planet.get("source") == "model" else "",
    ) + features

    rows = "".join([
        dossier_row("Class", label(planet.get("planet_type"))),
        dossier_row("Size", label(planet.get("size_class", "medium"))),
        dossier_row("Radius", f'{planet.get("radius_km", 0):,} km'),
        dossier_row("Surface", label(planet.get("surface_texture"))),
        dossier_row("Core", label(planet.get("core_type"))),
        dossier_row("Gravity", f'{planet.get("gravity_g", 1.0)} g · {label(planet.get("gravity_class"))}'),
        dossier_row("Mean temp", f'{planet.get("mean_temp_c", 0)} °C'),
        dossier_row("Atmosphere", label(planet.get("atmosphere_density", "thin"))),
        dossier_row("Weather", label(planet.get("weather"))),
        dossier_row("Local hour", label(planet.get("time_of_day"))),
        dossier_row("Light", label(planet.get("luminosity"))),
        dossier_row("Rings", label(planet.get("ring_style", "none"))),
        dossier_row("Moons", f'{planet.get("moon_count", 0)} · {label(planet.get("moon_style"))}'),
        dossier_row("Orbit", label(planet.get("orbit_behavior"))),
        dossier_row("Distance", f'{planet.get("orbital_radius_au", 0)} AU'),
        dossier_row("Year", f'{planet.get("orbital_period_yr", 0)} yr'),
        dossier_row("Day", f'{planet.get("rotation_hours", 0)} hr'),
        dossier_row("Axial tilt", f'{planet.get("axial_tilt_deg", 0)}°'),
        dossier_row("Age", label(planet.get("age_class"))),
        dossier_row("Resonance", f'{planet.get("resonance_hz", 0)} Hz'),
        dossier_row("Environment", label(planet.get("environment_effect", "none"))),
        dossier_row("Intensity", f'{planet.get("intensity", 0)} / 100'),
    ])

    anomaly_block = ""
    if planet.get("anomaly"):
        anomaly_block = (
            f'<div class="anomaly"><b>{esc(label(planet["anomaly"]))}</b><br>'
            f'{esc(planet.get("anomaly_note", ""))}</div>'
        )

    fusion_block = ""
    if planet.get("is_fusion"):
        sources = " + ".join(planet.get("fusion_sources", []))
        fusion_block = (
            f'<div class="anomaly" style="border-left-color:var(--flare);background:rgba(255,61,138,0.06);">'
            f'<b style="color:var(--flare);">Fused from {esc(sources)}</b><br>'
            f'{esc(planet.get("fusion_story", ""))}</div>'
        )

    stability = planet.get("stability_pct", 0)

    st.markdown(
        f'<div class="dossier">'
        f'<div class="designation">{esc(planet.get("designation", ""))}</div>'
        f'<div class="dossier-name">{esc(planet.get("title", "Untitled"))}</div>'
        f'{spectral_strip(planet.get("palette", []))}'
        f'<div>{features}</div>'
        f'<div class="dossier-grid">{rows}</div>'
        f'<div style="margin-top:16px;">'
        f'<div class="dossier-key">Stability {stability}%</div>'
        f'<div class="meter"><span style="width:{stability}%;"></span></div></div>'
        f'{fusion_block}{anomaly_block}'
        f'</div>',
        unsafe_allow_html=True,
    )

# =========================
# CONSTELLATIONS
# =========================

constellations = find_constellations(st.session_state.planets)
if constellations:
    entries = "".join(
        dossier_row(f"{name}", f"{len(members)} worlds")
        for name, members in constellations[:6]
    )
    st.markdown(
        f'<div class="info-card">'
        f'<div class="card-heading">Constellations</div>'
        f'<div class="card-body">Worlds that share an emotion and a theme. These are the patterns '
        f'you keep coming back to.</div>'
        f'<div class="dossier-grid" style="margin-top:12px;">{entries}</div>'
        f'</div>',
        unsafe_allow_html=True,
    )

# =========================
# METHOD
# =========================

st.markdown(
    '<div class="info-card">'
    '<div class="card-heading">How a world gets made</div>'
    '<div class="card-body">'
    'Your memory goes to a local model, which picks the symbolic traits: emotion, theme, planet type, '
    'palette, surface features, rings, moons, and atmosphere. From there the survey derives the rest — '
    'intensity is read off the language you used, and gravity, light, temperature, and orbit all follow '
    'from it. Intense memories orbit close in. Quiet ones sit out at the rim. '
    'Every world is then rendered in 3D from those exact numbers, and the same memory always produces '
    'the same world. Start the memory journey below to travel the galaxy in the order you wrote things down, and turn sound on to hear each world play its own drone.'
    '</div></div>',
    unsafe_allow_html=True,
)

# =========================
# RENDER
# =========================

if st.session_state.planets:
    render_galaxy(st.session_state.planets)
else:
    st.markdown(
        '<div class="info-card" style="text-align:center;padding:56px 24px;">'
        '<div class="dossier-name" style="opacity:0.9;">No worlds charted</div>'
        '<div class="card-body" style="max-width:46ch;margin:10px auto 0;">'
        'Open the console on the left and write down one memory. The first world takes a few seconds.'
        '</div></div>',
        unsafe_allow_html=True,
    )
