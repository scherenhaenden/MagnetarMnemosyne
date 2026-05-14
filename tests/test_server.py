import pytest
from fastapi.testclient import TestClient
import os
import sys
import json
from unittest.mock import patch

# Add src to path
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(os.path.join(BASE_DIR, 'src'))

from ui.server import app
from exams.questions import load_questions, save_question, load_exams, save_exam, load_results, get_question

client = TestClient(app)

@pytest.fixture(autouse=True)
def setup_test_db():
    # We are using the real DB for now, but we'll try to keep it clean or use a test DB in a real scenario
    # For this prototype, we'll just ensure there's at least one question and one exam
    qs = load_questions()
    if not qs:
        save_question({
            "type": "multiple_choice",
            "question": "Test Q?",
            "options": ["A", "B", "C", "D"],
            "correctAnswerIndex": 0,
            "explanation": "Exp"
        })
    
    exs = load_exams()
    if not exs:
        save_exam("Test Exam", [1])
    yield

def test_read_root():
    response = client.get("/")
    assert response.status_code == 200
    assert "Sistema de Exámenes" in response.text

def test_start_exam():
    # Need examId and studentName now
    exs = load_exams()
    exam_id = exs[0]["id"]
    response = client.post("/start", data={
        "feedbackMode": "immediate",
        "examId": exam_id,
        "studentName": "Tester"
    })
    assert response.status_code == 200
    assert "Tester" not in response.text # Student name is in state, not necessarily on page immediately
    # But questions should be there
    assert "1." in response.text

def test_full_exam_flow():
    exs = load_exams()
    exam_id = exs[0]["id"]
    client.post("/start", data={
        "feedbackMode": "immediate",
        "examId": exam_id,
        "studentName": "Tester"
    })
    
    # Select option
    response = client.post("/select", data={"optionIndex": 0})
    assert response.status_code == 200
    
    # Next (should finish if only 1 question)
    response = client.post("/next")
    assert response.status_code == 200
    assert "¡Buen trabajo, Tester!" in response.text
    
    # Check results
    results = load_results()
    assert any(r["student_name"] == "Tester" for r in results)

def test_admin_dashboard_tabs():
    for tab in ["questions", "exams", "audios", "results"]:
        response = client.get(f"/admin?tab={tab}")
        assert response.status_code == 200
        if tab == "questions": assert "Nueva Pregunta" in response.text
        if tab == "exams": assert "Nuevo Examen" in response.text
        if tab == "audios": assert "Crear Audio" in response.text
        if tab == "results": assert "Estudiante" in response.text

def test_admin_audio_create_view():
    response = client.get("/admin?tab=audios&mode=create")
    assert response.status_code == 200
    assert "Descripción del Audio" in response.text
    assert "Settings de Creación" in response.text
    assert "F5-TTS" in response.text
    assert "Kokoro" in response.text
    assert "Ruta raíz de F5-TTS" not in response.text
    assert 'name="device"' not in response.text
    assert 'name="checkpoint"' not in response.text
    assert 'name="vocab_file"' not in response.text
    assert "Se está creando el audio" in response.text

def test_admin_create_exam():
    # Add a question first to ensure we have one
    client.post("/admin/add", data={
        "type": "multiple_choice",
        "question": "Exam Question?",
        "option0": "1", "option1": "2", "option2": "3", "option3": "4",
        "correctIndex": 0,
        "explanation": "Exp"
    })
    
    # Create exam
    response = client.post("/admin/exams/add", data={
        "title": "New Exam",
        "q_ids": [1, 2]
    }, follow_redirects=True)
    assert response.status_code == 200
    assert "New Exam" in response.text

def test_admin_import_conversation_question():
    payload = {
        "question": "Escucha la conversación y responde a las preguntas.",
        "conversation": {
            "language": "es-ES",
            "difficulty": "A1",
            "speakers": [
                {"id": "teacher", "label": "Teacher", "descriptor": "calm Spanish woman from Madrid"},
                {"id": "student", "label": "Student", "descriptor": "young girl, slightly nervous"},
            ],
            "dialogue": """Teacher (calm Spanish woman from Madrid):
[warmly]
Buenos días. ¿Cómo te llamas?

Student (young girl, slightly nervous):
[nervous]
Hola. Me llamo Lía.""",
        },
    }

    response = client.post("/admin/import/conversation", data={
        "json_data": json.dumps(payload)
    }, follow_redirects=True)

    assert response.status_code == 200
    questions = load_questions()
    assert any(q["question"] == payload["question"] and q["type"] == "audio_listening" for q in questions)

def test_admin_create_audio_from_dashboard():
    response = client.post("/admin/audios/create", data={
        "title": "entrevista escolar",
        "language": "es-ES",
        "difficulty": "A1",
        "scene_description": "Una profesora habla con una alumna.",
        "conversation_json": json.dumps({
            "speakers": [
                {"id": "teacher", "label": "Teacher", "descriptor": "calm Spanish woman from Madrid", "reference_audio_url": "/tmp/teacher.wav", "reference_text": "Buenos días."},
                {"id": "student", "label": "Student", "descriptor": "young girl, slightly nervous", "reference_audio_url": "/tmp/student.wav", "reference_text": "Hola."},
            ],
            "dialogue": """Teacher (calm Spanish woman from Madrid):
[warmly]
Buenos días. ¿Cómo te llamas?

Student (young girl, slightly nervous):
[nervous]
Hola. Me llamo Lía."""
        }),
        "backend": "f5-tts",
        "output_name": "lia-school-scene.wav",
        "submit_action": "save",
    }, follow_redirects=True)

    assert response.status_code == 200
    assert "Audio guardado como borrador." in response.text
    assert "Crear Audio" in response.text
    questions = load_questions()
    assert any(q["question"] == "Escucha entrevista escolar y responde a las preguntas." for q in questions)

def test_admin_create_kokoro_audio_from_dashboard():
    response = client.post("/admin/audios/create", data={
        "title": "entrevista kokoro",
        "language": "es-ES",
        "difficulty": "A1",
        "scene_description": "Una escena usando kokoro.",
        "conversation_json": json.dumps({
            "speakers": [
                {"id": "teacher", "label": "Teacher", "descriptor": "teacher", "voice_id": "ef_dora"},
                {"id": "student", "label": "Student", "descriptor": "student", "voice_id": "ef_dora"},
            ],
            "dialogue": """Teacher (teacher):
Buenos días.

Student (student):
Hola."""
        }),
        "backend": "kokoro",
        "output_name": "kokoro-scene.wav",
        "submit_action": "save",
    }, follow_redirects=True)

    assert response.status_code == 200
    assert "Audio guardado como borrador." in response.text
    questions = load_questions()
    assert any(q["question"] == "Escucha entrevista kokoro y responde a las preguntas." for q in questions)

def test_admin_create_audio_renders_from_create_view_and_stays_on_page():
    with patch("ui.server.start_audio_render_job", return_value="job-123") as mock_start_job:
        response = client.post("/admin/audios/create", data={
            "title": "entrevista render",
            "language": "es-ES",
            "difficulty": "A1",
            "scene_description": "Una profesora habla con una alumna.",
            "conversation_json": json.dumps({
                "speakers": [
                    {"id": "teacher", "label": "Teacher", "descriptor": "calm Spanish woman from Madrid", "reference_audio_url": "/tmp/teacher.wav", "reference_text": "Buenos días."},
                    {"id": "student", "label": "Student", "descriptor": "young girl, slightly nervous", "reference_audio_url": "/tmp/student.wav", "reference_text": "Hola."},
                ],
                "dialogue": """Teacher (calm Spanish woman from Madrid):
[warmly]
Buenos días. ¿Cómo te llamas?

Student (young girl, slightly nervous):
[nervous]
Hola. Me llamo Lía."""
            }),
            "backend": "f5-tts",
            "output_name": "lia-school-created.wav",
            "submit_action": "render",
        }, follow_redirects=True)

    assert response.status_code == 200
    assert "Render iniciado. La página mostrará el progreso automáticamente." in response.text
    assert "Crear Audio" in response.text
    assert "job-123" in response.text
    mock_start_job.assert_called_once()
    created = next(q for q in reversed(load_questions()) if q["question"] == "Escucha entrevista render y responde a las preguntas.")
    assert created["conversation_payload"]["render"]["status"] == "queued"

def test_admin_create_audio_render_error_stays_on_create_view():
    with patch("ui.server.start_audio_render_job", side_effect=RuntimeError("missing reference audio")):
        response = client.post("/admin/audios/create", data={
            "title": "entrevista con error",
            "language": "es-ES",
            "difficulty": "A1",
            "scene_description": "Una profesora habla con una alumna.",
            "conversation_json": json.dumps({
                "speakers": [
                    {"id": "teacher", "label": "Teacher", "descriptor": "calm Spanish woman from Madrid", "reference_audio_url": "/tmp/teacher.wav", "reference_text": "Buenos días."},
                ],
                "dialogue": """Teacher (calm Spanish woman from Madrid):
Buenos días."""
            }),
            "backend": "f5-tts",
            "output_name": "lia-school-failed.wav",
            "submit_action": "render",
        }, follow_redirects=True)

    assert response.status_code == 400
    assert "Error al crear audio" in response.text
    assert "missing reference audio" in response.text
    assert "Crear Audio" in response.text
    created = next(q for q in load_questions() if q["question"] == "Escucha entrevista con error y responde a las preguntas.")
    assert created["conversation_payload"]["render"]["status"] in {"queued", "pending", "failed"}

def test_admin_render_audio_route():
    client.post("/admin/audios/create", data={
        "title": "audio para render",
        "language": "es-ES",
        "difficulty": "A1",
        "scene_description": "Render test.",
        "conversation_json": json.dumps({
            "speakers": [
                {"id": "teacher", "label": "Teacher", "descriptor": "calm Spanish woman from Madrid", "reference_audio_url": "/tmp/teacher.wav", "reference_text": "Buenos días."},
                {"id": "student", "label": "Student", "descriptor": "young girl, slightly nervous", "reference_audio_url": "/tmp/student.wav", "reference_text": "Hola."},
            ],
            "dialogue": """Teacher (calm Spanish woman from Madrid):
[warmly]
Buenos días.

Student (young girl, slightly nervous):
[nervous]
Hola.""",
        }),
        "backend": "f5-tts",
        "output_name": "audio-render-test.wav",
        "submit_action": "save",
    }, follow_redirects=True)

    target = next(q for q in load_questions() if q["question"] == "Escucha audio para render y responde a las preguntas.")

    with patch("ui.server.render_audio_question") as mock_render:
        mock_render.return_value = {
            "audio_url": "/tmp/audio-render-test.wav",
            "render_status": "ready",
            "transcript_path": "/tmp/audio-render-test.transcript.txt",
            "payload_path": "/tmp/audio-render-test.payload.json",
            "output_path": "/tmp/audio-render-test.wav",
            "backend_command": "fake-render-command",
            "backend_stdout": "ok",
        }
        response = client.post(f"/admin/audios/render/{target['id']}", follow_redirects=True)

    assert response.status_code == 200
    updated = get_question(target["id"])
    assert updated["audio_url"] == "/tmp/audio-render-test.wav"
    assert updated["conversation_payload"]["render"]["status"] == "ready"
    assert updated["conversation_payload"]["render"]["last_error"] == ""

def test_admin_render_audio_route_persists_failure():
    client.post("/admin/audios/create", data={
        "title": "audio con fallo",
        "language": "es-ES",
        "difficulty": "A1",
        "scene_description": "Render failure test.",
        "conversation_json": json.dumps({
            "speakers": [
                {"id": "teacher", "label": "Teacher", "descriptor": "calm Spanish woman from Madrid", "reference_audio_url": "/tmp/teacher.wav", "reference_text": "Buenos días."}
            ],
            "dialogue": """Teacher (calm Spanish woman from Madrid):
Buenos días."""
        }),
        "backend": "f5-tts",
        "output_name": "audio-render-failure.wav",
        "submit_action": "save",
    }, follow_redirects=True)

    target = next(q for q in load_questions() if q["question"] == "Escucha audio con fallo y responde a las preguntas.")

    with patch("ui.server.render_audio_question", side_effect=RuntimeError("boom")):
        response = client.post(f"/admin/audios/render/{target['id']}", follow_redirects=True)

    assert response.status_code == 200
    updated = get_question(target["id"])
    assert updated["conversation_payload"]["render"]["status"] == "failed"
    assert updated["conversation_payload"]["render"]["last_error"] == "boom"

def test_admin_render_kokoro_audio_route():
    client.post("/admin/audios/create", data={
        "title": "audio kokoro render",
        "language": "es-ES",
        "difficulty": "A1",
        "scene_description": "Render kokoro test.",
        "conversation_json": json.dumps({
            "speakers": [
                {"id": "teacher", "label": "Teacher", "descriptor": "teacher", "voice_id": "ef_dora"}
            ],
            "dialogue": """Teacher (teacher):
Buenos días."""
        }),
        "backend": "kokoro",
        "output_name": "kokoro-render-test.wav",
        "submit_action": "save",
    }, follow_redirects=True)

    target = next(q for q in load_questions() if q["question"] == "Escucha audio kokoro render y responde a las preguntas.")

    with patch("ui.server.render_audio_question") as mock_render:
        mock_render.return_value = {
            "audio_url": "/tmp/kokoro-render-test.wav",
            "render_status": "ready",
            "transcript_path": "/tmp/kokoro-render-test.transcript.txt",
            "payload_path": "/tmp/kokoro-render-test.payload.json",
            "output_path": "/tmp/kokoro-render-test.wav",
            "backend_command": "fake-kokoro-render",
            "backend_stdout": "ok",
        }
        response = client.post(f"/admin/audios/render/{target['id']}", follow_redirects=True)

    assert response.status_code == 200
    updated = get_question(target["id"])
    assert updated["audio_url"] == "/tmp/kokoro-render-test.wav"
    assert updated["conversation_payload"]["render"]["status"] == "ready"
