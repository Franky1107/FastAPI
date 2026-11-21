from fastapi import FastAPI, HTTPException, Query, status
from pydantic import BaseModel, Field  # 🆕 Field

app = FastAPI()

notes = [
    {"id": 1, "title": "Buy milk", "content": "2 litres"},
    {"id": 2, "title": "Learn FastAPI", "content": "Routes today"},
]


# ---------- models ----------
class NoteCreate(BaseModel):  # what a client sends to create/replace
    title: str = Field(min_length=1, max_length=100)  # 🆕
    content: str = Field(max_length=5000)  # 🆕


class NoteUpdate(BaseModel):  # what a client sends to patch
    title: str | None = Field(default=None, min_length=1, max_length=100)  # 🆕
    content: str | None = Field(default=None, max_length=5000)  # 🆕


class NoteOut(BaseModel):  # 🆕 what the API sends back
    id: int
    title: str
    content: str


# ---------- routes ----------
@app.get("/")
def home():
    return {"message": "Notes API is alive"}


@app.get("/health")
def health():
    return {"status": "healthy"}


@app.get("/notes", response_model=list[NoteOut])  # 🆕
def list_notes(
    search: str | None = Query(default=None, min_length=1),  # 🆕
    skip: int = Query(default=0, ge=0),  # 🆕
    limit: int = Query(default=10, ge=1, le=100),  # 🆕
):
    results = notes
    if search:
        term = search.lower()
        results = [
            note
            for note in notes
            if term in note["title"].lower() or term in note["content"].lower()
        ]
    return results[skip : skip + limit]


@app.get("/notes/count")
def count_notes():
    return {"count": len(notes)}


@app.get("/notes/{note_id}", response_model=NoteOut)  # 🆕
def get_note(note_id: int):
    for note in notes:
        if note["id"] == note_id:
            return note
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Note not found")


@app.post("/notes", response_model=NoteOut, status_code=status.HTTP_201_CREATED)  # 🆕
def create_note(note: NoteCreate):
    new_id = notes[-1]["id"] + 1 if notes else 1
    new_note = {"id": new_id, "title": note.title, "content": note.content}
    notes.append(new_note)
    return new_note


@app.put("/notes/{note_id}", response_model=NoteOut)  # 🆕
def update_note(note_id: int, updated: NoteCreate):
    for note in notes:
        if note["id"] == note_id:
            note["title"] = updated.title
            note["content"] = updated.content
            return note
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Note not found")


@app.patch("/notes/{note_id}", response_model=NoteOut)  # 🆕
def patch_note(note_id: int, changes: NoteUpdate):
    update_data = changes.model_dump(exclude_unset=True, exclude_none=True)  # 🆕 exclude_none
    if not update_data:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No fields to update")
    for note in notes:
        if note["id"] == note_id:
            note.update(update_data)
            return note
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Note not found")


@app.delete("/notes/{note_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_note(note_id: int):
    for idx, note in enumerate(notes):
        if note["id"] == note_id:
            notes.pop(idx)
            return
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Note not found")