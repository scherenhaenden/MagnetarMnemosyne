import os
import sys
from pathlib import Path

import pytest


BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(os.path.join(BASE_DIR, "src"))

from audio.render_runner import render_audio_question


F5_ROOT = "/Users/edwardflores/Projects/Development/F5-TTS"
F5_CLI = os.path.join(F5_ROOT, ".venv", "bin", "f5-tts_infer-cli")


@pytest.mark.skipif(
    (not os.path.exists(F5_CLI)) or os.environ.get("RUN_F5TTS_INTEGRATION") != "1",
    reason="F5-TTS integration test is opt-in and requires local installation",
)
def test_render_audio_question_with_f5tts_examples(tmp_path):
    output_path = tmp_path / "f5tts-integration.wav"
    question = {
        "type": "audio_listening",
        "conversation_payload": {
            "title": "integration test",
            "language": "en",
            "difficulty": "A1",
            "speakers": [
                {
                    "id": "main",
                    "label": "Main",
                    "descriptor": "main",
                    "reference_audio_url": f"{F5_ROOT}/src/f5_tts/infer/examples/multi/main.flac",
                    "reference_text": "",
                },
                {
                    "id": "town",
                    "label": "Town",
                    "descriptor": "town",
                    "reference_audio_url": f"{F5_ROOT}/src/f5_tts/infer/examples/multi/town.flac",
                    "reference_text": "",
                },
            ],
            "turns": [
                {"speaker_id": "main", "text": "This is the first speaker."},
                {"speaker_id": "town", "text": "This is the second speaker."},
            ],
            "render": {
                "backend": "f5-tts",
                "model": "F5TTS_v1_Base",
                "checkpoint": "hf://SWivid/F5-TTS/F5TTS_v1_Base/model_1250000.safetensors",
                "vocab_file": "hf://SWivid/F5-TTS/F5TTS_v1_Base/vocab.txt",
                "f5_tts_root": F5_ROOT,
                "device": "mps",
                "output_path": str(output_path),
            },
        },
    }

    result = render_audio_question(777, question)
    assert result["audio_url"] == str(output_path)
    assert os.path.exists(result["audio_url"])
    assert os.path.getsize(result["audio_url"]) > 0
