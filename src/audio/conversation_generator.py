import json
import re
from dataclasses import asdict, dataclass
from typing import Any


_DIALOGUE_BLOCK_RE = re.compile(
    r"(?ms)^\s*(?P<label>[^\n:]+?)\s*\((?P<descriptor>[^)]*)\):\s*\n(?P<body>.*?)(?=^\s*[^\n:]+?\s*\([^)]*\):\s*\n|\Z)"
)


@dataclass
class Speaker:
    id: str
    label: str
    descriptor: str
    persona: str = ""
    speech_direction: str = ""
    voice_id: str | None = None
    reference_audio_url: str | None = None
    reference_text: str | None = None


@dataclass
class Turn:
    speaker_id: str
    text: str


def _slugify(value: str) -> str:
    normalized = re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")
    return normalized or "speaker"


def _normalize_speakers(raw_speakers: list[dict[str, Any]]) -> list[Speaker]:
    speakers: list[Speaker] = []
    seen_ids: set[str] = set()

    for index, raw_speaker in enumerate(raw_speakers):
        label = str(raw_speaker.get("label") or raw_speaker.get("name") or f"Speaker {index + 1}").strip()
        speaker_id = str(raw_speaker.get("id") or _slugify(label)).strip()

        if not label:
            raise ValueError("Each speaker must include a non-empty label.")
        if speaker_id in seen_ids:
            raise ValueError(f"Duplicate speaker id '{speaker_id}' in conversation payload.")

        speakers.append(
            Speaker(
                id=speaker_id,
                label=label,
                descriptor=str(raw_speaker.get("descriptor") or raw_speaker.get("voice_hint") or "").strip(),
                persona=str(raw_speaker.get("persona") or "").strip(),
                speech_direction=str(raw_speaker.get("speech_direction") or "").strip(),
                voice_id=raw_speaker.get("voice_id"),
                reference_audio_url=raw_speaker.get("reference_audio_url"),
                reference_text=raw_speaker.get("reference_text"),
            )
        )
        seen_ids.add(speaker_id)

    return speakers


def _parse_dialogue_string(dialogue: str, speakers: list[Speaker]) -> list[Turn]:
    label_to_id = {speaker.label.casefold(): speaker.id for speaker in speakers}
    turns: list[Turn] = []

    for match in _DIALOGUE_BLOCK_RE.finditer(dialogue.strip()):
        label = match.group("label").strip()
        body = match.group("body").strip()
        speaker_id = label_to_id.get(label.casefold())
        if speaker_id is None:
            raise ValueError(f"Dialogue block references unknown speaker label '{label}'.")
        if not body:
            raise ValueError(f"Dialogue block for speaker '{label}' is empty.")
        turns.append(Turn(speaker_id=speaker_id, text=body))

    if not turns:
        raise ValueError("Conversation dialogue did not contain any valid speaker blocks.")

    return turns


def _normalize_turns(raw_turns: list[dict[str, Any]], speakers: list[Speaker]) -> list[Turn]:
    valid_speaker_ids = {speaker.id for speaker in speakers}
    turns: list[Turn] = []

    for raw_turn in raw_turns:
        speaker_id = str(raw_turn.get("speaker_id") or "").strip()
        text = str(raw_turn.get("text") or "").strip()
        if speaker_id not in valid_speaker_ids:
            raise ValueError(f"Turn references unknown speaker id '{speaker_id}'.")
        if not text:
            raise ValueError(f"Turn for speaker '{speaker_id}' is empty.")
        turns.append(Turn(speaker_id=speaker_id, text=text))

    if not turns:
        raise ValueError("Conversation payload must include at least one turn.")

    return turns


def _default_question_text(payload: dict[str, Any]) -> str:
    title = str(payload.get("title") or "la conversación").strip()
    return f"Escucha {title} y responde a las preguntas."


def parse_conversation_payload(raw_payload: str | dict[str, Any]) -> dict[str, Any]:
    if isinstance(raw_payload, str):
        payload = json.loads(raw_payload)
    else:
        payload = raw_payload

    conversation = payload.get("conversation", payload)
    speakers = _normalize_speakers(conversation.get("speakers") or [])
    if len(speakers) == 0:
        raise ValueError("Conversation payload must include at least one speaker.")

    raw_turns = conversation.get("turns")
    raw_dialogue = conversation.get("dialogue")
    if raw_turns:
        turns = _normalize_turns(raw_turns, speakers)
    elif raw_dialogue:
        turns = _parse_dialogue_string(str(raw_dialogue), speakers)
    else:
        raise ValueError("Conversation payload must include either 'turns' or 'dialogue'.")

    normalized = {
        "title": str(conversation.get("title") or payload.get("title") or "la conversación").strip(),
        "question": str(payload.get("question") or _default_question_text(conversation)).strip(),
        "language": str(conversation.get("language") or payload.get("language") or "").strip(),
        "difficulty": str(conversation.get("difficulty") or payload.get("difficulty") or "").strip(),
        "duration_target": str(conversation.get("duration_target") or payload.get("duration_target") or "").strip(),
        "scene_description": str(conversation.get("scene_description") or payload.get("scene_description") or "").strip(),
        "instructions": str(conversation.get("instructions") or payload.get("instructions") or "").strip(),
        "allowed_topics": conversation.get("allowed_topics") or payload.get("allowed_topics") or [],
        "speakers": [asdict(speaker) for speaker in speakers],
        "turns": [asdict(turn) for turn in turns],
        "audio_url": str(payload.get("audio_url") or conversation.get("audio_url") or "").strip(),
        "render": payload.get("render") or conversation.get("render") or {},
    }

    return normalized


def format_dialogue_for_render(conversation_payload: dict[str, Any]) -> str:
    speakers_by_id = {speaker["id"]: speaker for speaker in conversation_payload["speakers"]}
    blocks: list[str] = []

    for turn in conversation_payload["turns"]:
        speaker = speakers_by_id[turn["speaker_id"]]
        descriptor = speaker.get("descriptor") or speaker.get("persona") or "speaker"
        blocks.append(f'{speaker["label"]} ({descriptor}):\n{turn["text"]}')

    return "\n\n".join(blocks)


def build_render_job(raw_payload: str | dict[str, Any]) -> dict[str, Any]:
    conversation_payload = parse_conversation_payload(raw_payload)
    render_config = conversation_payload.get("render") or {}

    return {
        "backend": render_config.get("backend", "f5-tts"),
        "model": render_config.get("model", ""),
        "checkpoint": render_config.get("checkpoint", ""),
        "output_path": render_config.get("output_path", ""),
        "selected_voices": render_config.get("selected_voices", {}),
        "audio_url": conversation_payload.get("audio_url"),
        "transcript": format_dialogue_for_render(conversation_payload),
        "conversation": conversation_payload,
        "status": "pending" if not conversation_payload.get("audio_url") else "ready",
    }


def build_audio_question_from_payload(raw_payload: str | dict[str, Any]) -> dict[str, Any]:
    conversation_payload = parse_conversation_payload(raw_payload)
    render_job = build_render_job(conversation_payload)

    explanation_parts = [
        f"Idioma: {conversation_payload['language']}" if conversation_payload["language"] else "",
        f"Nivel: {conversation_payload['difficulty']}" if conversation_payload["difficulty"] else "",
        f"Duración objetivo: {conversation_payload['duration_target']}" if conversation_payload["duration_target"] else "",
    ]

    return {
        "type": "audio_listening",
        "question": conversation_payload["question"],
        "explanation": "\n".join(part for part in explanation_parts if part),
        "audio_url": conversation_payload["audio_url"] or None,
        "conversation_payload": conversation_payload,
        "render_job": render_job,
    }
