import pytest
from fastapi.testclient import TestClient
import os
import sys

# Add src to path
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(os.path.join(BASE_DIR, 'src'))

from ui.server import app
from exams.questions import load_questions, save_questions

client = TestClient(app)

@pytest.fixture(autouse=True)
def setup_test_questions():
    # Backup real questions if they exist, use a clean set for tests
    original_questions = load_questions()
    test_questions = [
        {
            "id": 1,
            "type": "multiple_choice",
            "question": "Test Question?",
            "options": ["A", "B", "C", "D"],
            "correctAnswerIndex": 0,
            "explanation": "Test Explanation"
        }
    ]
    save_questions(test_questions)
    yield
    save_questions(original_questions)

def test_read_root():
    response = client.get("/")
    assert response.status_code == 200
    assert "Examen de Prueba" in response.text

def test_start_exam():
    response = client.post("/start", data={"feedbackMode": "immediate"})
    assert response.status_code == 200
    assert "Test Question?" in response.text

def test_select_option():
    # First start the exam
    client.post("/start", data={"feedbackMode": "immediate"})
    # Select an option
    response = client.post("/select", data={"optionIndex": 0})
    assert response.status_code == 200
    assert "¡Correcto!" in response.text

def test_next_question():
    client.post("/start", data={"feedbackMode": "immediate"})
    client.post("/select", data={"optionIndex": 0})
    response = client.post("/next")
    assert response.status_code == 200
    # Since there's only 1 question, it should go to results
    assert "Examen Completado" in response.text

def test_restart():
    client.post("/start", data={"feedbackMode": "immediate"})
    response = client.post("/restart")
    assert response.status_code == 200
    assert "Examen de Prueba" in response.text

def test_admin_dashboard():
    response = client.get("/admin")
    assert response.status_code == 200
    assert "Admin Dashboard" in response.text

def test_admin_import_json():
    import json
    new_q = {
        "type": "multiple_choice",
        "question": "JSON Q?",
        "options": ["J1", "J2", "J3", "J4"],
        "correctAnswerIndex": 1,
        "explanation": "Exp"
    }
    response = client.post("/admin/import", data={
        "json_data": json.dumps([new_q])
    }, follow_redirects=True)
    assert response.status_code == 200
    assert "JSON Q?" in response.text

def test_admin_add_delete():
    # Add a question
    response = client.post("/admin/add", data={
        "type": "long_text",
        "question": "New Long Question",
        "explanation": "Exp"
    }, follow_redirects=True)
    assert response.status_code == 200
    assert "New Long Question" in response.text
    
    # Delete it
    # We need to find the ID of the new question. It should be 2.
    response = client.post("/admin/delete/2", follow_redirects=True)
    assert response.status_code == 200
    assert "New Long Question" not in response.text
