import threading
import uuid
import json
from typing import Any

from exams.questions import get_question, update_audio_question_assets, update_audio_question_render_state

from ui.server_support import public_audio_url
from .render_runner import render_audio_question


_jobs_lock = threading.Lock()
_jobs: dict[str, dict[str, Any]] = {}


def get_audio_job(job_id: str) -> dict[str, Any] | None:
    with _jobs_lock:
        job = _jobs.get(job_id)
        return dict(job) if job else None


def _set_audio_job(job_id: str, **updates: Any) -> None:
    with _jobs_lock:
        current = _jobs.setdefault(job_id, {})
        current.update(updates)


def start_audio_render_job(question_id: int) -> str:
    job_id = str(uuid.uuid4())
    _set_audio_job(
        job_id,
        question_id=question_id,
        status="queued",
        progress=0,
        message="Audio en cola.",
        audio_url="",
        error="",
    )

    def run() -> None:
        question = get_question(question_id)
        if question is None:
            _set_audio_job(job_id, status="failed", progress=100, error=f"Audio question {question_id} not found.", message="No se encontró la pregunta.")
            return

        def progress_callback(progress: int, message: str) -> None:
            _set_audio_job(job_id, status="running", progress=progress, message=message)
            update_audio_question_render_state(question_id, {"status": "rendering", "last_error": "", "progress": progress, "progress_message": message})

        input_payload = json.dumps(question.get("conversation_payload", {}), ensure_ascii=False, indent=2)
        _set_audio_job(job_id, input_payload=input_payload)

        try:
            render_result = render_audio_question(question_id, question, progress_callback=progress_callback)
            if render_result["render_status"] == "failed":
                error_message = render_result["error"]
                update_audio_question_render_state(question_id, {
                    "status": "failed",
                    "progress": 100,
                    "progress_message": "El render falló.",
                    "last_error": error_message,
                    "backend_stdout": render_result.get("backend_stdout", ""),
                    "backend_stderr": render_result.get("backend_stderr", ""),
                    "backend_command": render_result.get("backend_command", ""),
                })
                _set_audio_job(
                    job_id,
                    status="failed",
                    progress=100,
                    message="El render falló.",
                    error=error_message,
                    backend_stdout=render_result.get("backend_stdout", ""),
                    backend_stderr=render_result.get("backend_stderr", ""),
                    backend_command=render_result.get("backend_command", ""),
                )
                return
            web_audio_url = public_audio_url(render_result["audio_url"])
            update_audio_question_assets(question_id, web_audio_url, {
                "status": render_result["render_status"],
                "progress": 100,
                "progress_message": "Audio creado correctamente.",
                "transcript_path": render_result["transcript_path"],
                "payload_path": render_result["payload_path"],
                "output_path": render_result["output_path"],
                "local_audio_path": render_result["audio_url"],
                "backend_command": render_result["backend_command"],
                "backend_stdout": render_result["backend_stdout"],
                "backend_stderr": render_result.get("backend_stderr", ""),
                "last_error": "",
            })
            _set_audio_job(
                job_id,
                status="completed",
                progress=100,
                message="Audio creado correctamente.",
                audio_url=web_audio_url,
                local_audio_path=render_result["audio_url"],
                error="",
                backend_stdout=render_result["backend_stdout"],
                backend_stderr=render_result.get("backend_stderr", ""),
                backend_command=render_result["backend_command"],
            )
        except Exception as exc:
            error_message = str(exc)
            update_audio_question_render_state(
                question_id,
                {
                    "status": "failed",
                    "progress": 100,
                    "progress_message": "El render falló.",
                    "last_error": error_message,
                },
            )
            _set_audio_job(job_id, status="failed", progress=100, message="El render falló.", error=error_message)

    thread = threading.Thread(target=run, daemon=True)
    thread.start()
    return job_id
