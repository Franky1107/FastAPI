from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from pymongo import MongoClient
from bson import ObjectId
from bson.errors import InvalidId

app = FastAPI(title="My Notes API")

# --- Connect to MongoDB ---
client = MongoClient("mongodb://localhost:27017")
db = client["notes_app"]          # database
notes_col = db["notes"]           # collection (like a table)

# --- Models ---
class NoteIn(BaseModel):
    title: str = Field(min_length=1, max_length=100)
    content: str
    tags: list[str] = []

class Note(NoteIn):
    id: str                        # Mongo IDs are strings now, not 1, 2, 3

# --- Helpers ---
def to_note(doc: dict) -> Note:
    return Note(
        id=str(doc["_id"]),
        title=doc["title"],
        content=doc["content"],
        tags=doc.get("tags", []),
    )

def to_object_id(note_id: str) -> ObjectId:
    try:
        return ObjectId(note_id)
    except InvalidId:
        raise HTTPException(status_code=400, detail="Invalid note id")

# --- Endpoints ---
@app.get("/")
def home():
    return {"message": "Welcome to My Notes API"}

@app.post("/notes", status_code=201)
def create_note(note: NoteIn) -> Note:
    result = notes_col.insert_one(note.model_dump())
    return Note(id=str(result.inserted_id), **note.model_dump())

@app.get("/notes")
def list_notes(tag: str | None = None, limit: int = 10) -> list[Note]:
    query = {"tags": tag} if tag else {}
    return [to_note(doc) for doc in notes_col.find(query).limit(limit)]

@app.get("/notes/{note_id}")
def get_note(note_id: str) -> Note:
    doc = notes_col.find_one({"_id": to_object_id(note_id)})
    if doc is None:
        raise HTTPException(status_code=404, detail="Note not found")
    return to_note(doc)

@app.put("/notes/{note_id}")
def update_note(note_id: str, note: NoteIn) -> Note:
    result = notes_col.replace_one({"_id": to_object_id(note_id)}, note.model_dump())
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Note not found")
    return Note(id=note_id, **note.model_dump())

@app.delete("/notes/{note_id}", status_code=204)
def delete_note(note_id: str):
    result = notes_col.delete_one({"_id": to_object_id(note_id)})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Note not found")