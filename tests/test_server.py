import pytest
from fastapi.testclient import TestClient
import os
import sys
import json

# Add src to path
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(os.path.join(BASE_DIR, 'src'))

from ui.server import app
from exams.questions import load_questions, save_question, load_exams, save_exam, load_results

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
    for tab in ["questions", "exams", "results"]:
        response = client.get(f"/admin?tab={tab}")
        assert response.status_code == 200
        if tab == "questions": assert "Nueva Pregunta" in response.text
        if tab == "exams": assert "Nuevo Examen" in response.text
        if tab == "results": assert "Estudiante" in response.text

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
