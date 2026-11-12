# FastAPI Learning Notes

My notes from learning FastAPI by building a small **Notes API**. I built the app first, then took it apart line by line.

---

## 1. What is FastAPI?

FastAPI is a modern Python web framework for building APIs. You write normal Python functions with **type hints**, and FastAPI turns them into HTTP endpoints with:

- **Automatic validation**: bad input is rejected before your code runs
- **Automatic docs**: interactive Swagger UI at `/docs`
- **Speed**: built on Starlette (async web toolkit) and Pydantic (data validation)
- **Good editor support**: autocomplete and error checking, because everything is typed

### The restaurant analogy

| Restaurant | API world |
|---|---|
| Customer placing an order | **Client** (browser, app, another program) |
| Waiter who takes the order | **API** (FastAPI) |
| Kitchen that does the work | My **Python code** / database / ML model |
| Menu | **API docs** (`/docs`) |
| Order slip with fixed fields | **Request body**, checked by Pydantic |
| "Sorry, we don't have that dish" | **Error / status code** |
| The restaurant building and its door | **Uvicorn**, the actual web server |

---

## 2. Prerequisites

- Python basics: variables, `if`, loops, lists, dicts, functions, basic classes
- **Type hints**, the most important one for FastAPI:
  ```python
  def greet(name: str, age: int) -> str:
      return f"{name} is {age}"
  ```
- **JSON**, which looks like a Python dict:
  ```json
  {"title": "Shopping", "content": "Milk, eggs", "tags": ["home"]}
  ```
- **HTTP basics**: methods and status codes (below)
- `pip` and virtual environments

### HTTP methods

| Method | Meaning | Real life |
|---|---|---|
| `GET` | Read | Looking at the menu |
| `POST` | Create | Placing a new order |
| `PUT` | Replace / update | Rewriting the whole order slip |
| `PATCH` | Partial update | "Same order, just less spicy" |
| `DELETE` | Remove | Cancelling the order |

### Status codes

| Code | Meaning |
|---|---|
| `200` | OK, here you go |
| `201` | Created (order placed) |
| `204` | Done, nothing to return (e.g. after delete) |
| `404` | Not found |
| `422` | Request is invalid (bad JSON or breaks the rules) |
| `500` | Server crashed (a bug in my code) |

---

## 3. Setup (Windows + VS Code)

1. Install Python (tick **"Add Python to PATH"**) and VS Code.
2. In VS Code, install the **Python** extension (by Microsoft).
3. Open the project folder and the terminal (``Ctrl+` ``):

```bash
python -m venv venv
venv\Scripts\activate
pip install "fastapi[standard]"
```

> If activation fails with "running scripts is disabled":
> `Set-ExecutionPolicy -Scope CurrentUser RemoteSigned`

4. `Ctrl+Shift+P`, then **Python: Select Interpreter**, then pick the `venv` one.
5. Run the app:

```bash
fastapi dev main.py
```

6. Open **http://127.0.0.1:8000/docs**

`dev` mode auto-reloads on every save.

---

## 4. The code: `main.py`

```python
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

@app.put("/notes/{note_id}")
def update_note(note_id: int, note: NoteIn) -> Note:
    if note_id not in notes:
        raise HTTPException(status_code=404, detail="Note not found")
    updated_note = Note(id=note_id, **note.model_dump())
    notes[note_id] = updated_note
    return updated_note

@app.delete("/notes/{note_id}", status_code=204)
def delete_note(note_id: int):
    if note_id not in notes:
        raise HTTPException(status_code=404, detail="Note not found")
    del notes[note_id]
```

> The `PUT` endpoint was my own exercise. I wrote it by combining `get_note` (404 check) and `create_note` (building a `Note`).

---

## 5. Concepts, explained

### `app = FastAPI()`
Opens the restaurant. Everything hangs off `app`.

### `@app.get("/")`: route decorators
"When a GET request comes to `/`, run this function." The return value becomes JSON automatically.

### Pydantic models: the order slip
```python
class NoteIn(BaseModel):
    title: str = Field(min_length=1, max_length=100)
    content: str
    tags: list[str] = []
```
- Defines the **shape** of incoming data.
- Invalid data is rejected with `422` **before my function runs**, with no `if` checks needed.
- `= []` makes `tags` optional: if it's not sent, it defaults to an empty list.
- `Note(NoteIn)` = the same fields + `id`, like an order slip that gets an order number once accepted.

### Path parameters: `/notes/{note_id}`
Like a **hotel room number**: `/notes/3` means note number 3. `note_id: int` means `/notes/abc` is auto-rejected.

### Query parameters: `/notes?tag=work&limit=5`
Like **filters on Amazon/Swiggy**: same page, narrower results. Any function argument **not in the path** becomes a query parameter. Defaults make it optional.

### `HTTPException`
The waiter saying "sorry, we don't have that": a clean error response instead of a crash.

### Return type `-> Note`
FastAPI uses it to format and filter the response, and to document it in `/docs`.

### `Note(id=note_id, **note.model_dump())`
- `model_dump()` turns the Pydantic object into a plain dict.
- `**` unpacks the dict into keyword arguments, giving `Note(id=1, title=..., content=..., tags=[...])`.
- Like copying the customer's slip onto the official order form and stamping the order number on it.

### Why `global next_id` in `create_note` but not in `update_note`?
- `create_note` **reassigns** a variable (`next_id += 1`), so it needs `global`.
- `update_note` only **modifies the contents** of the `notes` dict, which is allowed without `global`.

---

## 6. Reading `/docs` (Swagger UI)

- Each coloured bar = one endpoint (blue GET, green POST, orange PUT, red DELETE).
- Endpoint names come from function names (`create_note` becomes "Create Note").
- **Schemas** at the bottom = my Pydantic models.
- After **Execute**:
  - **Server response** = what **actually happened** (look at the Code column).
  - **Responses** (lower down) = the **list of possible responses** (201, 422). It always shows both; it's documentation, not the result.
- **Curl** box = the same request as a terminal command.
- Response header `server: uvicorn` = Uvicorn is the real server running the app.

---

## 7. The two kinds of 422 error

### a) Broken JSON: FastAPI can't even read the slip
Sent:
```json
{ "title": "Learn FastAPI", "content": "...", "tags": }
```
Got:
```json
{
  "detail": [{
    "type": "json_invalid",
    "loc": ["body", 94],
    "msg": "JSON decode error",
    "ctx": {"error": "Expecting value"}
  }]
}
```
`loc: ["body", 94]` = the character position of the problem in the body.

### b) Valid JSON but breaks my rules: Pydantic rejects it
Sent:
```json
{ "title": "", "content": "test" }
```
Got `type: string_too_short`, because `min_length=1` caught it.

**In both cases my function never ran.** FastAPI rejected the request at the door.

---

## 8. Experiments I ran

| Request | Result | Why |
|---|---|---|
| `POST /notes` with valid body | `201` + note with `id` | Created |
| `GET /notes?tag=work` | Only matching notes | Query param filter |
| `GET /notes/999` | `404 Note not found` | My `HTTPException` |
| `GET /notes/abc` | `422` | `note_id: int` validation |
| `POST` with `"tags":` (no value) | `422 json_invalid` | Broken JSON |
| `POST` with `"title": ""` | `422 string_too_short` | Pydantic rule |
| `DELETE /notes/1` | `204` | Deleted, nothing to return |
| Restart server, then list | Empty | Data is only in memory, so I need a real DB |

---

## 9. PUT vs PATCH

| | Real life | API |
|---|---|---|
| **PUT** | Tear up the old slip, write a full new one | Send **all** fields |
| **PATCH** | "Same order, just less spicy" | Send **only changed** fields |

PATCH idea (to build):
```python
class NoteUpdate(BaseModel):
    title: str | None = None
    content: str | None = None
    tags: list[str] | None = None

# inside the endpoint:
changes = note.model_dump(exclude_unset=True)  # only fields actually sent
```

---

## 10. Roadmap: what's next

- [x] Routes, path/query params, request body, Pydantic validation
- [x] Status codes and `HTTPException`
- [x] Wrote my own `PUT` endpoint
- [ ] `PATCH` endpoint (partial update)
- [ ] Split the app into files with `APIRouter`
- [ ] Dependencies with `Depends` (like a security guard at the gate: auth, DB sessions)
- [ ] Real database: SQLite + SQLModel, then MongoDB
- [ ] `async def` (a waiter serving other tables while food cooks)
- [ ] File uploads with `UploadFile`, the bridge to my RAG notes app (`/upload` PDF, `/query`)
- [ ] Testing with `TestClient`
- [ ] Docker, then OpenShift

---

## Project structure

```
notes-api/
├── main.py
├── NOTES.md
├── requirements.txt   # pip freeze > requirements.txt
└── .gitignore         # contains: venv/  __pycache__/
```
