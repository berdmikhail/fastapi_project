import os
import sqlite3
from contextlib import asynccontextmanager
from typing import Optional

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

DB_DIR = os.getenv("DB_DIR", "/app/data")
DB_PATH = os.path.join(DB_DIR, "todo.db")


def get_connection():
    os.makedirs(DB_DIR, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    with get_connection() as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS items (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                description TEXT,
                completed BOOLEAN NOT NULL DEFAULT 0
            )
            """
        )
        conn.commit()


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield


app = FastAPI(title="ToDo Service", lifespan=lifespan)


class ItemCreate(BaseModel):
    title: str
    description: Optional[str] = None
    completed: bool = False


class ItemUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    completed: Optional[bool] = None


@app.post("/items", status_code=201)
def create_item(item: ItemCreate):
    with get_connection() as conn:
        cursor = conn.execute(
            "INSERT INTO items (title, description, completed) VALUES (?, ?, ?)",
            (item.title, item.description, int(item.completed)),
        )
        conn.commit()
        item_id = cursor.lastrowid
    return {
        "id": item_id,
        "title": item.title,
        "description": item.description,
        "completed": item.completed,
    }


@app.get("/items")
def get_items():
    with get_connection() as conn:
        rows = conn.execute("SELECT * FROM items").fetchall()
    return [
        {
            "id": row["id"],
            "title": row["title"],
            "description": row["description"],
            "completed": bool(row["completed"]),
        }
        for row in rows
    ]


@app.get("/items/{item_id}")
def get_item(item_id: int):
    with get_connection() as conn:
        row = conn.execute("SELECT * FROM items WHERE id = ?", (item_id,)).fetchone()
    if row is None:
        raise HTTPException(status_code=404, detail="Item not found")
    return {
        "id": row["id"],
        "title": row["title"],
        "description": row["description"],
        "completed": bool(row["completed"]),
    }


@app.put("/items/{item_id}")
def update_item(item_id: int, item: ItemUpdate):
    with get_connection() as conn:
        row = conn.execute("SELECT * FROM items WHERE id = ?", (item_id,)).fetchone()
        if row is None:
            raise HTTPException(status_code=404, detail="Item not found")

        new_title = item.title if item.title is not None else row["title"]
        new_description = item.description if item.description is not None else row["description"]
        new_completed = item.completed if item.completed is not None else bool(row["completed"])

        conn.execute(
            "UPDATE items SET title = ?, description = ?, completed = ? WHERE id = ?",
            (new_title, new_description, int(new_completed), item_id),
        )
        conn.commit()

    return {
        "id": item_id,
        "title": new_title,
        "description": new_description,
        "completed": new_completed,
    }


@app.delete("/items/{item_id}")
def delete_item(item_id: int):
    with get_connection() as conn:
        cursor = conn.execute("DELETE FROM items WHERE id = ?", (item_id,))
        conn.commit()
    if cursor.rowcount == 0:
        raise HTTPException(status_code=404, detail="Item not found")
    return {"detail": "Item deleted"}