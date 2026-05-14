import sqlite3
import os
import json

DB_PATH = os.path.join(os.path.dirname(__file__), "exams.db")

def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS questions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            type TEXT NOT NULL,
            question TEXT NOT NULL,
            options TEXT, -- JSON string for list of options
            correct_answer_index INTEGER,
            explanation TEXT
        )
    ''')
    
    # If table is empty, seed with initial data
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
    
    conn.commit()
    conn.close()

def load_questions():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM questions')
    rows = cursor.fetchall()
    conn.close()
    
    questions = []
    for row in rows:
        q = dict(row)
        if q["options"]:
            q["options"] = json.loads(q["options"])
        # Map DB column names to what the frontend expects
        if "correct_answer_index" in q:
            q["correctAnswerIndex"] = q["correct_answer_index"]
        questions.append(q)
    return questions

def save_question(q_data):
    conn = get_db_connection()
    cursor = conn.cursor()
    options_json = json.dumps(q_data.get("options")) if q_data.get("options") else None
    cursor.execute('''
        INSERT INTO questions (type, question, options, correct_answer_index, explanation)
        VALUES (?, ?, ?, ?, ?)
    ''', (q_data["type"], q_data["question"], options_json, q_data.get("correctAnswerIndex"), q_data.get("explanation")))
    conn.commit()
    conn.close()

def delete_question(q_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('DELETE FROM questions WHERE id = ?', (q_id,))
    conn.commit()
    conn.close()

# Initialize on import
init_db()
