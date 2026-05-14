import json
import os
import subprocess
import re
from typing import Any, Callable

from config import get_audio_setting
from .conversation_generator import build_render_job


def _generated_audio_dir() -> str:
    configured_dir = get_audio_setting("audio", "paths", "generated_audio_dir", default="src/generated_audio")
    if os.path.isabs(configured_dir):
        return configured_dir
    project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    return os.path.join(project_root, configured_dir)


def _backend_cache_dir(*parts: str) -> str:
    cache_dir = os.path.join(_generated_audio_dir(), ".cache", *parts)
    os.makedirs(cache_dir, exist_ok=True)
    return cache_dir


def _default_output_path(question_id: int) -> str:
    generated_audio_dir = _generated_audio_dir()
    os.makedirs(generated_audio_dir, exist_ok=True)
    return os.path.join(generated_audio_dir, f"audio-question-{question_id}.wav")


def _clean_turn_text(text: str) -> str:
    cleaned = re.sub(r"\[[^\]]+\]", "", text or "")
    cleaned = re.sub(r"\n\s*\n+", "\n", cleaned)
    return cleaned.strip()


def _validate_render_inputs(render_job: dict[str, Any]) -> None:
    conversation = render_job["conversation"]
    render_config = conversation.get("render") or {}
    backend = render_job["backend"]
    if backend == "f5-tts":
        for speaker in conversation.get("speakers", []):
            reference_audio = str(speaker.get("reference_audio_url") or "").strip()
            if not reference_audio:
                raise RuntimeError(f'Speaker "{speaker.get("label") or speaker.get("id")}" requires reference_audio_url.')
            if reference_audio.startswith("/absolute/path/"):
                raise RuntimeError(
                    f'Speaker "{speaker.get("label") or speaker.get("id")}" still uses the placeholder path "{reference_audio}". Replace it with a real local audio file.'
                )
            if not os.path.exists(reference_audio):
                raise RuntimeError(
                    f'Speaker "{speaker.get("label") or speaker.get("id")}" reference audio file not found: {reference_audio}'
                )
    elif backend == "kokoro":
        if not (render_config.get("kokoro_renderer_root") or os.environ.get("MAGNETAR_AUDIO_RENDERER_ROOT")):
            pass


def _resolve_output_path(question_id: int, render_job: dict[str, Any]) -> str:
    configured_output_path = render_job.get("output_path")
    if configured_output_path:
        return configured_output_path

    render_config = render_job.get("conversation", {}).get("render", {}) or {}
    output_name = str(render_config.get("output_name") or "").strip()
    if not output_name:
        return _default_output_path(question_id)

    generated_audio_dir = _generated_audio_dir()
    os.makedirs(generated_audio_dir, exist_ok=True)
    return os.path.join(generated_audio_dir, output_name)


def _write_render_inputs(question_id: int, render_job: dict[str, Any]) -> dict[str, str]:
    generated_audio_dir = _generated_audio_dir()
    os.makedirs(generated_audio_dir, exist_ok=True)
    transcript_path = os.path.join(generated_audio_dir, f"audio-question-{question_id}.transcript.txt")
    payload_path = os.path.join(generated_audio_dir, f"audio-question-{question_id}.payload.json")

    with open(transcript_path, "w", encoding="utf-8") as transcript_file:
        transcript_file.write(render_job["transcript"])

    with open(payload_path, "w", encoding="utf-8") as payload_file:
        json.dump(render_job["conversation"], payload_file, ensure_ascii=False, indent=2)

    return {"transcript_path": transcript_path, "payload_path": payload_path}


def _speaker_tag(speaker_id: str) -> str:
    sanitized = "".join(char if char.isalnum() or char == "_" else "_" for char in speaker_id.strip().lower())
    return sanitized or "speaker"


def _build_f5_story(conversation_payload: dict[str, Any]) -> str:
    parts: list[str] = []
    for turn in conversation_payload["turns"]:
        parts.append(f'[{_speaker_tag(turn["speaker_id"])}] {_clean_turn_text(turn["text"])}')
    return "\n".join(parts)


def _build_f5_toml(question_id: int, render_job: dict[str, Any], output_path: str) -> tuple[str, str]:
    conversation = render_job["conversation"]
    render_config = conversation.get("render") or {}
    f5_root = (
        render_config.get("f5_tts_root")
        or os.environ.get("F5TTS_ROOT")
        or get_audio_setting("audio", "paths", "f5_tts_root", default="/Users/edwardflores/Projects/Development/F5-TTS")
    )
    cli_path = os.path.join(f5_root, ".venv", "bin", "f5-tts_infer-cli")
    if not os.path.exists(cli_path):
        raise RuntimeError(f"F5-TTS CLI not found at {cli_path}. Set render.f5_tts_root or F5TTS_ROOT.")

    speakers = conversation["speakers"]
    if not speakers:
        raise RuntimeError("F5-TTS render requires at least one speaker.")

    main_speaker = speakers[0]
    if not main_speaker.get("reference_audio_url"):
        raise RuntimeError("Main speaker requires reference_audio_url for F5-TTS rendering.")

    generated_audio_dir = _generated_audio_dir()
    story_path = os.path.join(generated_audio_dir, f"audio-question-{question_id}.story.txt")
    config_path = os.path.join(generated_audio_dir, f"audio-question-{question_id}.toml")
    output_dir = os.path.dirname(output_path)
    output_file = os.path.basename(output_path)

    with open(story_path, "w", encoding="utf-8") as story_file:
        story_file.write(_build_f5_story(conversation))

    lines = [
        f'model = "{render_job.get("model") or "F5TTS_Base"}"',
        f'ckpt_file = "{render_job.get("checkpoint") or "hf://jpgallegoar/F5-Spanish/model_1200000.safetensors"}"',
        f'vocab_file = "{render_config.get("vocab_file") or "hf://jpgallegoar/F5-Spanish/vocab.txt"}"',
        f'ref_audio = "{main_speaker["reference_audio_url"]}"',
        f'ref_text = """{(main_speaker.get("reference_text") or "").strip()}"""',
        'gen_text = ""',
        f'gen_file = "{story_path}"',
        "remove_silence = true",
        f'output_dir = "{output_dir}"',
        f'output_file = "{output_file}"',
        f'device = "{render_config.get("device") or "mps"}"',
    ]

    for speaker in speakers[1:]:
        if not speaker.get("reference_audio_url"):
            raise RuntimeError(f'Speaker "{speaker["label"]}" requires reference_audio_url for F5-TTS rendering.')
        tag = _speaker_tag(speaker["id"])
        lines.extend([
            "",
            f"[voices.{tag}]",
            f'ref_audio = "{speaker["reference_audio_url"]}"',
            f'ref_text = """{(speaker.get("reference_text") or "").strip()}"""',
        ])

    with open(config_path, "w", encoding="utf-8") as config_file:
        config_file.write("\n".join(lines) + "\n")

    return cli_path, config_path


def _build_kokoro_scene(question_id: int, render_job: dict[str, Any], output_path: str) -> tuple[str, str]:
    conversation = render_job["conversation"]
    render_config = conversation.get("render") or {}
    renderer_root = (
        render_config.get("kokoro_renderer_root")
        or os.environ.get("MAGNETAR_AUDIO_RENDERER_ROOT")
        or get_audio_setting(
            "audio", "paths", "kokoro_renderer_root", default="/Users/edwardflores/Projects/Development/magnetar-audio-renderer"
        )
    )
    cli_entry = os.path.join(renderer_root, ".venv", "bin", "python")
    wrapper_path = os.path.join(renderer_root, "render_scene.py")
    if not os.path.exists(cli_entry):
        raise RuntimeError(
            f"Kokoro renderer Python not found at {cli_entry}. Set render.kokoro_renderer_root or MAGNETAR_AUDIO_RENDERER_ROOT."
        )
    if not os.path.exists(wrapper_path):
        raise RuntimeError(f"Kokoro renderer entrypoint not found at {wrapper_path}.")

    generated_audio_dir = _generated_audio_dir()
    scene_path = os.path.join(generated_audio_dir, f"audio-question-{question_id}.kokoro.scene.json")
    speakers = {}
    for speaker in conversation["speakers"]:
        speaker_id = speaker["id"]
        voice_name = speaker.get("voice_id") or "ef_dora"
        speakers[speaker_id] = {
            "display_name": speaker["label"],
            "role": speaker.get("persona") or speaker.get("descriptor") or speaker["label"],
            "voice_engine": "kokoro",
            "voice": voice_name,
            "base_speed": 1.0,
            "base_volume": 1.0,
            "description": speaker.get("descriptor") or speaker.get("persona") or "",
        }

    dialogue = []
    for turn in conversation["turns"]:
        dialogue.append(
            {
                "speaker": turn["speaker_id"],
                "style": [],
                "text": _clean_turn_text(turn["text"]),
            }
        )

    scene = {
        "scene_id": f"audio_question_{question_id}",
        "title": conversation.get("title") or f"audio question {question_id}",
        "language": "es",
        "accent_target": conversation.get("language") or "es",
        "level": conversation.get("difficulty") or "",
        "duration_target_seconds": 180,
        "sample_rate": 24000,
        "output_file": os.path.basename(output_path),
        "environment": {
            "name": "none",
            "ambience_file": "",
            "volume_db": -28,
            "enabled": False,
        },
        "speakers": speakers,
        "style_map": {},
        "dialogue": dialogue,
    }

    with open(scene_path, "w", encoding="utf-8") as scene_file:
        json.dump(scene, scene_file, ensure_ascii=False, indent=2)

    return cli_entry, wrapper_path, scene_path, renderer_root


def render_audio_question(
    question_id: int,
    question: dict[str, Any],
    progress_callback: Callable[[int, str], None] | None = None,
) -> dict[str, Any]:
    if question.get("type") != "audio_listening":
        raise ValueError("Only audio_listening questions can be rendered.")
    if not question.get("conversation_payload"):
        raise ValueError("Question does not contain a conversation payload.")

    render_job = build_render_job(question["conversation_payload"])
    if progress_callback:
        progress_callback(10, "Validando referencias y configuración del backend.")
    _validate_render_inputs(render_job)
    output_path = _resolve_output_path(question_id, render_job)
    if progress_callback:
        progress_callback(20, "Preparando transcript y payload del render.")
    paths = _write_render_inputs(question_id, render_job)
    backend = render_job["backend"]
    env = os.environ.copy()

    if backend == "f5-tts":
        cli_path, config_path = _build_f5_toml(question_id, render_job, output_path)
        command = [cli_path, "-c", config_path]
        workdir = (
            render_job["conversation"].get("render", {}).get("f5_tts_root")
            or get_audio_setting("audio", "paths", "f5_tts_root", default="/Users/edwardflores/Projects/Development/F5-TTS")
        )
        env.setdefault("MPLCONFIGDIR", _backend_cache_dir("f5tts", "matplotlib"))
        env.setdefault("XDG_CACHE_HOME", _backend_cache_dir("f5tts", "xdg"))
        env.setdefault("NUMBA_CACHE_DIR", _backend_cache_dir("f5tts", "numba"))
        env.setdefault("HOME", os.path.expanduser("~"))
    elif backend == "kokoro":
        cli_python, wrapper_path, scene_path, workdir = _build_kokoro_scene(question_id, render_job, output_path)
        command = [cli_python, wrapper_path, "--scene", scene_path, "--output", output_path]
    else:
        raise RuntimeError(f"Unsupported backend '{backend}'. Supported backends: f5-tts, kokoro.")

    if "MPLCONFIGDIR" in env:
        os.makedirs(env["MPLCONFIGDIR"], exist_ok=True)
    if "XDG_CACHE_HOME" in env:
        os.makedirs(env["XDG_CACHE_HOME"], exist_ok=True)
    if "NUMBA_CACHE_DIR" in env:
        os.makedirs(env["NUMBA_CACHE_DIR"], exist_ok=True)

    if progress_callback:
        progress_callback(60, f"Renderizando audio con backend {backend}.")
    completed = subprocess.run(command, capture_output=True, text=True, check=False, cwd=workdir, env=env)
    backend_stdout = completed.stdout.strip()
    backend_stderr = completed.stderr.strip()
    if completed.returncode != 0:
        error_msg = backend_stderr or backend_stdout or "unknown backend error"
        if progress_callback:
            progress_callback(100, "El render falló.")
        return {
            "audio_url": "",
            "render_status": "failed",
            "transcript_path": paths["transcript_path"],
            "payload_path": paths["payload_path"],
            "output_path": output_path,
            "backend_command": " ".join(command),
            "backend_stdout": backend_stdout,
            "backend_stderr": backend_stderr,
            "error": f"Audio render failed (returncode {completed.returncode}): {error_msg}",
        }
    if not os.path.exists(output_path):
        error_msg = f"Audio render finished but output file was not created: {output_path}"
        if progress_callback:
            progress_callback(100, "El render falló.")
        return {
            "audio_url": "",
            "render_status": "failed",
            "transcript_path": paths["transcript_path"],
            "payload_path": paths["payload_path"],
            "output_path": output_path,
            "backend_command": " ".join(command),
            "backend_stdout": backend_stdout,
            "backend_stderr": backend_stderr,
            "error": error_msg,
        }
    if progress_callback:
        progress_callback(95, "Backend terminado. Verificando el archivo final.")
    return {
        "audio_url": output_path,
        "render_status": "ready",
        "transcript_path": paths["transcript_path"],
        "payload_path": paths["payload_path"],
        "output_path": output_path,
        "backend_command": " ".join(command),
        "backend_stdout": backend_stdout,
        "backend_stderr": "",
    }
