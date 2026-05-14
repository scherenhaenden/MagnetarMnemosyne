import json
import os
import sys


BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(os.path.join(BASE_DIR, "src"))

from config.app_settings import get_audio_backend_options, get_audio_defaults, load_app_settings


def test_appsettings_json_exists():
    appsettings_path = os.path.join(BASE_DIR, "appsettings.json")
    assert os.path.exists(appsettings_path)


def test_appsettings_contains_audio_configuration():
    settings = load_app_settings()
    assert settings["audio"]["defaults"]["backend"] in {"f5-tts", "kokoro"}
    assert settings["audio"]["backends"]["f5-tts"]["enabled"] is True
    assert settings["audio"]["backends"]["kokoro"]["enabled"] is True
    assert settings["audio"]["paths"]["f5_tts_root"]
    assert settings["audio"]["paths"]["kokoro_renderer_root"]


def test_audio_defaults_flattens_defaults_and_paths():
    defaults = get_audio_defaults()
    assert defaults["backend"]
    assert defaults["checkpoint"]
    assert defaults["f5_tts_root"]
    assert defaults["kokoro_renderer_root"]


def test_audio_backend_options_exposes_enabled_backends():
    options = get_audio_backend_options()
    backend_ids = {option["id"] for option in options}
    assert "f5-tts" in backend_ids
    assert "kokoro" in backend_ids
