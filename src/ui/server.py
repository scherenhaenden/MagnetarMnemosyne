from fastapi import FastAPI, Request, Form, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from exams.questions import (
    save_question, load_questions, delete_question, 
    load_exams, save_exam, save_result, load_results,
    delete_exam, update_exam, get_question, update_audio_question_assets, update_audio_question_render_state
)
from audio import build_audio_question_from_payload, render_audio_question
from audio.job_manager import get_audio_job, start_audio_render_job
from config import get_audio_backend_config, get_audio_backend_options, get_audio_defaults
import uvicorn
import json
import re
import os
from ui.server_support import generated_audio_dir, public_audio_url

app = FastAPI()

templates_path = os.path.join(os.path.dirname(__file__), "templates")
templates = Jinja2Templates(directory=templates_path)

app.mount("/generated-audio", StaticFiles(directory=generated_audio_dir), name="generated-audio")


def _slugify_filename(value: str) -> str:
    slug = re.sub(r"[^a-zA-Z0-9._-]+", "-", value.strip()).strip("-._").lower()
    return slug or "audio-scene"


def build_audio_form_data(form_data=None):
    selected_backend = ""
    if form_data:
        selected_backend = form_data.get("backend") or ""
    defaults = {
        "title": "",
        "language": "",
        "difficulty": "",
        "scene_description": "",
        "conversation_json": "",
        "output_name": "",
        "selected_voices_json": "",
    }
    defaults.update(get_audio_defaults(selected_backend or None))
    if form_data:
        defaults.update({key: value for key, value in form_data.items() if value is not None})
    return defaults


def build_audio_create_context(form_data=None, create_error="", create_success="", created_question=None, render_job_id=None):
    audio_form_data = build_audio_form_data(form_data)
    return {
        "questions": load_questions(),
        "exams": load_exams(),
        "results": load_results(),
        "active_tab": "audios",
        "view_mode": "create",
        "audio_form_data": audio_form_data,
        "audio_backend_options": get_audio_backend_options(),
        "selected_audio_backend": get_audio_backend_config(audio_form_data.get("backend")),
        "audio_create_error": create_error,
        "audio_create_success": create_success,
        "created_audio_question": created_question,
        "audio_render_job_id": render_job_id,
    }

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
async def admin_dashboard(request: Request, tab: str = "questions", mode: str = "list"):
    if tab == "audios" and mode == "create":
        return templates.TemplateResponse(request, "admin.html", build_audio_create_context())
    questions = load_questions()
    exams = load_exams()
    results = load_results()
    return templates.TemplateResponse(request, "admin.html", {
        "questions": questions,
        "exams": exams,
        "results": results,
        "active_tab": tab,
        "view_mode": mode,
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
    print("Starting UI on http://0.0.0.0:8000")
    print("Admin Dashboard: http://0.0.0.0:8000/admin")
    uvicorn.run(app, host="0.0.0.0", port=8000)

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

@app.post("/admin/import/conversation", response_class=HTMLResponse)
async def import_conversation_question(request: Request, json_data: str = Form(...)):
    try:
        save_question(build_audio_question_from_payload(json_data))
    except Exception as e:
        print(f"Conversation import error: {e}")
    return RedirectResponse(url="/admin?tab=questions", status_code=303)

@app.post("/admin/audios/create", response_class=HTMLResponse)
async def create_audio_question(
    request: Request,
    title: str = Form("la conversación"),
    language: str = Form(""),
    difficulty: str = Form(""),
    scene_description: str = Form(""),
    conversation_json: str = Form(...),
    backend: str = Form(""),
    output_name: str = Form(""),
    selected_voices_json: str = Form(""),
    submit_action: str = Form("render"),
):
    config_defaults = get_audio_defaults(backend or None)
    resolved_output_name = output_name.strip() or _slugify_filename(title or "audio-scene")
    output_extension = str(config_defaults.get("output_extension") or "wav").lstrip(".")
    if not resolved_output_name.lower().endswith(f".{output_extension}"):
        resolved_output_name = f"{resolved_output_name}.{output_extension}"
    form_data = build_audio_form_data({
        "title": title,
        "language": language,
        "difficulty": difficulty,
        "scene_description": scene_description,
        "conversation_json": conversation_json,
        "backend": backend or config_defaults.get("backend", ""),
        "output_name": resolved_output_name,
        "selected_voices_json": selected_voices_json,
    })
    try:
        selected_voices = json.loads(selected_voices_json) if selected_voices_json.strip() else {}
        conversation_payload = json.loads(conversation_json)
        question_text = f"Escucha {title.strip() or 'el audio'} y responde a las preguntas."
        payload = {
            "question": question_text,
            "audio_url": "",
            "conversation": {
                "title": title,
                "language": language,
                "difficulty": difficulty,
                "scene_description": scene_description,
                "speakers": conversation_payload.get("speakers", []),
                "turns": conversation_payload.get("turns"),
                "dialogue": conversation_payload.get("dialogue"),
                "render": {
                    "backend": form_data["backend"],
                    "model": form_data["model"],
                    "checkpoint": form_data["checkpoint"],
                    "vocab_file": form_data["vocab_file"],
                    "f5_tts_root": form_data["f5_tts_root"],
                    "kokoro_renderer_root": form_data["kokoro_renderer_root"],
                    "device": form_data["device"],
                    "output_path": form_data.get("output_path", ""),
                    "output_name": form_data["output_name"],
                    "selected_voices": selected_voices,
                },
            },
        }
        audio_question = build_audio_question_from_payload(payload)
        save_question(audio_question)
        created_question = next(
            (q for q in reversed(load_questions()) if q["question"] == audio_question["question"] and q["type"] == "audio_listening"),
            None,
        )
        if created_question is None:
            raise RuntimeError("Audio question was created but could not be reloaded from the database.")

        if submit_action == "render":
            update_audio_question_render_state(
                created_question["id"],
                {"status": "queued", "progress": 0, "progress_message": "Audio en cola.", "last_error": ""},
            )
            job_id = start_audio_render_job(created_question["id"])
            created_question = get_question(created_question["id"])
            context = build_audio_create_context(
                form_data=form_data,
                create_success="Render iniciado. La página mostrará el progreso automáticamente.",
                created_question=created_question,
                render_job_id=job_id,
            )
            return templates.TemplateResponse(request, "admin.html", context)

        created_question = get_question(created_question["id"])
        return templates.TemplateResponse(
            request,
            "admin.html",
            build_audio_create_context(
                form_data=form_data,
                create_success="Audio guardado como borrador.",
                created_question=created_question,
            ),
        )
    except Exception as e:
        print(f"Audio creation error: {e}")
        return templates.TemplateResponse(
            request,
            "admin.html",
            build_audio_create_context(
                form_data=form_data,
                create_error=str(e),
            ),
            status_code=400,
        )


@app.websocket("/ws/audio-jobs/{job_id}")
async def audio_job_ws(websocket: WebSocket, job_id: str):
    import asyncio

    await websocket.accept()
    try:
        while True:
            job = get_audio_job(job_id)
            if job is None:
                await websocket.send_json({"status": "failed", "progress": 100, "message": "Trabajo no encontrado.", "error": "job_not_found"})
                break
            await websocket.send_json(job)
            if job.get("status") in {"completed", "failed"}:
                break
            await asyncio.sleep(0.5)
    except WebSocketDisconnect:
        return

@app.post("/admin/audios/render/{q_id}", response_class=HTMLResponse)
async def render_audio_route(request: Request, q_id: int):
    try:
        question = get_question(q_id)
        if question is None:
            raise ValueError(f"Audio question {q_id} not found.")
        update_audio_question_render_state(q_id, {"status": "rendering", "last_error": ""})
        render_result = render_audio_question(q_id, question)
        web_audio_url = public_audio_url(render_result["audio_url"])
        update_audio_question_assets(q_id, web_audio_url, {
            "status": render_result["render_status"],
            "transcript_path": render_result["transcript_path"],
            "payload_path": render_result["payload_path"],
            "output_path": render_result["output_path"],
            "local_audio_path": render_result["audio_url"],
            "backend_command": render_result["backend_command"],
            "backend_stdout": render_result.get("backend_stdout", ""),
            "last_error": "",
        })
    except Exception as e:
        print(f"Audio render error: {e}")
        update_audio_question_render_state(q_id, {"status": "failed", "last_error": str(e)})
    return RedirectResponse(url="/admin?tab=audios", status_code=303)

def run_ui():
    print("Starting UI on http://0.0.0.0:8000")
    print("Admin Dashboard: http://0.0.0.0:8000/admin")
    uvicorn.run(app, host="0.0.0.0", port=8000)

if __name__ == "__main__":
    run_ui()
