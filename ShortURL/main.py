import os
import secrets
import sqlite3
import string
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import RedirectResponse
from pydantic import BaseModel, HttpUrl

DB_DIR = os.getenv("DB_DIR", "/app/data")
DB_PATH = os.path.join(DB_DIR, "shorturl.db")


def get_connection():
    os.makedirs(DB_DIR, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    with get_connection() as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS urls (
                short_id TEXT PRIMARY KEY,
                full_url TEXT NOT NULL
            )
            """
        )
        conn.commit()


def generate_short_id(length: int = 6) -> str:
    alphabet = string.ascii_letters + string.digits
    return "".join(secrets.choice(alphabet) for _ in range(length))


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield


app = FastAPI(title="Short URL Service", lifespan=lifespan)


class URLRequest(BaseModel):
    url: HttpUrl


@app.post("/shorten")
def shorten_url(payload: URLRequest, request: Request):
    full_url = str(payload.url)
    with get_connection() as conn:
        while True:
            short_id = generate_short_id()
            exists = conn.execute(
                "SELECT 1 FROM urls WHERE short_id = ?", (short_id,)
            ).fetchone()
            if not exists:
                break

        conn.execute(
            "INSERT INTO urls (short_id, full_url) VALUES (?, ?)",
            (short_id, full_url),
        )
        conn.commit()

    base_url = str(request.base_url).rstrip("/")
    return {
        "short_id": short_id,
        "short_url": f"{base_url}/{short_id}",
        "full_url": full_url,
    }


@app.get("/stats/{short_id}")
def get_stats(short_id: str):
    with get_connection() as conn:
        row = conn.execute(
            "SELECT short_id, full_url FROM urls WHERE short_id = ?", (short_id,)
        ).fetchone()
    if row is None:
        raise HTTPException(status_code=404, detail="Short URL not found")
    return {
        "short_id": row["short_id"],
        "full_url": row["full_url"],
    }


@app.get("/{short_id}")
def redirect_to_url(short_id: str):
    with get_connection() as conn:
        row = conn.execute(
            "SELECT full_url FROM urls WHERE short_id = ?", (short_id,)
        ).fetchone()
    if row is None:
        raise HTTPException(status_code=404, detail="Short URL not found")
    return RedirectResponse(url=row["full_url"], status_code=307)