from __future__ import annotations

import shutil
import subprocess
import tempfile
from pathlib import Path


def to_wav_16k_mono(input_bytes: bytes, suffix: str = ".webm") -> Path:
    if not shutil.which("ffmpeg"):
        raise RuntimeError("ffmpeg not found on PATH. Run: brew install ffmpeg")

    in_file = Path(tempfile.mkstemp(suffix=suffix)[1])
    out_file = Path(tempfile.mkstemp(suffix=".wav")[1])
    in_file.write_bytes(input_bytes)

    subprocess.run(
        [
            "ffmpeg", "-y", "-loglevel", "error",
            "-i", str(in_file),
            "-ar", "16000", "-ac", "1", "-f", "wav",
            str(out_file),
        ],
        check=True,
    )
    in_file.unlink(missing_ok=True)
    return out_file
