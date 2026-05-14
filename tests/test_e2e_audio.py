import pytest
import time
import json
import os
import sys
from fastapi.testclient import TestClient

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(os.path.join(BASE_DIR, 'src'))

from ui.server import app
from exams.questions import load_questions, get_question
from audio.job_manager import get_audio_job

client = TestClient(app)

def test_e2e_audio_render_negative_flow():
    # Submit bad data to see how the system handles the error (negative test e2e)
    # Using f5-tts but giving bad placeholder data or just letting subprocess fail
    response = client.post("/admin/audios/create", data={
        "title": "e2e negative render",
        "language": "es-ES",
        "difficulty": "A1",
        "scene_description": "A test that should fail because of missing files.",
        "conversation_json": json.dumps({
            "speakers": [
                {"id": "teacher", "label": "Teacher", "descriptor": "calm", "reference_audio_url": "/absolute/path/to/missing-reference.wav", "reference_text": "Hola."}
            ],
            "dialogue": "Teacher (calm):\nHola."
        }),
        "backend": "f5-tts", # Let's use f5-tts with bad reference audio
        "output_name": "e2e-negative-test.wav",
        "submit_action": "render",
    }, follow_redirects=True)

    assert response.status_code == 200
    assert "Render iniciado" in response.text or "Se está creando el audio" in response.text
    
    # The job_id is injected in the HTML. We can find it.
    import re
    match = re.search(r'/ws/audio-jobs/([a-f0-9\-]+)', response.text)
    assert match is not None, "Should have job_id in HTML"
    job_id = match.group(1)

    # Wait for the background thread to finish (should be fast because file doesn't exist)
    timeout = 10
    start_time = time.time()
    job = None
    while time.time() - start_time < timeout:
        job = get_audio_job(job_id)
        if job and job.get("status") in ("completed", "failed"):
            break
        time.sleep(0.5)

    assert job is not None
    assert job["status"] == "failed", f"Expected failed status, got {job['status']}"
    assert "error" in job
    assert "missing-reference.wav" in job["error"] or "missing" in job["error"].lower() or "error" in job["error"].lower() or "fail" in job["error"].lower()

    # We also check the database state
    questions = load_questions()
    target_q = next(q for q in questions if q["question"] == "Escucha e2e negative render y responde a las preguntas.")
    
    # Reload from DB to be sure
    q_db = get_question(target_q["id"])
    render_state = q_db["conversation_payload"]["render"]
    
    assert render_state["status"] == "failed"
    err = render_state.get("last_error", "")
    assert "missing-reference.wav" in err or "missing" in err.lower() or "error" in err.lower() or "fail" in err.lower()

    print("End-to-end negative test passed successfully.")
