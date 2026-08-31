from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import sqlite3

app = FastAPI()



class Task(BaseModel):
    title: str
    done: bool = False

tasks = [
        {
                "id": 1,
                "title": "first task",
                "done": False

        },
        {
                "id": 2,
                "title": "task 2",
                "done": False
        },
        {
                "id": 3,
                "title": "task 3",
                "done": False
        }
    ]
    
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

@app.on_event("startup")
def startup_event():
    init_db()

@app.get("/")
def read_root():
    return {
            "name":"Task API",
            "version":"1.0",
            "enpoints":["/tasks"]
            }

@app.get("health")
def test_server_health():
    return {"status": "ok"}

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
    cursor.execute("SELECT id, title, done FROM tasks WHERE id = ?", (id,))
    row = cursor.fetchone()
    conn.close()

    if row is None:
        raise HTTPException(status_code=404, detail={"error": "Task not found"})
    return dict(row)


@app.post("/tasks")
async def create_task(task: Task):
    if not task.title:
        raise HTTPException(status_code=400, detail="Title is missing")

    task = {
            "id": tasks[-1]["id"] + 1,
            "title": task.title ,
            "done": False,
            }
    tasks.append(task) 
    return {
            "status": "ok",
            "code": 201,
            "msg": "task Created"
            }

@app.put("/tasks/{id}")
async def update_task(id: int, task: Task):
    if not id:
        return {
            "status": "bad",
            "code": 404,
            "msg": "id is not enterd, pls enter a valid id"
            }
    for task_loop in tasks:
        if task_loop["id"] == id:
            task_loop["title"] = task.title
            return {
            "status": "ok",
            "code": 201,
            "msg": "task updated"
            }
    raise HTTPException(status_code=404, detail="Task not found")

@app.delete("/tasks/{id}")
async def delete_task(id: int):
    if not id:
        return {
            "status": "bad",
            "code": 404,
            "msg": "id is not enterd, pls enter a valid id"
            }
    for task in tasks:
        if task["id"] == id:
            tasks.remove(task)
    return {
            "status": "ok",
            "code": 200,
            "msg": "task removed"
            }
