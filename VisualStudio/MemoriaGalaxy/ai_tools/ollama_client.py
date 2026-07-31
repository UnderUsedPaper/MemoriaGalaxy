"""
Ollama transport.

One job: send a prompt to a locally running Ollama and get parsed JSON back.
No prompt text lives here — that's memory_analyzer's business.
"""

import json
import re
import time

import requests

from config import OLLAMA_HOST, OLLAMA_MODEL, OLLAMA_TIMEOUT, OLLAMA_TEMPERATURE


class OllamaUnavailable(RuntimeError):
    """Ollama isn't running, or the model isn't pulled."""


class OllamaBadResponse(RuntimeError):
    """Ollama answered, but not with usable JSON."""


# Availability is checked on every rerun, so cache it briefly.
_probe_cache = {"checked_at": 0.0, "result": None}
_PROBE_TTL = 8.0


def is_available(force=False):
    """True if Ollama answers on the configured host. Cached for a few seconds."""
    now = time.time()
    if not force and _probe_cache["result"] is not None and now - _probe_cache["checked_at"] < _PROBE_TTL:
        return _probe_cache["result"]

    try:
        response = requests.get(f"{OLLAMA_HOST}/api/tags", timeout=2.0)
        result = response.status_code == 200
    except requests.RequestException:
        result = False

    _probe_cache.update({"checked_at": now, "result": result})
    return result


def installed_models():
    """Model names Ollama has pulled. Empty list if it isn't reachable."""
    try:
        response = requests.get(f"{OLLAMA_HOST}/api/tags", timeout=2.0)
        response.raise_for_status()
        return [model.get("name", "") for model in response.json().get("models", [])]
    except (requests.RequestException, ValueError):
        return []


def model_is_pulled(model=OLLAMA_MODEL):
    """Ollama tags carry a :tag suffix, so match on the base name."""
    base = model.split(":")[0]
    return any(name.split(":")[0] == base for name in installed_models())


def _extract_json(raw):
    """
    Pull an object out of a model response. Handles fenced blocks and stray
    prose on either side, which small models produce often enough to matter.
    """
    text = raw.strip()

    fenced = re.search(r"```(?:json)?\s*(.*?)```", text, re.DOTALL)
    if fenced:
        text = fenced.group(1).strip()

    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass

    start, depth = None, 0
    for i, char in enumerate(text):
        if char == "{":
            if depth == 0:
                start = i
            depth += 1
        elif char == "}":
            depth -= 1
            if depth == 0 and start is not None:
                try:
                    return json.loads(text[start:i + 1])
                except json.JSONDecodeError:
                    start = None

    raise OllamaBadResponse("no JSON object found in the model response")


def generate_json(prompt, system="", model=OLLAMA_MODEL, temperature=OLLAMA_TEMPERATURE):
    """Send a prompt and return parsed JSON. Raises if that isn't possible."""
    if not is_available():
        raise OllamaUnavailable(
            f"nothing answering at {OLLAMA_HOST}. Start it with `ollama serve`."
        )

    payload = {
        "model": model,
        "prompt": prompt,
        "system": system,
        "stream": False,
        "format": "json",
        "options": {"temperature": temperature, "top_p": 0.9},
    }

    try:
        response = requests.post(
            f"{OLLAMA_HOST}/api/generate", json=payload, timeout=OLLAMA_TIMEOUT
        )
    except requests.Timeout:
        raise OllamaUnavailable(f"{model} took longer than {OLLAMA_TIMEOUT}s to answer")
    except requests.RequestException as error:
        raise OllamaUnavailable(str(error))

    if response.status_code == 404:
        raise OllamaUnavailable(f"model '{model}' isn't pulled. Run `ollama pull {model}`.")
    if response.status_code != 200:
        raise OllamaUnavailable(f"Ollama returned HTTP {response.status_code}")

    try:
        body = response.json()
    except ValueError:
        raise OllamaBadResponse("Ollama returned a non-JSON envelope")

    return _extract_json(body.get("response", ""))
