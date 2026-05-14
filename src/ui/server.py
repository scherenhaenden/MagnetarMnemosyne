from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from exams.questions import (
    save_question, load_questions, delete_question, 
    load_exams, save_exam, save_result, load_results,
    delete_exam, update_exam
)
import uvicorn
import os
import json

app = FastAPI()

templates_path = os.path.join(os.path.dirname(__file__), "templates")
templates = Jinja2Templates(directory=templates_path)

def from_json(value):
    try:
        return json.loads(value)
    except:
        return []

templates.env.filters["from_json"] = from_json

# In-memory state for the exam taker
exam_state = {
    "appStage": "intro",
    "feedbackMode": "immediate",
    "currentQuestionIndex": 0,
    "userAnswers": {},
    "currentExamId": None,
    "studentName": "Invitado"
}

def get_stats(questions):
    correct = 0
    incorrect = 0
    for q_idx, ans_idx in exam_state["userAnswers"].items():
        q_idx_int = int(q_idx)
        if q_idx_int < len(questions) and questions[q_idx_int].get("type") == "multiple_choice":
            if ans_idx == questions[q_idx_int]["correctAnswerIndex"]:
                correct += 1
            else:
                incorrect += 1
    return {"correct": correct, "incorrect": incorrect, "total": len(questions)}

# --- EXAM TAKER ROUTES ---

@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    exams = load_exams()
    return templates.TemplateResponse(request, "index.html", {
        "state": exam_state, 
        "exams": exams
    })

@app.post("/start", response_class=HTMLResponse)
async def start_exam(request: Request, feedbackMode: str = Form(...), examId: int = Form(...), studentName: str = Form("Invitado")):
    exam_state["appStage"] = "exam"
    exam_state["feedbackMode"] = feedbackMode
    exam_state["currentQuestionIndex"] = 0
    exam_state["userAnswers"] = {}
    exam_state["currentExamId"] = examId
    exam_state["studentName"] = studentName
    
    # Load specific questions for this exam
    exams = load_exams()
    exam = next((e for e in exams if e["id"] == examId), None)
    all_questions = load_questions()
    
    if exam and exam["question_ids"]:
        q_ids = json.loads(exam["question_ids"])
        # Map questions in order
        q_map = {q["id"]: q for q in all_questions}
        exam_questions = [q_map[qid] for qid in q_ids if qid in q_map]
    else:
        exam_questions = all_questions

    return templates.TemplateResponse(request, "index.html", {
        "state": exam_state, 
        "questions": exam_questions,
        "stats": get_stats(exam_questions)
    })

@app.post("/select", response_class=HTMLResponse)
async def select_option(request: Request, optionIndex: int = Form(...)):
    curr_idx = exam_state["currentQuestionIndex"]
    
    # Reload questions for context
    exams = load_exams()
    exam = next((e for e in exams if e["id"] == exam_state["currentExamId"]), None)
    all_questions = load_questions()
    if exam and exam["question_ids"]:
        q_ids = json.loads(exam["question_ids"])
        q_map = {q["id"]: q for q in all_questions}
        exam_questions = [q_map[qid] for qid in q_ids if qid in q_map]
    else:
        exam_questions = all_questions

    if exam_state["feedbackMode"] == "immediate" and curr_idx in exam_state["userAnswers"]:
        pass
    else:
        exam_state["userAnswers"][curr_idx] = optionIndex
        
    return templates.TemplateResponse(request, "index.html", {
        "state": exam_state, 
        "questions": exam_questions,
        "stats": get_stats(exam_questions)
    })

@app.post("/next", response_class=HTMLResponse)
async def next_question(request: Request):
    exams = load_exams()
    exam = next((e for e in exams if e["id"] == exam_state["currentExamId"]), None)
    all_questions = load_questions()
    if exam and exam["question_ids"]:
        q_ids = json.loads(exam["question_ids"])
        q_map = {q["id"]: q for q in all_questions}
        exam_questions = [q_map[qid] for qid in q_ids if qid in q_map]
    else:
        exam_questions = all_questions

    if exam_state["currentQuestionIndex"] < len(exam_questions) - 1:
        exam_state["currentQuestionIndex"] += 1
    else:
        exam_state["appStage"] = "results"
        # Save result to DB
        stats = get_stats(exam_questions)
        percentage = (stats["correct"] / stats["total"]) * 100 if stats["total"] > 0 else 0
        save_result(exam_state["studentName"], exam_state["currentExamId"], stats["correct"], stats["total"], percentage)
        
    return templates.TemplateResponse(request, "index.html", {
        "state": exam_state, 
        "questions": exam_questions,
        "stats": get_stats(exam_questions)
    })

@app.post("/restart", response_class=HTMLResponse)
async def restart(request: Request):
    exam_state["appStage"] = "intro"
    exam_state["userAnswers"] = {}
    exam_state["currentQuestionIndex"] = 0
    return templates.TemplateResponse(request, "index.html", {
        "state": exam_state, 
        "exams": load_exams()
    })

# --- ADMIN DASHBOARD ROUTES ---

@app.get("/admin", response_class=HTMLResponse)
async def admin_dashboard(request: Request, tab: str = "questions"):
    questions = load_questions()
    exams = load_exams()
    results = load_results()
    return templates.TemplateResponse(request, "admin.html", {
        "questions": questions,
        "exams": exams,
        "results": results,
        "active_tab": tab
    })
@app.post("/admin/exams/delete/{exam_id}", response_class=HTMLResponse)
async def delete_exam_route(request: Request, exam_id: int):
    delete_exam(exam_id)
    return RedirectResponse(url="/admin?tab=exams", status_code=303)

@app.get("/admin/exams/edit/{exam_id}", response_class=HTMLResponse)
async def edit_exam_view(request: Request, exam_id: int):
    exams = load_exams()
    exam = next((e for e in exams if e["id"] == exam_id), None)
    questions = load_questions()
    selected_ids = json.loads(exam["question_ids"]) if exam and exam["question_ids"] else []
    return templates.TemplateResponse(request, "admin.html", {
        "questions": questions,
        "exams": exams,
        "active_tab": "exams",
        "editing_exam": exam,
        "selected_ids": selected_ids
    })

@app.post("/admin/exams/update/{exam_id}", response_class=HTMLResponse)
async def update_exam_route(request: Request, exam_id: int, title: str = Form(...), q_ids: list[int] = Form(...)):
    update_exam(exam_id, title, q_ids)
    return RedirectResponse(url="/admin?tab=exams", status_code=303)

@app.post("/admin/add", response_class=HTMLResponse)
async def add_question_route(
    request: Request,
    type: str = Form(...),
    question: str = Form(...),
    option0: str = Form(None),
    option1: str = Form(None),
    option2: str = Form(None),
    option3: str = Form(None),
    correctIndex: int = Form(None),
    explanation: str = Form(""),
    audioUrl: str = Form(None)
):
    new_q = {
        "type": type,
        "question": question,
        "explanation": explanation,
        "audio_url": audioUrl
    }
    if type == "multiple_choice":
        new_q["options"] = [option0, option1, option2, option3]
        new_q["correctAnswerIndex"] = correctIndex
    save_question(new_q)
    return RedirectResponse(url="/admin?tab=questions", status_code=303)

def run_ui():

@app.post("/admin/delete/{q_id}", response_class=HTMLResponse)
async def delete_question_route(request: Request, q_id: int):
    delete_question(q_id)
    return RedirectResponse(url="/admin?tab=questions", status_code=303)

@app.post("/admin/exams/add", response_class=HTMLResponse)
async def add_exam_route(request: Request, title: str = Form(...), q_ids: list[int] = Form(...)):
    save_exam(title, q_ids)
    return RedirectResponse(url="/admin?tab=exams", status_code=303)

@app.post("/admin/import", response_class=HTMLResponse)
async def import_questions(request: Request, json_data: str = Form(...)):
    try:
        data = json.loads(json_data)
        if isinstance(data, list):
            for q in data: save_question(q)
        else:
            save_question(data)
    except Exception as e:
        print(f"Import error: {e}")
    return RedirectResponse(url="/admin?tab=questions", status_code=303)

def run_ui():
    print("Starting UI on http://0.0.0.0:8000")
    print("Admin Dashboard: http://0.0.0.0:8000/admin")
    uvicorn.run(app, host="0.0.0.0", port=8000)

if __name__ == "__main__":
    run_ui()
