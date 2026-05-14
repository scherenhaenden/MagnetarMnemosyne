# User Guide

## Admin Dashboard (`/admin`)

### Manually Adding Questions
1. Select the **Type** (Multiple Choice, Long Text, or Audio).
2. Fill in the question content.
3. For Multiple Choice, provide 4 options and the index (0-3) of the correct one.
4. Add an explanation for better student learning.

### Bulk JSON Import
You can paste a JSON array into the import box.
**Format Example:**
```json
[
  {
    "type": "multiple_choice",
    "question": "Sample Question",
    "options": ["A", "B", "C", "D"],
    "correctAnswerIndex": 0,
    "explanation": "Because..."
  }
]
```

### Audio Scene Authoring

Audio listening scenes are managed in the `Audios` tab.

Flow:
1. Open `/admin?tab=audios`.
2. Click `Crear Audio`.
3. Fill title, description, language, level, and `conversation_json`.
4. Choose the backend from the dropdown:
   - `F5-TTS`
   - `Kokoro`
5. Click `Crear Audio` to save and render from the same page.
6. If something fails, the page stays in the create view and shows the exact error.

For the full audio guide, see [docs/AUDIOS.md](/Users/edwardflores/Projects/Development/MagnetarMnemosyne/docs/AUDIOS.md:1).

## Taking an Exam (`/`)
1. Choose between **Interactivo** (Immediate feedback) or **Clásico** (Delayed results).
2. Click **Comenzar Examen**.
3. Answer questions and navigate using the **Siguiente** button.
4. Review your final score and detailed breakdown at the end.
