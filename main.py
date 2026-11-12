from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

app = FastAPI(title="My Notes API")

# --- The "order slip": what a note must look like ---
class NoteIn(BaseModel):
    title: str = Field(min_length=1, max_length=100)
    content: str
    tags: list[str] = []

class Note(NoteIn):
    id: int

# --- Fake database (just a dict in memory) ---
notes: dict[int, Note] = {}
next_id = 1

@app.get("/")
def home():
    return {"message": "Welcome to My Notes API"}

@app.post("/notes", status_code=201)
def create_note(note: NoteIn) -> Note:
    global next_id
    new_note = Note(id=next_id, **note.model_dump())
    notes[next_id] = new_note
    next_id += 1
    return new_note

@app.get("/notes")
def list_notes(tag: str | None = None, limit: int = 10) -> list[Note]:
    result = list(notes.values())
    if tag:
        result = [n for n in result if tag in n.tags]
    return result[:limit]

@app.get("/notes/{note_id}")
def get_note(note_id: int) -> Note:
    if note_id not in notes:
        raise HTTPException(status_code=404, detail="Note not found")
    return notes[note_id]

@app.delete("/notes/{note_id}", status_code=204)
def delete_note(note_id: int):
    if note_id not in notes:
        raise HTTPException(status_code=404, detail="Note not found")
    del notes[note_id]