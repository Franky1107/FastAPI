from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel

app = FastAPI()

# fake "database" for now (a plain Python list); MongoDB comes in Phase 2
notes = [
    {"id": 1, "title": "Buy milk", "content": "2 litres"},
    {"id": 2, "title": "Learn FastAPI", "content": "Routes today"},
]


# the shape of the data a client must send
class NoteCreate(BaseModel):
    title: str
    content: str


class NoteUpdate(BaseModel):
    title: str | None = None
    content: str | None = None


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


@app.post("/notes", status_code=status.HTTP_201_CREATED)
def create_note(note: NoteCreate):
    new_id = notes[-1]["id"] + 1 if notes else 1
    new_note = {"id": new_id, "title": note.title, "content": note.content}
    notes.append(new_note)
    return new_note


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
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Note not found")


@app.delete("/notes/{note_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_note(note_id: int):
    for idx, note in enumerate(notes):
        if note["id"] == note_id:
            notes.pop(idx)
            return
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Note not found")


@app.get("/health")
def health():
    return {"status": "healthy"}


@app.put("/notes/{note_id}")
def update_note(note_id: int, updated: NoteCreate):
    for note in notes:
        if note["id"] == note_id:
            note["title"] = updated.title
            note["content"] = updated.content
            return note
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Note not found")


@app.patch("/notes/{note_id}")
def patch_note(note_id: int, changes: NoteUpdate):
    for note in notes:
        if note["id"] == note_id:
            update_data = changes.model_dump(
                exclude_unset=True
            )  # converts pydantic obj to dict
            # exclude_unset takes only what was sent
            note.update(
                update_data
            )  # copies keys from update_data,overwriting those keys and leaving the rest alone
            return note
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Note not found")


@app.patch("/notes/{note_id}")
def patch_note(note_id: int, changes: NoteUpdate):
    update_data = changes.model_dump(exclude_unset=True)
    if not update_data:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="No fields to update"
        )
    for note in notes:
        if note["id"] == note_id:
            note.update(update_data)
            return note
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Note not found")
