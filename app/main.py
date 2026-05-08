from __future__ import annotations

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from . import config, llm, rag, stt, tts
from .routes import router


@asynccontextmanager
async def lifespan(app: FastAPI):
    print("[startup] loading RAG corpus and embeddings ...")
    rag.load()
    print("[startup] loading Kokoro TTS ...")
    tts.load()
    print("[startup] warming up Whisper ...")
    stt.warmup()
    print("[startup] warming up LLM ...")
    llm.warmup()
    print("[startup] ready.")
    yield


app = FastAPI(title="HMK — Offline Company AI", lifespan=lifespan)
app.include_router(router)
app.mount("/static", StaticFiles(directory=str(config.STATIC_DIR)), name="static")


@app.get("/")
def index() -> FileResponse:
    return FileResponse(str(config.STATIC_DIR / "index.html"))


@app.get("/health")
def health() -> dict:
    return {"ok": True}
