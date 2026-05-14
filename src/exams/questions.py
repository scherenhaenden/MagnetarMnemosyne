import sqlite3
import os
import json
from datetime import datetime

DB_PATH = os.path.join(os.path.dirname(__file__), "exams.db")

def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()
    # Questions Table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS questions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            type TEXT NOT NULL, -- multiple_choice, long_text, audio_listening
            question TEXT NOT NULL,
            options TEXT, 
            correct_answer_index INTEGER,
            explanation TEXT,
            audio_url TEXT, -- URL or path to audio file
            conversation_json TEXT
        )
    ''')
    # Exams Table (Grouping of questions)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS exams (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            question_ids TEXT, -- JSON list of question IDs
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    cursor.execute("PRAGMA table_info(questions)")
    columns = {row[1] for row in cursor.fetchall()}
    if "audio_url" not in columns:
        cursor.execute("ALTER TABLE questions ADD COLUMN audio_url TEXT")
    if "conversation_json" not in columns:
        cursor.execute("ALTER TABLE questions ADD COLUMN conversation_json TEXT")
    # Results Table (Student attempts)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS results (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_name TEXT,
            exam_id INTEGER,
            score INTEGER,
            total_questions INTEGER,
            percentage REAL,
            completed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (exam_id) REFERENCES exams (id)
        )
    ''')
    
    # Seed default data if empty
    cursor.execute('SELECT COUNT(*) FROM questions')
    if cursor.fetchone()[0] == 0:
        default_q = {
            "type": "multiple_choice",
            "question": "Lee el siguiente cartel:\n«Lunes cerrado por descanso del personal. Martes a domingo: de 13:00 a 16:30 y de 20:00 a 23:30.»\n¿Qué tipo de establecimiento es probablemente?",
            "options": json.dumps(["Un restaurante", "Una oficina de correos", "Una farmacia", "Un banco local"]),
            "correct_answer_index": 0,
            "explanation": "El horario dividido en franjas para el almuerzo y la cena, junto con el día de descanso semanal, es característico de los locales de hostelería."
        }
        cursor.execute('''
            INSERT INTO questions (type, question, options, correct_answer_index, explanation)
            VALUES (?, ?, ?, ?, ?)
        ''', (default_q["type"], default_q["question"], default_q["options"], default_q["correct_answer_index"], default_q["explanation"]))
        
        # Create a default exam
        cursor.execute('INSERT INTO exams (title, question_ids) VALUES (?, ?)', ("Examen General", json.dumps([1])))

    conn.commit()
    conn.close()

# --- Question Functions ---
def load_questions():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM questions')
    rows = cursor.fetchall()
    conn.close()
    questions = []
    for row in rows:
        q = dict(row)
        if q["options"]: q["options"] = json.loads(q["options"])
        if "correct_answer_index" in q: q["correctAnswerIndex"] = q["correct_answer_index"]
        if q.get("conversation_json"):
            q["conversation_payload"] = json.loads(q["conversation_json"])
        questions.append(q)
    return questions

def get_question(q_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM questions WHERE id = ?', (q_id,))
    row = cursor.fetchone()
    conn.close()
    if row is None:
        return None

    q = dict(row)
    if q["options"]:
        q["options"] = json.loads(q["options"])
    if "correct_answer_index" in q:
        q["correctAnswerIndex"] = q["correct_answer_index"]
    if q.get("conversation_json"):
        q["conversation_payload"] = json.loads(q["conversation_json"])
    return q

def save_question(q_data):
    conn = get_db_connection()
    cursor = conn.cursor()
    options_json = json.dumps(q_data.get("options")) if q_data.get("options") else None
    conversation_json = json.dumps(q_data.get("conversation_payload")) if q_data.get("conversation_payload") else None
    cursor.execute('''
        INSERT INTO questions (type, question, options, correct_answer_index, explanation, audio_url, conversation_json)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', (
        q_data["type"],
        q_data["question"],
        options_json,
        q_data.get("correctAnswerIndex"),
        q_data.get("explanation"),
        q_data.get("audio_url"),
        conversation_json,
    ))
    conn.commit()
    conn.close()

def delete_question(q_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('DELETE FROM questions WHERE id = ?', (q_id,))
    conn.commit()
    conn.close()

def update_audio_question_assets(q_id, audio_url, render_updates=None):
    existing = get_question(q_id)
    if existing is None:
        return

    conversation_payload = existing.get("conversation_payload") or {}
    render_section = conversation_payload.get("render") or {}
    if render_updates:
        render_section.update(render_updates)
    conversation_payload["render"] = render_section
    conversation_payload["audio_url"] = audio_url

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        'UPDATE questions SET audio_url = ?, conversation_json = ? WHERE id = ?',
        (audio_url, json.dumps(conversation_payload), q_id)
    )
    conn.commit()
    conn.close()

def update_audio_question_render_state(q_id, render_updates):
    existing = get_question(q_id)
    if existing is None:
        return

    conversation_payload = existing.get("conversation_payload") or {}
    render_section = conversation_payload.get("render") or {}
    render_section.update(render_updates)
    conversation_payload["render"] = render_section

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        'UPDATE questions SET conversation_json = ? WHERE id = ?',
        (json.dumps(conversation_payload), q_id)
    )
    conn.commit()
    conn.close()

# --- Exam Functions ---
def load_exams():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM exams')
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]

def save_exam(title, question_ids):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('INSERT INTO exams (title, question_ids) VALUES (?, ?)', (title, json.dumps(question_ids)))
    conn.commit()
    conn.close()

def delete_exam(exam_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('DELETE FROM exams WHERE id = ?', (exam_id,))
    conn.commit()
    conn.close()

def update_exam(exam_id, title, question_ids):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('UPDATE exams SET title = ?, question_ids = ? WHERE id = ?', (title, json.dumps(question_ids), exam_id))
    conn.commit()
    conn.close()

# --- Results Functions ---
def save_result(student_name, exam_id, score, total, percentage):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO results (student_name, exam_id, score, total_questions, percentage)
        VALUES (?, ?, ?, ?, ?)
    ''', (student_name, exam_id, score, total, percentage))
    conn.commit()
    conn.close()

def load_results():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT r.*, e.title as exam_title 
        FROM results r 
        JOIN exams e ON r.exam_id = e.id 
        ORDER BY r.completed_at DESC
    ''')
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]

init_db()
