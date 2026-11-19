# FastAPI Study Notes 🚀

> Beginner-friendly notes for building APIs with **FastAPI**, **Pydantic** and **MongoDB** on **Windows + VS Code**.
> Every topic has a real-life analogy and builds on the same example project: a **Notes API**.

Versions these notes were written against (Nov 2026): FastAPI 0.16x, Pydantic 2.x, PyMongo 4.x, Python 3.12+.

---

## Table of Contents

1. [What FastAPI Is and Why It's Used](#1-what-fastapi-is-and-why-its-used)
2. [Prerequisites: Python, Type Hints, JSON, HTTP, Status Codes](#2-prerequisites-python-type-hints-json-http-status-codes)
3. [Setup on Windows + VS Code](#3-setup-on-windows--vs-code)
4. [Routes, Path Params, Query Params, Request Body](#4-routes-path-params-query-params-request-body)
5. [Pydantic Models and Validation](#5-pydantic-models-and-validation)
6. [Responses, Status Codes, HTTPException](#6-responses-status-codes-httpexception)
7. [Full CRUD: GET, POST, PUT, PATCH, DELETE](#7-full-crud-get-post-put-patch-delete)
8. [Reading Swagger /docs](#8-reading-swagger-docs)
9. [MongoDB with PyMongo](#9-mongodb-with-pymongo)
10. [Project Structure: APIRouter, Folders, Settings, .env](#10-project-structure-apirouter-folders-settings-env)
11. [Dependencies with Depends](#11-dependencies-with-depends)
12. [Authentication: Hashing, Register/Login, JWT](#12-authentication-hashing-registerlogin-jwt)
13. [Middleware, CORS, Error Handlers, Logging](#13-middleware-cors-error-handlers-logging)
14. [Async: async def, Async MongoDB, BackgroundTasks, Lifespan](#14-async-async-def-async-mongodb-backgroundtasks-lifespan)
15. [File Uploads and Streaming Responses](#15-file-uploads-and-streaming-responses)
16. [Testing with pytest and TestClient](#16-testing-with-pytest-and-testclient)
17. [Docker and docker-compose](#17-docker-and-docker-compose)
18. [Deployment Basics and GitHub Actions](#18-deployment-basics-and-github-actions)
19. [Quick-Reference Cheat Sheet](#19-quick-reference-cheat-sheet)

---

## The Example Project: Notes API

Everything in these notes builds one app. By the end it looks like this:

| Feature | Endpoint |
|---|---|
| Register / login | `POST /auth/register`, `POST /auth/login`, `GET /auth/me` |
| List notes (search, filter, paginate) | `GET /notes?q=milk&tag=home&skip=0&limit=10` |
| Get one note | `GET /notes/{note_id}` |
| Create a note | `POST /notes` |
| Replace a note | `PUT /notes/{note_id}` |
| Partly update a note | `PATCH /notes/{note_id}` |
| Delete a note | `DELETE /notes/{note_id}` |
| Upload an attachment | `POST /notes/{note_id}/attachments` |
| Export notes as CSV | `GET /notes/export` |

A note looks like this in JSON:

```json
{
  "id": "6740a1f2c9e77b2a1d3f0a11",
  "title": "Shopping list",
  "content": "Milk, eggs, bread",
  "tags": ["home", "errands"],
  "pinned": false,
  "created_at": "2026-11-18T10:00:00Z",
  "updated_at": "2026-11-18T10:00:00Z"
}
```

The project grows in stages:

| Sections | Where the data lives | Style |
|---|---|---|
| 4–8 | A Python dict in memory (lost on restart) | single `main.py`, `def` routes |
| 9 | MongoDB via PyMongo (sync) | single `main.py` |
| 10–13 | MongoDB, split into folders | `app/` package |
| 14–18 | MongoDB via PyMongo's **async** client | `async def` routes (final version) |

---

## 1. What FastAPI Is and Why It's Used

### What is an API?

> 🍽️ **Analogy: An API is a waiter.**
> You (the client: a browser, phone app, or another program) never walk into the kitchen (the server/database). You give your order to the waiter (the API), the waiter takes it to the kitchen, and brings back your food (the response). The menu tells you what you're allowed to order (the API's endpoints).

A **web API** is a program that listens for HTTP requests (like `GET /notes`) and sends back data, usually as JSON.

### What is FastAPI?

**FastAPI** is a Python framework for building web APIs. You write normal Python functions, and FastAPI turns them into HTTP endpoints.

> 🏭 **Analogy: FastAPI is a well-run restaurant kitchen with a smart manager.**
> You just write the recipes (Python functions). The manager automatically checks every order slip is filled in correctly (validation), prints an up-to-date menu for customers (automatic docs), and keeps multiple orders moving at once (async).

```python
from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def home():
    return {"message": "Hello, Notes API!"}
```

That's a complete, working API. Visiting `http://127.0.0.1:8000/` returns `{"message": "Hello, Notes API!"}`.

### Why people use it

| Feature | What it means for you |
|---|---|
| **Fast to write** | Little boilerplate. A route is just a function with a decorator. |
| **Fast to run** | Built on Starlette (web layer) and Pydantic (data layer); one of the fastest Python frameworks. |
| **Automatic validation** | Wrong data types are rejected with a clear error before your code runs. |
| **Automatic docs** | Interactive docs at `/docs` (Swagger) and `/redoc`, generated from your code. |
| **Type hints** | Your editor (VS Code + Pylance) gives autocomplete and catches mistakes. |
| **Async support** | Handles many slow tasks (DB calls, AI model calls) at the same time. |
| **Standards-based** | Uses OpenAPI and JSON Schema, so other tools understand your API. |

### FastAPI vs other Python frameworks

| | FastAPI | Flask | Django (+ DRF) |
|---|---|---|---|
| Main use | APIs | Small apps / APIs | Full websites + APIs |
| Built-in validation | ✅ Pydantic | ❌ add a library | ✅ serializers |
| Auto API docs | ✅ | ❌ | partial (add-ons) |
| Async | ✅ native | limited | partial |
| Learning curve | Low | Low | Higher |
| Batteries included (admin, ORM) | ❌ | ❌ | ✅ |

### Where FastAPI fits for data/AI engineers

- Serving ML/LLM models behind an endpoint (`POST /predict`, `POST /chat`).
- Building RAG backends (upload documents → embed → query).
- Exposing data pipelines or internal tools as small services.
- Streaming LLM output token by token (see Section 15).

### Key pieces under the hood

| Piece | Role | Analogy |
|---|---|---|
| **Starlette** | Handles HTTP, routing, middleware | The restaurant building and doors |
| **Pydantic** | Validates and converts data | The order-slip checker |
| **Uvicorn** | ASGI server that actually runs your app | The waiter on duty who takes requests from the street |
| **OpenAPI** | Machine-readable description of your API | The printed menu |

---

## 2. Prerequisites: Python, Type Hints, JSON, HTTP, Status Codes

### 2.1 Python basics you need

You need: functions, dicts, lists, classes, decorators (`@something`), f-strings, `import`, and `try/except`.

```python
# dict = key → value (this is how one note looks in Python)
note = {"title": "Shopping", "tags": ["home"], "pinned": False}
note["pinned"] = True
print(note.get("content", "no content"))   # .get() returns a default instead of crashing

# list comprehension
titles = [n["title"] for n in [note]]

# decorator = a function that wraps another function
# FastAPI's @app.get("/") registers your function as a route
```

### 2.2 Type hints

> 🏷️ **Analogy: Type hints are labels on kitchen jars.**
> Python doesn't force you to put sugar in the "sugar" jar, but the label helps everyone. FastAPI goes further: it **reads the labels and checks the contents** for you.

```python
def make_title(text: str, max_len: int = 50) -> str:
    return text[:max_len]

name: str = "Sourav"
tags: list[str] = ["home", "work"]
scores: dict[str, int] = {"math": 90}
maybe_text: str | None = None        # either a string or None (optional)
```

| Type hint | Means | Example value |
|---|---|---|
| `str` | text | `"hello"` |
| `int` | whole number | `42` |
| `float` | decimal number | `3.14` |
| `bool` | true/false | `True` |
| `list[str]` | list of strings | `["a", "b"]` |
| `dict[str, int]` | dict with str keys, int values | `{"a": 1}` |
| `str \| None` | string or nothing | `None` |
| `Literal["low", "high"]` | only these exact values | `"low"` |
| `datetime` | date + time | `datetime.now()` |

In plain Python, type hints are just notes. **In FastAPI they are rules**: if you say `note_id: int` and someone sends `"abc"`, FastAPI rejects it with a 422 error.

`Annotated` lets you attach extra info to a type. FastAPI uses it a lot:

```python
from typing import Annotated
from fastapi import Query

limit: Annotated[int, Query(ge=1, le=100)] = 10   # an int between 1 and 100, default 10
```

### 2.3 JSON

> 📦 **Analogy: JSON is a standard shipping box.**
> Every country (language) can open it: JavaScript, Python, Java, your phone. The box has labelled compartments (keys) with contents (values).

```json
{
  "title": "Shopping",
  "pinned": false,
  "tags": ["home", "errands"],
  "priority": 2,
  "content": null
}
```

| JSON | Python |
|---|---|
| `{ }` object | `dict` |
| `[ ]` array | `list` |
| `"text"` | `str` |
| `10`, `2.5` | `int`, `float` |
| `true` / `false` | `True` / `False` |
| `null` | `None` |

JSON rules beginners trip on: keys **must** use double quotes, no trailing commas, no comments, and `true/false/null` are lowercase.

```python
import json
text = json.dumps({"pinned": True})     # Python → JSON string: '{"pinned": true}'
data = json.loads('{"pinned": true}')   # JSON string → Python: {'pinned': True}
```

FastAPI does this conversion for you automatically.

### 2.4 HTTP basics

An HTTP **request** has:

| Part | Example | Analogy (sending a letter) |
|---|---|---|
| **Method** | `POST` | What you want done ("please file this") |
| **URL / path** | `/notes/5` | The address |
| **Query string** | `?tag=home&limit=5` | Notes on the envelope ("only urgent ones") |
| **Headers** | `Authorization: Bearer ...`, `Content-Type: application/json` | Stamps and labels on the envelope |
| **Body** | `{"title": "Shopping"}` | The letter inside |

An HTTP **response** has a **status code** (e.g. `200`), headers, and usually a body.

### 2.5 HTTP methods

> 🍽️ **Analogy (restaurant again):** GET = read the menu. POST = place a new order. PUT = replace your whole order. PATCH = "change just the drink". DELETE = cancel the order.

| Method | Purpose | Has body? | Safe? (no changes) | Idempotent?* | Notes API example |
|---|---|---|---|---|---|
| `GET` | Read data | No | ✅ | ✅ | `GET /notes`, `GET /notes/5` |
| `POST` | Create new item | Yes | ❌ | ❌ | `POST /notes` |
| `PUT` | Replace whole item | Yes | ❌ | ✅ | `PUT /notes/5` |
| `PATCH` | Update some fields | Yes | ❌ | usually ✅ | `PATCH /notes/5` |
| `DELETE` | Remove item | Usually no | ❌ | ✅ | `DELETE /notes/5` |

\* **Idempotent** = doing it twice gives the same result as doing it once. Pressing a lift button twice doesn't call two lifts (idempotent). Pressing "order pizza" twice gets you two pizzas (not idempotent, like POST).

### 2.6 Status codes

> 😀 **Analogy: Status codes are the waiter's reply.**
> 2xx = "Here you go!" 3xx = "That's at the other counter." 4xx = "You ordered something wrong." 5xx = "Sorry, the kitchen is on fire."

| Code | Name | When to use it in the Notes API |
|---|---|---|
| `200` | OK | Successful GET, PUT, PATCH |
| `201` | Created | Successful POST that created a note |
| `204` | No Content | Successful DELETE (no body returned) |
| `307` | Temporary Redirect | FastAPI redirecting `/notes/` ↔ `/notes` (trailing slash) |
| `400` | Bad Request | Request is understood but makes no sense (e.g. invalid id format, empty PATCH) |
| `401` | Unauthorized | Not logged in / bad or expired token |
| `403` | Forbidden | Logged in, but not allowed (someone else's note) |
| `404` | Not Found | Note doesn't exist, or wrong URL |
| `405` | Method Not Allowed | URL exists but not for this method (e.g. `DELETE /notes`) |
| `409` | Conflict | Email already registered |
| `413` | Content Too Large | Uploaded file too big |
| `415` | Unsupported Media Type | Wrong file type uploaded |
| `422` | Unprocessable Content | Body/params failed validation (FastAPI's automatic error) |
| `429` | Too Many Requests | Rate limited |
| `500` | Internal Server Error | Bug in your code (unhandled exception) |
| `503` | Service Unavailable | Database down, server overloaded |

**400 vs 404 vs 422 (the classic confusion):**

| You see | It means | Example |
|---|---|---|
| **422** | FastAPI's validation said the *shape/type* of the data is wrong | `title` missing, `limit=abc`, broken JSON |
| **400** | Data passed validation, but *your code* decided it's a bad request | `note_id="xyz"` isn't a valid MongoDB ObjectId; PATCH with no fields |
| **404** | Request is fine, but the thing doesn't exist | Valid id, but no note with that id. Or a typo in the URL. |

---

## 3. Setup on Windows + VS Code

### 3.1 What you need installed

| Tool | Check it's installed (PowerShell) | Get it from |
|---|---|---|
| Python 3.12+ | `python --version` or `py --version` | python.org (tick **"Add python.exe to PATH"** in the installer) |
| VS Code | `code --version` | code.visualstudio.com |
| Git | `git --version` | git-scm.com |
| MongoDB Community Server + Compass | `Get-Service MongoDB` | mongodb.com (Section 9) |
| Docker Desktop (later) | `docker --version` | docker.com (Section 17) |

VS Code extensions: **Python** (Microsoft), **Pylance**, and optionally **Docker** and **MongoDB for VS Code**.

### 3.2 Virtual environment (venv)

> 🎒 **Analogy: A venv is a separate lunchbox for each project.**
> Project A's lunchbox has FastAPI 0.115, project B's has FastAPI 0.164. They never mix, and nothing spills into your main bag (system Python).

```powershell
# 1. Create the project folder and open it
mkdir notes-api
cd notes-api

# 2. Create a virtual environment in a folder called .venv
python -m venv .venv
# (if you have several Pythons: py -3.12 -m venv .venv)

# 3. Activate it
.venv\Scripts\Activate.ps1        # PowerShell
# .venv\Scripts\activate.bat      # Command Prompt (cmd)
# source .venv/Scripts/activate   # Git Bash

# Your prompt now starts with (.venv)

# 4. Upgrade pip
python -m pip install --upgrade pip
```

To leave the venv: `deactivate`.

**Common Windows error when activating:**

```
.venv\Scripts\Activate.ps1 cannot be loaded because running scripts is disabled on this system.
```

PowerShell blocks scripts by default. Fix once for your user:

```powershell
Set-ExecutionPolicy -Scope CurrentUser -ExecutionPolicy RemoteSigned
```

### 3.3 Installing FastAPI

```powershell
pip install "fastapi[standard]"
```

The quotes matter in PowerShell because of the square brackets. `[standard]` adds the useful extras:

| Extra package | Why |
|---|---|
| `uvicorn` | The server that runs your app |
| `fastapi-cli` | The `fastapi dev` / `fastapi run` commands |
| `httpx` | Needed by `TestClient` for tests |
| `python-multipart` | Needed for forms and file uploads (login form, `UploadFile`) |
| `email-validator` | Needed for Pydantic's `EmailStr` |
| `jinja2` | Templates (not used in these notes) |

Save your dependencies so others (and Docker) can install the same ones:

```powershell
pip freeze > requirements.txt
# later, on another machine:
pip install -r requirements.txt
```

### 3.4 Select the interpreter in VS Code

1. Open the folder: `code .`
2. `Ctrl+Shift+P` → **Python: Select Interpreter** → pick the one with `.venv`.
3. New terminals in VS Code (`` Ctrl+` ``) now auto-activate the venv.

If imports like `from fastapi import FastAPI` show a yellow squiggle ("Import could not be resolved"), VS Code is using the wrong interpreter. Redo step 2.

### 3.5 First app and running it

Create `main.py`:

```python
from fastapi import FastAPI

app = FastAPI(title="Notes API", version="0.1.0")


@app.get("/")
def root():
    return {"message": "Welcome to the Notes API"}


@app.get("/health")
def health():
    return {"status": "ok"}
```

Run it:

```powershell
fastapi dev main.py
```

| Command | Use for | Auto-reload on save | Listens on |
|---|---|---|---|
| `fastapi dev main.py` | Development | ✅ | `127.0.0.1:8000` (your PC only) |
| `fastapi run main.py` | Production | ❌ | `0.0.0.0:8000` (all network interfaces) |
| `uvicorn main:app --reload` | Older/manual way, same as dev | ✅ | `127.0.0.1:8000` |

`main:app` means "file `main.py`, variable `app`".

Useful options: `--port 8001`, `--host 0.0.0.0` (let your phone on the same Wi‑Fi reach it).

### 3.6 The URLs to open

| URL | What you get |
|---|---|
| http://127.0.0.1:8000/ | Your root route's JSON |
| http://127.0.0.1:8000/docs | **Swagger UI**: interactive docs where you can test every endpoint |
| http://127.0.0.1:8000/redoc | ReDoc: prettier read-only docs |
| http://127.0.0.1:8000/openapi.json | The raw OpenAPI schema (machine-readable) |

### 3.7 .gitignore

Create `.gitignore` before your first commit:

```gitignore
.venv/
__pycache__/
*.pyc
.env
.pytest_cache/
uploads/
.vscode/
```

### 3.8 Setup errors

| Error | Meaning | Fix |
|---|---|---|
| `'python' is not recognized...` | Python not on PATH | Reinstall with "Add to PATH" ticked, or use `py` |
| Python opens the Microsoft Store | Windows "app execution alias" | Settings → Apps → Advanced app settings → App execution aliases → turn off `python.exe` / `python3.exe` |
| `running scripts is disabled` | PowerShell policy | `Set-ExecutionPolicy -Scope CurrentUser RemoteSigned` |
| `'fastapi' is not recognized` | venv not active or `[standard]` not installed | Activate venv; `pip install "fastapi[standard]"` |
| `ModuleNotFoundError: No module named 'fastapi'` | Running with a different Python than the venv | Activate venv; select interpreter in VS Code |
| `[WinError 10048] Only one usage of each socket address...` | Port 8000 already in use | Use `--port 8001`, or find and stop the old process (below) |
| `Error loading ASGI app. Could not import module "main"` | Wrong folder or file name | `cd` into the folder that contains `main.py` |

Find and kill whatever is using port 8000:

```powershell
netstat -ano | findstr :8000
taskkill /PID 12345 /F      # use the PID from the last column
```

---

## 4. Routes, Path Params, Query Params, Request Body

### 4.1 Routes (path operations)

> 🚪 **Analogy: A route is a labelled counter in a building.**
> "GET /notes" is the counter where you *view* notes. "POST /notes" is a different counter at the same address where you *hand in* new notes. Same address, different action.

```python
@app.get("/notes")        # method + path
def list_notes():         # the function that runs (the "path operation function")
    return [...]          # dicts/lists are converted to JSON automatically
```

A **route = HTTP method + path**. `GET /notes` and `POST /notes` are two different routes.

Our in-memory "database" for now (Sections 4–8):

```python
from fastapi import FastAPI

app = FastAPI(title="Notes API")

# Fake database: note id → note dict. Lost every time the server restarts.
notes_db: dict[int, dict] = {
    1: {"id": 1, "title": "Shopping", "content": "Milk, eggs", "tags": ["home"], "pinned": False},
    2: {"id": 2, "title": "Standup", "content": "Talk about the pipeline", "tags": ["work"], "pinned": True},
}
next_id = 3


@app.get("/notes")
def list_notes():
    return list(notes_db.values())
```

### 4.2 Path parameters

> 🏠 **Analogy: A path parameter is the house number in an address.**
> `/notes/2` → "go to the notes street, house number 2". It identifies **one specific thing**.

```python
@app.get("/notes/{note_id}")
def get_note(note_id: int):          # the name must match {note_id}
    return notes_db.get(note_id)
```

Because of `note_id: int`:
- `/notes/2` → `note_id = 2` (converted from the text "2" to the int 2)
- `/notes/abc` → **422** error, your function never runs.

Validate path params further with `Path`:

```python
from typing import Annotated
from fastapi import Path

@app.get("/notes/{note_id}")
def get_note(note_id: Annotated[int, Path(ge=1, description="The note's ID")]):
    return notes_db.get(note_id)
```

**Route order matters.** FastAPI checks routes top to bottom and uses the first match:

```python
@app.get("/notes/pinned")          # ✅ must come BEFORE /notes/{note_id}
def pinned_notes():
    return [n for n in notes_db.values() if n["pinned"]]

@app.get("/notes/{note_id}")
def get_note(note_id: int): ...
```

If `/notes/{note_id}` came first, `/notes/pinned` would try `note_id = "pinned"` → 422.

### 4.3 Query parameters

> 🍕 **Analogy: Query parameters are the "extra options" on an order.**
> "Pizza, **size=large, extra_cheese=yes**". Same pizza counter, but you customise/filter the result. They're optional and come after `?` in the URL.

Any function parameter that is **not** in the path and is a simple type (`str`, `int`, `bool`, ...) becomes a query parameter.

```python
from typing import Annotated
from fastapi import Query

@app.get("/notes")
def list_notes(
    tag: str | None = None,                                  # optional
    pinned: bool | None = None,                              # optional
    q: Annotated[str | None, Query(max_length=50)] = None,   # optional, validated
    limit: Annotated[int, Query(ge=1, le=100)] = 10,         # default 10, between 1 and 100
):
    results = list(notes_db.values())
    if tag:
        results = [n for n in results if tag in n["tags"]]
    if pinned is not None:
        results = [n for n in results if n["pinned"] == pinned]
    if q:
        results = [n for n in results if q.lower() in n["title"].lower()]
    return results[:limit]
```

| URL | Result |
|---|---|
| `/notes` | All notes (max 10) |
| `/notes?tag=work` | Notes tagged "work" |
| `/notes?pinned=true&limit=5` | Pinned notes, max 5 |
| `/notes?limit=500` | **422**: `less_than_equal` (limit must be ≤ 100) |

Required vs optional query parameters:

| Declaration | Meaning |
|---|---|
| `q: str` | **Required.** Missing → 422 `missing` |
| `q: str = "x"` | Optional, default `"x"` |
| `q: str \| None = None` | Optional, `None` if not given |

`bool` query params accept `true/false`, `1/0`, `yes/no`, `on/off`.

Common `Query`/`Path` validation options: `ge`, `gt`, `le`, `lt` (numbers), `min_length`, `max_length`, `pattern` (strings), `description`, `alias`.

### 4.4 Request body

> ✉️ **Analogy: The request body is the letter inside the envelope.**
> The path is the address, query params are notes on the envelope, and the **body** carries the actual content, like the whole new note you want to save.

Request bodies are declared with a **Pydantic model** (deep dive in Section 5):

```python
from pydantic import BaseModel

class NoteCreate(BaseModel):
    title: str
    content: str = ""
    tags: list[str] = []
    pinned: bool = False


@app.post("/notes")
def create_note(note: NoteCreate):          # a Pydantic model → read from the JSON body
    global next_id
    new_note = {"id": next_id, **note.model_dump()}
    notes_db[next_id] = new_note
    next_id += 1
    return new_note
```

Send this JSON body:

```json
{ "title": "Gym", "tags": ["health"] }
```

### 4.5 How FastAPI decides where a parameter comes from

| Parameter looks like | FastAPI reads it from |
|---|---|
| Name matches `{...}` in the path | **Path** |
| Simple type (`int`, `str`, `bool`, `float`, ...) | **Query string** |
| A Pydantic model | **JSON body** |
| `Annotated[..., Header()]` / `Cookie()` / `Form()` / `File()` | Header / cookie / form / file |
| `Annotated[..., Depends(...)]` | A dependency (Section 11) |

Combining all three:

```python
@app.put("/notes/{note_id}")
def replace_note(note_id: int, note: NoteCreate, notify: bool = False):
    # note_id → path, note → body, notify → query
    ...
```

---

## 5. Pydantic Models and Validation

### 5.1 What Pydantic does

> 🧾 **Analogy: A Pydantic model is an order slip with labelled boxes.**
> The slip says: "Title (required, 1–100 letters)", "Tags (list)", "Pinned (yes/no)". The checker at the counter (validation) looks at every slip. Missing a required box, or wrote "banana" in a yes/no box? The slip is handed back with a note saying exactly which box is wrong (a **422** error). Your kitchen (your function) only ever sees correctly filled slips.

Pydantic:
1. **Validates**: checks types and rules.
2. **Converts** (coerces): `"5"` → `5` for an `int` field, `"true"` → `True` for a `bool`.
3. **Documents**: FastAPI turns models into the schemas you see in `/docs`.
4. **Serializes**: turns model objects back into dicts/JSON.

### 5.2 The Notes API models

```python
from datetime import datetime
from pydantic import BaseModel, Field


class NoteBase(BaseModel):
    title: str = Field(min_length=1, max_length=100, examples=["Shopping list"])
    content: str = Field(default="", max_length=5000)
    tags: list[str] = Field(default_factory=list, max_length=10)
    pinned: bool = False


class NoteCreate(NoteBase):
    """Body for POST and PUT: the full note."""


class NoteUpdate(BaseModel):
    """Body for PATCH: every field optional."""
    title: str | None = Field(default=None, min_length=1, max_length=100)
    content: str | None = Field(default=None, max_length=5000)
    tags: list[str] | None = Field(default=None, max_length=10)
    pinned: bool | None = None


class NoteOut(NoteBase):
    """What the API sends back."""
    id: str
    created_at: datetime
    updated_at: datetime
```

Why several models for one "note"?

| Model | Used for | Why separate |
|---|---|---|
| `NoteCreate` | Input for POST/PUT | Client must not send `id` or timestamps; the server creates them |
| `NoteUpdate` | Input for PATCH | Everything optional |
| `NoteOut` | Output | Includes `id` and timestamps; never includes secret/internal fields |

(In Sections 4–8, `id` is an `int`; from Section 9 on it becomes a MongoDB `str` id.)

### 5.3 `Field`: rules for a single box

| Option | For | Example |
|---|---|---|
| `default=` | Default value | `Field(default="")` |
| `default_factory=` | Default for mutable types (list/dict) | `Field(default_factory=list)` |
| `min_length`, `max_length` | `str`, `list` | `Field(min_length=1, max_length=100)` |
| `ge`, `gt`, `le`, `lt` | Numbers | `Field(ge=1, le=5)` (rating 1–5) |
| `pattern` | Regex for `str` | `Field(pattern=r"^#[0-9a-fA-F]{6}$")` (hex colour) |
| `description`, `examples` | Shown in `/docs` | `Field(examples=["Shopping list"])` |
| `alias` | Different JSON name | `Field(alias="_id")` |

Tip: `tags: list[str] = []` is also safe in Pydantic (it copies defaults), but `default_factory=list` is the habit that's safe everywhere in Python.

### 5.4 Optional fields

| Declaration | Required? | Can be `null`? |
|---|---|---|
| `title: str` | ✅ yes | ❌ |
| `title: str = "Untitled"` | ❌ no | ❌ |
| `title: str \| None = None` | ❌ no | ✅ |
| `title: str \| None` | ✅ yes (must send it, but `null` allowed) | ✅ |

"Optional" in Pydantic means *has a default*, not just *can be None*.

### 5.5 Using models: create, validate, dump

```python
note = NoteCreate(title="Gym", tags=["health"])
print(note.title)            # "Gym"
print(note.model_dump())     # {'title': 'Gym', 'content': '', 'tags': ['health'], 'pinned': False}
print(note.model_dump_json())  # '{"title":"Gym","content":"","tags":["health"],"pinned":false}'

# Validate a dict yourself (FastAPI does this for you on requests)
data = {"title": "Read", "pinned": "yes"}
note = NoteCreate.model_validate(data)
print(note.pinned)           # True  ("yes" was converted)
```

| Method | Does | Pydantic v1 name (old tutorials) |
|---|---|---|
| `model_dump()` | Model → dict | `.dict()` |
| `model_dump_json()` | Model → JSON string | `.json()` |
| `model_validate(data)` | dict → model (validates) | `.parse_obj()` |
| `model_copy(update={...})` | Copy with changes | `.copy()` |
| `model_fields` | Info about fields | `__fields__` |

### 5.6 `exclude_unset`: only the boxes the client actually ticked

> ✏️ **Analogy:** A customer says "change my drink to tea". You should change **only the drink**, not blank out the starter and main course. `exclude_unset=True` gives you only the boxes the customer actually filled in.

```python
patch = NoteUpdate.model_validate({"pinned": True})

patch.model_dump()
# {'title': None, 'content': None, 'tags': None, 'pinned': True}   ❌ would wipe title/content/tags!

patch.model_dump(exclude_unset=True)
# {'pinned': True}                                                  ✅ only what was sent
```

| Option | Removes | Use when |
|---|---|---|
| `exclude_unset=True` | Fields the client didn't send | **PATCH** (partial updates) |
| `exclude_none=True` | Fields whose value is `None` | Hiding empty fields in output |
| `exclude_defaults=True` | Fields still equal to the default | Rare |
| `exclude={"field"}` / `include={...}` | Specific fields | Hiding something like `password` |

Gotcha: if a client explicitly sends `{"title": null}`, `exclude_unset` **keeps** it (it was "set"). Guard against that (Section 7.4).

### 5.7 Custom validators

```python
from pydantic import field_validator

class NoteCreate(NoteBase):
    @field_validator("tags")
    @classmethod
    def clean_tags(cls, tags: list[str]) -> list[str]:
        # lowercase, strip spaces, remove empties and duplicates (keeping order)
        cleaned = [t.strip().lower() for t in tags if t.strip()]
        return list(dict.fromkeys(cleaned))

    @field_validator("title")
    @classmethod
    def title_not_blank(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("title cannot be only spaces")
        return v.strip()
```

Sending `{"title": "   "}` gives a 422 with type `value_error` and msg `"Value error, title cannot be only spaces"`.

### 5.8 Model config: rejecting unknown fields

By default, unknown fields are silently **ignored**. To reject them:

```python
from pydantic import ConfigDict

class NoteCreate(NoteBase):
    model_config = ConfigDict(extra="forbid")   # {"title": "x", "colour": "red"} → 422 extra_forbidden
```

Other useful config: `str_strip_whitespace=True` (auto-strip all strings).

### 5.9 Reading a 422 error

FastAPI returns validation errors in this shape:

```json
{
  "detail": [
    {
      "type": "string_too_short",
      "loc": ["body", "title"],
      "msg": "String should have at least 1 character",
      "input": "",
      "ctx": { "min_length": 1 }
    }
  ]
}
```

| Key | Meaning |
|---|---|
| `type` | Machine-readable error kind (look this up in the table below) |
| `loc` | Where: `["body", "title"]`, `["query", "limit"]`, `["path", "note_id"]` |
| `msg` | Human-readable message |
| `input` | What the client actually sent |
| `ctx` | Extra info (the limit that was broken) |

### 5.10 Common 422 error types

| `type` | Example request | Meaning |
|---|---|---|
| `json_invalid` | Body: `{"title": "Gym",}` (trailing comma) or single quotes | The body isn't valid JSON at all. Pydantic never even saw your fields. `loc` is `["body", <character position>]`. |
| `missing` | Body: `{"content": "hi"}` | A required field wasn't sent |
| `string_too_short` | Body: `{"title": ""}` | Valid JSON, valid type, but breaks `min_length` |
| `string_too_long` | Title with 200 characters | Breaks `max_length` |
| `string_type` | Body: `{"title": 123}` | Expected a string |
| `int_parsing` | `/notes/abc` with `note_id: int` | Couldn't turn the text into an int |
| `bool_parsing` | `?pinned=maybe` | Couldn't turn the text into a bool |
| `greater_than_equal` / `less_than_equal` | `?limit=0` / `?limit=500` | Breaks `ge` / `le` |
| `list_type` | Body: `{"tags": "home"}` | Expected a list, got a string |
| `too_long` | 11 tags with `max_length=10` on a list | List too long |
| `extra_forbidden` | Unknown field with `extra="forbid"` | Field not allowed |
| `value_error` | Your `field_validator` raised `ValueError` | Your custom rule failed |
| `model_attributes_type` / `dict_type` | Body is a list or a string instead of an object | Expected a JSON object `{...}` |

**`json_invalid` vs `string_too_short`:** `json_invalid` = the envelope is torn, nothing inside could be read. `string_too_short` = the letter was readable, but one box was left too short. If you get `json_invalid`, check your quotes, commas, and that `Content-Type` is `application/json`.

---

## 6. Responses, Status Codes, HTTPException

### 6.1 What you can return

| You return | Client gets |
|---|---|
| `dict` / `list` | JSON |
| Pydantic model | JSON |
| `str` / `int` | JSON (`"hello"`, `5`) |
| `Response(...)`, `JSONResponse(...)`, `FileResponse(...)`, `StreamingResponse(...)` | Exactly that response (bypasses `response_model`) |

FastAPI uses `jsonable_encoder` under the hood, so `datetime` → ISO string, etc.

### 6.2 `response_model`: shaping the output

> 📋 **Analogy: `response_model` is the plating guide.**
> Whatever's in the kitchen pot, the plate must look like *this*: only these items, in this form. Extra things (like the chef's secret notes, or a user's password hash) never leave the kitchen.

```python
@app.get("/notes/{note_id}", response_model=NoteOut)
def get_note(note_id: int):
    return notes_db[note_id]          # extra keys in the dict are dropped; missing required keys → 500
```

Or use the return type annotation (FastAPI reads it the same way):

```python
@app.get("/notes/{note_id}")
def get_note(note_id: int) -> NoteOut:
    ...
```

Useful options:

| Option | Effect |
|---|---|
| `response_model=list[NoteOut]` | A list of notes |
| `response_model_exclude_none=True` | Drop `null` fields from the output |
| `response_model_exclude={"content"}` | Drop specific fields |

Benefits: filters out secret data, validates your *own* output, and documents the response in `/docs`.

### 6.3 Setting the status code

```python
from fastapi import status

@app.post("/notes", status_code=status.HTTP_201_CREATED, response_model=NoteOut)
def create_note(note: NoteCreate):
    ...
```

`status.HTTP_201_CREATED` is just `201` with a readable name (helps autocomplete).

### 6.4 `HTTPException`: saying "no"

> 🙅 **Analogy: HTTPException is the waiter coming back saying "Sorry, we're out of that dish."**
> Your function stops immediately and the client gets a polite, structured error instead of food.

```python
from fastapi import HTTPException, status

@app.get("/notes/{note_id}", response_model=NoteOut)
def get_note(note_id: int):
    note = notes_db.get(note_id)
    if note is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Note {note_id} not found",
        )
    return note
```

Response:

```json
{ "detail": "Note 99 not found" }
```

Notes:
- Use `raise`, not `return`. `return HTTPException(...)` sends it as normal data with status 200.
- `detail` can be a string, dict, or list.
- You can add headers: `HTTPException(401, "Not authenticated", headers={"WWW-Authenticate": "Bearer"})`.

### 6.5 Returning nothing: 204 No Content

```python
from fastapi import Response

@app.delete("/notes/{note_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_note(note_id: int):
    if notes_db.pop(note_id, None) is None:
        raise HTTPException(404, detail=f"Note {note_id} not found")
    return Response(status_code=status.HTTP_204_NO_CONTENT)
```

A 204 must have **no body**. Returning `Response(...)` guarantees that.

### 6.6 Custom response objects

```python
from fastapi.responses import JSONResponse

@app.get("/custom")
def custom():
    return JSONResponse(
        status_code=202,
        content={"message": "Accepted"},
        headers={"X-Notes-Version": "1"},
    )
```

| Response class | Use for |
|---|---|
| `JSONResponse` | JSON with a custom status/headers |
| `Response` | Raw response (e.g. 204) |
| `PlainTextResponse` | Plain text |
| `HTMLResponse` | HTML |
| `RedirectResponse` | Redirect to another URL |
| `FileResponse` | Send a file from disk (Section 15) |
| `StreamingResponse` | Send data piece by piece (Section 15) |

### 6.7 Response errors

| Error | Meaning | Fix |
|---|---|---|
| `500` + `ResponseValidationError` in terminal | Your *returned* data doesn't match `response_model` (e.g. missing `id`) | Fix what you return, or the model |
| Client gets `{"status_code": 404, "detail": ...}` with status 200 | You `return`ed the HTTPException | Use `raise` |
| `500` + `TypeError: Object of type ObjectId is not JSON serializable` | Returning a raw MongoDB document | Convert `_id` to `str` (Section 9) |
| `RuntimeError: Response content longer than Content-Length` / 204 with body | Returned a body with 204 | Return `Response(status_code=204)` |

---

## 7. Full CRUD: GET, POST, PUT, PATCH, DELETE

> 🗂️ **Analogy: CRUD is everything you can do with a paper file in a cabinet.**
> **C**reate (put a new file in), **R**ead (look at a file), **U**pdate (rewrite the whole page = PUT, or use correction tape on one line = PATCH), **D**elete (shred it).

| CRUD | HTTP | Path | Success code | Body in | Body out |
|---|---|---|---|---|---|
| Create | `POST` | `/notes` | `201` | `NoteCreate` | `NoteOut` |
| Read all | `GET` | `/notes` | `200` | – | `list[NoteOut]` |
| Read one | `GET` | `/notes/{id}` | `200` | – | `NoteOut` |
| Replace | `PUT` | `/notes/{id}` | `200` | `NoteCreate` (all fields) | `NoteOut` |
| Partial update | `PATCH` | `/notes/{id}` | `200` | `NoteUpdate` (any fields) | `NoteOut` |
| Delete | `DELETE` | `/notes/{id}` | `204` | – | nothing |

### 7.1 PUT vs PATCH

| | PUT | PATCH |
|---|---|---|
| Meaning | Replace the whole thing | Change some fields |
| Body | Full object | Only changed fields |
| Fields not sent | Reset to defaults | Left unchanged |
| Pydantic model | `NoteCreate` (required fields) | `NoteUpdate` (all optional) |
| Dump with | `model_dump()` | `model_dump(exclude_unset=True)` |
| Analogy | Rewrite the whole page | Correction tape on one line |

Example: the note is `{"title": "Gym", "content": "Leg day", "pinned": true}`.

| Request | Result |
|---|---|
| `PUT {"title": "Gym 2"}` | `{"title": "Gym 2", "content": "", "pinned": false}` (others reset!) |
| `PATCH {"title": "Gym 2"}` | `{"title": "Gym 2", "content": "Leg day", "pinned": true}` |

### 7.2 Complete in-memory CRUD (`main.py`)

```python
from datetime import datetime, timezone

from fastapi import FastAPI, HTTPException, Response, status
from pydantic import BaseModel, Field

app = FastAPI(title="Notes API", version="0.2.0")


# ---------- Models ----------
class NoteBase(BaseModel):
    title: str = Field(min_length=1, max_length=100)
    content: str = Field(default="", max_length=5000)
    tags: list[str] = Field(default_factory=list)
    pinned: bool = False


class NoteCreate(NoteBase):
    pass


class NoteUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=100)
    content: str | None = Field(default=None, max_length=5000)
    tags: list[str] | None = None
    pinned: bool | None = None


class NoteOut(NoteBase):
    id: int
    created_at: datetime
    updated_at: datetime


# ---------- Fake database ----------
notes_db: dict[int, dict] = {}
next_id = 1


def now() -> datetime:
    return datetime.now(timezone.utc)


def get_or_404(note_id: int) -> dict:
    note = notes_db.get(note_id)
    if note is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail=f"Note {note_id} not found")
    return note


# ---------- Routes ----------
@app.post("/notes", response_model=NoteOut, status_code=status.HTTP_201_CREATED)
def create_note(note: NoteCreate):
    global next_id
    timestamp = now()
    new_note = {"id": next_id, **note.model_dump(), "created_at": timestamp, "updated_at": timestamp}
    notes_db[next_id] = new_note
    next_id += 1
    return new_note


@app.get("/notes", response_model=list[NoteOut])
def list_notes(tag: str | None = None, pinned: bool | None = None):
    results = list(notes_db.values())
    if tag:
        results = [n for n in results if tag in n["tags"]]
    if pinned is not None:
        results = [n for n in results if n["pinned"] == pinned]
    return results


@app.get("/notes/{note_id}", response_model=NoteOut)
def get_note(note_id: int):
    return get_or_404(note_id)


@app.put("/notes/{note_id}", response_model=NoteOut)
def replace_note(note_id: int, note: NoteCreate):
    existing = get_or_404(note_id)
    updated = {
        "id": note_id,
        **note.model_dump(),                       # every field replaced
        "created_at": existing["created_at"],      # keep original creation time
        "updated_at": now(),
    }
    notes_db[note_id] = updated
    return updated


@app.patch("/notes/{note_id}", response_model=NoteOut)
def update_note(note_id: int, note: NoteUpdate):
    existing = get_or_404(note_id)
    changes = note.model_dump(exclude_unset=True)  # only fields the client sent
    if not changes:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, detail="No fields to update")
    existing.update(changes)
    existing["updated_at"] = now()
    return existing


@app.delete("/notes/{note_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_note(note_id: int):
    get_or_404(note_id)
    del notes_db[note_id]
    return Response(status_code=status.HTTP_204_NO_CONTENT)
```

### 7.3 Trying it from PowerShell

Swagger (`/docs`) is easiest, but you can also use `Invoke-RestMethod`:

```powershell
# Create
Invoke-RestMethod -Method Post -Uri http://127.0.0.1:8000/notes `
  -ContentType "application/json" `
  -Body '{"title": "Gym", "content": "Leg day", "tags": ["health"]}'

# Read
Invoke-RestMethod http://127.0.0.1:8000/notes
Invoke-RestMethod http://127.0.0.1:8000/notes/1

# Patch
Invoke-RestMethod -Method Patch -Uri http://127.0.0.1:8000/notes/1 `
  -ContentType "application/json" -Body '{"pinned": true}'

# Delete
Invoke-RestMethod -Method Delete -Uri http://127.0.0.1:8000/notes/1
```

In PowerShell, `curl` is an alias for `Invoke-WebRequest`. To use real curl, type `curl.exe`:

```powershell
curl.exe -X POST http://127.0.0.1:8000/notes -H "Content-Type: application/json" -d "{\"title\": \"Gym\"}"
```

(Escaping quotes for `curl.exe` in PowerShell is painful; that's why Swagger or `Invoke-RestMethod` is nicer on Windows.)

### 7.4 CRUD gotchas

| Problem | Cause | Fix |
|---|---|---|
| PATCH wipes other fields | Used `model_dump()` instead of `model_dump(exclude_unset=True)` | Use `exclude_unset=True` |
| PATCH `{"title": null}` sets title to null | `exclude_unset` keeps explicitly-sent nulls | Also drop `None`s for required fields: `{k: v for k, v in changes.items() if v is not None}` |
| `405 Method Not Allowed` | Route exists for another method only (e.g. `DELETE /notes`) | Check method + path |
| `307 Temporary Redirect` | `/notes/` vs `/notes` trailing slash mismatch | Call the exact path declared |
| PUT loses `created_at` | Replaced the whole dict | Copy over server-owned fields (id, created_at) |

---

## 8. Reading Swagger /docs

> 📖 **Analogy: `/docs` is an interactive menu with a "try it" button.**
> Each dish (endpoint) shows its ingredients (parameters), what it looks like (response schema), and you can order a sample right from the menu.

Open http://127.0.0.1:8000/docs while the server is running.

### 8.1 What you see

| Part of the page | What it tells you |
|---|---|
| Title + version at the top | From `FastAPI(title=..., version=...)` |
| Coloured bars per endpoint | Method colour: GET blue, POST green, PUT orange, PATCH teal, DELETE red |
| Groups (e.g. "notes", "auth") | From `tags=[...]` |
| **Parameters** section | Path/query/header params, with `*required` markers and limits |
| **Request body** | The Pydantic model as an example JSON, plus a **Schema** tab |
| **Responses** | Status codes, example output, and the `422` "Validation Error" shape |
| **Schemas** (bottom of page) | Every Pydantic model, with field types and rules |
| 🔒 padlock / **Authorize** button | Protected routes (after Section 12) |

### 8.2 Testing an endpoint

1. Click an endpoint (e.g. **POST /notes**) to expand it.
2. Click **Try it out**.
3. Edit the example JSON body / fill in parameters.
4. Click **Execute**.
5. Read the result:
   - **Curl**: the equivalent command.
   - **Request URL**: the exact URL called (check your query params here).
   - **Server response**: the real status code and body.
   - **Responses**: what's *documented* (can differ from what actually happened).

### 8.3 Making your docs better

```python
app = FastAPI(
    title="Notes API",
    version="1.0.0",
    description="A simple notes service built while learning FastAPI.",
)

@app.post(
    "/notes",
    response_model=NoteOut,
    status_code=201,
    tags=["notes"],
    summary="Create a note",
    responses={409: {"description": "A note with this title already exists"}},
)
def create_note(note: NoteCreate):
    """
    Create a new note.

    - **title**: 1–100 characters (required)
    - **tags**: optional list of labels
    """
    ...
```

| What you add | Where it appears in `/docs` |
|---|---|
| `tags=["notes"]` | Groups the endpoint |
| `summary="..."` | Short title on the bar |
| Function docstring | Description when expanded (Markdown supported) |
| `Field(description=..., examples=[...])` | Field docs and example values |
| `responses={...}` | Extra documented status codes |
| `deprecated=True` | Endpoint shown crossed out |

### 8.4 /docs gotchas

| Symptom | Cause |
|---|---|
| Your new endpoint isn't shown | Server didn't reload (check terminal for errors) or you forgot the decorator |
| "Failed to fetch" | Server stopped/crashed, or a CORS issue if docs are served elsewhere |
| 401 on every protected route | You haven't clicked **Authorize** and logged in (Section 12) |
| Body field shows `"string"` | No `examples` set; just edit the value |
| Want to hide an endpoint | `@app.get("/internal", include_in_schema=False)` |
| Turn docs off in production | `FastAPI(docs_url=None, redoc_url=None)` |

---

## 9. MongoDB with PyMongo

### 9.1 MongoDB in one picture

> 🗄️ **Analogy: MongoDB is a filing cabinet.**
> The **database** is the cabinet (`notes_db`). Each **collection** is a drawer (`notes`, `users`). Each **document** is a folder in the drawer: a JSON-like page that can have any fields. Every folder gets a unique barcode sticker: the **ObjectId** (`_id`).

| SQL world | MongoDB world |
|---|---|
| Database | Database |
| Table | Collection |
| Row | Document |
| Column | Field |
| Primary key `id` | `_id` (an `ObjectId` by default) |
| Fixed schema | Flexible schema (Pydantic gives you the rules instead) |
| `JOIN` | Embed data, or `$lookup` |

**PyMongo** is the official Python driver. It has a sync client (`MongoClient`) and an async client (`AsyncMongoClient`, Section 14). The older async library **Motor** is deprecated in favour of PyMongo's async client.

### 9.2 Make sure MongoDB is running (Windows)

MongoDB Community Server on Windows usually installs as a **Windows service** that starts automatically.

```powershell
Get-Service MongoDB            # Status should be "Running"
# If stopped (run PowerShell as Administrator):
net start MongoDB
```

In **MongoDB Compass**: click **Add new connection** → URI `mongodb://localhost:27017` → **Connect**. Your `notes_db` database appears after you insert the first document (MongoDB creates databases and collections lazily).

Install the driver in your venv:

```powershell
pip install pymongo
```

### 9.3 Connecting

```python
from pymongo import MongoClient

client = MongoClient("mongodb://localhost:27017", serverSelectionTimeoutMS=5000)
db = client["notes_db"]          # or client.notes_db
notes = db["notes"]              # or db.notes

client.admin.command("ping")     # raises an error if MongoDB isn't reachable
```

Create **one** client for the whole app and reuse it. It manages a pool of connections internally. Don't create a client per request.

| Connection string | For |
|---|---|
| `mongodb://localhost:27017` | Local MongoDB on Windows |
| `mongodb://mongo:27017` | From inside Docker Compose (service name `mongo`, Section 17) |
| `mongodb+srv://user:pass@cluster0.xxxxx.mongodb.net` | MongoDB Atlas (cloud) |

### 9.4 ObjectId

> 🏷️ **Analogy: ObjectId is a barcode sticker.** It's unique, it's printed automatically when a folder enters the cabinet, and it even encodes *when* the sticker was printed.

```python
from bson import ObjectId

oid = ObjectId()                       # e.g. ObjectId('6740a1f2c9e77b2a1d3f0a11')
str(oid)                               # '6740a1f2c9e77b2a1d3f0a11'  (24 hex characters)
ObjectId("6740a1f2c9e77b2a1d3f0a11")   # string → ObjectId
ObjectId.is_valid("hello")             # False
oid.generation_time                    # datetime when it was created
```

**The two ObjectId problems every beginner hits:**

| Problem | Why | Fix |
|---|---|---|
| `TypeError: Object of type ObjectId is not JSON serializable` (or `ResponseValidationError`) | JSON doesn't know what an ObjectId is | Convert: `doc["id"] = str(doc.pop("_id"))` |
| `find_one({"_id": "6740a1..."})` returns `None` even though it exists | You compared an ObjectId with a *string* | Convert: `{"_id": ObjectId(note_id)}` |
| `bson.errors.InvalidId: 'abc' is not a valid ObjectId` | String isn't 24 hex chars | Validate and return **400** |

### 9.5 PyMongo operations cheat table

| Task | Code | Returns |
|---|---|---|
| Insert one | `notes.insert_one(doc)` | `InsertOneResult` → `.inserted_id` |
| Insert many | `notes.insert_many([d1, d2])` | `.inserted_ids` |
| Find one | `notes.find_one({"_id": oid})` | dict or `None` |
| Find many | `notes.find({"tags": "work"})` | cursor (iterate it) |
| Count | `notes.count_documents(query)` | int |
| Replace whole doc | `notes.replace_one({"_id": oid}, new_doc)` | `.matched_count`, `.modified_count` |
| Update fields | `notes.update_one({"_id": oid}, {"$set": {...}})` | `.matched_count`, `.modified_count` |
| Update + get new doc | `notes.find_one_and_update(filter, update, return_document=ReturnDocument.AFTER)` | dict or `None` |
| Delete one | `notes.delete_one({"_id": oid})` | `.deleted_count` |
| Sort / skip / limit | `notes.find(q).sort("updated_at", -1).skip(10).limit(10)` | cursor |
| Projection (pick fields) | `notes.find(q, {"title": 1})` | docs with only `_id` + `title` |
| Create index | `notes.create_index("tags")` | index name |

### 9.6 Update operators

> ✏️ **Analogy:** `replace_one` = throw the page away and write a new one. `$set` = correction tape on just the lines you name.

| Operator | Does | Example |
|---|---|---|
| `$set` | Set fields (others untouched) | `{"$set": {"pinned": True}}` |
| `$unset` | Remove a field | `{"$unset": {"color": ""}}` |
| `$inc` | Add to a number | `{"$inc": {"views": 1}}` |
| `$push` | Append to an array | `{"$push": {"tags": "urgent"}}` |
| `$addToSet` | Append if not already there | `{"$addToSet": {"tags": "urgent"}}` |
| `$pull` | Remove from an array | `{"$pull": {"tags": "old"}}` |

Gotcha: `update_one({"_id": oid}, {"pinned": True})` (no `$`) raises `ValueError: update only works with $ operators`.

### 9.7 Query operators (filters)

| Filter | Meaning |
|---|---|
| `{"pinned": True}` | Equal |
| `{"tags": "work"}` | Array *contains* "work" |
| `{"tags": {"$in": ["work", "home"]}}` | Contains any of these |
| `{"tags": {"$all": ["work", "urgent"]}}` | Contains all of these |
| `{"views": {"$gte": 10}}` | ≥ 10 (`$gt`, `$lt`, `$lte`, `$ne` too) |
| `{"title": {"$regex": "gym", "$options": "i"}}` | Contains "gym", case-insensitive |
| `{"$or": [{...}, {...}]}` | Either condition |
| `{"$text": {"$search": "milk eggs"}}` | Full-text search (needs a text index) |

### 9.8 Search: regex vs text index

| | `$regex` | `$text` (text index) |
|---|---|---|
| Setup | None | `notes.create_index([("title", "text"), ("content", "text")])` |
| Matches | Any substring ("gy" matches "gym") | Whole words, with stemming ("running" ≈ "run") |
| Speed on big data | Slow (scans everything) | Fast |
| Relevance ranking | No | Yes (`{"score": {"$meta": "textScore"}}`) |
| Good for | Small apps, learning | Real search |

Always `re.escape()` user input before putting it in a regex, otherwise `?q=(` crashes the query and users can craft slow regexes.

### 9.9 Pagination

> 📚 **Analogy: Pagination is reading a book page by page.** `limit` = how many lines per page, `skip` = how many lines to jump over to reach your page. Page 3 with 10 per page → `skip=20, limit=10`.

```python
cursor = notes.find(query).sort("updated_at", -1).skip(skip).limit(limit)
total = notes.count_documents(query)
```

Always **sort** before paginating, otherwise the order (and so the pages) can change between requests. `skip` gets slow for huge offsets (it still walks over skipped docs); for very large collections use "cursor/keyset" pagination (`{"_id": {"$lt": last_seen_id}}`) instead.

### 9.10 Notes API with MongoDB (single file, sync)

`main.py`:

```python
import re
from datetime import datetime, timezone
from typing import Annotated

from bson import ObjectId
from fastapi import FastAPI, HTTPException, Query, Response, status
from pydantic import BaseModel, Field
from pymongo import MongoClient, ReturnDocument

app = FastAPI(title="Notes API", version="0.3.0")

client = MongoClient("mongodb://localhost:27017", serverSelectionTimeoutMS=5000)
db = client["notes_db"]
notes = db["notes"]


# ---------- Models ----------
class NoteBase(BaseModel):
    title: str = Field(min_length=1, max_length=100)
    content: str = Field(default="", max_length=5000)
    tags: list[str] = Field(default_factory=list)
    pinned: bool = False


class NoteCreate(NoteBase):
    pass


class NoteUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=100)
    content: str | None = Field(default=None, max_length=5000)
    tags: list[str] | None = None
    pinned: bool | None = None


class NoteOut(NoteBase):
    id: str
    created_at: datetime
    updated_at: datetime


class NotePage(BaseModel):
    total: int
    skip: int
    limit: int
    items: list[NoteOut]


# ---------- Helpers ----------
def now() -> datetime:
    return datetime.now(timezone.utc)


def to_object_id(note_id: str) -> ObjectId:
    """Turn a string into an ObjectId, or answer 400 if it's not a valid id."""
    if not ObjectId.is_valid(note_id):
        raise HTTPException(status.HTTP_400_BAD_REQUEST, detail=f"'{note_id}' is not a valid note id")
    return ObjectId(note_id)


def serialize(doc: dict) -> dict:
    """MongoDB document → API-friendly dict (_id: ObjectId → id: str)."""
    doc["id"] = str(doc.pop("_id"))
    return doc


def not_found(note_id: str) -> HTTPException:
    return HTTPException(status.HTTP_404_NOT_FOUND, detail=f"Note {note_id} not found")


# ---------- Routes ----------
@app.post("/notes", response_model=NoteOut, status_code=status.HTTP_201_CREATED)
def create_note(note: NoteCreate):
    doc = note.model_dump()
    doc["created_at"] = doc["updated_at"] = now()
    notes.insert_one(doc)              # PyMongo adds doc["_id"] for us
    return serialize(doc)


@app.get("/notes", response_model=NotePage)
def list_notes(
    q: Annotated[str | None, Query(max_length=100, description="Search title/content")] = None,
    tag: str | None = None,
    pinned: bool | None = None,
    skip: Annotated[int, Query(ge=0)] = 0,
    limit: Annotated[int, Query(ge=1, le=100)] = 10,
):
    query: dict = {}
    if q:
        pattern = {"$regex": re.escape(q), "$options": "i"}
        query["$or"] = [{"title": pattern}, {"content": pattern}]
    if tag:
        query["tags"] = tag
    if pinned is not None:
        query["pinned"] = pinned

    cursor = notes.find(query).sort("updated_at", -1).skip(skip).limit(limit)
    return {
        "total": notes.count_documents(query),
        "skip": skip,
        "limit": limit,
        "items": [serialize(d) for d in cursor],
    }


@app.get("/notes/{note_id}", response_model=NoteOut)
def get_note(note_id: str):
    doc = notes.find_one({"_id": to_object_id(note_id)})
    if doc is None:
        raise not_found(note_id)
    return serialize(doc)


@app.put("/notes/{note_id}", response_model=NoteOut)
def replace_note(note_id: str, note: NoteCreate):
    oid = to_object_id(note_id)
    existing = notes.find_one({"_id": oid}, {"created_at": 1})
    if existing is None:
        raise not_found(note_id)
    new_doc = {**note.model_dump(), "created_at": existing["created_at"], "updated_at": now()}
    notes.replace_one({"_id": oid}, new_doc)
    new_doc["_id"] = oid
    return serialize(new_doc)


@app.patch("/notes/{note_id}", response_model=NoteOut)
def update_note(note_id: str, note: NoteUpdate):
    oid = to_object_id(note_id)
    changes = {k: v for k, v in note.model_dump(exclude_unset=True).items() if v is not None}
    if not changes:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, detail="No fields to update")
    changes["updated_at"] = now()
    doc = notes.find_one_and_update(
        {"_id": oid},
        {"$set": changes},
        return_document=ReturnDocument.AFTER,   # give back the updated doc, not the old one
    )
    if doc is None:
        raise not_found(note_id)
    return serialize(doc)


@app.delete("/notes/{note_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_note(note_id: str):
    result = notes.delete_one({"_id": to_object_id(note_id)})
    if result.deleted_count == 0:
        raise not_found(note_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
```

Why `def` and not `async def` here? PyMongo's `MongoClient` is **blocking**. FastAPI runs `def` routes in a thread pool, so a slow DB call doesn't freeze the server. **Never call the sync `MongoClient` inside an `async def` route** (Section 14 explains why).

### 9.11 Dates

- Store `datetime.now(timezone.utc)` (timezone-aware UTC). MongoDB stores dates in UTC with millisecond precision.
- PyMongo returns **naive** datetimes by default (no timezone). For aware ones: `MongoClient(url, tz_aware=True)`.
- Convert to IST only for display, in the frontend.

### 9.12 MongoDB errors

| Error | Meaning | Fix |
|---|---|---|
| `ServerSelectionTimeoutError: localhost:27017: [WinError 10061] No connection could be made...` | MongoDB isn't running/reachable | `net start MongoDB` (admin), check the URL |
| `bson.errors.InvalidId` | Bad id string passed to `ObjectId()` | Validate with `ObjectId.is_valid()` → 400 |
| `DuplicateKeyError: E11000 duplicate key error` | Unique index violated (e.g. same email) | Catch it → 409 Conflict |
| `ValueError: update only works with $ operators` | `update_one` without `$set` | Wrap fields in `{"$set": ...}` |
| `ValueError: replacement can not include $ operators` | `replace_one` with `$set` | Pass a plain document |
| `OperationFailure: text index required for $text query` | `$text` without a text index | Create the text index |
| Found `None` for an existing doc | Compared string with ObjectId | `ObjectId(note_id)` |
| `ObjectId is not JSON serializable` | Returned raw doc | `serialize()` it |

---

## 10. Project Structure: APIRouter, Folders, Settings, .env

### 10.1 Why split the code

One `main.py` is fine for 100 lines. At 1,000 lines it's a mess.

> 🏬 **Analogy: `APIRouter` is a department in a big store.**
> The store (`app`) has departments: Notes, Auth. Each department (router) manages its own counters and staff, and the store just puts up signs pointing to them (`include_router`).

### 10.2 Folder layout

```text
notes-api/
├── app/
│   ├── __init__.py          # empty file: makes "app" a Python package
│   ├── main.py              # creates FastAPI(), includes routers
│   ├── config.py            # settings loaded from .env
│   ├── database.py          # Mongo client + get_db dependency
│   ├── dependencies.py      # shared dependencies (pagination, current user)
│   ├── utils.py             # to_object_id, serialize, now
│   ├── core/
│   │   ├── __init__.py
│   │   └── security.py      # password hashing + JWT (Section 12)
│   ├── schemas/
│   │   ├── __init__.py
│   │   ├── note.py          # NoteCreate, NoteUpdate, NoteOut, NotePage
│   │   └── user.py          # UserCreate, UserOut, Token (Section 12)
│   └── routers/
│       ├── __init__.py
│       ├── notes.py         # /notes routes
│       └── auth.py          # /auth routes (Section 12)
├── tests/
│   ├── conftest.py
│   └── test_notes.py
├── .env                     # real secrets, NOT committed
├── .env.example             # template, committed
├── .gitignore
├── requirements.txt
├── pytest.ini
├── Dockerfile
├── docker-compose.yml
└── NOTES.md
```

Create the empty `__init__.py` files in PowerShell:

```powershell
mkdir app, app\core, app\schemas, app\routers, tests
New-Item app\__init__.py, app\core\__init__.py, app\schemas\__init__.py, app\routers\__init__.py -ItemType File
```

Run the app from the project root (the folder that *contains* `app/`):

```powershell
fastapi dev app/main.py
```

| Layer | Folder | Job | Analogy |
|---|---|---|---|
| Routers | `routers/` | HTTP: paths, status codes | Front counter |
| Schemas | `schemas/` | Shape of data in/out | Order slips |
| Database | `database.py` | Connection | The cabinet key |
| Core | `core/` | Security, shared logic | Back office |
| Config | `config.py` | Settings | Manager's rulebook |

(Bigger projects add a `services/` or `crud/` layer between routers and the database. Optional for now.)

### 10.3 `.env` and pydantic-settings

> 🔐 **Analogy: `.env` is a locked drawer of secrets, and `pydantic-settings` is the manager who reads it.**
> Your code never has the passwords written in it. On your laptop the drawer has dev secrets; on the server it has production secrets. Same code, different drawer.

```powershell
pip install pydantic-settings
python -c "import secrets; print(secrets.token_hex(32))"     # generate a SECRET_KEY
```

`.env` (never commit this):

```dotenv
APP_NAME=Notes API
MONGO_URL=mongodb://localhost:27017
MONGO_DB=notes_db
SECRET_KEY=paste-the-64-character-hex-string-here
ACCESS_TOKEN_EXPIRE_MINUTES=30
CORS_ORIGINS=["http://localhost:3000","http://localhost:5173"]
```

`.env.example` (commit this, with fake values, so others know what to set):

```dotenv
APP_NAME=Notes API
MONGO_URL=mongodb://localhost:27017
MONGO_DB=notes_db
SECRET_KEY=change-me
ACCESS_TOKEN_EXPIRE_MINUTES=30
CORS_ORIGINS=["http://localhost:3000"]
```

`app/config.py`:

```python
from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "Notes API"
    mongo_url: str = "mongodb://localhost:27017"
    mongo_db: str = "notes_db"
    secret_key: str                       # no default → app refuses to start without it
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    cors_origins: list[str] = ["http://localhost:3000"]

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
```

How values are found (highest priority first):
1. Real environment variables (e.g. set by Docker or your host)
2. The `.env` file
3. Defaults in the class

Names are matched case-insensitively (`MONGO_URL` → `mongo_url`) and converted to the right type (`"30"` → `30`). Lists/dicts are written as JSON in `.env`.

Set an environment variable just for one PowerShell session:

```powershell
$env:MONGO_DB = "notes_test"
fastapi dev app/main.py
```

| Error | Meaning |
|---|---|
| `ValidationError: 1 validation error for Settings secret_key Field required` | `SECRET_KEY` missing in `.env` / environment, or `.env` not in the folder you ran from |
| `ModuleNotFoundError: No module named 'pydantic_settings'` | `pip install pydantic-settings` (it's a separate package since Pydantic v2) |
| `error parsing value for field "cors_origins"` | List in `.env` isn't valid JSON (use `["a","b"]` with double quotes) |

### 10.4 The split files (sync version)

`app/database.py`:

```python
from pymongo import MongoClient
from pymongo.database import Database

from app.config import settings

client = MongoClient(settings.mongo_url, serverSelectionTimeoutMS=5000)


def get_db() -> Database:
    return client[settings.mongo_db]
```

`app/utils.py`:

```python
from datetime import datetime, timezone

from bson import ObjectId
from fastapi import HTTPException, status


def now() -> datetime:
    return datetime.now(timezone.utc)


def to_object_id(value: str) -> ObjectId:
    if not ObjectId.is_valid(value):
        raise HTTPException(status.HTTP_400_BAD_REQUEST, detail=f"'{value}' is not a valid id")
    return ObjectId(value)


def serialize(doc: dict) -> dict:
    doc["id"] = str(doc.pop("_id"))
    return doc
```

`app/schemas/note.py`: the `NoteBase`, `NoteCreate`, `NoteUpdate`, `NoteOut`, `NotePage` models from Section 9.10 (with the `from datetime import datetime` and `from pydantic import BaseModel, Field` imports).

`app/routers/notes.py`:

```python
from fastapi import APIRouter, HTTPException, status

from app.database import get_db
from app.schemas.note import NoteCreate, NoteOut
from app.utils import now, serialize, to_object_id

router = APIRouter(prefix="/notes", tags=["notes"])


@router.post("", response_model=NoteOut, status_code=status.HTTP_201_CREATED)
def create_note(note: NoteCreate):
    db = get_db()
    doc = {**note.model_dump(), "created_at": now(), "updated_at": now()}
    db.notes.insert_one(doc)
    return serialize(doc)


@router.get("/{note_id}", response_model=NoteOut)       # full path: /notes/{note_id}
def get_note(note_id: str):
    doc = get_db().notes.find_one({"_id": to_object_id(note_id)})
    if doc is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail=f"Note {note_id} not found")
    return serialize(doc)

# ... list, put, patch, delete exactly as in Section 9.10, using get_db().notes
```

`@router.post("")` with `prefix="/notes"` gives exactly `/notes`. Using `"/"` would give `/notes/` and requests to `/notes` would get a 307 redirect.

`app/main.py`:

```python
from fastapi import FastAPI

from app.config import settings
from app.routers import notes

app = FastAPI(title=settings.app_name, version="0.4.0")
app.include_router(notes.router)


@app.get("/health", tags=["health"])
def health():
    return {"status": "ok"}
```

`include_router` options: `prefix="/api/v1"` (version your API), `tags=[...]`, `dependencies=[Depends(...)]` (apply to every route in the router).

### 10.5 Import errors after splitting

| Error | Cause | Fix |
|---|---|---|
| `ModuleNotFoundError: No module named 'app'` | Running from inside `app/`, or missing `__init__.py` | Run from project root: `fastapi dev app/main.py` |
| `ImportError: cannot import name 'X' from partially initialized module` | **Circular import** (A imports B, B imports A) | Move shared code to a third module (`utils.py`, `dependencies.py`) |
| Routes missing from `/docs` | Forgot `app.include_router(...)` | Add it in `main.py` |

---

## 11. Dependencies with Depends

### 11.1 The idea

> 🔌 **Analogy: `Depends` is a power socket in the wall.**
> Your appliance (route) just says "I need electricity" (a database connection, the current user, pagination settings). It doesn't build its own power plant. FastAPI plugs it in before the route runs, and you can swap the power source for testing (dependency overrides) without rewiring the appliance.

A **dependency** is just a function (or class). FastAPI calls it for you, passes its result into your route, and handles its own parameters (query, headers, other dependencies) too.

```python
from typing import Annotated
from fastapi import Depends

def get_db():
    return client[settings.mongo_db]

@router.get("/{note_id}")
def get_note(note_id: str, db: Annotated[Database, Depends(get_db)]):
    ...
```

### 11.2 Why bother

| Benefit | Example |
|---|---|
| Reuse | Pagination logic written once, used by every list endpoint |
| Less repetition | "Load note or 404" in one place |
| Security | `get_current_user` protects any route that asks for it |
| Testing | Replace the real DB/user with a fake via `app.dependency_overrides` |
| Docs | Query params inside dependencies show up in `/docs` automatically |

### 11.3 Type aliases with `Annotated`

Write the dependency once, give it a short name, reuse everywhere:

`app/dependencies.py`:

```python
from typing import Annotated

from fastapi import Depends, HTTPException, Query, status
from pymongo.database import Database

from app.database import get_db
from app.utils import to_object_id

DbDep = Annotated[Database, Depends(get_db)]


def pagination(
    skip: Annotated[int, Query(ge=0, description="Items to skip")] = 0,
    limit: Annotated[int, Query(ge=1, le=100, description="Max items to return")] = 10,
) -> dict:
    return {"skip": skip, "limit": limit}


PageDep = Annotated[dict, Depends(pagination)]


def get_note_or_404(note_id: str, db: DbDep) -> dict:
    """Dependency that loads the note from the path's {note_id} or raises 404."""
    doc = db.notes.find_one({"_id": to_object_id(note_id)})
    if doc is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail=f"Note {note_id} not found")
    return doc


NoteDep = Annotated[dict, Depends(get_note_or_404)]
```

Routes become short and readable:

```python
from app.dependencies import DbDep, NoteDep, PageDep
from app.utils import serialize


@router.get("", response_model=NotePage)
def list_notes(db: DbDep, page: PageDep, tag: str | None = None):
    query = {"tags": tag} if tag else {}
    cursor = db.notes.find(query).sort("updated_at", -1).skip(page["skip"]).limit(page["limit"])
    return {"total": db.notes.count_documents(query), **page, "items": [serialize(d) for d in cursor]}


@router.get("/{note_id}", response_model=NoteOut)
def get_note(note: NoteDep):          # loading + 404 handled by the dependency
    return serialize(note)
```

### 11.4 Kinds of dependencies

| Kind | Example | Use for |
|---|---|---|
| Plain function | `def pagination(...)` | Shared params, lookups |
| Dependency using another dependency | `get_note_or_404` uses `get_db` | Building blocks (FastAPI resolves the chain) |
| Class | `Depends(Pagination)` where `Pagination` has an `__init__` with params | Grouped params with attributes |
| `yield` dependency | Open → `yield` → clean up | DB sessions, files, timing |
| Router-level | `APIRouter(dependencies=[Depends(verify_key)])` | Protect a whole router |
| App-level | `FastAPI(dependencies=[...])` | Apply to every route |

Dependency with `yield` (setup + teardown):

```python
import logging
import time

logger = logging.getLogger("notes_api")

def timed_operation():
    start = time.perf_counter()
    yield                                            # the route runs here
    logger.info("Route took %.1f ms", (time.perf_counter() - start) * 1000)
```

FastAPI **caches** a dependency per request: if `get_db` is needed by three different dependencies in the same request, it's called once.

### 11.5 Overriding dependencies (for tests)

```python
def fake_user():
    return {"id": "test-user", "email": "test@example.com"}

app.dependency_overrides[get_current_user] = fake_user   # every route now sees fake_user
app.dependency_overrides.clear()                          # undo
```

Override the **original function object** you passed to `Depends`, not the `Annotated` alias.

### 11.6 Depends errors

| Mistake | Effect | Fix |
|---|---|---|
| `Depends(get_db())` (with brackets) | Calls the function once at import time and hands FastAPI the result instead of the function; usually crashes or behaves strangely | `Depends(get_db)` (no brackets) |
| Dependency param without type/default | FastAPI treats it as a required query param, shows in `/docs` | Add proper type hints |
| Overriding the alias instead of the function | Override silently doesn't work | Override `get_db`, not `DbDep` |

---

## 12. Authentication: Hashing, Register/Login, JWT

### 12.1 The big picture

| Term | Question it answers | Analogy |
|---|---|---|
| **Authentication** | *Who* are you? | Showing your ID at the cinema ticket counter |
| **Authorization** | *What* are you allowed to do? | Your ticket only lets you into Screen 3 |
| **Password hashing** | How do we store passwords safely? | A blender (see below) |
| **JWT** | How do you prove who you are on every request? | A cinema wristband |
| **OAuth2PasswordBearer** | Where does FastAPI look for the token? | The guard checking wrists at each screen door |

The flow:

```text
1. POST /auth/register  {email, password}        → user saved with a HASHED password
2. POST /auth/login     form: username, password → server checks hash, returns a JWT
3. GET  /notes          header: Authorization: Bearer <JWT>
                        → server verifies JWT signature + expiry → knows who you are
```

### 12.2 Password hashing

> 🥤 **Analogy: Hashing is a blender.**
> Put strawberries in, get a smoothie. You can't turn the smoothie back into strawberries. To check a login, you blend the password they typed and see if it makes **the same smoothie**. A "salt" is a random extra ingredient per user, so two people with the same password get different smoothies.

**Never store plain passwords.** Never "encrypt" them either (encryption can be reversed). Use a slow, salted password hash: **Argon2** (recommended) or bcrypt.

FastAPI's docs now use **`pwdlib`** (the older `passlib` is unmaintained):

```powershell
pip install "pwdlib[argon2]"
```

```python
from pwdlib import PasswordHash

password_hash = PasswordHash.recommended()     # Argon2 with good defaults

hashed = password_hash.hash("my-secret-pass")
# '$argon2id$v=19$m=65536,t=3,p=4$...'  (different every time, because of the salt)

password_hash.verify("my-secret-pass", hashed)   # True
password_hash.verify("wrong", hashed)            # False
```

### 12.3 JWT (JSON Web Token)

> 🎟️ **Analogy: A JWT is a cinema wristband.**
> At the ticket counter (login) you prove who you are once, and get a wristband. It's printed with your seat (user id) and a "valid until 9 pm" time (expiry), and stamped with the cinema's special hologram (signature). Guards at each screen (protected routes) don't call the ticket counter. They just check the hologram is genuine and the time hasn't passed. Anyone can *read* the wristband, but nobody can *forge* the hologram without the cinema's secret stamp (`SECRET_KEY`).

A JWT looks like `xxxxx.yyyyy.zzzzz`:

| Part | Contains | Secret? |
|---|---|---|
| Header | Algorithm (`HS256`) | No (just base64) |
| Payload | Claims: `sub` (user id), `exp` (expiry), anything else | **No, anyone can decode it.** Never put passwords or private data in it. |
| Signature | HMAC of header + payload using `SECRET_KEY` | Proves it wasn't changed |

Paste a token into jwt.io to see this for yourself.

Standard claims: `sub` (subject = user id), `exp` (expiry time), `iat` (issued at).

```powershell
pip install pyjwt
```

### 12.4 User schemas: `app/schemas/user.py`

```python
from datetime import datetime

from pydantic import BaseModel, EmailStr, Field


class UserCreate(BaseModel):
    email: EmailStr                                        # needs email-validator (in fastapi[standard])
    password: str = Field(min_length=8, max_length=128)


class UserOut(BaseModel):
    id: str
    email: EmailStr
    created_at: datetime                                   # note: NO password field


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
```

### 12.5 Security helpers: `app/core/security.py`

```python
from datetime import datetime, timedelta, timezone

import jwt
from pwdlib import PasswordHash

from app.config import settings

password_hash = PasswordHash.recommended()


def hash_password(password: str) -> str:
    return password_hash.hash(password)


def verify_password(plain: str, hashed: str) -> bool:
    return password_hash.verify(plain, hashed)


def create_access_token(subject: str) -> str:
    expire = datetime.now(timezone.utc) + timedelta(minutes=settings.access_token_expire_minutes)
    payload = {"sub": subject, "exp": expire}
    return jwt.encode(payload, settings.secret_key, algorithm=settings.algorithm)


def decode_access_token(token: str) -> dict:
    # Raises jwt.InvalidTokenError (incl. ExpiredSignatureError) if bad or expired
    return jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
```

### 12.6 `OAuth2PasswordBearer` and the current user: `app/dependencies.py`

> 💂 **Analogy:** `OAuth2PasswordBearer` is the guard at the door who looks for a wristband on your wrist (the `Authorization: Bearer <token>` header). No wristband → "401, go to the ticket counter at `/auth/login`". `get_current_user` is the guard checking the hologram and looking up your seat.

Add to `app/dependencies.py`:

```python
import jwt
from bson import ObjectId
from fastapi.security import OAuth2PasswordBearer

from app.core.security import decode_access_token

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")   # tells /docs where to log in


def get_current_user(token: Annotated[str, Depends(oauth2_scheme)], db: DbDep) -> dict:
    credentials_error = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = decode_access_token(token)
    except jwt.InvalidTokenError:
        raise credentials_error

    user_id = payload.get("sub")
    if not user_id or not ObjectId.is_valid(user_id):
        raise credentials_error

    user = db.users.find_one({"_id": ObjectId(user_id)})
    if user is None:
        raise credentials_error
    user["id"] = str(user.pop("_id"))
    return user


CurrentUser = Annotated[dict, Depends(get_current_user)]
```

### 12.7 Register, login, me: `app/routers/auth.py`

```python
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from pymongo.errors import DuplicateKeyError

from app.core.security import create_access_token, hash_password, verify_password
from app.dependencies import CurrentUser, DbDep
from app.schemas.user import Token, UserCreate, UserOut
from app.utils import now, serialize

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=UserOut, status_code=status.HTTP_201_CREATED)
def register(user: UserCreate, db: DbDep):
    doc = {
        "email": user.email.lower(),
        "hashed_password": hash_password(user.password),
        "created_at": now(),
    }
    try:
        db.users.insert_one(doc)                # unique index on email (see below)
    except DuplicateKeyError:
        raise HTTPException(status.HTTP_409_CONFLICT, detail="Email already registered")
    return serialize(doc)                       # UserOut drops hashed_password


@router.post("/login", response_model=Token)
def login(form: Annotated[OAuth2PasswordRequestForm, Depends()], db: DbDep):
    # OAuth2 form fields are called "username" and "password"; we use the email as username
    user = db.users.find_one({"email": form.username.lower()})
    if user is None or not verify_password(form.password, user["hashed_password"]):
        raise HTTPException(
            status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",          # same message for both cases
            headers={"WWW-Authenticate": "Bearer"},
        )
    return {"access_token": create_access_token(str(user["_id"])), "token_type": "bearer"}


@router.get("/me", response_model=UserOut)
def me(current_user: CurrentUser):
    return current_user
```

Create the unique index once (we do it at startup in Section 14's lifespan; for now, run once in a Python shell):

```python
from pymongo import MongoClient
MongoClient("mongodb://localhost:27017").notes_db.users.create_index("email", unique=True)
```

Include the router in `app/main.py`:

```python
from app.routers import auth, notes

app.include_router(auth.router)
app.include_router(notes.router)
```

Notes:
- `/auth/login` takes **form data** (`application/x-www-form-urlencoded`), not JSON. That's the OAuth2 standard and what Swagger's **Authorize** button sends.
- Form data needs `python-multipart` (already in `fastapi[standard]`).
- Same error message for "no such email" and "wrong password", so attackers can't discover which emails are registered.

### 12.8 Protecting the notes routes (each user sees only their notes)

Every note now stores an `owner_id`, and every query filters by it.

```python
from app.dependencies import CurrentUser, DbDep, PageDep


@router.post("", response_model=NoteOut, status_code=status.HTTP_201_CREATED)
def create_note(note: NoteCreate, db: DbDep, user: CurrentUser):
    doc = {**note.model_dump(), "owner_id": user["id"], "created_at": now(), "updated_at": now()}
    db.notes.insert_one(doc)
    return serialize(doc)


@router.get("", response_model=NotePage)
def list_notes(db: DbDep, user: CurrentUser, page: PageDep, tag: str | None = None):
    query: dict = {"owner_id": user["id"]}
    if tag:
        query["tags"] = tag
    cursor = db.notes.find(query).sort("updated_at", -1).skip(page["skip"]).limit(page["limit"])
    return {"total": db.notes.count_documents(query), **page, "items": [serialize(d) for d in cursor]}
```

And update `get_note_or_404` to filter by owner too:

```python
def get_note_or_404(note_id: str, db: DbDep, user: CurrentUser) -> dict:
    doc = db.notes.find_one({"_id": to_object_id(note_id), "owner_id": user["id"]})
    if doc is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail=f"Note {note_id} not found")
    return doc
```

(Define `get_current_user`/`CurrentUser` above `get_note_or_404` in the file.) Returning **404** instead of 403 for someone else's note avoids revealing that the note exists.

To protect a whole router at once: `APIRouter(prefix="/notes", dependencies=[Depends(get_current_user)])`. (But you still need the `user` parameter in routes that use the user's id.)

### 12.9 Logging in from Swagger

1. `POST /auth/register` → Try it out → `{"email": "me@example.com", "password": "supersecret"}`.
2. Click **Authorize** 🔓 (top right) → enter the email as *username* and the password → **Authorize** → Close.
3. Every protected route now sends `Authorization: Bearer <token>` automatically. The padlocks show closed 🔒.

From PowerShell:

```powershell
$login = Invoke-RestMethod -Method Post -Uri http://127.0.0.1:8000/auth/login `
  -ContentType "application/x-www-form-urlencoded" `
  -Body "username=me@example.com&password=supersecret"

$headers = @{ Authorization = "Bearer $($login.access_token)" }
Invoke-RestMethod http://127.0.0.1:8000/notes -Headers $headers
```

### 12.10 401 vs 403 and auth errors

| Code | Meaning | Analogy |
|---|---|---|
| **401 Unauthorized** | We don't know who you are (no token, bad token, expired token) | No wristband, or a fake/expired one |
| **403 Forbidden** | We know who you are, but you're not allowed | Valid wristband, but for a different screen |

| What you see | Cause | Fix |
|---|---|---|
| `401 {"detail": "Not authenticated"}` | No `Authorization` header sent | Click **Authorize** / add the header |
| `401 Could not validate credentials` | Token expired, tampered, or signed with another `SECRET_KEY` | Log in again; keep `SECRET_KEY` stable |
| All tokens die after a restart | `SECRET_KEY` generated randomly at startup | Put a fixed key in `.env` |
| `422` on `/auth/login` with `missing username` | Sent JSON instead of form data | Send form fields `username` + `password` |
| `422 value is not a valid email address` | `EmailStr` rejected it | Use a real-looking email |
| `409 Email already registered` | Unique index caught a duplicate | Use another email / log in |
| `Form data requires "python-multipart" to be installed` | Missing package | `pip install python-multipart` |
| `jwt.exceptions.InvalidAlgorithmError` / decode fails | `algorithms=` mismatch | Use the same `HS256` for encode and decode |

Security checklist: long random `SECRET_KEY` from `.env`; short token expiry (15–60 min); HTTPS in production; never log tokens or passwords; never return `hashed_password`.

---

## 13. Middleware, CORS, Error Handlers, Logging

### 13.1 Middleware

> 🛂 **Analogy: Middleware is airport security.**
> *Every* passenger (request) passes through it on the way in, and *every* response passes back through on the way out. It can check, stamp, time, or turn people away, without each gate (route) needing to do it.

```text
Request  → [Middleware 1] → [Middleware 2] → Route
Response ← [Middleware 1] ← [Middleware 2] ← Route
```

A timing + logging middleware in `app/main.py`:

```python
import logging
import time

from fastapi import FastAPI, Request

logger = logging.getLogger("notes_api")

app = FastAPI(title="Notes API")


@app.middleware("http")
async def log_requests(request: Request, call_next):
    start = time.perf_counter()
    response = await call_next(request)                 # pass the request on to the route
    elapsed_ms = (time.perf_counter() - start) * 1000
    response.headers["X-Process-Time-ms"] = f"{elapsed_ms:.1f}"
    logger.info("%s %s -> %s (%.1f ms)", request.method, request.url.path,
                response.status_code, elapsed_ms)
    return response
```

| Middleware vs Dependency | Middleware | Dependency |
|---|---|---|
| Runs for | Every request (incl. 404s and `/docs`) | Only routes that declare it |
| Sees the response | ✅ | ❌ (only with `yield`, partly) |
| Good for | Logging, timing, headers, CORS, request IDs | Auth, DB access, shared params |
| Shows in `/docs` | ❌ | ✅ (its params do) |

Order: the middleware added **last** runs **first** (outermost).

### 13.2 CORS

> 📋 **Analogy: CORS is a guest list kept by the browser.**
> A web page from `localhost:3000` (your React app) wants to call your API on `localhost:8000`. The **browser** asks the API "is localhost:3000 on your guest list?" If the API's answer doesn't include it, the browser blocks the response.

Key facts:
- CORS is enforced by **browsers only**. Swagger, PowerShell, Postman, Python scripts and tests are **not** affected.
- Different port = different origin. `http://localhost:3000` ≠ `http://localhost:8000` ≠ `http://127.0.0.1:3000`.

```python
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,     # e.g. ["http://localhost:3000"]
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],                     # includes Authorization
)
```

| Setting | Meaning |
|---|---|
| `allow_origins` | Exact list of allowed sites (scheme + host + port, no trailing slash) |
| `allow_origin_regex` | Pattern, e.g. `r"https://.*\.vercel\.app"` |
| `allow_methods` | Allowed HTTP methods |
| `allow_headers` | Allowed request headers |
| `allow_credentials` | Allow cookies/auth headers. **Can't** be combined with `allow_origins=["*"]` |

Typical browser console error:

```text
Access to fetch at 'http://localhost:8000/notes' from origin 'http://localhost:5173'
has been blocked by CORS policy: No 'Access-Control-Allow-Origin' header is present...
```

Fix: add `http://localhost:5173` to `CORS_ORIGINS`. Note: if your route crashes with a 500, the browser may *also* show a CORS error, so check the server terminal too.

### 13.3 Custom error handlers

> 🧾 **Analogy: An exception handler is the complaints desk.**
> Whatever goes wrong in the building, complaints are answered with the same official form, so customers (frontends) always know what shape the reply will have.

`app/main.py`:

```python
from fastapi import Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse


# 1. Your own exception type for business errors
class NoteLimitReached(Exception):
    def __init__(self, limit: int):
        self.limit = limit


@app.exception_handler(NoteLimitReached)
async def note_limit_handler(request: Request, exc: NoteLimitReached):
    return JSONResponse(
        status_code=status.HTTP_403_FORBIDDEN,
        content={"error": "note_limit_reached", "detail": f"Free plan allows {exc.limit} notes"},
    )


# 2. Reshape FastAPI's 422 validation errors into a simpler format
@app.exception_handler(RequestValidationError)
async def validation_handler(request: Request, exc: RequestValidationError):
    errors = [
        {"field": ".".join(str(p) for p in e["loc"][1:]), "message": e["msg"], "type": e["type"]}
        for e in exc.errors()
    ]
    return JSONResponse(status_code=422, content={"error": "validation_error", "errors": errors})


# 3. Catch-all for unexpected crashes: log the details, hide them from the client
@app.exception_handler(Exception)
async def unhandled_handler(request: Request, exc: Exception):
    logger.exception("Unhandled error on %s %s", request.method, request.url.path)
    return JSONResponse(status_code=500, content={"error": "internal_error", "detail": "Something went wrong"})
```

Raise it anywhere: `raise NoteLimitReached(limit=100)`.

The reshaped 422 now looks like:

```json
{ "error": "validation_error",
  "errors": [{ "field": "title", "message": "String should have at least 1 character", "type": "string_too_short" }] }
```

If you change the 422 shape, remember your frontend and tests must expect the new shape. Many teams keep FastAPI's default.

### 13.4 Logging

> 📓 **Analogy: Logs are the ship's logbook.** When something goes wrong at 3 am, you read the logbook to find out what happened. `print()` is shouting into the wind: no time, no level, can't be switched off.

Configure once at startup (`app/main.py`, before creating `app`):

```python
import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
)
logger = logging.getLogger("notes_api")
```

Use it anywhere:

```python
logger = logging.getLogger("notes_api")

logger.debug("Query: %s", query)                  # detailed, usually hidden
logger.info("Note %s created by %s", note_id, user_id)
logger.warning("Slow query: %.0f ms", elapsed)
logger.error("Could not save attachment")
logger.exception("Crash!")                        # inside except: logs the full traceback
```

| Level | Use for |
|---|---|
| `DEBUG` | Detailed info for debugging |
| `INFO` | Normal events (startup, note created) |
| `WARNING` | Something odd but handled |
| `ERROR` | Something failed |
| `CRITICAL` | App can't continue |

Tips:
- Use `%s` placeholders (`logger.info("id=%s", x)`), not f-strings. Formatting only happens if the message is actually logged.
- Never log passwords, tokens, or full request bodies with personal data.
- Uvicorn has its own loggers (`uvicorn.error`, `uvicorn.access`); `fastapi dev` shows them in the terminal.
- In production, log to stdout and let Docker/your host collect it.

---

## 14. Async: async def, Async MongoDB, BackgroundTasks, Lifespan

### 14.1 Sync vs async

> 🧑‍🍳 **Analogy: One waiter, many tables.**
> A **sync** waiter takes your order, walks to the kitchen, and *stands there* until your food is cooked. Other tables wait. An **async** waiter takes your order, hands it to the kitchen, and *serves other tables while the food cooks* (`await`). When the food's ready, they come back for it. The waiter is the **event loop**; `await` means "I'm waiting on something slow, go help someone else meanwhile".

Async helps when your code spends time **waiting** (database, HTTP calls to other APIs, LLM APIs, file/network I/O). It does **not** make CPU-heavy work (pandas crunching, model inference on CPU) faster.

### 14.2 `def` vs `async def` in FastAPI

| | `def` route | `async def` route |
|---|---|---|
| Where FastAPI runs it | In a **thread pool** (separate threads) | Directly on the **event loop** |
| Can use `await` | ❌ | ✅ |
| Use with | Blocking libraries: sync `MongoClient`, `requests`, `pandas`, most SDKs | Async libraries: `AsyncMongoClient`, `httpx.AsyncClient`, async OpenAI/Anthropic clients |
| If you call something blocking | Fine: only that thread waits | ❌ **Whole server freezes** for everyone until it finishes |
| Concurrency limit | Thread pool size (~40 by default) | Thousands of waiting requests |

**Golden rule:**
- Using an `await`-able library → `async def`.
- Using a blocking library → plain `def`.
- Not sure → `def` is the safer choice.

Mistakes that freeze an `async def` route: `time.sleep(5)` (use `await asyncio.sleep(5)`), `requests.get(...)` (use `httpx.AsyncClient`), sync `MongoClient` calls (use `AsyncMongoClient`).

Need a blocking function inside `async def`? Push it to a thread:

```python
from starlette.concurrency import run_in_threadpool

result = await run_in_threadpool(heavy_blocking_function, arg1, arg2)
```

### 14.3 Lifespan: opening and closing the restaurant

> 🏪 **Analogy: Lifespan is the opening and closing routine.**
> Before the first customer: unlock doors, turn on ovens (connect to MongoDB, create indexes, load an ML model). After the last customer: switch off ovens, lock up (close connections). Code **before `yield`** runs at startup, code **after `yield`** at shutdown.

`@app.on_event("startup")` is the old, deprecated way. Use `lifespan`.

### 14.4 Async MongoDB with PyMongo's `AsyncMongoClient`

Same driver, async API. Most methods become `await`-able:

| Sync (`MongoClient`) | Async (`AsyncMongoClient`) |
|---|---|
| `doc = notes.find_one(q)` | `doc = await notes.find_one(q)` |
| `notes.insert_one(doc)` | `await notes.insert_one(doc)` |
| `notes.count_documents(q)` | `await notes.count_documents(q)` |
| `for d in notes.find(q):` | `async for d in notes.find(q):` |
| `list(notes.find(q))` | `await notes.find(q).to_list()` |
| `client.close()` | `await client.close()` |

`find()` itself is **not** awaited: it returns a cursor immediately. You await when you *read* from it.

### 14.5 Final async version of the project

`app/database.py`:

```python
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from pymongo import AsyncMongoClient
from pymongo.asynchronous.database import AsyncDatabase

from app.config import settings

logger = logging.getLogger("notes_api")


@asynccontextmanager
async def lifespan(app: FastAPI):
    # ---- startup ----
    client = AsyncMongoClient(settings.mongo_url, serverSelectionTimeoutMS=5000, tz_aware=True)
    db = client[settings.mongo_db]
    await client.admin.command("ping")                                  # fail fast if Mongo is down
    await db.users.create_index("email", unique=True)
    await db.notes.create_index([("owner_id", 1), ("updated_at", -1)])
    app.state.db = db
    logger.info("Connected to MongoDB database '%s'", settings.mongo_db)

    yield                                                               # app runs here

    # ---- shutdown ----
    await client.close()
    logger.info("MongoDB connection closed")


def get_db(request: Request) -> AsyncDatabase:
    return request.app.state.db
```

`app/dependencies.py`:

```python
from typing import Annotated

import jwt
from bson import ObjectId
from fastapi import Depends, HTTPException, Query, status
from fastapi.security import OAuth2PasswordBearer
from pymongo.asynchronous.database import AsyncDatabase

from app.core.security import decode_access_token
from app.database import get_db
from app.utils import to_object_id

DbDep = Annotated[AsyncDatabase, Depends(get_db)]
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


def pagination(
    skip: Annotated[int, Query(ge=0)] = 0,
    limit: Annotated[int, Query(ge=1, le=100)] = 10,
) -> dict:
    return {"skip": skip, "limit": limit}


PageDep = Annotated[dict, Depends(pagination)]


async def get_current_user(token: Annotated[str, Depends(oauth2_scheme)], db: DbDep) -> dict:
    credentials_error = HTTPException(
        status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = decode_access_token(token)
    except jwt.InvalidTokenError:
        raise credentials_error
    user_id = payload.get("sub")
    if not user_id or not ObjectId.is_valid(user_id):
        raise credentials_error
    user = await db.users.find_one({"_id": ObjectId(user_id)})
    if user is None:
        raise credentials_error
    user["id"] = str(user.pop("_id"))
    return user


CurrentUser = Annotated[dict, Depends(get_current_user)]


async def get_note_or_404(note_id: str, db: DbDep, user: CurrentUser) -> dict:
    doc = await db.notes.find_one({"_id": to_object_id(note_id), "owner_id": user["id"]})
    if doc is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail=f"Note {note_id} not found")
    return doc


NoteDep = Annotated[dict, Depends(get_note_or_404)]
```

`app/routers/notes.py`:

```python
import logging
import re
from typing import Annotated

from fastapi import APIRouter, BackgroundTasks, HTTPException, Query, Response, status
from pymongo import ReturnDocument

from app.dependencies import CurrentUser, DbDep, NoteDep, PageDep
from app.schemas.note import NoteCreate, NoteOut, NotePage, NoteUpdate
from app.utils import now, serialize

logger = logging.getLogger("notes_api")
router = APIRouter(prefix="/notes", tags=["notes"])


async def record_activity(db, user_id: str, action: str, note_id: str) -> None:
    """Runs AFTER the response is sent (BackgroundTasks)."""
    await db.activity.insert_one(
        {"user_id": user_id, "action": action, "note_id": note_id, "at": now()}
    )


@router.post("", response_model=NoteOut, status_code=status.HTTP_201_CREATED)
async def create_note(note: NoteCreate, db: DbDep, user: CurrentUser, background_tasks: BackgroundTasks):
    doc = {**note.model_dump(), "owner_id": user["id"], "created_at": now(), "updated_at": now()}
    await db.notes.insert_one(doc)
    note_out = serialize(doc)
    background_tasks.add_task(record_activity, db, user["id"], "created", note_out["id"])
    return note_out


@router.get("", response_model=NotePage)
async def list_notes(
    db: DbDep,
    user: CurrentUser,
    page: PageDep,
    q: Annotated[str | None, Query(max_length=100)] = None,
    tag: str | None = None,
    pinned: bool | None = None,
):
    query: dict = {"owner_id": user["id"]}
    if q:
        pattern = {"$regex": re.escape(q), "$options": "i"}
        query["$or"] = [{"title": pattern}, {"content": pattern}]
    if tag:
        query["tags"] = tag
    if pinned is not None:
        query["pinned"] = pinned

    cursor = db.notes.find(query).sort("updated_at", -1).skip(page["skip"]).limit(page["limit"])
    items = [serialize(d) async for d in cursor]
    total = await db.notes.count_documents(query)
    return {"total": total, **page, "items": items}


@router.get("/{note_id}", response_model=NoteOut)
async def get_note(note: NoteDep):
    return serialize(note)


@router.put("/{note_id}", response_model=NoteOut)
async def replace_note(note: NoteCreate, existing: NoteDep, db: DbDep):
    new_doc = {
        **note.model_dump(),
        "owner_id": existing["owner_id"],
        "attachments": existing.get("attachments", []),
        "created_at": existing["created_at"],
        "updated_at": now(),
    }
    await db.notes.replace_one({"_id": existing["_id"]}, new_doc)
    new_doc["_id"] = existing["_id"]
    return serialize(new_doc)


@router.patch("/{note_id}", response_model=NoteOut)
async def update_note(changes_in: NoteUpdate, existing: NoteDep, db: DbDep):
    changes = {k: v for k, v in changes_in.model_dump(exclude_unset=True).items() if v is not None}
    if not changes:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, detail="No fields to update")
    changes["updated_at"] = now()
    doc = await db.notes.find_one_and_update(
        {"_id": existing["_id"]}, {"$set": changes}, return_document=ReturnDocument.AFTER
    )
    return serialize(doc)


@router.delete("/{note_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_note(existing: NoteDep, db: DbDep, user: CurrentUser, background_tasks: BackgroundTasks):
    await db.notes.delete_one({"_id": existing["_id"]})
    background_tasks.add_task(record_activity, db, user["id"], "deleted", str(existing["_id"]))
    return Response(status_code=status.HTTP_204_NO_CONTENT)
```

`app/routers/auth.py` (async version):

```python
import logging
from typing import Annotated

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from pymongo.errors import DuplicateKeyError

from app.core.security import create_access_token, hash_password, verify_password
from app.dependencies import CurrentUser, DbDep
from app.schemas.user import Token, UserCreate, UserOut
from app.utils import now, serialize

logger = logging.getLogger("notes_api")
router = APIRouter(prefix="/auth", tags=["auth"])


def send_welcome_email(email: str) -> None:
    """Pretend email sender. A plain def background task runs in a thread,
    so a blocking call (e.g. smtplib or requests to an email API) is OK here."""
    logger.info("Welcome email sent to %s", email)


@router.post("/register", response_model=UserOut, status_code=status.HTTP_201_CREATED)
async def register(user: UserCreate, db: DbDep, background_tasks: BackgroundTasks):
    doc = {"email": user.email.lower(), "hashed_password": hash_password(user.password), "created_at": now()}
    try:
        await db.users.insert_one(doc)
    except DuplicateKeyError:
        raise HTTPException(status.HTTP_409_CONFLICT, detail="Email already registered")
    background_tasks.add_task(send_welcome_email, doc["email"])
    return serialize(doc)


@router.post("/login", response_model=Token)
async def login(form: Annotated[OAuth2PasswordRequestForm, Depends()], db: DbDep):
    user = await db.users.find_one({"email": form.username.lower()})
    if user is None or not verify_password(form.password, user["hashed_password"]):
        raise HTTPException(
            status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return {"access_token": create_access_token(str(user["_id"])), "token_type": "bearer"}


@router.get("/me", response_model=UserOut)
async def me(current_user: CurrentUser):
    return current_user
```

(Argon2 hashing is deliberately slow CPU work, ~tens of ms. For a learning project calling it inside `async def` is fine; under heavy load wrap it with `run_in_threadpool`.)

`app/main.py` (final):

```python
import logging
import time

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.database import lifespan
from app.dependencies import DbDep
from app.routers import auth, notes

logging.basicConfig(level=logging.INFO, format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s")
logger = logging.getLogger("notes_api")

app = FastAPI(title=settings.app_name, version="1.0.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def log_requests(request: Request, call_next):
    start = time.perf_counter()
    response = await call_next(request)
    elapsed_ms = (time.perf_counter() - start) * 1000
    response.headers["X-Process-Time-ms"] = f"{elapsed_ms:.1f}"
    logger.info("%s %s -> %s (%.1f ms)", request.method, request.url.path, response.status_code, elapsed_ms)
    return response


app.include_router(auth.router)
app.include_router(notes.router)


@app.get("/health", tags=["health"])
async def health(db: DbDep):
    await db.command("ping")
    return {"status": "ok", "database": "ok"}
```

(Add the custom exception handlers from Section 13.3 here too if you want them.)

### 14.6 BackgroundTasks

> 📧 **Analogy: "Your receipt will be emailed to you."**
> The shop hands you your purchase **right away** and sends the receipt afterwards. The customer doesn't wait for the email to be sent.

```python
from fastapi import BackgroundTasks

@router.post("/register")
async def register(..., background_tasks: BackgroundTasks):
    ...
    background_tasks.add_task(send_welcome_email, email)   # function, then its arguments
    return user                                            # response goes out first, then the task runs
```

| Good for | Not good for |
|---|---|
| Sending emails/notifications | Long jobs (minutes/hours) |
| Writing audit/activity logs | Jobs that must survive a server restart |
| Small cleanup tasks | Jobs that need retries or scheduling |

For heavy/long jobs (embedding thousands of documents for RAG, video processing) use a real task queue: **Celery**, **RQ**, **Dramatiq**, or **ARQ** with Redis.

Background task functions can be `def` (run in a thread) or `async def` (run on the event loop; same no-blocking rule applies). If a background task raises, the client never knows (they already got their response), so log errors inside it.

### 14.7 Async errors

| Error | Meaning | Fix |
|---|---|---|
| `RuntimeWarning: coroutine '...' was never awaited` | Called an async function without `await` | Add `await` |
| `TypeError: 'coroutine' object is not subscriptable` | `doc = db.notes.find_one(...)` then `doc["title"]` without `await` | `doc = await db.notes.find_one(...)` |
| `TypeError: 'AsyncCursor' object is not iterable` | Used `for` on an async cursor | `async for`, or `await cursor.to_list()` |
| `TypeError: object dict can't be used in 'await' expression` | Awaited something that isn't async (e.g. sync client) | Remove `await` or use the async client |
| `SyntaxError: 'await' outside async function` | `await` inside a `def` | Make it `async def` |
| Whole server hangs during one request | Blocking call inside `async def` | Use async library, `run_in_threadpool`, or make the route `def` |
| `RuntimeError: ... attached to a different loop` | Async client created on one event loop, used on another (e.g. created at import time, or reused across tests) | Create the client in `lifespan` |
| `AttributeError: 'State' object has no attribute 'db'` | Lifespan didn't run (e.g. `TestClient(app)` without `with`) | Pass `lifespan=` to `FastAPI(...)`; use `with TestClient(app)` |

---

## 15. File Uploads and Streaming Responses

### 15.1 UploadFile

> 📦 **Analogy: `UploadFile` is a parcel arriving at reception.**
> Reception (FastAPI) receives it and keeps it in a small cupboard (memory); if it's too big, in the storeroom (a temp file on disk). You get a slip with the label (`filename`), the type (`content_type`), and a handle to open the parcel (`await file.read()`).

Uploads use `multipart/form-data` (not JSON), which needs `python-multipart` (in `fastapi[standard]`).

| Attribute / method | Meaning |
|---|---|
| `file.filename` | Original name from the user's computer (**don't trust it**) |
| `file.content_type` | e.g. `image/png`, `application/pdf` (sent by the client, also not 100% trustworthy) |
| `file.size` | Size in bytes |
| `await file.read(n)` | Read up to `n` bytes (all if no `n`) |
| `await file.seek(0)` | Go back to the start |
| `file.file` | The underlying Python file object (for sync code) |

`UploadFile` vs `bytes`:

| | `file: UploadFile` | `file: Annotated[bytes, File()]` |
|---|---|---|
| Storage | Memory, then spills to disk when large | Whole file in memory |
| Big files | ✅ | ❌ (memory blowup) |
| Gives you filename/type | ✅ | ❌ |

### 15.2 Attachments for notes

Add an attachments list to the output schema in `app/schemas/note.py`:

```python
class Attachment(BaseModel):
    id: str              # stored file name on disk
    filename: str        # original name, for display/download
    content_type: str
    size: int


class NoteOut(NoteBase):
    id: str
    attachments: list[Attachment] = Field(default_factory=list)
    created_at: datetime
    updated_at: datetime
```

Add to `app/routers/notes.py`:

```python
import uuid
from pathlib import Path

from fastapi import UploadFile
from fastapi.responses import FileResponse

UPLOAD_DIR = Path("uploads")
MAX_BYTES = 5 * 1024 * 1024                          # 5 MB
ALLOWED_TYPES = {"image/png", "image/jpeg", "application/pdf", "text/plain"}


@router.post("/{note_id}/attachments", response_model=NoteOut, status_code=status.HTTP_201_CREATED)
async def upload_attachment(note: NoteDep, db: DbDep, file: UploadFile):
    if file.content_type not in ALLOWED_TYPES:
        raise HTTPException(status.HTTP_415_UNSUPPORTED_MEDIA_TYPE, detail=f"Type {file.content_type} not allowed")

    UPLOAD_DIR.mkdir(exist_ok=True)
    stored_name = f"{uuid.uuid4().hex}{Path(file.filename or '').suffix.lower()}"   # never use the raw filename
    dest = UPLOAD_DIR / stored_name

    size, too_big = 0, False
    with dest.open("wb") as out:
        while chunk := await file.read(1024 * 1024):   # read 1 MB at a time, never all at once
            size += len(chunk)
            if size > MAX_BYTES:
                too_big = True
                break
            out.write(chunk)
    if too_big:
        dest.unlink(missing_ok=True)                    # file is closed now (needed on Windows)
        raise HTTPException(status.HTTP_413_CONTENT_TOO_LARGE, detail="File larger than 5 MB")

    attachment = {"id": stored_name, "filename": file.filename, "content_type": file.content_type, "size": size}
    doc = await db.notes.find_one_and_update(
        {"_id": note["_id"]},
        {"$push": {"attachments": attachment}, "$set": {"updated_at": now()}},
        return_document=ReturnDocument.AFTER,
    )
    return serialize(doc)


@router.get("/{note_id}/attachments/{attachment_id}")
async def download_attachment(note: NoteDep, attachment_id: str):
    att = next((a for a in note.get("attachments", []) if a["id"] == attachment_id), None)
    if att is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Attachment not found")
    return FileResponse(UPLOAD_DIR / att["id"], media_type=att["content_type"], filename=att["filename"])
```

Safety rules for uploads:
- Never save using `file.filename` directly. A name like `..\..\app\main.py` could overwrite your code (path traversal). Generate your own name (`uuid4`).
- Limit size and allowed types.
- Read in chunks, not `await file.read()` for big files.
- In production, store files in object storage (S3, Azure Blob, GCS) instead of the server's disk; the DB keeps only metadata.

Multiple files at once: `files: list[UploadFile]`. File + other fields in the same request: use `Form()` fields, not a JSON body (`title: Annotated[str, Form()]`), because a request can't be both multipart and JSON.

Test an upload from PowerShell (PowerShell 7+):

```powershell
Invoke-RestMethod -Method Post -Uri "http://127.0.0.1:8000/notes/<note_id>/attachments" `
  -Headers $headers -Form @{ file = Get-Item ".\receipt.pdf" }
```

Or with real curl: `curl.exe -H "Authorization: Bearer <token>" -F "file=@receipt.pdf" http://127.0.0.1:8000/notes/<note_id>/attachments`

### 15.3 StreamingResponse

> 🚰 **Analogy: Streaming is a tap, not a bucket.**
> A normal response fills a whole bucket and then hands it over (the full response is built in memory first). Streaming opens a tap: water (data) flows as it's produced. Think Netflix playing while still downloading, or ChatGPT typing its answer word by word.

Use it for: big exports, large files, live progress, and **LLM token streaming**.

**Export all notes as CSV** (add **above** the `/{note_id}` routes so `/notes/export` isn't treated as an id):

```python
import csv
import io

from fastapi.responses import StreamingResponse


@router.get("/export")
async def export_notes(db: DbDep, user: CurrentUser):
    async def generate_csv():
        buffer = io.StringIO()
        writer = csv.writer(buffer)

        def flush() -> str:
            data = buffer.getvalue()
            buffer.seek(0)
            buffer.truncate(0)
            return data

        yield "﻿"                                  # BOM so Excel on Windows shows UTF-8 correctly
        writer.writerow(["id", "title", "tags", "pinned", "updated_at"])
        yield flush()
        async for doc in db.notes.find({"owner_id": user["id"]}).sort("updated_at", -1):
            writer.writerow([str(doc["_id"]), doc["title"], ";".join(doc["tags"]),
                             doc["pinned"], doc["updated_at"].isoformat()])
            yield flush()                               # one row at a time, never the whole table in memory

    return StreamingResponse(
        generate_csv(),
        media_type="text/csv",
        headers={"Content-Disposition": 'attachment; filename="notes.csv"'},
    )
```

**Streaming text like an LLM** (word by word):

```python
import asyncio


@router.get("/{note_id}/summary-stream")
async def stream_summary(note: NoteDep):
    async def fake_llm():
        text = f"Summary of '{note['title']}': {note['content'][:200]}"
        for word in text.split():
            yield word + " "
            await asyncio.sleep(0.05)       # pretend we're waiting on the model

    return StreamingResponse(fake_llm(), media_type="text/plain")
```

Watch it stream: `curl.exe -N -H "Authorization: Bearer <token>" http://127.0.0.1:8000/notes/<id>/summary-stream` (`-N` turns off buffering). With a real LLM SDK, you'd `yield` each chunk from its async stream. For browsers, the common format is **Server-Sent Events** (`media_type="text/event-stream"`, each chunk formatted as `data: ...\n\n`).

| Response | Use when |
|---|---|
| `JSONResponse` (default) | Normal API data |
| `FileResponse` | Sending an existing file from disk |
| `StreamingResponse` | Generating data on the fly / big or live data |

### 15.4 Upload & streaming errors

| Error | Meaning | Fix |
|---|---|---|
| `Form data requires "python-multipart" to be installed` | Missing package | `pip install python-multipart` |
| `422 missing` for `file` | Sent JSON, or the form field isn't named `file` | Send `multipart/form-data` with field `file` |
| `413` / `415` | Your own size/type checks | Smaller file / allowed type |
| `PermissionError: [WinError 32] The process cannot access the file because it is being used by another process` | Deleting/moving a file that's still open (Windows locks open files) | Close the file first (`with` block ends), then delete |
| `/notes/export` returns 400 "not a valid id" | Route defined *after* `/{note_id}` | Move `/export` above it |
| Stream arrives all at once | Client/proxy buffering | `curl.exe -N`; disable proxy buffering (e.g. Nginx `X-Accel-Buffering: no`) |

---

## 16. Testing with pytest and TestClient

### 16.1 The idea

> 🕵️ **Analogy: `TestClient` is a mystery shopper.**
> It walks into your restaurant, places real orders (HTTP requests) and checks what comes back, but without opening the doors to the public (no real server, no network). **pytest** is the inspector who runs all the mystery shoppers and writes the report: ✅ passed / ❌ failed.

```powershell
pip install pytest          # httpx (needed by TestClient) comes with fastapi[standard]
```

### 16.2 Setup files

`pytest.ini` (project root):

```ini
[pytest]
pythonpath = .
testpaths = tests
```

`pythonpath = .` lets tests do `from app.main import app` when you run `pytest` from the project root.

`tests/conftest.py` (shared fixtures; pytest finds this file automatically):

```python
import os

# Must be set BEFORE importing the app, so settings pick them up
os.environ["MONGO_DB"] = "notes_test"                       # never test against your real data
os.environ.setdefault("SECRET_KEY", "test-secret-key-that-is-at-least-32-bytes")

import pytest
from fastapi.testclient import TestClient
from pymongo import MongoClient

from app.config import settings
from app.main import app


@pytest.fixture
def client():
    with TestClient(app) as c:            # "with" runs the lifespan → connects to MongoDB
        yield c
    with MongoClient(settings.mongo_url) as mongo:
        mongo.drop_database(settings.mongo_db)              # clean slate for the next test


def register_and_login(client, email: str, password: str = "password123") -> dict:
    client.post("/auth/register", json={"email": email, "password": password})
    r = client.post("/auth/login", data={"username": email, "password": password})   # form data!
    return {"Authorization": f"Bearer {r.json()['access_token']}"}


@pytest.fixture
def auth_headers(client):
    return register_and_login(client, "test@example.com")
```

> 🧪 **Fixture analogy:** A fixture is the test kitchen's prep station: before each test it sets out clean equipment (a client, a logged-in user), and cleans up after.

These tests talk to a real local MongoDB (database `notes_test`), so MongoDB must be running.

### 16.3 Tests: `tests/test_notes.py`

```python
import pytest

from tests.conftest import register_and_login


def test_health(client):
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json()["status"] == "ok"


def test_notes_require_login(client):
    r = client.get("/notes")
    assert r.status_code == 401
    assert r.json()["detail"] == "Not authenticated"


def test_create_and_get_note(client, auth_headers):
    r = client.post("/notes", json={"title": "Gym", "tags": ["health"]}, headers=auth_headers)
    assert r.status_code == 201
    note = r.json()
    assert note["title"] == "Gym"
    assert note["pinned"] is False

    r = client.get(f"/notes/{note['id']}", headers=auth_headers)
    assert r.status_code == 200
    assert r.json()["id"] == note["id"]


def test_empty_title_is_rejected(client, auth_headers):
    r = client.post("/notes", json={"title": ""}, headers=auth_headers)
    assert r.status_code == 422
    assert r.json()["detail"][0]["type"] == "string_too_short"


def test_broken_json_is_rejected(client, auth_headers):
    r = client.post(
        "/notes",
        content='{"title": "Gym",}',                          # trailing comma = invalid JSON
        headers={**auth_headers, "Content-Type": "application/json"},
    )
    assert r.status_code == 422
    assert r.json()["detail"][0]["type"] == "json_invalid"


@pytest.mark.parametrize(
    "note_id, expected_status",
    [
        ("not-an-id", 400),                    # bad format → our to_object_id() says 400
        ("6740a1f2c9e77b2a1d3f0a11", 404),     # valid format, doesn't exist → 404
    ],
)
def test_get_note_errors(client, auth_headers, note_id, expected_status):
    r = client.get(f"/notes/{note_id}", headers=auth_headers)
    assert r.status_code == expected_status


def test_patch_changes_only_sent_fields(client, auth_headers):
    note = client.post("/notes", json={"title": "Gym", "content": "Leg day"}, headers=auth_headers).json()
    r = client.patch(f"/notes/{note['id']}", json={"pinned": True}, headers=auth_headers)
    assert r.status_code == 200
    assert r.json()["pinned"] is True
    assert r.json()["content"] == "Leg day"                   # untouched


def test_delete_note(client, auth_headers):
    note = client.post("/notes", json={"title": "Temp"}, headers=auth_headers).json()
    assert client.delete(f"/notes/{note['id']}", headers=auth_headers).status_code == 204
    assert client.get(f"/notes/{note['id']}", headers=auth_headers).status_code == 404


def test_search_and_pagination(client, auth_headers):
    for i in range(15):
        client.post("/notes", json={"title": f"Note {i}", "tags": ["bulk"]}, headers=auth_headers)
    r = client.get("/notes", params={"tag": "bulk", "skip": 10, "limit": 10}, headers=auth_headers)
    body = r.json()
    assert body["total"] == 15
    assert len(body["items"]) == 5


def test_users_cannot_see_each_others_notes(client, auth_headers):
    note = client.post("/notes", json={"title": "Private"}, headers=auth_headers).json()
    other = register_and_login(client, "other@example.com")
    assert client.get(f"/notes/{note['id']}", headers=other).status_code == 404


def test_duplicate_email(client):
    body = {"email": "dup@example.com", "password": "password123"}
    assert client.post("/auth/register", json=body).status_code == 201
    assert client.post("/auth/register", json=body).status_code == 409
```

Add `tests/__init__.py` (empty) so `from tests.conftest import ...` works.

### 16.4 Overriding dependencies in tests

Skip the login step entirely by faking the current user:

```python
from app.dependencies import get_current_user
from app.main import app


def test_me_with_fake_user(client):
    app.dependency_overrides[get_current_user] = lambda: {
        "id": "fake-id", "email": "fake@example.com", "created_at": "2026-01-01T00:00:00Z",
    }
    try:
        r = client.get("/auth/me")
        assert r.json()["email"] == "fake@example.com"
    finally:
        app.dependency_overrides.clear()          # always undo, or other tests break
```

### 16.5 Running tests

```powershell
pytest                    # run everything
pytest -v                 # verbose: one line per test
pytest -x                 # stop at first failure
pytest -k patch           # only tests with "patch" in the name
pytest --lf               # re-run only last failures
pytest -s                 # show print() output
pip install pytest-cov
pytest --cov=app          # coverage report
```

In VS Code: Testing panel (flask icon) → Configure Python Tests → pytest → `tests` folder. Then run/debug tests with one click.

### 16.6 What to test

| Test type | Example |
|---|---|
| Happy path | Create → 201, get → 200 |
| Validation | Empty title → 422 `string_too_short` |
| Not found / bad id | 404 vs 400 |
| Auth | No token → 401; other user's note → 404 |
| Business rules | PATCH doesn't wipe fields; duplicate email → 409 |

### 16.7 Testing errors

| Error | Meaning | Fix |
|---|---|---|
| `ModuleNotFoundError: No module named 'app'` | Python can't find your package | Add `pythonpath = .` in `pytest.ini`, run from project root |
| `AttributeError: 'State' object has no attribute 'db'` | Used `TestClient(app)` without `with`, so lifespan didn't run | `with TestClient(app) as c:` |
| `ServerSelectionTimeoutError` in tests | MongoDB not running | Start MongoDB / run tests in Docker Compose |
| Tests pass alone, fail together | Shared state (leftover DB data, overrides not cleared) | Clean DB in fixture; `dependency_overrides.clear()` |
| `RuntimeError: ... different event loop` | Async client reused across TestClients | Create the client in `lifespan` (as in Section 14) |
| `InsecureKeyLengthWarning` from PyJWT | Test `SECRET_KEY` shorter than 32 bytes | Use a longer key |

---

## 17. Docker and docker-compose

### 17.1 Why Docker

> 📦 **Analogy: Docker is a shipping container for your app.**
> "Works on my machine" happens because your laptop has a specific Python, packages, and settings. A container packs the app **with** its own Python and packages into a sealed box that runs the same on your Windows laptop, your colleague's Mac, and a Linux server.

| Term | Meaning | Analogy |
|---|---|---|
| **Dockerfile** | Recipe for building an image | Recipe card |
| **Image** | Built, read-only package (app + Python + deps) | A frozen ready-meal |
| **Container** | A running instance of an image | The meal heated up and served |
| **Volume** | Storage that survives container restarts | A fridge outside the container |
| **docker-compose** | Runs several containers together | A combo meal: API + MongoDB in one order |

On Windows: install **Docker Desktop** (uses WSL 2; let the installer enable it). Check: `docker --version` and `docker compose version`.

### 17.2 Dockerfile

Save the requirements first:

```powershell
pip freeze > requirements.txt
```

(Or keep a short hand-written `requirements.txt`: `fastapi[standard]`, `pymongo`, `pydantic-settings`, `pyjwt`, `pwdlib[argon2]`, `pytest`.)

`Dockerfile` (project root):

```dockerfile
FROM python:3.12-slim

# Don't write .pyc files; show logs immediately
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /code

# Copy requirements first: Docker caches this layer, so code changes don't reinstall packages
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY ./app ./app

EXPOSE 8000
CMD ["fastapi", "run", "app/main.py", "--port", "8000"]
```

`.dockerignore` (keeps junk and secrets out of the image):

```text
.venv
__pycache__
*.pyc
.env
.git
.pytest_cache
uploads
tests
```

Build and run just the API:

```powershell
docker build -t notes-api .
docker run --rm -p 8000:8000 --env-file .env -e MONGO_URL=mongodb://host.docker.internal:27017 notes-api
```

- `-p 8000:8000` = "laptop port 8000 → container port 8000".
- Inside a container, `localhost` means **the container itself**, not your laptop. `host.docker.internal` reaches your Windows machine (where your MongoDB service runs).

### 17.3 docker-compose: API + MongoDB together

`docker-compose.yml`:

```yaml
services:
  api:
    build: .
    ports:
      - "8000:8000"
    env_file:
      - .env
    environment:
      MONGO_URL: mongodb://mongo:27017       # "mongo" = the service name below
    depends_on:
      - mongo
    volumes:
      - ./uploads:/code/uploads              # keep uploaded files on your laptop

  mongo:
    image: mongo:8
    ports:
      - "27018:27017"                        # 27018 on Windows, to avoid clashing with the local MongoDB service
    volumes:
      - mongo_data:/data/db                  # data survives "docker compose down"

volumes:
  mongo_data:
```

Connect **Compass** to the Docker MongoDB with `mongodb://localhost:27018`.

```powershell
docker compose up --build          # build + start, logs in the terminal (Ctrl+C to stop)
docker compose up -d               # start in background
docker compose logs -f api         # follow API logs
docker compose ps                  # what's running
docker compose exec api pytest     # run commands inside the api container
docker compose down                # stop and remove containers (data volume kept)
docker compose down -v             # ...and delete the data volume too ⚠️
```

Note: `environment:` overrides values from `env_file:`. That's how the same `.env` works for both local runs (`localhost`) and Compose (`mongo`).

To run the test suite in Docker, `tests` must be in the image; remove `tests` from `.dockerignore` and add `COPY ./tests ./tests` and `COPY pytest.ini .` to the Dockerfile.

### 17.4 Docker errors (Windows)

| Error | Meaning | Fix |
|---|---|---|
| `error during connect: ... The system cannot find the file specified` / `Cannot connect to the Docker daemon` | Docker Desktop isn't running | Start Docker Desktop, wait for "Engine running" |
| `WSL 2 installation is incomplete` | WSL 2 missing | Run `wsl --install` (admin PowerShell), restart |
| `Bind for 0.0.0.0:27017 failed: port is already allocated` | Local Windows MongoDB already uses 27017 | Map `27018:27017` (as above) or stop the local service |
| API can't reach Mongo (`localhost:27017 ... Connection refused`) | Used `localhost` inside a container | Use `mongodb://mongo:27017` (Compose) or `host.docker.internal` |
| `ValidationError ... secret_key Field required` | `.env` not passed to the container | `env_file: .env` / `--env-file .env` |
| Code changes not showing | Image not rebuilt | `docker compose up --build` |
| Container exits immediately | App crashed at startup | `docker compose logs api` |

---

## 18. Deployment Basics and GitHub Actions

### 18.1 What deployment means

> 🚚 **Analogy: Deployment is moving your food truck from your garage to the street.**
> In the garage (your laptop) only you can eat. On the street (a server with a public URL), anyone can. You need: the truck (your container), a parking spot (a host), a licence (HTTPS/domain), supplies delivered (a cloud database), and a way to restock without closing (CI/CD).

### 18.2 Development vs production

| | Development | Production |
|---|---|---|
| Command | `fastapi dev app/main.py` | `fastapi run app/main.py` (or Docker) |
| Auto-reload | On | **Off** |
| Host | `127.0.0.1` | `0.0.0.0` |
| Workers | 1 | Several (`--workers 4`) or several containers |
| Database | Local MongoDB | MongoDB Atlas (managed) or managed DB |
| Secrets | `.env` file | Host's environment variables / secret manager |
| HTTPS | No | **Yes** (platform or reverse proxy, e.g. Nginx/Caddy) |
| `/docs` | Open | Often disabled or protected |
| CORS | `localhost` origins | Only your real frontend domain |
| Logs | Terminal | Platform log viewer / log service |

### 18.3 Where to deploy

| Option | How it works | Good for |
|---|---|---|
| **PaaS** (Render, Railway, Fly.io, Koyeb) | Connect your GitHub repo or Dockerfile; they build and run it, give you HTTPS | Beginners, side projects |
| **Container services** (AWS App Runner/ECS, Google Cloud Run, Azure Container Apps) | Push an image; they run and scale it | Production on a big cloud |
| **Virtual machine** (EC2, Azure VM, DigitalOcean droplet) | You install Docker, run Compose, set up Nginx + HTTPS yourself | Learning servers, full control |

Database: create a free cluster on **MongoDB Atlas**, add a database user, allow your host's IP in **Network Access**, and set `MONGO_URL=mongodb+srv://...` as an environment variable on your host.

### 18.4 Production checklist

- [ ] All secrets come from environment variables; `.env` never committed (check `git status`).
- [ ] Strong `SECRET_KEY`, unique per environment.
- [ ] HTTPS only.
- [ ] `CORS_ORIGINS` lists only your real frontend(s).
- [ ] No `--reload`; use `fastapi run`.
- [ ] `/health` endpoint for the platform's health checks.
- [ ] Indexes created (lifespan does this).
- [ ] Logs go to stdout; errors aren't leaking stack traces to clients.
- [ ] Uploaded files go to object storage (container disks are usually wiped on redeploy).
- [ ] Tests pass in CI before deploying.

Behind a proxy/load balancer that terminates HTTPS, run with `fastapi run app/main.py --proxy-headers` so FastAPI sees the real scheme/client IP.

### 18.5 GitHub Actions (CI)

> 🤖 **Analogy: GitHub Actions is a robot assistant in your repo.**
> Every time you push, the robot gets a fresh computer, installs your app, starts a MongoDB, runs your tests, and puts a ✅ or ❌ next to your commit. Broken code gets caught before it's deployed.

Create `.github/workflows/ci.yml`:

```yaml
name: CI

on:
  push:
    branches: [main]
  pull_request:

jobs:
  test:
    runs-on: ubuntu-latest

    services:
      mongo:                         # a MongoDB container just for this job
        image: mongo:8
        ports:
          - 27017:27017

    env:
      MONGO_URL: mongodb://localhost:27017
      MONGO_DB: notes_test
      SECRET_KEY: ci-secret-key-that-is-at-least-32-bytes-long

    steps:
      - uses: actions/checkout@v4

      - uses: actions/setup-python@v5
        with:
          python-version: "3.12"
          cache: pip

      - name: Install dependencies
        run: pip install -r requirements.txt

      - name: Run tests
        run: pytest -v
```

Notes:
- The runner is Linux even though you develop on Windows. That's fine: Python code is portable. Watch for Windows-only paths like `C:\...` or `\` in code (use `pathlib.Path`).
- If `pip freeze` on Windows added Windows-only packages (e.g. `pywin32`), the Linux install fails. Prefer a hand-written `requirements.txt` with only what you import.
- Secrets for real deployments go in **GitHub → Settings → Secrets and variables → Actions**, used as `${{ secrets.MY_SECRET }}`. Never hard-code them in the YAML.

### 18.6 Adding a deploy step (CD)

A second job that builds and pushes a Docker image to GitHub's container registry (GHCR) after tests pass on `main`:

```yaml
  build-and-push:
    needs: test                                   # only if tests passed
    if: github.ref == 'refs/heads/main'
    runs-on: ubuntu-latest
    permissions:
      contents: read
      packages: write
    steps:
      - uses: actions/checkout@v4
      - uses: docker/login-action@v3
        with:
          registry: ghcr.io
          username: ${{ github.actor }}
          password: ${{ secrets.GITHUB_TOKEN }}
      - uses: docker/build-push-action@v6
        with:
          push: true
          tags: ghcr.io/${{ github.repository }}:latest
```

(Image names on GHCR must be lowercase; if your username has capitals, set the tag explicitly in lowercase.) Your host then pulls `ghcr.io/<you>/<repo>:latest`. Many PaaS platforms skip this and auto-deploy straight from your GitHub repo when `main` changes.

### 18.7 Deployment & CI errors

| Problem | Cause | Fix |
|---|---|---|
| Works locally, 502/503 on host | App listening on `127.0.0.1` or wrong port | `fastapi run` (binds `0.0.0.0`); use the port the host expects (often `$PORT`) |
| `ServerSelectionTimeoutError` with Atlas | Host IP not allowed in Atlas Network Access | Add the IP (or `0.0.0.0/0` for testing only) |
| CI: `ModuleNotFoundError` | Package missing from `requirements.txt` | Add it |
| CI: `secret_key Field required` | Env var not set in the workflow | Add it under `env:` |
| Uploaded files vanish after redeploy | Container disk is temporary | Use object storage |
| CORS errors only in production | Production frontend origin not in `CORS_ORIGINS` | Add the exact `https://...` origin |

---

## 19. Quick-Reference Cheat Sheet

### 19.1 Windows commands

```powershell
# venv
python -m venv .venv
.venv\Scripts\Activate.ps1                     # PowerShell (cmd: .venv\Scripts\activate.bat)
Set-ExecutionPolicy -Scope CurrentUser RemoteSigned   # if activation is blocked
deactivate

# packages
pip install "fastapi[standard]" pymongo pydantic-settings pyjwt "pwdlib[argon2]" pytest
pip freeze > requirements.txt
pip install -r requirements.txt

# run
fastapi dev app/main.py                        # dev, auto-reload, http://127.0.0.1:8000/docs
fastapi run app/main.py                        # production mode
uvicorn app.main:app --reload --port 8001      # alternative

# port busy
netstat -ano | findstr :8000
taskkill /PID <pid> /F

# MongoDB service
Get-Service MongoDB
net start MongoDB                              # admin PowerShell

# secret key
python -c "import secrets; print(secrets.token_hex(32))"

# tests
pytest -v
pytest -x -k patch

# docker
docker compose up --build
docker compose down
docker compose logs -f api
```

### 19.2 Analogies at a glance

| Concept | Analogy |
|---|---|
| API | Waiter between you and the kitchen |
| Route | A labelled counter (method + path) |
| Path param | House number |
| Query param | Extra options on an order ("extra cheese") |
| Request body | The letter inside the envelope |
| Pydantic model | Order slip with labelled boxes |
| Validation / 422 | Slip handed back: "box X is wrong" |
| `exclude_unset` | Only the boxes you actually ticked |
| `response_model` | Plating guide: only these items leave the kitchen |
| HTTPException | "Sorry, we're out of that dish" |
| PUT vs PATCH | Rewrite the page vs correction tape |
| Swagger `/docs` | Interactive menu with a "try it" button |
| MongoDB | Filing cabinet (db) → drawers (collections) → folders (documents) |
| ObjectId | Barcode sticker |
| Pagination | Pages of a book (skip / limit) |
| APIRouter | Store departments |
| `.env` + pydantic-settings | Locked drawer of secrets + the manager who reads it |
| `Depends` | Power socket |
| Password hashing | Blender (can't un-blend) |
| JWT | Cinema wristband with a hologram |
| OAuth2PasswordBearer | Guard checking wristbands |
| Middleware | Airport security (everyone passes, both ways) |
| CORS | Browser's guest list |
| Exception handler | Complaints desk with a standard form |
| Logging | Ship's logbook |
| async / await | One waiter serving many tables while food cooks |
| Lifespan | Opening and closing the restaurant |
| BackgroundTasks | "Receipt will be emailed to you" |
| UploadFile | Parcel at reception |
| StreamingResponse | A tap, not a bucket |
| TestClient | Mystery shopper |
| Docker | Shipping container |
| docker-compose | Combo meal (API + DB) |
| Deployment | Food truck from garage to street |
| GitHub Actions | Robot that checks every push |

### 19.3 Core imports

```python
from typing import Annotated
from fastapi import (FastAPI, APIRouter, Depends, HTTPException, status, Query, Path,
                     Body, Form, File, UploadFile, Request, Response, BackgroundTasks)
from fastapi.responses import JSONResponse, FileResponse, StreamingResponse
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError
from fastapi.testclient import TestClient
from pydantic import BaseModel, Field, EmailStr, ConfigDict, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict
from pymongo import MongoClient, AsyncMongoClient, ReturnDocument
from pymongo.errors import DuplicateKeyError
from bson import ObjectId
```

### 19.4 Route patterns

```python
@router.get("", response_model=NotePage)                                   # list
@router.get("/{note_id}", response_model=NoteOut)                          # one
@router.post("", response_model=NoteOut, status_code=201)                  # create
@router.put("/{note_id}", response_model=NoteOut)                          # replace
@router.patch("/{note_id}", response_model=NoteOut)                        # partial update
@router.delete("/{note_id}", status_code=204)                              # delete → return Response(status_code=204)

def f(note_id: str,                                       # path
      note: NoteCreate,                                   # JSON body
      db: DbDep,                                          # dependency
      user: CurrentUser,                                  # auth
      q: str | None = None,                               # optional query (defaults go last)
      limit: Annotated[int, Query(ge=1, le=100)] = 10): ...  # validated query
```

### 19.5 Pydantic

```python
class NoteCreate(BaseModel):
    title: str = Field(min_length=1, max_length=100)
    tags: list[str] = Field(default_factory=list)
    content: str | None = None

note.model_dump()                       # → dict
note.model_dump(exclude_unset=True)     # → only sent fields (PATCH)
note.model_dump(exclude_none=True)      # → drop None
note.model_dump_json()                  # → JSON string
NoteCreate.model_validate(data)         # dict → model
```

### 19.6 PyMongo (sync → async: add `await`, use `async for` / `.to_list()`)

```python
db.notes.insert_one(doc)                                        # .inserted_id
db.notes.find_one({"_id": ObjectId(id)})                        # dict | None
db.notes.find(q).sort("updated_at", -1).skip(s).limit(l)        # cursor
db.notes.count_documents(q)
db.notes.replace_one({"_id": oid}, new_doc)                     # whole doc
db.notes.update_one({"_id": oid}, {"$set": changes})            # some fields
db.notes.find_one_and_update(f, {"$set": c}, return_document=ReturnDocument.AFTER)
db.notes.delete_one({"_id": oid})                               # .deleted_count
db.users.create_index("email", unique=True)
{"title": {"$regex": re.escape(q), "$options": "i"}}            # case-insensitive search
doc["id"] = str(doc.pop("_id"))                                 # make JSON-safe
```

### 19.7 Auth in five lines

```python
password_hash = PasswordHash.recommended()                       # pwdlib
hashed = password_hash.hash(pw); password_hash.verify(pw, hashed)
token = jwt.encode({"sub": user_id, "exp": expire}, SECRET_KEY, algorithm="HS256")
payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])    # raises jwt.InvalidTokenError
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")     # reads "Authorization: Bearer ..."
```

### 19.8 Status codes

| Code | Use |
|---|---|
| 200 | OK (GET/PUT/PATCH) |
| 201 | Created (POST) |
| 204 | Deleted, no body |
| 400 | Bad request (invalid id, empty PATCH) |
| 401 | Not logged in / bad token |
| 403 | Logged in but not allowed |
| 404 | Doesn't exist |
| 405 | Wrong method for this path |
| 409 | Conflict (duplicate email) |
| 413 / 415 | File too big / wrong type |
| 422 | Validation failed |
| 500 | Server bug |

### 19.9 Comparison tables in one place

| `def` | `async def` |
|---|---|
| Thread pool | Event loop |
| Blocking libs (sync PyMongo, requests, pandas) | Async libs (AsyncMongoClient, httpx.AsyncClient) |
| Can't `await` | Must `await` async calls, never block |

| PUT | PATCH |
|---|---|
| Replace everything | Change some fields |
| `NoteCreate`, `model_dump()` | `NoteUpdate`, `model_dump(exclude_unset=True)` |
| `replace_one` | `update_one` / `find_one_and_update` with `$set` |

| Middleware | Dependency |
|---|---|
| Every request, sees response | Only routes that ask |
| Logging, timing, CORS | Auth, DB, shared params |

| `$regex` | `$text` |
|---|---|
| Substrings, no index, slower | Whole words, needs text index, ranked |

### 19.10 Error lookup

| You see | Likely cause |
|---|---|
| 422 `json_invalid` | Body isn't valid JSON (trailing comma, single quotes, wrong Content-Type) |
| 422 `missing` | Required field/param not sent |
| 422 `string_too_short` / `string_too_long` | Breaks `min_length` / `max_length` |
| 422 `int_parsing` / `bool_parsing` | Text couldn't convert to int/bool |
| 422 `greater_than_equal` / `less_than_equal` | Breaks `ge` / `le` |
| 422 on `/auth/login` | Sent JSON instead of form data |
| 400 "not a valid id" | Bad ObjectId string (or a route-order clash like `/notes/export`) |
| 404 | Valid request, item doesn't exist / belongs to someone else / wrong URL |
| 401 "Not authenticated" | No token sent |
| 401 "Could not validate credentials" | Expired/tampered token, or `SECRET_KEY` changed |
| 405 | Wrong HTTP method |
| 307 | Trailing slash mismatch |
| 500 `ResponseValidationError` | Your returned data doesn't match `response_model` |
| `ObjectId is not JSON serializable` | Returned raw Mongo doc; convert `_id` |
| `ServerSelectionTimeoutError` | MongoDB not running / wrong URL / Atlas IP not allowed |
| `DuplicateKeyError E11000` | Unique index violated → return 409 |
| `coroutine ... was never awaited` | Missing `await` |
| Server hangs | Blocking call in `async def` |
| Browser "blocked by CORS policy" | Frontend origin not in `allow_origins` (or the route crashed) |
| `running scripts is disabled` | PowerShell execution policy |
| `[WinError 10048]` | Port in use |
| `[WinError 32]` | File still open on Windows |
| `ModuleNotFoundError: app` | Not running from project root / missing `__init__.py` / pytest `pythonpath` |
| `secret_key Field required` | `.env` missing or not loaded |

---

*Happy building! 🚀*
