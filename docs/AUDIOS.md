# Audio Authoring Guide

## Purpose

This guide explains how to create listening-comprehension audios from the admin dashboard, how `appsettings.json` controls the available audio engines, and how to diagnose render errors.

The system currently supports two interchangeable local backends:
- `F5-TTS`
- `Kokoro`

The admin workflow is intentionally JSON-driven. The audio scene is described in `conversation_json`, and the selected backend renders the final file.

## Where Audio Is Managed

- Admin grid: `http://localhost:8000/admin?tab=audios`
- Create page: `http://localhost:8000/admin?tab=audios&mode=create`

The audio grid shows:
- created audios
- pending audios
- backend used
- output path
- last render error
- render command and backend stdout

## Audio Creation Workflow

1. Open `Audios`.
2. Click `Crear Audio`.
3. Fill in:
   - `Título`
   - `Descripción`
   - `Idioma`
   - `Nivel`
   - `conversation_json`
4. Choose the backend from the dropdown:
   - `F5-TTS`
   - `Kokoro`
5. Review the backend settings below.
6. Click `Crear Audio`.

Behavior:
- If rendering succeeds, the page stays on `Crear Audio` and shows a success message.
- If rendering fails, the page stays on `Crear Audio` and shows the exact error.
- If you only want to persist the scene without rendering yet, click `Guardar Borrador`.

## `conversation_json` Format

The page expects a JSON payload describing speakers and either `dialogue` or `turns`.

### Minimal F5-TTS Example

```json
{
  "speakers": [
    {
      "id": "teacher",
      "label": "Teacher",
      "descriptor": "calm Spanish woman from Madrid",
      "reference_audio_url": "/absolute/path/to/teacher.wav",
      "reference_text": "Buenos días. ¿Cómo te llamas?"
    },
    {
      "id": "student",
      "label": "Student",
      "descriptor": "young girl, slightly nervous",
      "reference_audio_url": "/absolute/path/to/student.wav",
      "reference_text": "Hola. Me llamo Lía."
    }
  ],
  "dialogue": "Teacher (calm Spanish woman from Madrid):\n[warmly]\nBuenos días. ¿Cómo te llamas?\n\nStudent (young girl, slightly nervous):\n[nervous]\nHola. Me llamo Lía."
}
```

### Minimal Kokoro Example

```json
{
  "speakers": [
    {
      "id": "teacher",
      "label": "Teacher",
      "descriptor": "adult female teacher",
      "voice_id": "ef_dora"
    },
    {
      "id": "student",
      "label": "Student",
      "descriptor": "young student",
      "voice_id": "ef_dora"
    }
  ],
  "turns": [
    {
      "speaker_id": "teacher",
      "text": "Buenos días. ¿Cómo te llamas?"
    },
    {
      "speaker_id": "student",
      "text": "Hola. Me llamo Lía."
    }
  ]
}
```

## Backend Selection

The backend dropdown is populated from `appsettings.json`.

Current ids:
- `f5-tts`
- `kokoro`

These ids are not free text anymore in the UI. If a backend is disabled in `appsettings.json`, it should not appear in the dropdown.

## `appsettings.json`

The root file [appsettings.json](/Users/edwardflores/Projects/Development/MagnetarMnemosyne/appsettings.json:1) controls backend defaults and paths.

Example:

```json
{
  "audio": {
    "defaults": {
      "backend": "f5-tts",
      "output_path": ""
    },
    "backends": {
      "f5-tts": {
        "enabled": true,
        "label": "F5-TTS",
        "model": "F5TTS_Base",
        "checkpoint": "hf://jpgallegoar/F5-Spanish/model_1200000.safetensors",
        "vocab_file": "hf://jpgallegoar/F5-Spanish/vocab.txt",
        "device": "mps"
      },
      "kokoro": {
        "enabled": true,
        "label": "Kokoro",
        "model": "kokoro",
        "checkpoint": "",
        "vocab_file": "",
        "device": "cpu"
      }
    },
    "paths": {
      "f5_tts_root": "/absolute/path/to/F5-TTS",
      "kokoro_renderer_root": "/absolute/path/to/magnetar-audio-renderer",
      "generated_audio_dir": "src/generated_audio"
    }
  }
}
```

### What Each Setting Does

- `audio.defaults.backend`: default backend selected in the create page.
- `audio.backends.<id>.enabled`: controls whether the backend is offered in the UI.
- `audio.backends.<id>.label`: human-readable name shown in the dropdown.
- `audio.backends.<id>.model`: default model name for that backend.
- `audio.backends.<id>.checkpoint`: default checkpoint.
- `audio.backends.<id>.vocab_file`: default vocabulary file when needed.
- `audio.backends.<id>.device`: default target device, such as `cpu`, `cuda`, or `mps`.
- `audio.paths.f5_tts_root`: root directory of the local `F5-TTS` clone.
- `audio.paths.kokoro_renderer_root`: root directory of the local Kokoro renderer project.
- `audio.paths.generated_audio_dir`: where generated payloads, transcripts, temp configs, and local outputs are stored.

## F5-TTS Notes

Use `F5-TTS` when you need multi-speaker rendering based on reference audios.

Requirements:
- valid local `F5-TTS` install
- valid local reference audio per speaker
- optional local checkpoints if you want fully offline execution

Important:
- `reference_audio_url` must point to a real local file.
- `reference_text` should match that reference audio when possible.
- if the backend tries to resolve checkpoints or vocoder assets from Hugging Face and the machine has no network or no cached assets, render will fail

## Kokoro Notes

Use `Kokoro` when you want a local JSON scene renderer without voice cloning.

Requirements:
- local `magnetar-audio-renderer`
- working Python environment there
- available Kokoro voice ids

Important:
- Kokoro uses `voice_id` per speaker
- it does not require `reference_audio_url`
- scene styles are interpreted by the external renderer

## Error Handling

The app surfaces render errors in two places:
- immediately on the `Crear Audio` page after a failed render
- on the audio card in the grid under `Último error de render`

Typical failure categories:
- missing local reference audio
- invalid `conversation_json`
- missing backend installation
- bad backend path in `appsettings.json`
- network download failure for model assets
- unsupported device setting

### Real Example of a F5-TTS Error

An actual render attempt from the app failed with a Hugging Face download error because the backend still needed a remote asset:

```text
Audio render failed: ... nodename nor servname provided, or not known ...
```

That means:
- the UI flow was working
- the backend command started
- the machine or backend cache was missing a required remote dependency

## Recommended Operating Modes

### Fully Offline F5-TTS

Recommended when you want repeatable local generation:
- clone `F5-TTS`
- pre-download required checkpoints
- pre-download any vocoder assets
- point `checkpoint`, `vocab_file`, and tool paths to local files

### Fast Local Alternative

Recommended when you want simpler local rendering without voice cloning:
- enable `kokoro`
- keep a known-good Kokoro install in `audio.paths.kokoro_renderer_root`
- use `voice_id` values that exist in that renderer environment

## Related Files

- [docs/USAGE.md](/Users/edwardflores/Projects/Development/MagnetarMnemosyne/docs/USAGE.md:1)
- [docs/DEVELOPMENT.md](/Users/edwardflores/Projects/Development/MagnetarMnemosyne/docs/DEVELOPMENT.md:1)
- [src/ui/server.py](/Users/edwardflores/Projects/Development/MagnetarMnemosyne/src/ui/server.py:1)
- [src/audio/render_runner.py](/Users/edwardflores/Projects/Development/MagnetarMnemosyne/src/audio/render_runner.py:1)
- [examples/audios/f5tts-audio-template.txt](/Users/edwardflores/Projects/Development/MagnetarMnemosyne/examples/audios/f5tts-audio-template.txt:1)
