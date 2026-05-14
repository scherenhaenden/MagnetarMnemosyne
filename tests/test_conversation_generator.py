import os
import sys


BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(os.path.join(BASE_DIR, "src"))

from audio import build_audio_question_from_payload, build_render_job, format_dialogue_for_render


SAMPLE_PAYLOAD = {
    "question": "Escucha la conversación y responde a las preguntas.",
    "conversation": {
        "title": "una entrevista escolar",
        "language": "es-ES",
        "difficulty": "A1",
        "duration_target": "about 3 minutes",
        "speakers": [
            {
                "id": "teacher",
                "label": "Teacher",
                "descriptor": "calm Spanish woman from Madrid",
                "persona": "adult female teacher from Spain",
                "reference_audio_url": "/tmp/teacher.wav",
                "reference_text": "Buenos días. ¿Cómo te llamas?",
            },
            {
                "id": "student",
                "label": "Student",
                "descriptor": "young girl, slightly nervous",
                "persona": "12-year-old girl, slightly nervous but friendly",
                "reference_audio_url": "/tmp/student.wav",
                "reference_text": "Hola. Me llamo Lía.",
            },
        ],
        "dialogue": """Teacher (calm Spanish woman from Madrid):
[warmly]
Buenos días. ¿Cómo te llamas?

Student (young girl, slightly nervous):
[nervous]
Hola. Me llamo Lía.""",
        "render": {
            "backend": "f5-tts",
            "selected_voices": {
                "teacher": "voice-teacher-es",
                "student": "voice-student-es",
            },
        },
    },
}


def test_build_audio_question_from_payload():
    question = build_audio_question_from_payload(SAMPLE_PAYLOAD)
    assert question["type"] == "audio_listening"
    assert question["question"] == "Escucha la conversación y responde a las preguntas."
    assert question["conversation_payload"]["language"] == "es-ES"
    assert len(question["conversation_payload"]["turns"]) == 2


def test_format_dialogue_for_render():
    question = build_audio_question_from_payload(SAMPLE_PAYLOAD)
    transcript = format_dialogue_for_render(question["conversation_payload"])
    assert "Teacher (calm Spanish woman from Madrid):" in transcript
    assert "Student (young girl, slightly nervous):" in transcript


def test_build_render_job_marks_pending_without_audio_url():
    render_job = build_render_job(SAMPLE_PAYLOAD)
    assert render_job["backend"] == "f5-tts"
    assert render_job["status"] == "pending"
    assert render_job["selected_voices"]["teacher"] == "voice-teacher-es"
