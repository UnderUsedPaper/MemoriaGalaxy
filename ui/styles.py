"""
Memoria Galaxy — visual system.

Direction: a photographic survey plate from an observatory that catalogs
memories instead of stars. Deep plate-black ground, a fine measurement grid,
corner fiducial marks on every card, catalog designations, and readouts set in
mono. Boldness is spent in exactly two places — the spectral strip and the
action buttons — and everything else stays quiet.

Type: Instrument Serif for names and headlines, IBM Plex Mono for every label,
value, and control. Serif for what the memory is, mono for what we measured.
"""

import streamlit as st

STYLES = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Instrument+Serif:ital@0;1&family=IBM+Plex+Mono:wght@400;500;600;700&display=swap');

:root {
  /* plate */
  --plate:      #04050D;
  --plate-2:    #090C19;
  --plate-3:    #0E1226;
  --hairline:   rgba(126,146,214,0.16);
  --hairline-2: rgba(126,146,214,0.30);

  /* emulsion */
  --emulsion: #EAEDFF;
  --halide:   #99A2CA;
  --faint:    #626B92;

  /* spectral accents */
  --plasma: #29E7D2;
  --flare:  #FF3D8A;
  --sodium: #FFB338;
  --violet: #9B6BFF;

  --serif: 'Instrument Serif', 'Iowan Old Style', Georgia, serif;
  --mono:  'IBM Plex Mono', ui-monospace, 'SF Mono', Menlo, monospace;

  --tick: 3px;
}

/* ============================================================
   GROUND
   ============================================================ */

.stApp {
  background:
    radial-gradient(900px 620px at 12% -8%,  rgba(155,107,255,0.20), transparent 62%),
    radial-gradient(760px 560px at 88% 4%,   rgba(41,231,210,0.13),  transparent 60%),
    radial-gradient(1100px 780px at 60% 108%, rgba(255,61,138,0.11), transparent 64%),
    var(--plate);
  color: var(--emulsion);
  font-family: var(--mono);
}

/* the measurement grid — 1px lines, barely there */
.stApp::before {
  content: "";
  position: fixed;
  inset: 0;
  pointer-events: none;
  z-index: 0;
  background-image:
    linear-gradient(rgba(126,146,214,0.055) 1px, transparent 1px),
    linear-gradient(90deg, rgba(126,146,214,0.055) 1px, transparent 1px);
  background-size: 96px 96px;
  mask-image: radial-gradient(ellipse 78% 62% at 50% 34%, #000 25%, transparent 88%);
  -webkit-mask-image: radial-gradient(ellipse 78% 62% at 50% 34%, #000 25%, transparent 88%);
}

.block-container { padding-top: 2.4rem; padding-bottom: 4rem; position: relative; z-index: 1; }
#MainMenu, footer, [data-testid="stDecoration"] { visibility: hidden; }

/* ============================================================
   TYPE
   ============================================================ */

h1, h2, h3 { font-family: var(--serif) !important; font-weight: 400 !important; }

.stApp h1 {
  font-size: clamp(2.9rem, 6.2vw, 4.6rem) !important;
  line-height: 0.94 !important;
  letter-spacing: -0.022em !important;
  margin: 0 0 0.1em 0 !important;
  color: var(--emulsion) !important;
}

/* the one flourish: the last word burns */
.stApp h1 em, .title-accent {
  font-style: italic;
  background: linear-gradient(96deg, var(--plasma), var(--violet) 48%, var(--flare));
  -webkit-background-clip: text;
  background-clip: text;
  color: transparent;
}

.eyebrow {
  font-family: var(--mono);
  font-size: 0.66rem;
  font-weight: 600;
  letter-spacing: 0.28em;
  text-transform: uppercase;
  color: var(--faint);
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 14px;
}
.eyebrow::after {
  content: "";
  flex: 1;
  height: 1px;
  background: linear-gradient(90deg, var(--hairline-2), transparent);
}

.main-subtitle {
  font-family: var(--mono);
  font-size: 0.94rem;
  line-height: 1.72;
  color: var(--halide);
  max-width: 62ch;
  margin: 14px 0 30px 0;
}

/* ============================================================
   PLATE CARDS — hairline box, fiducial corners, no glass blur
   ============================================================ */

.info-card, .archive-card, .metric-box, .dossier {
  position: relative;
  background:
    linear-gradient(180deg, rgba(255,255,255,0.035), rgba(255,255,255,0.012)),
    var(--plate-2);
  border: 1px solid var(--hairline);
  border-radius: 4px;
}

/* the fiducial marks — two opposing corner brackets, like a real survey plate */
.info-card::before, .info-card::after,
.metric-box::before, .metric-box::after,
.dossier::before, .dossier::after {
  content: "";
  position: absolute;
  width: 9px;
  height: 9px;
  opacity: 0.5;
  pointer-events: none;
}
.info-card::before, .metric-box::before, .dossier::before {
  top: 6px; left: 6px;
  border-top: 1px solid var(--plasma);
  border-left: 1px solid var(--plasma);
}
.info-card::after, .metric-box::after, .dossier::after {
  bottom: 6px; right: 6px;
  border-bottom: 1px solid var(--flare);
  border-right: 1px solid var(--flare);
}

.info-card, .dossier { padding: 22px 24px; margin: 18px 0; }

/* ============================================================
   READOUTS
   ============================================================ */

.metric-row {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
  gap: 12px;
  margin: 8px 0 26px 0;
}

.metric-box {
  padding: 18px 18px 16px 18px;
  overflow: hidden;
  transition: border-color 160ms ease, transform 160ms ease;
}
.metric-box:hover { border-color: var(--hairline-2); transform: translateY(-2px); }

/* spectral tick along the top edge */
.metric-box > .tick {
  position: absolute;
  top: 0; left: 0; right: 0;
  height: var(--tick);
  background: linear-gradient(90deg, var(--plasma), var(--violet) 55%, var(--flare));
  opacity: 0.9;
}

.metric-value {
  font-family: var(--serif);
  font-size: 2.35rem;
  line-height: 1;
  letter-spacing: -0.02em;
  color: var(--emulsion);
  font-variant-numeric: tabular-nums;
  margin-bottom: 9px;
}

.metric-label {
  font-family: var(--mono);
  font-size: 0.6rem;
  font-weight: 600;
  letter-spacing: 0.2em;
  text-transform: uppercase;
  color: var(--faint);
}

/* ============================================================
   SPECTRAL STRIP — the signature element.
   Each world's palette, printed as a literal spectrum.
   ============================================================ */

.spectral-strip {
  height: 7px;
  border-radius: 2px;
  margin: 12px 0 16px 0;
  position: relative;
  box-shadow: 0 0 22px -6px currentColor;
}
.spectral-strip::after {
  content: "";
  position: absolute;
  inset: 0;
  background: repeating-linear-gradient(90deg, rgba(4,5,13,0.55) 0 1px, transparent 1px 9px);
  border-radius: inherit;
}

/* ============================================================
   DOSSIER TABLE — the ephemeris readout
   ============================================================ */

.dossier-name {
  font-family: var(--serif);
  font-size: 1.85rem;
  line-height: 1.08;
  letter-spacing: -0.015em;
  color: var(--emulsion);
  margin-bottom: 4px;
}

.designation {
  font-family: var(--mono);
  font-size: 0.68rem;
  font-weight: 600;
  letter-spacing: 0.16em;
  color: var(--plasma);
}

.dossier-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(184px, 1fr));
  gap: 0 26px;
  margin-top: 6px;
}

.dossier-row {
  display: flex;
  align-items: baseline;
  gap: 8px;
  padding: 7px 0;
  border-bottom: 1px dotted rgba(126,146,214,0.18);
}
.dossier-key {
  font-size: 0.63rem;
  font-weight: 600;
  letter-spacing: 0.15em;
  text-transform: uppercase;
  color: var(--faint);
  white-space: nowrap;
}
.dossier-key::after {
  content: "";
  display: inline-block;
}
.dossier-row .spacer { flex: 1; border-bottom: 1px dotted rgba(126,146,214,0.14); }
.dossier-val {
  font-size: 0.82rem;
  font-weight: 500;
  color: var(--emulsion);
  font-variant-numeric: tabular-nums;
  text-align: right;
}

/* ============================================================
   CHIPS
   ============================================================ */

.chip {
  display: inline-block;
  font-family: var(--mono);
  font-size: 0.62rem;
  font-weight: 600;
  letter-spacing: 0.13em;
  text-transform: uppercase;
  padding: 4px 10px;
  border-radius: 2px;
  border: 1px solid var(--hairline-2);
  color: var(--halide);
  margin: 0 6px 6px 0;
}
.chip.is-plasma { color: var(--plasma); border-color: rgba(41,231,210,0.42); background: rgba(41,231,210,0.08); }
.chip.is-flare  { color: var(--flare);  border-color: rgba(255,61,138,0.42);  background: rgba(255,61,138,0.09); }
.chip.is-sodium { color: var(--sodium); border-color: rgba(255,179,56,0.42);  background: rgba(255,179,56,0.09); }

.anomaly {
  margin-top: 16px;
  padding: 12px 14px;
  border-left: 2px solid var(--sodium);
  background: rgba(255,179,56,0.06);
  font-size: 0.82rem;
  line-height: 1.62;
  color: var(--halide);
}
.anomaly b { color: var(--sodium); letter-spacing: 0.1em; text-transform: uppercase; font-size: 0.66rem; }

/* stability bar */
.meter { height: 4px; background: rgba(126,146,214,0.16); border-radius: 2px; overflow: hidden; margin-top: 6px; }
.meter > span { display: block; height: 100%; background: linear-gradient(90deg, var(--plasma), var(--violet)); }

/* ============================================================
   ARCHIVE
   ============================================================ */

.archive-card {
  padding: 13px 14px;
  margin-bottom: 9px;
  border-left: 2px solid var(--hairline-2);
  border-radius: 0 4px 4px 0;
  transition: border-left-color 150ms ease, background 150ms ease, transform 150ms ease;
}
.archive-card:hover {
  border-left-color: var(--plasma);
  background: linear-gradient(90deg, rgba(41,231,210,0.07), rgba(255,255,255,0.012));
  transform: translateX(3px);
}
.archive-tag {
  font-size: 0.58rem;
  font-weight: 600;
  letter-spacing: 0.15em;
  text-transform: uppercase;
  color: var(--faint);
  margin-bottom: 6px;
}
.archive-title {
  font-family: var(--serif);
  font-size: 1.12rem;
  line-height: 1.2;
  color: var(--emulsion);
  margin-bottom: 4px;
}
.archive-body { font-size: 0.76rem; line-height: 1.58; color: var(--halide); }

.card-heading {
  font-family: var(--mono);
  font-size: 0.63rem;
  font-weight: 700;
  letter-spacing: 0.22em;
  text-transform: uppercase;
  color: var(--faint);
  margin-bottom: 12px;
}
.card-body { color: var(--halide); line-height: 1.74; font-size: 0.88rem; }

/* ============================================================
   BUTTONS — the second place boldness is spent
   ============================================================ */

.stButton > button,
.stDownloadButton > button {
  position: relative;
  overflow: hidden;
  width: 100%;
  font-family: var(--mono) !important;
  font-size: 0.74rem !important;
  font-weight: 700 !important;
  letter-spacing: 0.15em !important;
  text-transform: uppercase !important;
  padding: 0.78rem 1.1rem !important;
  border-radius: 3px !important;
  border: none !important;
  color: #05060F !important;
  background: linear-gradient(112deg, var(--plasma) 0%, var(--violet) 52%, var(--flare) 100%) !important;
  background-size: 190% 100% !important;
  background-position: 0% 50% !important;
  box-shadow:
    0 0 0 1px rgba(41,231,210,0.55),
    0 10px 26px -10px rgba(255,61,138,0.75),
    0 6px 30px -14px rgba(41,231,210,0.9) !important;
  transition: transform 140ms cubic-bezier(.2,.8,.3,1),
              box-shadow 180ms ease,
              background-position 460ms ease !important;
}

/* light sweep on hover */
.stButton > button::after,
.stDownloadButton > button::after {
  content: "";
  position: absolute;
  top: 0; left: -70%;
  width: 45%; height: 100%;
  background: linear-gradient(100deg, transparent, rgba(255,255,255,0.55), transparent);
  transform: skewX(-18deg);
  transition: left 620ms cubic-bezier(.2,.8,.3,1);
}

.stButton > button:hover,
.stDownloadButton > button:hover {
  transform: translateY(-2px);
  background-position: 100% 50% !important;
  box-shadow:
    0 0 0 1px rgba(41,231,210,0.85),
    0 16px 34px -10px rgba(255,61,138,0.9),
    0 0 46px -12px rgba(41,231,210,0.95) !important;
}
.stButton > button:hover::after,
.stDownloadButton > button:hover::after { left: 130%; }

.stButton > button:active,
.stDownloadButton > button:active { transform: translateY(0); }

.stButton > button:focus-visible,
.stDownloadButton > button:focus-visible {
  outline: 2px solid var(--sodium) !important;
  outline-offset: 3px !important;
}

/* quieter secondary action, so the primary keeps its weight */
.btn-quiet .stButton > button {
  background: transparent !important;
  color: var(--halide) !important;
  border: 1px solid var(--hairline-2) !important;
  box-shadow: none !important;
}
.btn-quiet .stButton > button:hover {
  color: var(--flare) !important;
  border-color: rgba(255,61,138,0.55) !important;
  background: rgba(255,61,138,0.07) !important;
  box-shadow: none !important;
}
.btn-quiet .stButton > button::after { display: none; }

/* ============================================================
   SIDEBAR — the console
   ============================================================ */

[data-testid="stSidebar"] {
  background: linear-gradient(180deg, var(--plate-3), var(--plate)) !important;
  border-right: 1px solid var(--hairline);
}
[data-testid="stSidebar"] .block-container { padding-top: 1.6rem; }
[data-testid="stSidebar"] h2 {
  font-family: var(--mono) !important;
  font-size: 0.68rem !important;
  font-weight: 700 !important;
  letter-spacing: 0.24em !important;
  text-transform: uppercase !important;
  color: var(--plasma) !important;
  margin-bottom: 6px !important;
}
[data-testid="stSidebar"] p { color: var(--halide); font-size: 0.79rem; line-height: 1.66; }
[data-testid="stSidebar"] hr { border-color: var(--hairline); margin: 22px 0; }

/* connection status — plain statement of fact, not an alarm */
.status {
  font-family: var(--mono);
  font-size: 0.62rem;
  font-weight: 600;
  letter-spacing: 0.15em;
  text-transform: uppercase;
  padding: 10px 12px;
  border-radius: 3px;
  margin-bottom: 18px;
  border: 1px solid var(--hairline);
}
.status span {
  display: block;
  margin-top: 7px;
  font-weight: 400;
  font-size: 0.68rem;
  letter-spacing: 0.02em;
  text-transform: none;
  line-height: 1.6;
  color: var(--halide);
}
.status code {
  background: rgba(4,5,13,0.7);
  border: 1px solid var(--hairline);
  border-radius: 2px;
  padding: 1px 5px;
  color: var(--emulsion);
}
.status.is-online  { color: var(--plasma); border-color: rgba(41,231,210,0.38); background: rgba(41,231,210,0.07); }
.status.is-offline { color: var(--sodium); border-color: rgba(255,179,56,0.38); background: rgba(255,179,56,0.06); }

/* ============================================================
   INPUTS
   ============================================================ */

.stTextArea textarea, .stTextInput input {
  background: rgba(4,5,13,0.72) !important;
  border: 1px solid var(--hairline) !important;
  border-radius: 3px !important;
  color: var(--emulsion) !important;
  font-family: var(--mono) !important;
  font-size: 0.83rem !important;
  line-height: 1.66 !important;
  transition: border-color 150ms ease, box-shadow 150ms ease;
}
.stTextArea textarea:focus, .stTextInput input:focus {
  border-color: var(--plasma) !important;
  box-shadow: 0 0 0 3px rgba(41,231,210,0.14) !important;
}
.stTextArea textarea::placeholder { color: var(--faint) !important; font-style: italic; }

label, .stSelectbox label, .stTextArea label {
  font-family: var(--mono) !important;
  font-size: 0.6rem !important;
  font-weight: 600 !important;
  letter-spacing: 0.2em !important;
  text-transform: uppercase !important;
  color: var(--faint) !important;
}

[data-baseweb="select"] > div {
  background: rgba(4,5,13,0.72) !important;
  border: 1px solid var(--hairline) !important;
  border-radius: 3px !important;
  font-family: var(--mono) !important;
  font-size: 0.8rem !important;
  color: var(--emulsion) !important;
}
[data-baseweb="select"] > div:hover { border-color: var(--hairline-2) !important; }
[data-baseweb="popover"] li { font-family: var(--mono) !important; font-size: 0.8rem !important; }

/* ============================================================
   MESSAGES
   ============================================================ */

[data-testid="stAlert"], .stAlert {
  background: rgba(9,12,25,0.9) !important;
  border: 1px solid var(--hairline) !important;
  border-left: 2px solid var(--plasma) !important;
  border-radius: 0 3px 3px 0 !important;
  font-family: var(--mono) !important;
  font-size: 0.78rem !important;
  color: var(--halide) !important;
}

.stExpander {
  border: 1px solid var(--hairline) !important;
  border-radius: 4px !important;
  background: rgba(9,12,25,0.6) !important;
}
.stExpander summary { font-family: var(--mono) !important; font-size: 0.72rem !important; letter-spacing: 0.14em; text-transform: uppercase; }

hr { border-color: var(--hairline); }

::-webkit-scrollbar { width: 9px; height: 9px; }
::-webkit-scrollbar-track { background: var(--plate); }
::-webkit-scrollbar-thumb { background: rgba(126,146,214,0.26); border-radius: 0; }
::-webkit-scrollbar-thumb:hover { background: var(--plasma); }

::selection { background: rgba(255,61,138,0.32); color: var(--emulsion); }

/* ============================================================
   RESPONSIVE + REDUCED MOTION
   ============================================================ */

@media (max-width: 640px) {
  .metric-row { grid-template-columns: repeat(2, 1fr); }
  .metric-value { font-size: 1.8rem; }
  .dossier-grid { grid-template-columns: 1fr; }
}

@media (prefers-reduced-motion: reduce) {
  *, *::before, *::after {
    animation-duration: 0.001ms !important;
    transition-duration: 0.001ms !important;
  }
  .stButton > button::after, .stDownloadButton > button::after { display: none; }
}
</style>
"""


def load_styles():
    """Inject the stylesheet. Call once, right after set_page_config."""
    st.markdown(STYLES, unsafe_allow_html=True)


# ---------------------------------------------------------
# Small HTML builders, so main.py stays readable
# ---------------------------------------------------------

def spectral_strip(palette):
    """The signature element: a world's palette printed as a spectrum."""
    colors = list(palette)[:3] or ["#29E7D2", "#9B6BFF", "#FF3D8A"]
    while len(colors) < 3:
        colors.append(colors[-1])
    stops = f"{colors[0]}, {colors[1]} 50%, {colors[2]}"
    return (
        f'<div class="spectral-strip" style="background:linear-gradient(90deg,{stops});'
        f'color:{colors[1]};"></div>'
    )


def metric_box(value, label):
    return (
        f'<div class="metric-box"><div class="tick"></div>'
        f'<div class="metric-value">{value}</div>'
        f'<div class="metric-label">{label}</div></div>'
    )


def dossier_row(key, value):
    return (
        f'<div class="dossier-row"><span class="dossier-key">{key}</span>'
        f'<span class="spacer"></span><span class="dossier-val">{value}</span></div>'
    )


def chip(text, tone=""):
    tone_class = f" is-{tone}" if tone else ""
    return f'<span class="chip{tone_class}">{text}</span>'
