from __future__ import annotations

from pathlib import Path

import mlx_whisper

from . import config


def warmup() -> None:
    # First call downloads weights and JITs MLX kernels; do it before serving traffic.
    silent = Path("/tmp/_hmk_silent.wav")
    if not silent.exists():
        import wave
        with wave.open(str(silent), "wb") as w:
            w.setnchannels(1)
            w.setsampwidth(2)
            w.setframerate(16000)
            w.writeframes(b"\x00\x00" * 16000)
    mlx_whisper.transcribe(str(silent), path_or_hf_repo=config.WHISPER_MODEL)


def transcribe(wav_path: Path) -> str:
    result = mlx_whisper.transcribe(
        str(wav_path), path_or_hf_repo=config.WHISPER_MODEL
    )
    return result["text"].strip()
