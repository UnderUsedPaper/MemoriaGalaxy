"""
The 3D galaxy.

Nothing here is decorative. Every mesh, colour, and speed is read off a trait
the analyzer or the derivation set, so two worlds only look alike if the
memories behind them were alike:

  palette + surface_features + surface_texture -> the painted surface map
  luminosity                                   -> emissive strength
  atmosphere_density                           -> the glow shell
  ring_style (+ ring_gap anomaly)              -> rings
  moon_count + moon_style                      -> moon arrangement
  axial_tilt_deg / rotation_hours              -> tilt and spin
  environment_effect                           -> the particle field
  orbital_radius_au                            -> distance from the core
  anomaly                                      -> one extra, strange object
"""

import hashlib
import html
import json

import streamlit.components.v1 as components

RENDER_HEIGHT = 780


def _seed(planet):
    basis = f'{planet.get("designation", "")}|{planet.get("title", "")}'
    return int(hashlib.sha256(basis.encode("utf-8")).hexdigest()[:8], 16)


def _spec(planet):
    """
    The slice of a planet the renderer actually needs.

    Anything that ends up in innerHTML on the JS side is escaped here. The
    memory text is whatever the person typed, so it gets the same treatment as
    any other untrusted string.
    """
    palette = planet.get("palette") or ["#29E7D2", "#9B6BFF", "#FF3D8A"]
    safe = lambda value: html.escape(str(value or ""))
    return {
        "seed": _seed(planet),
        "designation": safe(planet.get("designation", "")),
        "title": safe(planet.get("title", "Untitled")),
        "emotion": planet.get("emotion", "calm"),
        "theme": planet.get("theme", "unknown"),
        "type": planet.get("planet_type", "rocky"),
        "palette": list(palette)[:3],
        "features": planet.get("surface_features", []),
        "texture": planet.get("surface_texture", "smooth"),
        "ring": planet.get("ring_style", "none"),
        "moons": int(planet.get("moon_count", 0) or 0),
        "moonStyle": planet.get("moon_style", "none"),
        "atmosphere": planet.get("atmosphere_density", "thin"),
        "environment": planet.get("environment_effect", "none"),
        "luminosity": planet.get("luminosity", "soft"),
        "weather": planet.get("weather", "clear"),
        "gravity": planet.get("gravity_g", 1.0),
        "temp": planet.get("mean_temp_c", 0),
        "tilt": planet.get("axial_tilt_deg", 0),
        "rotation": planet.get("rotation_hours", 24),
        "intensity": planet.get("intensity", 50),
        "stability": planet.get("stability_pct", 100),
        "anomaly": planet.get("anomaly"),
        "isFusion": bool(planet.get("is_fusion")),
        "radius": planet.get("display_radius", 1.25),
        "position": planet.get("position") or [0, 0, 0],
        "orbit": planet.get("orbital_radius_au", 1.5),
        "group": f'{planet.get("emotion", "")}/{planet.get("theme", "")}',
        # the journey reads the memory itself back to you
        "text": safe((planet.get("text") or "")[:520]),
        "createdAt": planet.get("created_at", 0),
        "core": planet.get("core_type", "molten"),
        "hour": planet.get("time_of_day", "noon"),
        "orbitStyle": planet.get("orbit_behavior", "steady"),
        "age": planet.get("age_class", "settled"),
        "resonance": planet.get("resonance_hz", 110.0),
        "fusionStory": safe(planet.get("fusion_story", "")),
        "fusionSources": [safe(x) for x in planet.get("fusion_sources", [])],
    }


def render_galaxy(planets, height=RENDER_HEIGHT):
    """Draw the galaxy. Safe to call with an empty list."""
    payload = json.dumps([_spec(p) for p in planets])
    components.html(_TEMPLATE.replace("__PLANETS__", payload), height=height, scrolling=False)


_TEMPLATE = r"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Instrument+Serif&family=IBM+Plex+Mono:wght@400;600;700&display=swap');

* { box-sizing: border-box; }
html, body { margin:0; padding:0; background:transparent; overflow:hidden; }

#wrap {
  position: relative;
  width: 100%;
  height: 100vh;
  border: 1px solid rgba(126,146,214,0.16);
  border-radius: 4px;
  overflow: hidden;
  background: #04050D;
  font-family: 'IBM Plex Mono', ui-monospace, monospace;
}
#scene { display:block; width:100%; height:100%; cursor: grab; }
#scene:active { cursor: grabbing; }

/* fiducial marks, same language as the page */
.fid { position:absolute; width:11px; height:11px; pointer-events:none; opacity:.55; z-index:3; }
.fid.tl { top:8px; left:8px;  border-top:1px solid #29E7D2; border-left:1px solid #29E7D2; }
.fid.br { bottom:8px; right:8px; border-bottom:1px solid #FF3D8A; border-right:1px solid #FF3D8A; }

#hud {
  position:absolute; left:16px; bottom:16px; z-index:4;
  width: min(310px, 46%);
  padding:14px 16px;
  background: rgba(9,12,25,0.92);
  border:1px solid rgba(126,146,214,0.22);
  border-left:2px solid #29E7D2;
  border-radius:0 4px 4px 0;
  opacity:0; transform: translateY(6px);
  transition: opacity 180ms ease, transform 180ms ease;
  pointer-events:none;
}
#hud.on { opacity:1; transform:none; }
#hud .desig { font-size:.6rem; font-weight:700; letter-spacing:.16em; color:#29E7D2; }
#hud .name  { font-family:'Instrument Serif',Georgia,serif; font-size:1.5rem; line-height:1.1; color:#EAEDFF; margin:3px 0 9px; }
#hud .strip { height:5px; border-radius:2px; margin-bottom:10px; }
#hud .row   { display:flex; justify-content:space-between; gap:10px; padding:3px 0; font-size:.68rem; }
#hud .k     { color:#626B92; letter-spacing:.13em; text-transform:uppercase; }
#hud .v     { color:#EAEDFF; }
#hud .anom  { margin-top:9px; padding-top:8px; border-top:1px dotted rgba(126,146,214,.25); font-size:.66rem; color:#FFB338; letter-spacing:.1em; text-transform:uppercase; }

#hint {
  position:absolute; top:14px; right:16px; z-index:4;
  font-size:.58rem; letter-spacing:.18em; text-transform:uppercase; color:#626B92;
  text-align:right; line-height:1.9; pointer-events:none;
}
#count {
  position:absolute; top:14px; left:18px; z-index:4;
  font-size:.58rem; letter-spacing:.2em; text-transform:uppercase; color:#626B92;
}
#count b { color:#29E7D2; font-weight:600; }
/* ---- audio toggle ---- */
#audio {
  position:absolute; top:12px; right:16px; z-index:6;
  display:flex; align-items:center; gap:7px;
  padding:7px 11px; cursor:pointer;
  background:rgba(9,12,25,0.9);
  border:1px solid rgba(126,146,214,0.22); border-radius:3px;
  font-family:'IBM Plex Mono',monospace; font-size:.56rem; font-weight:700;
  letter-spacing:.18em; text-transform:uppercase; color:#626B92;
  transition:color 150ms ease, border-color 150ms ease;
}
#audio:hover { color:#EAEDFF; border-color:rgba(126,146,214,0.45); }
#audio.on { color:#29E7D2; border-color:rgba(41,231,210,0.5); background:rgba(41,231,210,0.08); }
#audio .bars { display:flex; align-items:flex-end; gap:2px; height:11px; }
#audio .bars i { width:2px; background:currentColor; height:3px; border-radius:1px; }
#audio.on .bars i { animation:eq 900ms ease-in-out infinite; }
#audio.on .bars i:nth-child(2) { animation-delay:150ms; }
#audio.on .bars i:nth-child(3) { animation-delay:320ms; }
#audio.on .bars i:nth-child(4) { animation-delay:90ms; }
@keyframes eq { 0%,100%{height:3px;} 50%{height:11px;} }

/* ---- journey ---- */
#start {
  position:absolute; left:50%; bottom:22px; transform:translateX(-50%); z-index:6;
  padding:11px 20px; cursor:pointer;
  background:linear-gradient(112deg,#29E7D2,#9B6BFF 52%,#FF3D8A);
  border:none; border-radius:3px; color:#05060F;
  font-family:'IBM Plex Mono',monospace; font-size:.62rem; font-weight:700;
  letter-spacing:.19em; text-transform:uppercase;
  box-shadow:0 0 0 1px rgba(41,231,210,.5), 0 10px 26px -10px rgba(255,61,138,.7);
  transition:transform 140ms ease, box-shadow 180ms ease;
}
#start:hover { transform:translateX(-50%) translateY(-2px);
               box-shadow:0 0 0 1px rgba(41,231,210,.9), 0 16px 34px -10px rgba(255,61,138,.9); }
#start[disabled] { display:none; }

#journeybar {
  position:absolute; left:50%; bottom:20px; transform:translateX(-50%) translateY(8px);
  z-index:6; display:none; align-items:center; gap:14px;
  padding:9px 14px;
  background:rgba(9,12,25,0.94);
  border:1px solid rgba(126,146,214,0.24); border-radius:3px;
  font-family:'IBM Plex Mono',monospace;
  opacity:0; transition:opacity 220ms ease, transform 220ms ease;
}
#journeybar.on { display:flex; opacity:1; transform:translateX(-50%); }
#journeybar button {
  background:none; border:1px solid rgba(126,146,214,0.28); border-radius:2px;
  color:#99A2CA; cursor:pointer; padding:5px 9px;
  font-family:inherit; font-size:.62rem; letter-spacing:.1em;
  transition:color 140ms ease, border-color 140ms ease;
}
#journeybar button:hover { color:#29E7D2; border-color:rgba(41,231,210,0.5); }
#journeybar .pos { font-size:.58rem; letter-spacing:.18em; text-transform:uppercase; color:#626B92; }
#journeybar .pos b { color:#29E7D2; }
#journeybar .exit { color:#FF3D8A; border-color:rgba(255,61,138,0.35); }
#journeybar .exit:hover { color:#FF3D8A; border-color:rgba(255,61,138,0.8); }

#progress {
  position:absolute; left:0; right:0; bottom:0; height:2px; z-index:6;
  background:rgba(126,146,214,0.12); display:none;
}
#progress.on { display:block; }
#progress > i { display:block; height:100%; width:0;
                background:linear-gradient(90deg,#29E7D2,#9B6BFF,#FF3D8A); }

#journeycard {
  position:absolute; top:52px; right:16px; z-index:5;
  width:min(340px, 42%); max-height:calc(100% - 130px); overflow:hidden;
  padding:18px 20px;
  background:rgba(9,12,25,0.94);
  border:1px solid rgba(126,146,214,0.22);
  border-left:2px solid #9B6BFF; border-radius:0 4px 4px 0;
  opacity:0; transform:translateX(14px); pointer-events:none;
  transition:opacity 420ms ease, transform 420ms ease;
  font-family:'IBM Plex Mono',monospace;
}
#journeycard.on { opacity:1; transform:none; }
#journeycard .step { font-size:.55rem; letter-spacing:.22em; text-transform:uppercase; color:#626B92; }
#journeycard .desig { font-size:.6rem; font-weight:700; letter-spacing:.16em; color:#9B6BFF; margin-top:8px; }
#journeycard .name { font-family:'Instrument Serif',Georgia,serif; font-size:1.75rem;
                     line-height:1.08; color:#EAEDFF; margin:4px 0 10px; }
#journeycard .strip { height:6px; border-radius:2px; margin-bottom:14px; }
#journeycard .memory {
  font-size:.76rem; line-height:1.78; color:#99A2CA;
  border-left:1px solid rgba(126,146,214,0.28); padding-left:12px; margin-bottom:14px;
  max-height:180px; overflow:hidden;
}
#journeycard .tags { display:flex; flex-wrap:wrap; gap:5px; }
#journeycard .tag { font-size:.55rem; letter-spacing:.13em; text-transform:uppercase;
                    color:#99A2CA; border:1px solid rgba(126,146,214,0.28);
                    border-radius:2px; padding:3px 7px; }

#empty {
  position:absolute; inset:0; display:flex; align-items:center; justify-content:center;
  color:#626B92; font-size:.66rem; letter-spacing:.2em; text-transform:uppercase; z-index:2;
}
</style>

<div id="wrap">
  <canvas id="scene"></canvas>
  <div class="fid tl"></div><div class="fid br"></div>
  <div id="count"></div>
  <div id="hint">drag to orbit &middot; scroll to zoom<br>click a world to focus<br>space pause &middot; &larr; &rarr; step &middot; esc exit</div>
  <div id="hud"></div>

  <div id="audio" title="Each world plays its own drone, built from its traits">
    <span class="bars"><i></i><i></i><i></i><i></i></span><span id="audiolabel">Sound off</span>
  </div>

  <button id="start">Begin memory journey</button>

  <div id="journeycard"></div>

  <div id="journeybar">
    <button id="prev">&#9664;</button>
    <button id="toggle">&#9208;</button>
    <button id="next">&#9654;</button>
    <span class="pos" id="pos"></span>
    <button class="exit" id="exit">Exit</button>
  </div>
  <div id="progress"><i></i></div>
</div>

<script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
<script>
(function () {
  var PLANETS = __PLANETS__;

  var wrap = document.getElementById('wrap');
  var canvas = document.getElementById('scene');
  var hud = document.getElementById('hud');
  document.getElementById('count').innerHTML = '<b>' + PLANETS.length + '</b> worlds charted';

  if (!window.THREE) {
    wrap.insertAdjacentHTML('beforeend', '<div id="empty">renderer unavailable &mdash; check your connection</div>');
    return;
  }
  if (!PLANETS.length) {
    wrap.insertAdjacentHTML('beforeend', '<div id="empty">no worlds charted yet</div>');
    return;
  }

  /* ---------------------------------------------------------
     seeded randomness, so a world looks the same every reload
     --------------------------------------------------------- */
  function rand(seed) {
    var a = seed >>> 0;
    return function () {
      a |= 0; a = (a + 0x6D2B79F5) | 0;
      var t = Math.imul(a ^ (a >>> 15), 1 | a);
      t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t;
      return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
    };
  }
  function rgba(hex, alpha) {
    var h = (hex || '#888888').replace('#', '');
    if (h.length === 3) h = h[0]+h[0]+h[1]+h[1]+h[2]+h[2];
    var n = parseInt(h, 16);
    return 'rgba(' + ((n>>16)&255) + ',' + ((n>>8)&255) + ',' + (n&255) + ',' + alpha + ')';
  }

  /* ---------------------------------------------------------
     AUDIO — every world plays itself

     Nothing is sampled. Each drone is built live from the world's own
     numbers, so the sound is as derived as the surface is:

       resonance_hz       -> the fundamental the drone sits on
       emotion            -> the mode the melody notes come from
       planet_type        -> timbre (waveform, detune, filter shape)
       intensity          -> how often notes arrive
       atmosphere_density -> reverb length
       luminosity         -> filter brightness
       stability_pct      -> pitch drift; unstable worlds wander
       weather            -> the noise layer underneath
     --------------------------------------------------------- */

  var MODES = {
    happy:     [0, 2, 4, 7, 9],            // major pentatonic
    calm:      [0, 2, 5, 7, 10],           // open and suspended
    sad:       [0, 2, 3, 5, 7, 8, 10],     // aeolian
    nostalgic: [0, 2, 3, 5, 7, 9, 10],     // dorian
    angry:     [0, 1, 4, 5, 7, 8, 11],     // phrygian dominant
    anxious:   [0, 2, 4, 6, 8, 10]         // whole tone, no home note
  };

  var TIMBRE = {
    rocky:       { wave: 'triangle', detune: 6,  cutoff: 1100, q: 2,  attack: 0.6 },
    oceanic:     { wave: 'sine',     detune: 4,  cutoff: 820,  q: 4,  attack: 1.4 },
    icy:         { wave: 'sine',     detune: 11, cutoff: 2600, q: 8,  attack: 0.25 },
    volcanic:    { wave: 'sawtooth', detune: 14, cutoff: 640,  q: 6,  attack: 0.35 },
    gaseous:     { wave: 'sine',     detune: 8,  cutoff: 700,  q: 2,  attack: 2.2 },
    forest:      { wave: 'triangle', detune: 5,  cutoff: 1400, q: 3,  attack: 0.9 },
    crystalline: { wave: 'square',   detune: 3,  cutoff: 3200, q: 12, attack: 0.05 },
    desert:      { wave: 'sawtooth', detune: 17, cutoff: 900,  q: 3,  attack: 1.0 },
    storm:       { wave: 'sawtooth', detune: 22, cutoff: 560,  q: 5,  attack: 0.5 }
  };

  var REVERB_SECONDS = { none: 0.5, thin: 1.5, medium: 2.8, thick: 4.6 };
  var BRIGHTNESS = { dim: 0.55, soft: 1.0, radiant: 1.7, blinding: 2.6 };
  var WEATHER_BED = {
    clear:           null,
    static_calm:     null,
    warm_drizzle:    { type: 'lowpass',  freq: 900,  gain: 0.030, wobble: 0.4 },
    ion_rain:        { type: 'bandpass', freq: 3200, gain: 0.026, wobble: 6.0 },
    perpetual_storm: { type: 'lowpass',  freq: 320,  gain: 0.062, wobble: 0.7 },
    ash_fall:        { type: 'lowpass',  freq: 520,  gain: 0.040, wobble: 0.25 },
    whiteout:        { type: 'highpass', freq: 2400, gain: 0.024, wobble: 0.15 },
    aurora_veil:     { type: 'bandpass', freq: 1600, gain: 0.022, wobble: 1.6 }
  };

  var Audio = (function () {
    var ctx = null, master = null, wet = null, enabled = false;
    var voice = null, timer = null;

    function noiseBuffer(seconds, decay) {
      var len = Math.max(1, Math.floor(ctx.sampleRate * seconds));
      var buf = ctx.createBuffer(2, len, ctx.sampleRate);
      for (var c = 0; c < 2; c++) {
        var data = buf.getChannelData(c);
        for (var i = 0; i < len; i++) {
          data[i] = (Math.random() * 2 - 1) * Math.pow(1 - i / len, decay);
        }
      }
      return buf;
    }

    function boot() {
      if (ctx) return true;
      var AC = window.AudioContext || window.webkitAudioContext;
      if (!AC) return false;
      ctx = new AC();
      master = ctx.createGain();
      master.gain.value = 0.0;
      master.connect(ctx.destination);
      wet = ctx.createGain();
      wet.gain.value = 0.5;
      wet.connect(master);
      return true;
    }

    function stopVoice(fade) {
      if (!voice) return;
      var dying = voice;
      voice = null;
      if (timer) { clearInterval(timer); timer = null; }
      var t = ctx.currentTime;
      dying.gain.gain.cancelScheduledValues(t);
      dying.gain.gain.setValueAtTime(dying.gain.gain.value, t);
      dying.gain.gain.linearRampToValueAtTime(0.0001, t + (fade || 1.2));
      setTimeout(function () {
        dying.sources.forEach(function (s) { try { s.stop(); } catch (e) {} });
        try { dying.gain.disconnect(); } catch (e) {}
      }, (fade || 1.2) * 1000 + 120);
    }

    function build(p) {
      var t = ctx.currentTime;
      var tone = TIMBRE[p.type] || TIMBRE.rocky;
      var root = Math.max(38, Math.min(180, p.resonance));
      var drift = (100 - p.stability) / 100;

      var out = ctx.createGain();
      out.gain.value = 0.0001;
      out.connect(master);

      // reverb sized by how much atmosphere there is to bounce around in
      var verb = ctx.createConvolver();
      var secs = REVERB_SECONDS[p.atmosphere] !== undefined ? REVERB_SECONDS[p.atmosphere] : 2.0;
      verb.buffer = noiseBuffer(secs, 2.4);
      var send = ctx.createGain();
      send.gain.value = 0.28 + secs * 0.07;
      verb.connect(wet);
      send.connect(verb);

      var filter = ctx.createBiquadFilter();
      filter.type = 'lowpass';
      filter.frequency.value = tone.cutoff * (BRIGHTNESS[p.luminosity] || 1);
      filter.Q.value = tone.q * 0.25;
      filter.connect(out);
      filter.connect(send);

      var sources = [];

      // the drone: root, fifth, octave
      [1, 1.5, 2].forEach(function (mult, i) {
        var osc = ctx.createOscillator();
        osc.type = tone.wave;
        osc.frequency.value = root * mult;
        osc.detune.value = (i - 1) * tone.detune;
        var g = ctx.createGain();
        g.gain.value = [0.20, 0.10, 0.06][i];
        osc.connect(g); g.connect(filter);
        osc.start(t);
        sources.push(osc);

        // unstable worlds wander off pitch
        if (drift > 0.15) {
          var lfo = ctx.createOscillator();
          lfo.frequency.value = 0.05 + drift * 0.4;
          var depth = ctx.createGain();
          depth.gain.value = drift * 22;
          lfo.connect(depth); depth.connect(osc.detune);
          lfo.start(t);
          sources.push(lfo);
        }
      });

      // weather bed
      var bed = WEATHER_BED[p.weather];
      if (bed) {
        var noise = ctx.createBufferSource();
        noise.buffer = noiseBuffer(4, 0);
        noise.loop = true;
        var bf = ctx.createBiquadFilter();
        bf.type = bed.type; bf.frequency.value = bed.freq; bf.Q.value = 1.2;
        var bg = ctx.createGain();
        bg.gain.value = bed.gain;
        noise.connect(bf); bf.connect(bg); bg.connect(filter);
        noise.start(t);
        sources.push(noise);

        var swell = ctx.createOscillator();
        swell.frequency.value = bed.wobble * 0.12;
        var swellDepth = ctx.createGain();
        swellDepth.gain.value = bed.gain * 0.7;
        swell.connect(swellDepth); swellDepth.connect(bg.gain);
        swell.start(t);
        sources.push(swell);
      }

      out.gain.setValueAtTime(0.0001, t);
      out.gain.linearRampToValueAtTime(0.85, t + tone.attack + 0.4);

      return { gain: out, filter: filter, send: send, sources: sources, tone: tone,
               root: root, mode: MODES[p.emotion] || MODES.calm, spec: p };
    }

    function pluck(v) {
      var t = ctx.currentTime;
      var semi = v.mode[Math.floor(Math.random() * v.mode.length)]
               + 12 * (1 + Math.floor(Math.random() * 2));
      var freq = v.root * Math.pow(2, semi / 12);

      var osc = ctx.createOscillator();
      osc.type = v.tone.wave === 'sawtooth' ? 'triangle' : v.tone.wave;
      osc.frequency.value = freq;

      var g = ctx.createGain();
      var peak = 0.055 + Math.random() * 0.035;
      var len = 1.6 + Math.random() * 2.4;
      g.gain.setValueAtTime(0.0001, t);
      g.gain.linearRampToValueAtTime(peak, t + 0.04 + Math.random() * 0.25);
      g.gain.exponentialRampToValueAtTime(0.0001, t + len);

      osc.connect(g); g.connect(v.filter);
      osc.start(t); osc.stop(t + len + 0.1);
    }

    return {
      supported: function () {
        return !!(window.AudioContext || window.webkitAudioContext);
      },
      isOn: function () { return enabled; },
      toggle: function () {
        if (!boot()) return false;
        enabled = !enabled;
        if (ctx.state === 'suspended') ctx.resume();
        var t = ctx.currentTime;
        master.gain.cancelScheduledValues(t);
        master.gain.setValueAtTime(master.gain.value, t);
        master.gain.linearRampToValueAtTime(enabled ? 0.5 : 0.0001, t + 0.5);
        if (!enabled) stopVoice(0.5);
        return enabled;
      },
      playFor: function (p) {
        if (!enabled || !ctx) return;
        if (voice && voice.spec.designation === p.designation) return;
        stopVoice(1.0);
        voice = build(p);
        // note density rises with how intense the memory is
        var every = 3400 - p.intensity * 22;
        timer = setInterval(function () {
          if (voice && enabled) pluck(voice);
        }, Math.max(700, every));
      },
      silence: function () { stopVoice(1.4); }
    };
  })();

  var audioBtn = document.getElementById('audio');
  var audioLabel = document.getElementById('audiolabel');
  if (!Audio.supported()) {
    audioBtn.style.display = 'none';
  } else {
    audioBtn.addEventListener('click', function () {
      var on = Audio.toggle();
      audioBtn.classList.toggle('on', on);
      audioLabel.textContent = on ? 'Sound on' : 'Sound off';
      if (on && current) Audio.playFor(current.spec);
    });
  }

  /* ---------------------------------------------------------
     SURFACE PAINTERS — one per feature in the vocabulary
     --------------------------------------------------------- */
  var W = 1024, H = 512;

  var PAINT = {
    craters: function (g, r, c) {
      for (var i = 0; i < 46; i++) {
        var x = r()*W, y = 40 + r()*(H-80), s = 6 + r()*26;
        var grd = g.createRadialGradient(x, y, s*0.1, x, y, s);
        grd.addColorStop(0, rgba('#000000', 0.34));
        grd.addColorStop(0.72, rgba('#000000', 0.12));
        grd.addColorStop(1, rgba('#FFFFFF', 0.16));
        g.fillStyle = grd; g.beginPath(); g.arc(x, y, s, 0, 6.2832); g.fill();
      }
    },
    meteor_scars: function (g, r, c) {
      for (var i = 0; i < 8; i++) {
        var x = r()*W, y = 60 + r()*(H-120), s = 26 + r()*46;
        var grd = g.createRadialGradient(x, y, 1, x, y, s);
        grd.addColorStop(0, rgba('#000000', 0.5));
        grd.addColorStop(1, rgba('#000000', 0));
        g.fillStyle = grd; g.beginPath(); g.arc(x, y, s, 0, 6.2832); g.fill();
        g.strokeStyle = rgba('#FFFFFF', 0.13); g.lineWidth = 1;
        for (var k = 0; k < 10; k++) {
          var a = r()*6.2832;
          g.beginPath(); g.moveTo(x + Math.cos(a)*s*0.7, y + Math.sin(a)*s*0.7);
          g.lineTo(x + Math.cos(a)*s*1.8, y + Math.sin(a)*s*1.8); g.stroke();
        }
      }
    },
    lava_cracks: function (g, r, c) {
      g.lineCap = 'round';
      for (var i = 0; i < 22; i++) {
        var x = r()*W, y = r()*H;
        g.strokeStyle = '#FF7B2C'; g.shadowColor = '#FF4400'; g.shadowBlur = 16;
        g.lineWidth = 1 + r()*3; g.beginPath(); g.moveTo(x, y);
        for (var s = 0; s < 9; s++) { x += (r()-0.5)*74; y += (r()-0.5)*46; g.lineTo(x, y); }
        g.stroke();
      }
      g.shadowBlur = 0;
    },
    shattered_crust: function (g, r, c) {
      g.strokeStyle = rgba('#000000', 0.45); g.lineWidth = 1.6;
      for (var i = 0; i < 30; i++) {
        var x = r()*W, y = r()*H;
        g.beginPath(); g.moveTo(x, y);
        for (var s = 0; s < 5; s++) { x += (r()-0.5)*130; y += (r()-0.5)*90; g.lineTo(x, y); }
        g.stroke();
      }
    },
    oceans: function (g, r, c) {
      for (var i = 0; i < 12; i++) {
        var x = r()*W, y = 50 + r()*(H-100), rx = 60 + r()*180, ry = 34 + r()*90;
        var grd = g.createRadialGradient(x, y, 4, x, y, rx);
        grd.addColorStop(0, rgba(c[2], 0.95)); grd.addColorStop(1, rgba(c[2], 0.15));
        g.fillStyle = grd; g.beginPath(); g.ellipse(x, y, rx, ry, r()*3, 0, 6.2832); g.fill();
      }
    },
    tide_pools: function (g, r, c) {
      for (var i = 0; i < 60; i++) {
        var x = r()*W, y = 60 + r()*(H-120);
        g.fillStyle = rgba(c[0], 0.5 + r()*0.4);
        g.beginPath(); g.ellipse(x, y, 3 + r()*10, 2 + r()*6, r()*3, 0, 6.2832); g.fill();
      }
    },
    reef_shelves: function (g, r, c) {
      g.lineWidth = 5;
      for (var i = 0; i < 16; i++) {
        g.strokeStyle = rgba(c[0], 0.28 + r()*0.3);
        g.beginPath(); g.arc(r()*W, r()*H, 30 + r()*110, r()*6, r()*6 + 2.4); g.stroke();
      }
    },
    glass_seas: function (g, r, c) {
      for (var i = 0; i < 9; i++) {
        var x = r()*W, y = r()*H, w = 90 + r()*220, h = 26 + r()*70;
        g.fillStyle = rgba(c[0], 0.24); g.fillRect(x, y, w, h);
        g.strokeStyle = rgba('#FFFFFF', 0.4); g.lineWidth = 1;
        for (var k = 0; k < 5; k++) {
          var yy = y + r()*h;
          g.beginPath(); g.moveTo(x, yy); g.lineTo(x + w, yy - 6); g.stroke();
        }
      }
    },
    ice_caps: function (g, r, c) {
      [[0, 1], [H, -1]].forEach(function (cap) {
        var grd = g.createLinearGradient(0, cap[0], 0, cap[0] + cap[1] * (72 + r()*54));
        grd.addColorStop(0, rgba('#FFFFFF', 0.95)); grd.addColorStop(1, rgba('#FFFFFF', 0));
        g.fillStyle = grd; g.fillRect(0, Math.min(cap[0], cap[0] + cap[1]*130), W, 130);
      });
    },
    forests: function (g, r, c) {
      for (var i = 0; i < 900; i++) {
        var x = r()*W, y = 55 + r()*(H-110);
        g.fillStyle = rgba(r() > 0.5 ? '#1E5E3A' : '#2D8B4E', 0.28 + r()*0.42);
        g.beginPath(); g.arc(x, y, 2 + r()*7, 0, 6.2832); g.fill();
      }
    },
    root_networks: function (g, r, c) {
      g.strokeStyle = rgba('#0B2C1C', 0.55); g.lineCap = 'round';
      for (var i = 0; i < 26; i++) {
        var x = r()*W, y = r()*H, a = r()*6.2832;
        g.lineWidth = 3;
        for (var s = 0; s < 12; s++) {
          var nx = x + Math.cos(a)*22, ny = y + Math.sin(a)*22;
          g.beginPath(); g.moveTo(x, y); g.lineTo(nx, ny); g.stroke();
          x = nx; y = ny; a += (r()-0.5)*1.1; g.lineWidth = Math.max(0.6, g.lineWidth*0.9);
        }
      }
    },
    bioluminescence: function (g, r, c) {
      for (var i = 0; i < 260; i++) {
        var x = r()*W, y = r()*H;
        g.fillStyle = rgba(c[0], 0.75); g.shadowColor = c[0]; g.shadowBlur = 12;
        g.beginPath(); g.arc(x, y, 1 + r()*3, 0, 6.2832); g.fill();
      }
      g.shadowBlur = 0;
    },
    crystals: function (g, r, c) {
      for (var i = 0; i < 90; i++) {
        var x = r()*W, y = r()*H, s = 8 + r()*30;
        g.fillStyle = rgba('#FFFFFF', 0.14 + r()*0.28);
        g.strokeStyle = rgba(c[0], 0.6); g.lineWidth = 1;
        g.beginPath(); g.moveTo(x, y - s); g.lineTo(x + s*0.45, y + s*0.6);
        g.lineTo(x - s*0.45, y + s*0.6); g.closePath(); g.fill(); g.stroke();
      }
    },
    spire_fields: function (g, r, c) {
      for (var i = 0; i < 130; i++) {
        var x = r()*W, y = r()*H, h = 12 + r()*46;
        g.fillStyle = rgba('#FFFFFF', 0.1 + r()*0.24);
        g.beginPath(); g.moveTo(x, y); g.lineTo(x + 3, y - h); g.lineTo(x + 6, y); g.closePath(); g.fill();
      }
    },
    dunes: function (g, r, c) {
      g.lineWidth = 8;
      for (var i = 0; i < 40; i++) {
        var y = r()*H, amp = 8 + r()*26;
        g.strokeStyle = rgba(r() > 0.5 ? '#000000' : '#FFFFFF', 0.07 + r()*0.09);
        g.beginPath();
        for (var x = 0; x <= W; x += 16) g.lineTo(x, y + Math.sin(x*0.012 + i)*amp);
        g.stroke();
      }
    },
    salt_flats: function (g, r, c) {
      for (var i = 0; i < 14; i++) {
        var x = r()*W, y = r()*H;
        g.fillStyle = rgba('#FFFFFF', 0.16 + r()*0.2);
        g.beginPath(); g.ellipse(x, y, 50 + r()*140, 26 + r()*60, r()*3, 0, 6.2832); g.fill();
        g.strokeStyle = rgba('#000000', 0.16); g.lineWidth = 1;
        for (var k = 0; k < 14; k++) {
          g.beginPath(); g.moveTo(x - 60 + r()*120, y - 30 + r()*60);
          g.lineTo(x - 60 + r()*120, y - 30 + r()*60); g.stroke();
        }
      }
    },
    canyons: function (g, r, c) {
      g.lineCap = 'round';
      for (var i = 0; i < 16; i++) {
        var x = r()*W, y = r()*H;
        g.strokeStyle = rgba('#000000', 0.3); g.lineWidth = 4 + r()*12;
        g.beginPath(); g.moveTo(x, y);
        for (var s = 0; s < 7; s++) { x += 40 + r()*90; y += (r()-0.5)*70; g.lineTo(x, y); }
        g.stroke();
      }
    },
    terraced_cliffs: function (g, r, c) {
      for (var i = 0; i < 30; i++) {
        var y = r()*H, h = 6 + r()*18, x = r()*W, w = 90 + r()*260;
        g.fillStyle = rgba(r() > 0.5 ? '#FFFFFF' : '#000000', 0.08 + r()*0.1);
        g.fillRect(x, y, w, h);
        g.fillRect(x + 18, y + h, w - 36, h*0.7);
      }
    },
    storms: function (g, r, c) {
      for (var i = 0; i < 5; i++) {
        var cx = r()*W, cy = 90 + r()*(H-180), rad = 40 + r()*90;
        for (var t = 0; t < 5.4; t += 0.09) {
          var rr = rad * (t/5.4);
          g.fillStyle = rgba('#FFFFFF', 0.09);
          g.beginPath(); g.arc(cx + Math.cos(t*3)*rr, cy + Math.sin(t*3)*rr*0.55, 7, 0, 6.2832); g.fill();
        }
        g.fillStyle = rgba('#000000', 0.34);
        g.beginPath(); g.arc(cx, cy, rad*0.16, 0, 6.2832); g.fill();
      }
    },
    cloud_bands: function (g, r, c) {
      for (var i = 0; i < 22; i++) {
        var y = r()*H, h = 8 + r()*40;
        g.fillStyle = rgba(r() > 0.5 ? '#FFFFFF' : c[2], 0.07 + r()*0.13);
        g.beginPath();
        g.moveTo(0, y);
        for (var x = 0; x <= W; x += 24) g.lineTo(x, y + Math.sin(x*0.008 + i*2)*7);
        g.lineTo(W, y + h); 
        for (var x2 = W; x2 >= 0; x2 -= 24) g.lineTo(x2, y + h + Math.sin(x2*0.008 + i*2)*7);
        g.closePath(); g.fill();
      }
    },
    ash_plains: function (g, r, c) {
      for (var i = 0; i < 2600; i++) {
        g.fillStyle = rgba('#1A1A1F', 0.06 + r()*0.16);
        g.fillRect(r()*W, r()*H, 2 + r()*7, 2 + r()*5);
      }
    },
    geysers: function (g, r, c) {
      for (var i = 0; i < 26; i++) {
        var x = r()*W, y = 60 + r()*(H-120);
        var grd = g.createLinearGradient(x, y, x, y - 60);
        grd.addColorStop(0, rgba('#FFFFFF', 0.62)); grd.addColorStop(1, rgba('#FFFFFF', 0));
        g.fillStyle = grd; g.beginPath(); g.ellipse(x, y - 26, 7, 32, 0, 0, 6.2832); g.fill();
      }
    },
    city_lights: function (g, r, c) {
      for (var i = 0; i < 30; i++) {
        var cx = r()*W, cy = 60 + r()*(H-120), spread = 24 + r()*70;
        for (var k = 0; k < 60; k++) {
          g.fillStyle = rgba('#FFE9A8', 0.45 + r()*0.5);
          g.fillRect(cx + (r()-0.5)*spread, cy + (r()-0.5)*spread*0.6, 1.6, 1.6);
        }
      }
    },
    aurora: function (g, r, c) {
      [80, H - 80].forEach(function (base) {
        for (var i = 0; i < 7; i++) {
          g.strokeStyle = rgba(i % 2 ? c[0] : '#8AFFD1', 0.16 + r()*0.2);
          g.lineWidth = 10 + r()*26;
          g.beginPath();
          for (var x = 0; x <= W; x += 20) g.lineTo(x, base + Math.sin(x*0.007 + i)*34);
          g.stroke();
        }
      });
    },
    silent_zone: function (g, r, c) {
      var x = r()*W, y = r()*H;
      var grd = g.createRadialGradient(x, y, 5, x, y, 190);
      grd.addColorStop(0, rgba('#000000', 0.82)); grd.addColorStop(1, rgba('#000000', 0));
      g.fillStyle = grd; g.beginPath(); g.arc(x, y, 190, 0, 6.2832); g.fill();
    }
  };

  var OVERLAY = {
    smooth: function () {},
    cratered: function (g, r) { PAINT.craters(g, r); },
    fractured: function (g, r) {
      g.strokeStyle = rgba('#000000', 0.28); g.lineWidth = 1.2;
      for (var i = 0; i < 46; i++) {
        var x = r()*W, y = r()*H;
        g.beginPath(); g.moveTo(x, y);
        for (var s = 0; s < 4; s++) { x += (r()-0.5)*110; y += (r()-0.5)*80; g.lineTo(x, y); }
        g.stroke();
      }
    },
    banded: function (g, r) {
      for (var i = 0; i < 34; i++) {
        g.fillStyle = rgba(r() > 0.5 ? '#FFFFFF' : '#000000', 0.05 + r()*0.07);
        g.fillRect(0, r()*H, W, 5 + r()*22);
      }
    },
    molten: function (g, r) {
      for (var i = 0; i < 30; i++) {
        var x = r()*W, y = r()*H, s = 20 + r()*70;
        var grd = g.createRadialGradient(x, y, 1, x, y, s);
        grd.addColorStop(0, rgba('#FF8A3C', 0.42)); grd.addColorStop(1, rgba('#FF8A3C', 0));
        g.fillStyle = grd; g.beginPath(); g.arc(x, y, s, 0, 6.2832); g.fill();
      }
    },
    glassine: function (g, r) {
      for (var i = 0; i < 40; i++) {
        g.strokeStyle = rgba('#FFFFFF', 0.06 + r()*0.14); g.lineWidth = 1 + r()*4;
        var x = r()*W, y = r()*H;
        g.beginPath(); g.moveTo(x, y); g.lineTo(x + 60 + r()*180, y - 40 - r()*90); g.stroke();
      }
    },
    terraced: function (g, r) {
      for (var i = 0; i < 20; i++) {
        var y = r()*H;
        g.fillStyle = rgba('#000000', 0.09); g.fillRect(0, y, W, 3);
        g.fillStyle = rgba('#FFFFFF', 0.07); g.fillRect(0, y + 3, W, 3);
      }
    },
    porous: function (g, r) {
      for (var i = 0; i < 3400; i++) {
        g.fillStyle = rgba('#000000', 0.05 + r()*0.14);
        g.beginPath(); g.arc(r()*W, r()*H, 1 + r()*3, 0, 6.2832); g.fill();
      }
    }
  };

  function surfaceTexture(p) {
    var c = document.createElement('canvas'); c.width = W; c.height = H;
    var g = c.getContext('2d');
    var r = rand(p.seed);
    var pal = p.palette;

    var base = g.createLinearGradient(0, 0, 0, H);
    base.addColorStop(0, pal[2]); base.addColorStop(0.42, pal[0]);
    base.addColorStop(0.72, pal[1]); base.addColorStop(1, pal[2]);
    g.fillStyle = base; g.fillRect(0, 0, W, H);

    (p.features || []).forEach(function (f) { if (PAINT[f]) PAINT[f](g, r, pal); });
    (OVERLAY[p.texture] || OVERLAY.smooth)(g, r, pal);
    if (p.anomaly === 'silent_zone') PAINT.silent_zone(g, r, pal);

    // fused worlds carry a visible seam
    if (p.isFusion) {
      var seam = g.createLinearGradient(0, 0, W, 0);
      seam.addColorStop(0.42, rgba('#FF3D8A', 0));
      seam.addColorStop(0.5, rgba('#FF3D8A', 0.55));
      seam.addColorStop(0.58, rgba('#FF3D8A', 0));
      g.fillStyle = seam; g.fillRect(0, 0, W, H);
    }

    var tex = new THREE.CanvasTexture(c);
    tex.anisotropy = 4;
    return tex;
  }

  var GLOWING = { lava_cracks:1, city_lights:1, bioluminescence:1, aurora:1, geysers:1, crystals:1 };

  function emissiveTexture(p) {
    var lit = (p.features || []).filter(function (f) { return GLOWING[f]; });
    if (!lit.length) return null;
    var c = document.createElement('canvas'); c.width = W; c.height = H;
    var g = c.getContext('2d');
    g.fillStyle = '#000000'; g.fillRect(0, 0, W, H);
    var r = rand(p.seed + 7);
    lit.forEach(function (f) { PAINT[f](g, r, p.palette); });
    return new THREE.CanvasTexture(c);
  }

  /* ---------------------------------------------------------
     SCENE
     --------------------------------------------------------- */
  var renderer = new THREE.WebGLRenderer({ canvas: canvas, antialias: true, alpha: false });
  renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
  renderer.setSize(wrap.clientWidth, wrap.clientHeight, false);

  var scene = new THREE.Scene();
  scene.fog = new THREE.FogExp2(0x04050D, 0.0055);

  var camera = new THREE.PerspectiveCamera(52, wrap.clientWidth / wrap.clientHeight, 0.1, 3000);

  scene.add(new THREE.AmbientLight(0x4a5580, 0.42));

  // The key light sits at the core, so every world is lit from the centre of
  // the galaxy and carries a real terminator.
  var keyLight = new THREE.PointLight(0xFFF3E0, 3.4, 0, 1.4);
  keyLight.position.set(0, 0, 0);
  scene.add(keyLight);

  // A weak fill that follows the camera, so the night side never goes to pure
  // black and you can still read a planet you're looking straight at.
  var fillLight = new THREE.PointLight(0x8FA8FF, 0.42, 0);
  scene.add(fillLight);

  var rimLight = new THREE.DirectionalLight(0x29E7D2, 0.35);
  rimLight.position.set(-1, 0.6, -1);
  scene.add(rimLight);

  // starfield
  (function () {
    var n = 2600, pos = new Float32Array(n*3), col = new Float32Array(n*3);
    var r = rand(99), tint = new THREE.Color();
    for (var i = 0; i < n; i++) {
      var th = r()*6.2832, ph = Math.acos(2*r()-1), rad = 420 + r()*820;
      pos[i*3]   = rad*Math.sin(ph)*Math.cos(th);
      pos[i*3+1] = rad*Math.cos(ph)*0.55;
      pos[i*3+2] = rad*Math.sin(ph)*Math.sin(th);
      tint.setHSL(0.55 + r()*0.16, 0.5, 0.55 + r()*0.4);
      col[i*3] = tint.r; col[i*3+1] = tint.g; col[i*3+2] = tint.b;
    }
    var geo = new THREE.BufferGeometry();
    geo.setAttribute('position', new THREE.BufferAttribute(pos, 3));
    geo.setAttribute('color', new THREE.BufferAttribute(col, 3));
    scene.add(new THREE.Points(geo, new THREE.PointsMaterial({
      size: 1.5, vertexColors: true, transparent: true, opacity: 0.85,
      sizeAttenuation: false, fog: false
    })));
  })();

  // the core: the point everything orbits
  var core = new THREE.Mesh(
    new THREE.IcosahedronGeometry(1.5, 1),
    new THREE.MeshBasicMaterial({ color: 0xFFF0D0, wireframe: true, transparent: true, opacity: 0.62 })
  );
  scene.add(core);
  scene.add(new THREE.Mesh(
    new THREE.SphereGeometry(3.4, 24, 24),
    new THREE.MeshBasicMaterial({ color: 0x29E7D2, transparent: true, opacity: 0.07,
                                  blending: THREE.AdditiveBlending, side: THREE.BackSide })
  ));

  function ringTexture(colorA, colorB, gap) {
    var c = document.createElement('canvas'); c.width = 256; c.height = 8;
    var g = c.getContext('2d');
    var grd = g.createLinearGradient(0, 0, 256, 0);
    grd.addColorStop(0, rgba(colorA, 0));
    grd.addColorStop(0.16, rgba(colorA, 0.75));
    grd.addColorStop(0.5, rgba(colorB, 0.5));
    grd.addColorStop(0.84, rgba(colorA, 0.7));
    grd.addColorStop(1, rgba(colorA, 0));
    g.fillStyle = grd; g.fillRect(0, 0, 256, 8);
    if (gap) { g.clearRect(112, 0, 16, 8); }
    for (var i = 0; i < 90; i++) {
      g.fillStyle = rgba('#000000', 0.16);
      g.fillRect(Math.random()*256, 0, 1, 8);
    }
    return new THREE.CanvasTexture(c);
  }

  function makeRing(inner, outer, tex, opacity, additive, thetaLength) {
    var geo = new THREE.RingGeometry(inner, outer, 128, 1, 0, thetaLength || Math.PI*2);
    // remap UVs so the texture runs outward, not around
    var pos = geo.attributes.position, uv = geo.attributes.uv, v = new THREE.Vector3();
    for (var i = 0; i < pos.count; i++) {
      v.fromBufferAttribute(pos, i);
      uv.setXY(i, (v.length() - inner) / (outer - inner), 0.5);
    }
    var mesh = new THREE.Mesh(geo, new THREE.MeshBasicMaterial({
      map: tex, transparent: true, opacity: opacity, side: THREE.DoubleSide,
      depthWrite: false, blending: additive ? THREE.AdditiveBlending : THREE.NormalBlending
    }));
    mesh.rotation.x = Math.PI / 2;
    return mesh;
  }

  var ATMOS = { none: 0, thin: 0.10, medium: 0.20, thick: 0.34 };
  var LUMEN = { dim: 0.06, soft: 0.20, radiant: 0.48, blinding: 0.85 };
  var ENV_COLOR = {
    dust: 0xB9A98A, sparkles: 0xFFF3B0, embers: 0xFF6B2C,
    snow_mist: 0xDDF2FF, debris: 0x8E93AB, plasma: 0xB06BFF
  };

  var worlds = [];
  var pickable = [];

  PLANETS.forEach(function (p, index) {
    var group = new THREE.Group();
    group.position.set(p.position[0], p.position[1], p.position[2]);
    scene.add(group);

    var emissiveMap = emissiveTexture(p);
    var body = new THREE.Mesh(
      new THREE.SphereGeometry(p.radius, 56, 48),
      new THREE.MeshStandardMaterial({
        map: surfaceTexture(p),
        emissiveMap: emissiveMap,
        emissive: new THREE.Color(emissiveMap ? 0xffffff : p.palette[0]),
        emissiveIntensity: LUMEN[p.luminosity] !== undefined ? LUMEN[p.luminosity] : 0.2,
        roughness: p.texture === 'glassine' ? 0.22 : p.texture === 'molten' ? 0.5 : 0.86,
        metalness: p.texture === 'glassine' ? 0.45 : 0.08
      })
    );
    body.rotation.z = p.tilt * Math.PI / 180;
    body.userData.spec = p;
    group.add(body);
    pickable.push(body);

    // atmosphere shell
    var haze = ATMOS[p.atmosphere] || 0;
    if (haze > 0) {
      group.add(new THREE.Mesh(
        new THREE.SphereGeometry(p.radius * (1 + haze*0.5), 32, 32),
        new THREE.MeshBasicMaterial({
          color: new THREE.Color(p.palette[0]), transparent: true, opacity: haze,
          side: THREE.BackSide, blending: THREE.AdditiveBlending, depthWrite: false
        })
      ));
    }

    // rings
    if (p.ring && p.ring !== 'none') {
      var gap = p.anomaly === 'ring_gap';
      var tex = ringTexture(p.palette[0], p.palette[2], gap);
      var specs = {
        thin:    [[1.45, 1.78, 0.72, false]],
        wide:    [[1.35, 2.45, 0.62, false]],
        double:  [[1.35, 1.68, 0.72, false], [1.9, 2.5, 0.5, false]],
        dust:    [[1.3, 2.8, 0.3, false]],
        glowing: [[1.4, 2.15, 0.85, true]]
      }[p.ring] || [];
      specs.forEach(function (s) {
        var ring = makeRing(p.radius*s[0], p.radius*s[1], tex, s[2], s[3],
                            gap ? Math.PI*1.72 : null);
        ring.rotation.z = p.tilt * Math.PI / 180 * 0.6;
        group.add(ring);
      });
    }

    // moons
    var moonCount = p.moons;
    if (p.moonStyle === 'swarm') moonCount = Math.max(moonCount, 6);
    if (p.moonStyle === 'none') moonCount = 0;
    var moonOrbits = [];
    var mr = rand(p.seed + 31);
    for (var m = 0; m < moonCount; m++) {
      var size = p.radius * (p.moonStyle === 'shattered' ? (0.05 + mr()*0.16)
                            : p.moonStyle === 'swarm' ? 0.07
                            : 0.14 + mr()*0.09);
      var dist = p.radius * (p.moonStyle === 'shepherd' ? 2.05
                            : p.moonStyle === 'captured' ? 3.6 + mr()*1.2
                            : 2.4 + mr()*1.6);
      var pivot = new THREE.Group();
      pivot.rotation.x = (p.moonStyle === 'captured' ? 0.9 : 0.16) * (mr() - 0.5) * 2;
      pivot.rotation.y = p.moonStyle === 'twin' ? m * Math.PI : mr() * 6.2832;
      var moon = new THREE.Mesh(
        new THREE.IcosahedronGeometry(size, p.moonStyle === 'shattered' ? 0 : 2),
        new THREE.MeshStandardMaterial({ color: 0x9AA3BE, roughness: 0.95 })
      );
      moon.position.x = dist;
      pivot.add(moon);
      group.add(pivot);
      moonOrbits.push({ pivot: pivot, speed: 0.24 / Math.sqrt(dist) * (mr() > 0.5 ? 1 : -1) });
    }

    // environment particles
    var particles = null;
    if (p.environment && p.environment !== 'none') {
      var count = 260, pts = new Float32Array(count*3), pr = rand(p.seed + 5);
      for (var i = 0; i < count; i++) {
        var th = pr()*6.2832, ph = Math.acos(2*pr()-1), rad = p.radius*(1.25 + pr()*1.5);
        pts[i*3]   = rad*Math.sin(ph)*Math.cos(th);
        pts[i*3+1] = rad*Math.cos(ph);
        pts[i*3+2] = rad*Math.sin(ph)*Math.sin(th);
      }
      var pgeo = new THREE.BufferGeometry();
      pgeo.setAttribute('position', new THREE.BufferAttribute(pts, 3));
      particles = new THREE.Points(pgeo, new THREE.PointsMaterial({
        color: ENV_COLOR[p.environment] || 0xffffff,
        size: p.environment === 'debris' ? 0.09 : 0.055,
        transparent: true, opacity: 0.8, blending: THREE.AdditiveBlending, depthWrite: false
      }));
      group.add(particles);
    }

    // anomalies get exactly one strange object each
    var anomalyMesh = null, derelict = null;
    if (p.anomaly === 'time_dilation_halo') {
      anomalyMesh = new THREE.Mesh(
        new THREE.TorusGeometry(p.radius*2.1, 0.035, 8, 96),
        new THREE.MeshBasicMaterial({ color: 0xFFB338, transparent: true, opacity: 0.72,
                                      blending: THREE.AdditiveBlending })
      );
      anomalyMesh.rotation.x = 1.1;
      group.add(anomalyMesh);
    } else if (p.anomaly === 'chorus_signal') {
      anomalyMesh = new THREE.Mesh(
        new THREE.IcosahedronGeometry(p.radius*1.5, 1),
        new THREE.MeshBasicMaterial({ color: 0x29E7D2, wireframe: true,
                                      transparent: true, opacity: 0.3 })
      );
      group.add(anomalyMesh);
    } else if (p.anomaly === 'orbiting_derelict' || p.anomaly === 'impossible_moon') {
      derelict = new THREE.Group();
      var thing = p.anomaly === 'impossible_moon'
        ? new THREE.Mesh(new THREE.IcosahedronGeometry(p.radius*0.16, 2),
                         new THREE.MeshStandardMaterial({ color: 0xE7E2FF, roughness: 0.8 }))
        : new THREE.Mesh(new THREE.BoxGeometry(0.16, 0.07, 0.07),
                         new THREE.MeshStandardMaterial({ color: 0xFFB338, emissive: 0x442200 }));
      thing.position.x = p.radius * 2.9;
      derelict.add(thing);
      derelict.rotation.x = 0.6;
      group.add(derelict);
    } else if (p.anomaly === 'second_shadow' || p.anomaly === 'twin_sunrise') {
      var extra = new THREE.PointLight(
        p.anomaly === 'twin_sunrise' ? 0xFFB338 : 0x6B4BFF, 1.5, p.radius*14);
      extra.position.set(-p.radius*4, p.radius*2, p.radius*3);
      group.add(extra);
    }

    worlds.push({
      spec: p, group: group, body: body, moons: moonOrbits,
      particles: particles, anomalyMesh: anomalyMesh, derelict: derelict,
      spin: 0.5 / Math.max(p.rotation, 4)
    });

    // faint orbit trace
    var pts2 = [], ringR = Math.hypot(p.position[0], p.position[2]);
    for (var a = 0; a <= 128; a++) {
      var t = a / 128 * 6.2832;
      pts2.push(new THREE.Vector3(Math.cos(t)*ringR, 0, Math.sin(t)*ringR));
    }
    scene.add(new THREE.Line(
      new THREE.BufferGeometry().setFromPoints(pts2),
      new THREE.LineBasicMaterial({ color: 0x7E92D6, transparent: true, opacity: 0.075 })
    ));
  });

  // constellation links: worlds sharing an emotion and a theme
  (function () {
    var groups = {};
    PLANETS.forEach(function (p) { (groups[p.group] = groups[p.group] || []).push(p); });
    Object.keys(groups).forEach(function (key) {
      var members = groups[key];
      if (members.length < 2) return;
      var pts = members.map(function (m) {
        return new THREE.Vector3(m.position[0], m.position[1], m.position[2]);
      });
      scene.add(new THREE.Line(
        new THREE.BufferGeometry().setFromPoints(pts),
        new THREE.LineBasicMaterial({
          color: new THREE.Color(members[0].palette[0]),
          transparent: true, opacity: 0.24
        })
      ));
    });
  })();

  /* ---------------------------------------------------------
     CAMERA — hand-rolled orbit control, no extra dependency
     --------------------------------------------------------- */
  var extent = 24;
  PLANETS.forEach(function (p) {
    extent = Math.max(extent, Math.hypot(p.position[0], p.position[2]) + 12);
  });

  var cam = { theta: 0.7, phi: 1.02, dist: extent * 1.5 };
  var target = new THREE.Vector3(0, 0, 0);
  var desired = new THREE.Vector3(0, 0, 0);
  var idle = 0;

  function place() {
    camera.position.set(
      target.x + cam.dist * Math.sin(cam.phi) * Math.cos(cam.theta),
      target.y + cam.dist * Math.cos(cam.phi),
      target.z + cam.dist * Math.sin(cam.phi) * Math.sin(cam.theta)
    );
    camera.lookAt(target);
  }

  var dragging = false, lastX = 0, lastY = 0;

  canvas.addEventListener('pointerdown', function (e) {
    dragging = true; lastX = e.clientX; lastY = e.clientY; idle = 0;
    canvas.setPointerCapture(e.pointerId);
  });
  canvas.addEventListener('pointerup', function (e) {
    dragging = false;
    try { canvas.releasePointerCapture(e.pointerId); } catch (err) {}
  });
  canvas.addEventListener('pointermove', function (e) {
    if (dragging) {
      cam.theta -= (e.clientX - lastX) * 0.006;
      cam.phi = Math.max(0.15, Math.min(3.0, cam.phi - (e.clientY - lastY) * 0.006));
      lastX = e.clientX; lastY = e.clientY; idle = 0;
    }
    hover(e);
  });
  canvas.addEventListener('wheel', function (e) {
    e.preventDefault();
    cam.dist = Math.max(6, Math.min(extent*3.4, cam.dist * (1 + Math.sign(e.deltaY)*0.09)));
    idle = 0;
  }, { passive: false });
  canvas.addEventListener('dblclick', function () {
    journey.stop();
    releaseFocus();
  });

  /* ---------------------------------------------------------
     HOVER + FOCUS
     --------------------------------------------------------- */
  var raycaster = new THREE.Raycaster();
  var pointer = new THREE.Vector2();
  var focused = null;   // whatever the pointer is over
  var current = null;   // the world we're actually parked on

  function focusOn(world, framing) {
    current = world;
    world.body.getWorldPosition(desired);
    cam.dist = Math.max(5.5, world.spec.radius * (framing || 7));
    Audio.playFor(world.spec);
    showHud(world.spec);
  }

  function releaseFocus() {
    current = null;
    desired.set(0, 0, 0);
    cam.dist = extent * 1.5;
    Audio.silence();
    hud.classList.remove('on');
  }

  function hover(e) {
    var box = canvas.getBoundingClientRect();
    pointer.x = ((e.clientX - box.left) / box.width) * 2 - 1;
    pointer.y = -((e.clientY - box.top) / box.height) * 2 + 1;
    raycaster.setFromCamera(pointer, camera);
    var hits = raycaster.intersectObjects(pickable, false);
    if (hits.length) {
      showHud(hits[0].object.userData.spec);
      focused = hits[0].object;
      canvas.style.cursor = 'pointer';
    } else {
      focused = null;
      if (current) showHud(current.spec);
      else hud.classList.remove('on');
      if (!dragging) canvas.style.cursor = 'grab';
    }
  }

  canvas.addEventListener('click', function () {
    if (!focused) return;
    journey.stop();
    var world = worlds.filter(function (w) { return w.body === focused; })[0];
    if (world) focusOn(world);
  });

  function row(k, v) {
    return '<div class="row"><span class="k">' + k + '</span><span class="v">' + v + '</span></div>';
  }
  function nice(s) {
    return String(s).replace(/_/g, ' ').replace(/\b\w/g, function (m) { return m.toUpperCase(); });
  }

  function showHud(p) {
    hud.innerHTML =
      '<div class="desig">' + p.designation + '</div>' +
      '<div class="name">' + p.title + '</div>' +
      '<div class="strip" style="background:linear-gradient(90deg,' +
        p.palette[0] + ',' + p.palette[1] + ' 50%,' + p.palette[2] + ');"></div>' +
      row('Class', nice(p.type)) +
      row('Weather', nice(p.weather)) +
      row('Gravity', p.gravity + ' g') +
      row('Mean temp', p.temp + ' °C') +
      row('Moons', p.moons + ' · ' + nice(p.moonStyle)) +
      row('Intensity', p.intensity + ' / 100') +
      row('Stability', p.stability + '%') +
      (p.anomaly ? '<div class="anom">Anomaly · ' + nice(p.anomaly) + '</div>' : '') +
      (p.isFusion ? '<div class="anom" style="color:#FF3D8A;">Fused world</div>' : '');
    hud.classList.add('on');
  }

  /* ---------------------------------------------------------
     MEMORY JOURNEY

     Walks the galaxy in the order the memories were written down, holds on
     each world long enough to read it, and reads the memory back to you.
     --------------------------------------------------------- */

  var HOLD = 11;   // seconds per world

  var journey = (function () {
    var order = worlds.map(function (w, i) { return i; }).sort(function (a, b) {
      return (worlds[a].spec.createdAt || a) - (worlds[b].spec.createdAt || b);
    });

    var active = false, paused = false, step = 0, elapsed = 0;

    var bar = document.getElementById('journeybar');
    var card = document.getElementById('journeycard');
    var progress = document.getElementById('progress');
    var fill = progress.firstElementChild;
    var posLabel = document.getElementById('pos');
    var toggleBtn = document.getElementById('toggle');
    var startBtn = document.getElementById('start');

    function paint() {
      var world = worlds[order[step]];
      var p = world.spec;
      var tags = [p.emotion, p.theme, p.type, p.weather, p.hour, p.age]
        .map(function (v) { return '<span class="tag">' + nice(v) + '</span>'; }).join('');

      card.innerHTML =
        '<div class="step">World ' + (step + 1) + ' of ' + order.length + '</div>' +
        '<div class="desig">' + p.designation + '</div>' +
        '<div class="name">' + p.title + '</div>' +
        '<div class="strip" style="background:linear-gradient(90deg,' +
          p.palette[0] + ',' + p.palette[1] + ' 50%,' + p.palette[2] + ');"></div>' +
        (p.text ? '<div class="memory">' + p.text + '</div>' : '') +
        (p.fusionStory ? '<div class="memory" style="border-left-color:#FF3D8A;">'
                       + p.fusionStory + '</div>' : '') +
        '<div class="tags">' + tags + '</div>';

      card.classList.add('on');
      posLabel.innerHTML = '<b>' + (step + 1) + '</b> / ' + order.length;
      focusOn(world, 6);
      elapsed = 0;
    }

    function go(index) {
      step = (index + order.length) % order.length;
      paint();
    }

    return {
      start: function () {
        if (!order.length) return;
        active = true; paused = false; step = 0;
        bar.classList.add('on');
        progress.classList.add('on');
        startBtn.setAttribute('disabled', 'disabled');
        toggleBtn.innerHTML = '&#9208;';
        paint();
      },
      stop: function () {
        if (!active) return;
        active = false;
        bar.classList.remove('on');
        progress.classList.remove('on');
        card.classList.remove('on');
        startBtn.removeAttribute('disabled');
      },
      pause: function () {
        if (!active) return;
        paused = !paused;
        toggleBtn.innerHTML = paused ? '&#9654;' : '&#9208;';
      },
      next: function () { if (active) go(step + 1); },
      prev: function () { if (active) go(step - 1); },
      isActive: function () { return active; },
      tick: function (dt) {
        if (!active || paused) return;
        elapsed += dt;
        fill.style.width = Math.min(100, (elapsed / HOLD) * 100) + '%';
        if (elapsed >= HOLD) {
          if (step === order.length - 1) {
            this.stop();
            releaseFocus();
          } else {
            go(step + 1);
          }
        }
      }
    };
  })();

  document.getElementById('start').addEventListener('click', function () { journey.start(); });
  document.getElementById('exit').addEventListener('click', function () {
    journey.stop(); releaseFocus();
  });
  document.getElementById('toggle').addEventListener('click', function () { journey.pause(); });
  document.getElementById('next').addEventListener('click', function () { journey.next(); });
  document.getElementById('prev').addEventListener('click', function () { journey.prev(); });

  window.addEventListener('keydown', function (e) {
    if (e.key === ' ' && journey.isActive()) { e.preventDefault(); journey.pause(); }
    else if (e.key === 'ArrowRight') journey.next();
    else if (e.key === 'ArrowLeft') journey.prev();
    else if (e.key === 'Escape') { journey.stop(); releaseFocus(); }
  });

  /* ---------------------------------------------------------
     LOOP
     --------------------------------------------------------- */
  var clock = new THREE.Clock();
  var reduced = window.matchMedia('(prefers-reduced-motion: reduce)').matches;

  function frame() {
    requestAnimationFrame(frame);
    var dt = Math.min(clock.getDelta(), 0.05);
    var t = clock.getElapsedTime();

    if (!reduced) {
      idle += dt;
      if (idle > 4 && !dragging) cam.theta += dt * (journey.isActive() ? 0.09 : 0.035);

      worlds.forEach(function (w) {
        w.body.rotation.y += w.spin * dt;
        w.moons.forEach(function (m) { m.pivot.rotation.y += m.speed * dt; });
        if (w.particles) { w.particles.rotation.y += dt * 0.12; w.particles.rotation.x += dt * 0.04; }
        if (w.derelict) w.derelict.rotation.y += dt * 1.5;
        if (w.anomalyMesh) {
          w.anomalyMesh.rotation.z += dt * 0.4;
          var pulse = 1 + Math.sin(t * 2.2) * 0.05;
          w.anomalyMesh.scale.setScalar(pulse);
        }
      });
      core.rotation.y += dt * 0.25;
      core.rotation.x += dt * 0.12;
    }

    journey.tick(dt);
    target.lerp(desired, journey.isActive() ? 0.045 : 0.07);
    place();
    fillLight.position.copy(camera.position);
    renderer.render(scene, camera);
  }

  function resize() {
    var w = wrap.clientWidth, h = wrap.clientHeight;
    camera.aspect = w / h;
    camera.updateProjectionMatrix();
    renderer.setSize(w, h, false);
  }
  window.addEventListener('resize', resize);

  resize();
  place();
  frame();
})();
</script>
"""
