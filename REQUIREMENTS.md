# Requirements for Magnetar Mnemosyne

## Functional Requirements

### Must-Have

- The system must allow administrators to create, edit, and delete questions.
- The system must support at least `multiple_choice`, `long_text`, and `audio_listening` question types.
- The system must allow administrators to group questions into named exams.
- The system must store student results including student name, exam, score, and completion timestamp.
- The system must allow administrators to define listening scenes through structured JSON or a dedicated admin form.
- The system must support multi-speaker audio conversation definitions with speaker metadata, dialogue turns, and render configuration.
- The system must render or reference audio assets for listening questions using local AI-capable backends.

### Should-Have

- The system should support CEFR-oriented metadata such as language, difficulty, and duration targets.
- The admin dashboard should show previews of stored audio scenes and attached audio files.
- The system should preserve render metadata such as backend, model, checkpoint, selected voices, and output path.
- The platform should support bulk imports of question banks and conversation definitions.

### Could-Have

- The system could support reusable voice profiles and scene templates for recurring exam formats.
- The system could support asynchronous rendering queues and job status tracking.
- The system could support export of exams and listening assets for offline distribution.

### Won't-Have

- The current scope will not include cloud-only TTS dependency as a requirement.
- The current scope will not include full LMS integration in the initial implementation.

## Non-Functional Requirements

### Must-Have

- The application must run locally on supported Python environments.
- The application must store persistent data reliably in SQLite unless replaced by an approved storage layer.
- The application must keep governance artifacts synchronized with implementation changes.
- Automated tests must cover critical server flows and structured conversation parsing.

### Should-Have

- The system should remain usable with minimal manual setup.
- The admin UI should remain understandable for non-technical content creators.
- Audio scene parsing and persistence should fail clearly on invalid input.

### Could-Have

- The system could support background processing for long-running TTS renders.
- The system could support richer analytics and reporting on exam performance.
