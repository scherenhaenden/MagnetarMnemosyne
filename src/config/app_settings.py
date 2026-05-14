import json
import os
from functools import lru_cache
from typing import Any


ROOT_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
APPSETTINGS_PATH = os.environ.get("MAGNETAR_APPSETTINGS_PATH", os.path.join(ROOT_DIR, "appsettings.json"))

DEFAULT_APP_SETTINGS: dict[str, Any] = {
    "audio": {
        "defaults": {
            "backend": "f5-tts",
            "output_path": "",
        },
        "backends": {
            "f5-tts": {
                "enabled": True,
                "label": "F5-TTS",
                "model": "F5TTS_Base",
                "checkpoint": "hf://jpgallegoar/F5-Spanish/model_1200000.safetensors",
                "vocab_file": "hf://jpgallegoar/F5-Spanish/vocab.txt",
                "device": "mps",
            },
            "kokoro": {
                "enabled": True,
                "label": "Kokoro",
                "model": "kokoro",
                "checkpoint": "",
                "vocab_file": "",
                "device": "cpu",
            },
        },
        "paths": {
            "f5_tts_root": "/Users/edwardflores/Projects/Development/F5-TTS",
            "kokoro_renderer_root": "/Users/edwardflores/Projects/Development/magnetar-audio-renderer",
            "generated_audio_dir": "src/generated_audio",
        },
    }
}


def _deep_merge(base: dict[str, Any], override: dict[str, Any]) -> dict[str, Any]:
    merged = dict(base)
    for key, value in override.items():
        if isinstance(value, dict) and isinstance(merged.get(key), dict):
            merged[key] = _deep_merge(merged[key], value)
        else:
            merged[key] = value
    return merged


@lru_cache(maxsize=1)
def load_app_settings() -> dict[str, Any]:
    settings = DEFAULT_APP_SETTINGS
    if not os.path.exists(APPSETTINGS_PATH):
        return settings

    with open(APPSETTINGS_PATH, "r", encoding="utf-8") as appsettings_file:
        loaded = json.load(appsettings_file)
    if not isinstance(loaded, dict):
        raise ValueError("appsettings.json must contain a JSON object at the root.")
    return _deep_merge(settings, loaded)


def get_audio_backend_options() -> list[dict[str, str]]:
    backends = load_app_settings().get("audio", {}).get("backends") or {}
    options = []
    for backend_id, backend_config in backends.items():
        if backend_config.get("enabled", True):
            options.append({
                "id": backend_id,
                "label": str(backend_config.get("label") or backend_id),
            })
    return options


def get_audio_backend_config(backend: str | None = None) -> dict[str, Any]:
    audio_settings = load_app_settings().get("audio", {})
    defaults = audio_settings.get("defaults") or {}
    selected_backend = backend or defaults.get("backend") or "f5-tts"
    backend_config = dict((audio_settings.get("backends") or {}).get(selected_backend) or {})
    backend_config["id"] = selected_backend
    backend_config["paths"] = dict(audio_settings.get("paths") or {})
    return backend_config


def get_audio_defaults(backend: str | None = None) -> dict[str, str]:
    audio_settings = load_app_settings().get("audio", {})
    defaults = dict(audio_settings.get("defaults") or {})
    selected_backend = backend or defaults.get("backend") or "f5-tts"
    backend_defaults = dict((audio_settings.get("backends") or {}).get(selected_backend) or {})
    backend_defaults.pop("enabled", None)
    backend_defaults.pop("label", None)
    defaults.update(backend_defaults)
    defaults["backend"] = selected_backend
    defaults.update(audio_settings.get("paths") or {})
    return defaults


def get_audio_setting(*path: str, default: Any = None) -> Any:
    current: Any = load_app_settings()
    for key in path:
        if not isinstance(current, dict):
            return default
        current = current.get(key)
        if current is None:
            return default
    return current
