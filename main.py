from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import sqlite3
import os
from supabase import create_client, Client
from dotenv import load_dotenv
from fastapi import Header
from fastapi import Depends, Response


app = FastAPI()

load_dotenv()

url: str = os.environ.get("SUPABASE_URL")
key: str = os.environ.get("SUPABASE_KEY")
supabase: Client = create_client(url, key)

@app.on_event("startup")
def startup_event():
    init_db()
    print("Server running and connected to Supabase")

    
class AuthCredentials(BaseModel):
    email: str
    password: str

class Task(BaseModel):
    title: str
    done: bool = False


def init_db():
    conn = sqlite3.connect("tasks.db")
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            done BOOLEAN NOT NULL
        )
    """)

    cursor.execute("SELECT COUNT(*) FROM tasks")
    count = cursor.fetchone()[0]

    if count == 0:
        example_tasks = [
            ("Learn Python", 0),
            ("Build a SQLite database", 0),
            ("Commit to git", 0)
        ]
        cursor.executemany("INSERT INTO tasks (title, done) VALUES (?, ?)", example_tasks)
        conn.commit()

    conn.close()


@app.get("/")
def read_root():
    return {
            "name":"Task API",
            "version":"1.0",
            "enpoints":["/tasks"]
            }

@app.get("/health")
def test_server_health():
    return {"status": "ok"}

def verify_auth_token(authorization: str = Header(None)):
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail={"error": "Access token required"})

    token = authorization.split(" ")[1]
    if not token:
        raise HTTPException(status_code=401, detail={"error": "Access token required"})

    try:
        user_response = supabase.auth.get_user(token)
        return {"user": user_response.user, "token": token}
    except Exception:
        raise HTTPException(status_code=401, detail={"error": "Invalid or expired token"})

@app.post("/auth/signup", status_code=201)
def signup(credentials: AuthCredentials):
    if not credentials.email or not credentials.password:
        raise HTTPException(status_code=400, detail="Bad Request")

    try:
        response = supabase.auth.sign_up({
            "email": credentials.email,
            "password": credentials.password
        })
        return response
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/auth/login", status_code=200)
def login(credentials: AuthCredentials):
    if not credentials.email or not credentials.password:
        raise HTTPException(status_code=400, detail="Bad Request")

    try:
        response = supabase.auth.sign_in_with_password({
            "email": credentials.email,
            "password": credentials.password
        })
        return {
            "access_token": response.session.access_token,
            "refresh_token": response.session.refresh_token
        }
    except Exception:
        raise HTTPException(status_code=401, detail={"error": "Invalid login credentials"})


@app.get("/public/info", status_code=200)
def public_info():
    return {"message": "Welcome stranger! This info is public."}

@app.get("/protected/profile", status_code=200)
def protected_profile(auth_data: dict = Depends(verify_auth_token)):
    return {
        "status": "success",
        "user": auth_data["user"]
    }

@app.get("/protected/dashboard", status_code=200)
def protected_dashboard(auth_data: dict = Depends(verify_auth_token)):
    return {
        "status": "success",
        "message": "Welcome to the secure dashboard",
        "user": auth_data["user"]
    }

@app.post("/auth/logout", status_code=204)
def logout(auth_data: dict = Depends(verify_auth_token)):
    try:
        supabase.auth.sign_out()
        return Response(status_code=204)
    except Exception:
        raise HTTPException(status_code=400, detail={"error": "Logout failed"})
        
            
@app.get("/tasks")
def get_all_tasks():
    conn = sqlite3.connect("tasks.db")
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT id, title, done FROM tasks")
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]

@app.get("/task/{task_id}")
def get_task_by_id(task_id: int):
    conn = sqlite3.connect("tasks.db")
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT id, title, done FROM tasks WHERE id = ?", (task_id,))
    row = cursor.fetchone()
    conn.close()

    if row is None:
        raise HTTPException(status_code=404, detail={"error": "Task not found"})
    return dict(row)


@app.post("/tasks")
async def create_task(task: Task):
    if not task.title:
        raise HTTPException(status_code=400, detail="Title is missing")

    conn = sqlite3.connect("tasks.db")
    cursor = conn.cursor()
    cursor.execute("INSERT INTO tasks (title, done) VALUES (?, ?)", (task.title, int(task.done)))
    conn.commit()
    new_id = cursor.lastrowid
    conn.close()

    return {
        "status": "ok",
        "code": 201,
        "msg": "task Created",
        "id": new_id
    }

@app.put("/tasks/{id}")
async def update_task(id: int, task: Task):
    conn = sqlite3.connect("tasks.db")
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM tasks WHERE id = ?", (id,))
    if not cursor.fetchone():
        conn.close()
        raise HTTPException(status_code=404, detail={"error": "Task not found"})

    cursor.execute("UPDATE tasks SET title = ?, done = ? WHERE id = ?", (task.title, int(task.done), id))
    conn.commit()
    conn.close()
    return {
        "status": "ok",
        "code": 200,
        "msg": "task updated"
    }

@app.delete("/tasks/{id}")
async def delete_task(id: int):
    conn = sqlite3.connect("tasks.db")
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM tasks WHERE id = ?", (id,))
    if not cursor.fetchone():
        conn.close()
        raise HTTPException(status_code=404, detail={"error": "Task not found"})

    cursor.execute("DELETE FROM tasks WHERE id = ?", (id,))
    conn.commit()
    conn.close()
    return {
        "status": "ok",
        "code": 200,
        "msg": "task removed"
    }

