from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from exams.questions import EXAM_QUESTIONS, save_questions, load_questions
import uvicorn
import os

app = FastAPI()

templates_path = os.path.join(os.path.dirname(__file__), "templates")
templates = Jinja2Templates(directory=templates_path)

# In-memory state for the exam taker
exam_state = {
    "appStage": "intro",
    "feedbackMode": "immediate",
    "currentQuestionIndex": 0,
    "userAnswers": {},
}

def get_stats():
    questions = load_questions()
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
    questions = load_questions()
    return templates.TemplateResponse(request, "index.html", {
        "state": exam_state, 
        "questions": questions,
        "stats": get_stats()
    })

@app.post("/start", response_class=HTMLResponse)
async def start_exam(request: Request, feedbackMode: str = Form(...)):
    exam_state["appStage"] = "exam"
    exam_state["feedbackMode"] = feedbackMode
    exam_state["currentQuestionIndex"] = 0
    exam_state["userAnswers"] = {}
    return templates.TemplateResponse(request, "index.html", {
        "state": exam_state, 
        "questions": load_questions(),
        "stats": get_stats()
    })

@app.post("/select", response_class=HTMLResponse)
async def select_option(request: Request, optionIndex: int = Form(...)):
    curr_idx = exam_state["currentQuestionIndex"]
    if exam_state["feedbackMode"] == "immediate" and curr_idx in exam_state["userAnswers"]:
        pass
    else:
        exam_state["userAnswers"][curr_idx] = optionIndex
    return templates.TemplateResponse(request, "index.html", {
        "state": exam_state, 
        "questions": load_questions(),
        "stats": get_stats()
    })

@app.post("/next", response_class=HTMLResponse)
async def next_question(request: Request):
    questions = load_questions()
    if exam_state["currentQuestionIndex"] < len(questions) - 1:
        exam_state["currentQuestionIndex"] += 1
    else:
        exam_state["appStage"] = "results"
    return templates.TemplateResponse(request, "index.html", {
        "state": exam_state, 
        "questions": questions,
        "stats": get_stats()
    })

@app.post("/restart", response_class=HTMLResponse)
async def restart(request: Request):
    exam_state["appStage"] = "intro"
    exam_state["userAnswers"] = {}
    exam_state["currentQuestionIndex"] = 0
    return templates.TemplateResponse(request, "index.html", {
        "state": exam_state, 
        "questions": load_questions(),
        "stats": get_stats()
    })

# --- ADMIN DASHBOARD ROUTES ---

@app.get("/admin", response_class=HTMLResponse)
async def admin_dashboard(request: Request):
    questions = load_questions()
    return templates.TemplateResponse(request, "admin.html", {
        "questions": questions
    })

@app.post("/admin/add", response_class=HTMLResponse)
async def add_question(
    request: Request,
    type: str = Form(...),
    question: str = Form(...),
    option0: str = Form(None),
    option1: str = Form(None),
    option2: str = Form(None),
    option3: str = Form(None),
    correctIndex: int = Form(None),
    explanation: str = Form("")
):
    questions = load_questions()
    new_q = {
        "id": len(questions) + 1,
        "type": type,
        "question": question,
        "explanation": explanation
    }
    
    if type == "multiple_choice":
        new_q["options"] = [option0, option1, option2, option3]
        new_q["correctAnswerIndex"] = correctIndex
    
    questions.append(new_q)
    save_questions(questions)
    
    return RedirectResponse(url="/admin", status_code=303)

@app.post("/admin/delete/{q_id}", response_class=HTMLResponse)
async def delete_question(request: Request, q_id: int):
    questions = load_questions()
    questions = [q for q in questions if q["id"] != q_id]
    save_questions(questions)
    return RedirectResponse(url="/admin", status_code=303)

@app.post("/admin/import", response_class=HTMLResponse)
async def import_questions(request: Request, json_data: str = Form(...)):
    try:
        data = json.loads(json_data)
        if isinstance(data, list):
            for q in data:
                save_question(q)
        else:
            save_question(data)
    except Exception as e:
        print(f"Import error: {e}")
    return RedirectResponse(url="/admin", status_code=303)

def run_ui():
    print("Starting UI on http://0.0.0.0:8000")
    print("Admin Dashboard: http://0.0.0.0:8000/admin")
    uvicorn.run(app, host="0.0.0.0", port=8000)

if __name__ == "__main__":
    run_ui()
