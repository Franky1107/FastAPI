from fastapi import FastAPI, HTTPException

app = FastAPI()

# fake "database" for now (a plain Python list); MongoDB comes in Phase 2
notes = [
    {"id": 1, "title": "Buy milk", "content": "2 litres"},
    {"id": 2, "title": "Learn FastAPI", "content": "Routes today"},
]


@app.get("/")
def home():
    return {"message": "Notes API is alive"}


@app.get("/notes")
def list_notes(search: str | None = None, skip: int = 0, limit: int = 10):
    results = notes
    if search:
        term = search.lower()
        results = [
            note
            for note in notes
            if term in note["title"].lower() or term in note["content"].lower()
        ]
    return results[skip : skip + limit]


@app.post("/notes")
def create_note():
    return {"message": "POST /notes reached (we'll accept real data in Step 3)"}


@app.get("/about")
def about():
    return {"app": "Notes API", "author": "Sourav"}


@app.get("/notes/count")
def count_notes():
    return {"count": len(notes)}


@app.get("/notes/{note_id}")
def get_note(note_id: int):
    for note in notes:
        if note["id"] == note_id:
            return note
    raise HTTPException(status_code=404, detail="Note not found")


@app.delete("/notes/{note_id}")
def delete_note(note_id: int):
    for idx, note in enumerate(notes):
        if note["id"] == note_id:
            notes.pop(idx)
            return {"message": f"Note {note_id} has been deleted"}
    raise HTTPException(status_code=404, detail="Note not found")


@app.get("/health")
def health():
    return {"status": "healthy"}