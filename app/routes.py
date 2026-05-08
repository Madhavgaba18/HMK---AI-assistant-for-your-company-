from __future__ import annotations

import base64

from fastapi import APIRouter, File, Form, HTTPException, UploadFile
from pydantic import BaseModel

from . import audio, llm, stt, tts


router = APIRouter(prefix="/api")


class ChatRequest(BaseModel):
    message: str
    session_id: str = "default"


class ChatResponse(BaseModel):
    reply: str


@router.post("/chat", response_model=ChatResponse)
def chat(req: ChatRequest) -> ChatResponse:
    if not req.message.strip():
        raise HTTPException(400, "message is empty")
    return ChatResponse(reply=llm.answer(req.message, req.session_id))


@router.post("/voice")
async def voice(
    audio_file: UploadFile = File(...),
    session_id: str = Form("default"),
):
    raw = await audio_file.read()
    if not raw:
        raise HTTPException(400, "empty audio upload")

    suffix = ".webm"
    if audio_file.content_type and "mp4" in audio_file.content_type:
        suffix = ".mp4"
    elif audio_file.content_type and "ogg" in audio_file.content_type:
        suffix = ".ogg"

    wav_path = audio.to_wav_16k_mono(raw, suffix=suffix)
    try:
        transcript = stt.transcribe(wav_path)
    finally:
        wav_path.unlink(missing_ok=True)

    if not transcript:
        raise HTTPException(400, "no speech detected")

    reply = llm.answer(transcript, session_id)
    audio_b64 = base64.b64encode(tts.synthesize(reply)).decode("ascii")
    return {"transcript": transcript, "reply": reply, "audio_b64": audio_b64}


@router.post("/reset")
def reset(req: ChatRequest):
    llm.reset(req.session_id)
    return {"ok": True}
